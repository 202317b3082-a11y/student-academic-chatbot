# Student Academic Chatbot

A Flask-based intelligent chatbot system designed to answer student queries about college policies, academic procedures, and administrative guidelines using Natural Language Processing (NLP) and vector-based semantic search.

## Features

- **User Authentication**: Secure JWT-based authentication system
- **Admin Dashboard**: Manage users and knowledge base
- **NLP-Powered Search**: Semantic search using FAISS vector database
- **Feedback System**: Collect and learn from user feedback
- **Query Suggestions**: Intelligent suggestions based on similar past queries
- **Multi-role Support**: Student and Admin roles with different permissions

## Project Structure

```
StudentAcademicChatbot/
├── public/                          # Front‑end (HTML/CSS/JS)
│   ├── ChatUI.html                 # Chat interface for students
│   ├── admin.html                  # Admin dashboard UI
│   ├── login.html                  # Login page
│   └── signup.html                 # Sign‑up page
├── flask_app.py                    # Flask app, routes, JWT authentication
├── logic_response.py               # Core query processing & FAISS search
├── suggestion.py                   # Suggestion engine (feedback index)
├── feedback_embedding.py           # Generates embeddings for feedback data
├── evaluation.py                   # Evaluation metrics and scripts
├── db.py                           # SQLite wrapper for users.db
├── create_embedding.py             # Builds main knowledge‑base FAISS index
├── create_admin.py                 # Creates initial admin account
├── college_policy.txt              # Knowledge‑base source document
├── users.db                        # SQLite database for user accounts
├── feedback.csv                    # Logged user feedback
├── faiss_index/                    # Primary FAISS index (index.faiss, index.pkl)
├── faiss_feedback_index/           # Feedback FAISS index (index.faiss, index.pkl)
├── requirements.txt                # Python dependencies
├── __pycache__/                    # Python bytecode cache
├── hf_cache/                       # HuggingFace model cache
└── README.md                       # Project documentation
```

## Prerequisites

- **Python**: 3.8 or higher
- **pip**: Python package manager

## Installation Steps

### 1. Clone or Download the Project

```bash
# Navigate to your workspace
cd d:\prabh\collage-ai-main
```

### 2. Install Dependencies (no virtual environment required)

```bash
pip install -r requirements.txt
```

The following packages will be installed by `pip`:

- Flask & Flask‑CORS: Web framework and cross‑origin support
- PyJWT: JWT authentication tokens
- Werkzeug: Security utilities
- LangChain: LLM orchestration framework
- FAISS: Vector similarity search
- Sentence‑Transformers: Embedding generation (all‑MiniLM‑L6‑v2)
- PyTorch: Deep learning framework (required by transformers)
- Pandas & NumPy: Data processing
### 4. Initialize the Knowledge Base (One-time Setup)

Generate embeddings from the college policy file:

```bash
python create_embedding.py
```

This creates the `faiss_index/` directory with vector embeddings from `college_policy.txt`.

### 5. Generate Feedback Embeddings (Optional but Recommended)

Create embeddings from historical feedback for better suggestions:

```bash
python feedback_embedding.py
```

This creates the `faiss_feedback_index/` directory.

### 6. Create Admin User (One-time Setup)

Set up the initial admin account:

```bash
python create_admin.py
```

You'll be prompted to enter:
- Admin email
- Admin password
- Admin name

### 7. Run the Flask Application

```bash
python flask_app.py
```

The application will start on `http://localhost:5000`

### 8. Access the Application

Open your browser and navigate to:

```
http://localhost:5000
```

You'll be directed to the login page. Sign up or log in with your credentials.

## Usage Guide

### For Students

1. **Sign Up**: Create an account with email and password at `/signup`
2. **Login**: Log in with your credentials - you'll be automatically redirected to **ChatUI.html**
3. **Chat**: Ask questions about academic policies, procedures, evaluation criteria, etc.
4. **View Suggestions**: See similar past queries for context
5. **Provide Feedback**: Rate chatbot responses (yes/no) to improve future answers

### For Administrators

1. **Sign Up/Login**: Use admin credentials
2. **Auto-redirect**: Upon login, admins are automatically redirected to **admin.html**
3. **Access Admin Dashboard**: View at `/admin` (auto-redirected after login)
4. **Manage Users**: View and manage registered users
5. **Update Knowledge Base**: Add or modify college policies
6. **View Analytics**: See feedback and response metrics

## Login Flow

The application uses role-based automatic redirection:

- **Students**: Login → Automatic redirect to `/chat` (ChatUI.html)
- **Admins**: Login → Automatic redirect to `/admin` (admin.html)

The redirect is determined by the user's role stored in the database and sent by the server in the login response.

## Key API Endpoints

### Authentication
- `POST /signup` - Register a new user
- `POST /login` - Login and get JWT token
- `GET /logout` - Logout and clear session
- `GET /me` - Get current user info

### Chat
- `POST /chat` - Send query and get response with confidence score and suggestions

### Feedback
- `POST /feedback` - Submit feedback on a response

### Admin
- `GET /admin` - Admin dashboard
- `GET /users` - List all users (admin only)
- `POST /user/<email>/role` - Update user role (admin only)

## Configuration

Edit `flask_app.py` to modify:

```python
app.config["SECRET_KEY"] = "swastik"  # Change this to a secure key
app.config["JWT_EXPIRY_HOURS"] = 2    # JWT token expiry time
```

## Embedding Models

The project uses **sentence-transformers/all-MiniLM-L6-v2** for generating semantic embeddings:
- Fast and efficient
- Suitable for semantic similarity search
- Pre-trained on large text datasets

## Database

- **users.db**: SQLite database storing user information and authentication
- **feedback.csv**: CSV file logging user queries, responses, and feedback ratings

## Troubleshooting

### Issue: "FAISS index not found"
**Solution**: Run `python create_embedding.py` to generate the knowledge base embeddings.

### Issue: "ModuleNotFoundError: No module named 'langchain'"
**Solution**: Ensure dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: "Port 5000 already in use"
**Solution**: Modify the port in `flask_app.py`:
```python
app.run(debug=True, port=5001)  # Use a different port
```

### Issue: JWT token expired
**Solution**: Login again. Token expiry is set to 2 hours by default (configurable).

### Issue: Embedding model not downloading
**Solution**: Ensure you have internet connection. The first run will download the embedding model (~130MB).

## Performance Optimization

For better performance:

1. **Use GPU**: Install `torch` with CUDA support for faster embeddings
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

2. **Enable Debug Mode**: Set `debug=True` in development
   ```python
   app.run(debug=True)
   ```

3. **Production Deployment**: Use a production WSGI server like Gunicorn
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 flask_app:app
   ```

## Environment Variables (Optional)

Create a `.env` file for sensitive configuration:

```
FLASK_SECRET_KEY=your-secret-key
JWT_EXPIRY_HOURS=2
DEBUG=True
```

## Development Notes

- **Testing**: Run `python evaluation.py` to evaluate chatbot response quality
- **Logs**: Check console output for detailed operation logs
- **Cache**: Clear `__pycache__/` if experiencing import issues
  ```bash
  rm -r __pycache__  # macOS/Linux
  rmdir /s __pycache__  # Windows
  ```

## Dependencies Breakdown

| Package | Version | Purpose |
|---------|---------|---------|
| Flask | 3.0.0 | Web framework |
| flask-cors | 4.0.0 | Cross-origin request handling |
| PyJWT | 2.8.1 | JWT token generation/verification |
| werkzeug | 3.0.1 | Security utilities |
| langchain | 0.1.10 | LLM orchestration |
| langchain-community | 0.0.24 | LangChain community integrations |
| langchain-huggingface | 0.0.16 | HuggingFace integration |
| faiss-cpu | 1.7.4.post1 | Vector similarity search |
| sentence-transformers | 2.2.2 | Embedding generation |
| torch | 2.1.1 | Deep learning framework |
| pandas | 2.1.3 | Data manipulation |
| numpy | 1.26.2 | Numerical computing |
| scikit-learn | 1.3.2 | Machine learning utilities |
| requests | 2.31.0 | HTTP client library |

## License

This project is developed for BITS Pilani students.

## Support & Feedback

For issues or suggestions, contact: supportservices@pilani.bits-pilani.ac.in
