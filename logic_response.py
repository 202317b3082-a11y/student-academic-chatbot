import os
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# ================= CONFIG =================
FAISS_DIR = "faiss_index"
POLICY_FILE = "college_policy.txt"

MODEL_NAME = "google/flan-t5-small"  # fast model
MODEL_DIR = "models/flan-t5-small"

# ================= MODEL SETUP =================
def setup_model():
    print("🧠 Checking model...")

    if not os.path.exists(MODEL_DIR):
        print("⬇️ Model not found. Downloading...")

        os.makedirs(MODEL_DIR, exist_ok=True)

        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

        tokenizer.save_pretrained(MODEL_DIR)
        model.save_pretrained(MODEL_DIR)

        print("✅ Model downloaded & saved")

    else:
        print("✅ Using local model")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, local_files_only=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_DIR, local_files_only=True)

    return tokenizer, model


# ================= GENERATE ANSWER =================
def generate_answer(query, context):
    prompt = f"""
You are an academic assistant chatbot.

Answer the question using ONLY the provided context.

Rules:
- Answer must be between 50 to 60 words
- Be clear and complete
- Do not use outside knowledge
- Avoid repetition

Context:
{context}

Question:
{query}

Answer:
"""

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    outputs = model.generate(
        **inputs,
        max_new_tokens=220,
        min_new_tokens=50,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
        no_repeat_ngram_size=3,
        num_beams=2
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True).strip()


# ================= EMBEDDINGS =================
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


# ================= LOAD FAISS =================
def load_vectorstore(embeddings):
    if not os.path.exists(FAISS_DIR):
        raise Exception("❌ FAISS index not found. Run create_index.py first.")

    return FAISS.load_local(
        FAISS_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )


# ================= LOAD PARAGRAPHS =================
def load_policy_paragraphs():
    if not os.path.exists(POLICY_FILE):
        return []

    with open(POLICY_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    return [p.strip() for p in content.split("\n\n") if p.strip()]


# ================= CONFIDENCE =================
def similarity_to_confidence(score):
    confidence = 100 / (1 + score * 0.3)
    return max(0, min(100, confidence))


# ================= PARAGRAPH MATCH =================
def find_full_paragraph(chunk_text):
    for para in policy_paragraphs:
        if chunk_text in para or para in chunk_text:
            return para
    return chunk_text


# ================= INIT =================
print("🚀 Initializing...")

tokenizer, model = setup_model()

print("📦 Loading embeddings & FAISS...")
embeddings = get_embeddings()
vectorstore = load_vectorstore(embeddings)
policy_paragraphs = load_policy_paragraphs()


# ================= ✅ YOUR SAME FUNCTION =================
def nlpcall(query):
    results = vectorstore.similarity_search_with_score(query, k=2)

    if not results:
        return {"response": ["No relevant answer found"], "confidence": 0.0}

    confidences = []
    context = ""

    for doc, score in results:
        confidences.append(similarity_to_confidence(score))
        context += find_full_paragraph(doc.page_content) + "\n\n"

    answer = generate_answer(query, context)

    return {
        "response": [answer],
        "confidence": round(sum(confidences) / len(confidences), 2)
    }


# ================= CLI =================
if __name__ == "__main__":
    print("\n🎓 Academic Chatbot (Auto Download + Offline)")
    print("=" * 60)

    while True:
        query = input("\nAsk: ").strip()

        if query.lower() == "exit":
            print("👋 Exiting...")
            break

        if not query:
            continue

        result = nlpcall(query)

        print(f"\n📊 Confidence: {result['confidence']}%")
        print("\n✅ Response:\n")

        for resp in result["response"]:
            print(resp)

        print("\n" + "=" * 60)