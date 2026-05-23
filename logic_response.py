import json
import os

# ✅ FORCE OFFLINE MODE (VERY IMPORTANT)
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


FAISS_DIR = "faiss_index"
POLICY_FILE = "college_policy.txt"

# ================= LOCAL LLM =================
print("🧠 Loading local LLM (FAST MODE)...")

MODEL_NAME = "google/flan-t5-base"
# 👉 If slow, use:
# MODEL_NAME = "google/flan-t5-small"

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    local_files_only=True
)

model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
    local_files_only=True
)


def generate_answer(query, context):
    prompt = f"""
You are an academic assistant chatbot.

Read the context carefully and answer the question using ONLY the given context.

Instructions:
- Write an answer between 50 to 60 words.
- Provide a clear, complete, and informative explanation.
- Do not include any information not present in the context.
- Avoid repetition and unnecessary words.
- Keep the answer precise and easy to understand.

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

        max_new_tokens=110,       # slightly higher → more complete answers
        min_new_tokens=60,        # ensures proper length
        do_sample=True,
        temperature=0.7,          # 🔧 slightly lower → more stable
        top_p=0.9,
        no_repeat_ngram_size=3,   # ✅ prevents repetition (VERY IMPORTANT)
        num_beams=1
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)


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

    with open(POLICY_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    return paragraphs


# ================= INIT =================
print("📦 Loading embeddings & FAISS...")

embeddings = get_embeddings()
vectorstore = load_vectorstore(embeddings)
policy_paragraphs = load_policy_paragraphs()


# ================= CONFIDENCE =================
def similarity_to_confidence(score: float) -> float:
    confidence = 100 / (1 + score * 0.3)
    return max(0.0, min(100.0, confidence))


# ================= FIND FULL PARAGRAPH =================
def find_full_paragraph(chunk_text: str) -> str:
    for para in policy_paragraphs:
        if chunk_text in para or para in chunk_text:
            return para
    return chunk_text


# ================= MAIN NLP FUNCTION =================
def nlpcall(query: str) -> dict:
    results = vectorstore.similarity_search_with_score(query, k=1)

    if not results:
        return {
            "response": ["No relevant answer found"],
            "confidence": 0.0
        }

    confidences = []
    responses = []

    for doc, score in results:
        confidence = similarity_to_confidence(score)
        confidences.append(confidence)

        # ✅ full paragraph
        full_para = find_full_paragraph(doc.page_content)

        # ✅ LLM output
        answer = generate_answer(query, full_para)

        responses.append(answer)

    overall_confidence = sum(confidences) / len(confidences)

    return {
        "response": responses,
        "confidence": round(overall_confidence, 2)
    }


# ================= CLI =================
if __name__ == "__main__":
    print("\n🎓 Academic Chatbot (FAST Local RAG)")
    print("=" * 50)
    print("Type 'exit' to quit\n")

    while True:
        q = input("Ask: ").strip()

        if q.lower() == "exit":
            print("👋 Exiting...")
            break

        if not q:
            continue

        result = nlpcall(q)

        print(f"\n📊 Confidence: {result['confidence']}")
        print("\n✅ Response:\n")

        for resp in result['response']:
            print(resp)

        print("\n" + "=" * 50 + "\n")
