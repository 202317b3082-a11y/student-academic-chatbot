from flask import (
    Flask, request, jsonify, send_from_directory,
    make_response, redirect, url_for
)
from logic_response import nlpcall
from translate import translate_to_english, translate_from_english
import sqlite3
import db
import csv
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
from flask_cors import CORS
from suggestion import hint
from evaluation import evaluate, metrics

# --------------------------------------------------
# FlaskApp         Configuration
# --------------------------------------------------

app = Flask(
    __name__,
    static_folder="public",
    static_url_path=""
)

CORS(app, supports_credentials=True)

app.config["SECRET_KEY"] = "swastik"
app.config["JWT_EXPIRY_HOURS"] = 2

# --------------------------------------------------
# Initialize Database
# --------------------------------------------------

db.init_db()
db.init_responses_db()

# --------------------------------------------------
# JWT Utilities
# --------------------------------------------------

def generate_jwt(user):
    payload = {
        "email": user["email"],
        "role": user["role"],
        "exp": datetime.utcnow() + timedelta(hours=app.config["JWT_EXPIRY_HOURS"])
    }
    return jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")


def handle_unauthorized():
    if request.accept_mimetypes.accept_html:
        return redirect(url_for("login_page"))
    return jsonify({"message": "Authentication required"}), 401


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("access_token")

        if not token:
            return handle_unauthorized()

        try:
            request.user = jwt.decode(
                token,
                app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return handle_unauthorized()

        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.user.get("role") != "admin":
            return jsonify({"message": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated

# --------------------------------------------------
# Current User Info
# --------------------------------------------------

@app.route("/me", methods=["GET"])
@jwt_required
def get_current_user():
    user = db.get_user_by_email(request.user["email"])

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "name": user["name"],
        "email": user["email"],
        "role": user["role"]
    }), 200

# --------------------------------------------------
# ✅ ADMIN: Get All Users
# --------------------------------------------------

@app.route("/admin/users", methods=["GET"])
@jwt_required
@admin_required
def get_all_users():
    users = db.get_all_users()

    result = []
    for user in users:
        result.append({
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "mobile": user["mobile"],
            "role": user["role"]
        })

    return jsonify({"users": result}), 200

# --------------------------------------------------
# ✅ ADMIN: Update User Role
# --------------------------------------------------

@app.route("/admin/users/role", methods=["PUT"])
@jwt_required
@admin_required
def update_user_role():
    data = request.get_json()

    email = data.get("email")
    new_role = data.get("role")

    if not email or not new_role:
        return jsonify({"message": "Email and role are required"}), 400

    user = db.get_user_by_email(email)
    if not user:
        return jsonify({"message": "User not found"}), 404

    db.update_user_role(email, new_role)

    return jsonify({
        "message": "User role updated successfully",
        "email": email,
        "new_role": new_role
    }), 200

# --------------------------------------------------
# Admin: delete user
# --------------------------------------------------

@app.route('/admin/users/delete', methods=['DELETE'])
@jwt_required
@admin_required
def admin_delete_user():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'message': 'Email required'}), 400
    db.delete_user(email)
    return jsonify({'message': 'User deleted'}), 200

# --------------------------------------------------
# Feedback
# --------------------------------------------------

@app.route("/feedback", methods=["POST"])
@jwt_required
def feedback():
    data = request.get_json()
    CSV_FILE = "feedback.csv"

    timestamp = datetime.utcnow().isoformat()
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "timestamp", "user_query", "chatbot_response",
                "feedback", "user_email", "confidence_score"
            ])

        writer.writerow([
            timestamp,
            data.get("user_query", ""),
            data.get("bot_response", ""),
            data.get("feedback", data.get("is_helpful", "")),
            request.user["email"],
            data.get("confidence_score", "")
        ])

    return jsonify({"message": "Feedback saved successfully"}), 200

# --------------------------------------------------
# Chat API
# --------------------------------------------------

@app.route("/chat", methods=["POST"])
@jwt_required
def chat_api():
    data = request.get_json()
    message = data.get("message", "").strip()
    user_language = data.get("language", "English").strip()

    if not message:
        return jsonify({"error": "Message is required"}), 400

    try:
        # Step 1: Translate user message to English if needed
        english_message = message
        detected_language = user_language
        
        if user_language.lower() != "english":
            translate_response = translate_to_english(message, user_language)
            print("Translation response:", translate_response)
            if translate_response['success']:
                english_message = translate_response['translated_text']
            else:
                # Log error but continue with original message
                print(f"Translation warning: {translate_response.get('error', 'Unknown error')}")
                english_message = message
        
        # Step 2: Process with NLP using English text
        try:
            nlp_result = nlpcall(english_message)
            if isinstance(nlp_result, dict):
                resp = nlp_result.get("response", [])
                conf = nlp_result.get("confidence", 0)
            else:
                resp = nlp_result if nlp_result else []
                conf = 0
        except Exception as e:
            print(f"Error in nlpcall: {str(e)}")
            resp = ["I apologize, but I encountered an error processing your request. Please try again."]
            conf = 0

        # Ensure resp is a list
        if not isinstance(resp, list):
            resp = [str(resp)] if resp else ["No response generated"]

        # Step 3: Translate response back to user language if needed
        if user_language.lower() != "english":
            response_text = "\n".join(resp) if isinstance(resp, list) else str(resp)
            translate_back_response = translate_from_english(response_text, user_language)
            print("Back-translation response:", translate_back_response)
            if translate_back_response['success']:
                translated_resp = [translate_back_response['translated_text']]
            else:
                # If translation fails, return original response with warning
                print(f"Back-translation warning: {translate_back_response.get('error', 'Unknown error')}")
                translated_resp = resp
        else:
            translated_resp = resp

        # Step 4: Get hint if available
        try:
            hint_result = hint(english_message)
        except Exception as e:
            print(f"Error in hint: {str(e)}")
            hint_result = ""

        # Convert confidence to float
        try:
            conf = float(conf) if conf is not None else 0
        except (TypeError, ValueError):
            conf = 0

        return jsonify({
            "response": translated_resp,
            "confidence": conf,
            "confidence_score": conf,
            "hint": hint_result,
            "user": request.user["email"],
            "user_language": user_language,
            "detected_language": detected_language
        }), 200
    
    except Exception as e:
        print(f"Error in chat_api: {str(e)}")
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

# --------------------------------------------------
# Static Pages
# --------------------------------------------------

@app.route("/", methods=["GET"])
def root():
    return redirect(url_for("login_page"))

@app.route("/login", methods=["GET"])
def login_page():
    return send_from_directory("public", "login.html")

@app.route("/chat", methods=["GET"])
@jwt_required
def chat_page():
    return send_from_directory("public", "ChatUI.html")

@app.route("/admin", methods=["GET"])
@jwt_required
@admin_required
def admin_page():
    return send_from_directory("public", "admin.html")

@app.route('/public/<path:filename>')
def serve_public_file(filename):
    """Serve files from the public directory at /public/<filename>"""
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'public'), filename)

# --------------------------------------------------
# Signup
# --------------------------------------------------

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    if not all(data.get(k) for k in ("name", "email", "mobile", "password")):
        return jsonify({"message": "All fields are required"}), 400

    try:
        db.create_user(
            data["name"],
            data["email"],
            data["mobile"],
            generate_password_hash(data["password"]),
            "student"
        )
        return jsonify({"message": "Signup successful"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"message": "Email already exists"}), 400

# --------------------------------------------------
# Login
# --------------------------------------------------

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = db.get_user_by_email(data.get("email"))

    if not user or not check_password_hash(user["password"], data.get("password")):
        return jsonify({"message": "Invalid email or password"}), 401

    token = generate_jwt(user)

    # Determine redirect URL based on user role
    redirect_url = "/admin" if user["role"] == "admin" else "/chat"

    response = make_response(jsonify({
        "message": "Login successful",
        "redirect_url": redirect_url,
        "user": {
            "name": user["name"],
            "email": user["email"],
            "mobile": user["mobile"],
            "role": user["role"]
        }
    }))

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=app.config["JWT_EXPIRY_HOURS"] * 3600
    )

    return response, 200

# --------------------------------------------------
# Logout
# --------------------------------------------------

@app.route("/logout", methods=["POST"])
def logout():
    response = make_response(jsonify({"message": "Logged out successfully"}))
    response.set_cookie("access_token", "", expires=0)
    return response, 200

# --------------------------------------------------
# KB management endpoints
# --------------------------------------------------

KB_FILE = os.path.join(os.path.dirname(__file__), 'college_policy.txt')
KB_FILE_HI = os.path.join(os.path.dirname(__file__), 'college_policy_hi.txt')

@app.route('/admin/kb', methods=['GET'])
@jwt_required
@admin_required
def kb_list():
    q = request.args.get('q', '').strip().lower()
    lang = request.args.get('lang', 'en')
    path = KB_FILE if lang == 'en' else KB_FILE_HI
    if not os.path.exists(path):
        return jsonify({'items': []}), 200
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    parts = [p.strip() for p in content.split('\n\n') if p.strip()]
    if q:
        parts = [p for p in parts if q in p.lower()]
    items = [{'id': idx, 'text': parts[idx]} for idx in range(len(parts))]
    return jsonify({'items': items}), 200

@app.route('/admin/kb', methods=['POST'])
@jwt_required
@admin_required
def kb_add():
    data = request.get_json()
    text = data.get('text', '').strip()
    lang = data.get('lang', 'en')
    path = KB_FILE if lang == 'en' else KB_FILE_HI
    if not text:
        return jsonify({'message': 'Text required'}), 400
    with open(path, 'a', encoding='utf-8') as f:
        f.write('\n\n' + text.strip() + '\n')
    return jsonify({'message': 'Added'}), 201

@app.route('/admin/kb/<int:item_id>', methods=['PUT'])
@jwt_required
@admin_required
def kb_update(item_id):
    data = request.get_json()
    text = data.get('text', '').strip()
    lang = data.get('lang', 'en')
    path = KB_FILE if lang == 'en' else KB_FILE_HI
    if not os.path.exists(path):
        return jsonify({'message': 'KB missing'}), 404
    with open(path, 'r', encoding='utf-8') as f:
        parts = [p.strip() for p in f.read().split('\n\n') if p.strip()]
    if item_id < 0 or item_id >= len(parts):
        return jsonify({'message': 'Item not found'}), 404
    parts[item_id] = text
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(parts) + '\n')
    return jsonify({'message': 'Updated'}), 200

@app.route('/admin/kb/<int:item_id>', methods=['DELETE'])
@jwt_required
@admin_required
def kb_delete(item_id):
    lang = request.args.get('lang', 'en')
    path = KB_FILE if lang == 'en' else KB_FILE_HI
    if not os.path.exists(path):
        return jsonify({'message': 'KB missing'}), 404
    with open(path, 'r', encoding='utf-8') as f:
        parts = [p.strip() for p in f.read().split('\n\n') if p.strip()]
    if item_id < 0 or item_id >= len(parts):
        return jsonify({'message': 'Item not found'}), 404
    parts.pop(item_id)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(parts) + '\n')
    return jsonify({'message': 'Deleted'}), 200

# Admin: feedback report
@app.route('/admin/feedback', methods=['GET'])
@jwt_required
@admin_required
def admin_feedback_report():
    fb_path = os.path.join(os.path.dirname(__file__), 'feedback.csv')
    if not os.path.exists(fb_path):
        return jsonify({'items': [], 'metrics': {}}), 200
    
    # Get feedback items from CSV
    items = []
    try:
        with open(fb_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames:
                for row in reader:
                    items.append(row)
    except Exception as e:
        return jsonify({'items': [], 'metrics': {}, 'error': str(e)}), 200
    
    # Get counts from evaluate function
    eval_results = evaluate()
    
    # Get detailed metrics from evaluation module (already in decimal form 0-1)
    detailed_metrics = metrics()
    
    # Format metrics for display (convert to percentage and ensure valid numbers)
    formatted_metrics = {
        'total': eval_results.get('total', 0),
        'yes': eval_results.get('yes', 0),
        'no': eval_results.get('no', 0),
        'accuracy': round(float(detailed_metrics.get('accuracy', 0)) * 100, 2),
        'precision': round(float(detailed_metrics.get('precision', 0)) * 100, 2),
        'recall': round(float(detailed_metrics.get('recall', 0)) * 100, 2),
        'f1': round(float(detailed_metrics.get('f1', 0)) * 100, 2)
    }
    
    return jsonify({'items': items, 'metrics': formatted_metrics}), 200

# --------------------------------------------------
# Manual Admin Responses
# --------------------------------------------------

@app.route('/admin/manual-response', methods=['POST'])
@jwt_required
@admin_required
def save_manual_response():
    data = request.get_json()
    user_email = data.get('user_email', '').strip()
    question = data.get('question', '').strip()
    response = data.get('response', '').strip()
    
    if not all([user_email, question, response]):
        return jsonify({'message': 'All fields are required'}), 400
    
    try:
        db.save_manual_response(user_email, question, response)
        return jsonify({'message': 'Response saved successfully'}), 201
    except Exception as e:
        print(f"Error saving manual response: {str(e)}")
        return jsonify({'message': f'Error: {str(e)}'}), 500

@app.route('/user/responses', methods=['GET'])
@jwt_required
def get_user_responses():
    user_email = request.user['email']
    try:
        responses = db.get_user_responses(user_email)
        return jsonify({'responses': responses}), 200
    except Exception as e:
        print(f"Error fetching responses: {str(e)}")
        return jsonify({'responses': [], 'message': f'Error: {str(e)}'}), 500

@app.route('/user/response/<int:response_id>', methods=['DELETE'])
@jwt_required
def delete_user_response(response_id):
    user_email = request.user['email']
    try:
        db.delete_response(response_id, user_email)
        return jsonify({'message': 'Response deleted'}), 200
    except Exception as e:
        print(f"Error deleting response: {str(e)}")
        return jsonify({'message': f'Error: {str(e)}'}), 500
# Run App
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)