import json
import os

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

FAISS_DIR = "faiss_index"


# Load embeddings
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


# Load FAISS index
def load_vectorstore(embeddings):
    if not os.path.exists(FAISS_DIR):
        raise Exception("❌ FAISS index not found. Run create_index.py first.")

    return FAISS.load_local(
        FAISS_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )


embeddings = get_embeddings()
vectorstore = load_vectorstore(embeddings)


# Convert similarity score → confidence
def similarity_to_confidence(score: float) -> float:
    confidence = 100 / (1 + score * 0.3)
    return max(0.0, min(100.0, confidence))


def nlpcall(query: str) -> dict:
    results = vectorstore.similarity_search_with_score(query, k=3)

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
        responses.append(doc.page_content)

    overall_confidence = sum(confidences) / len(confidences)

    return {
        "response": responses,
        "confidence": round(overall_confidence, 2)
    }


# CLI test
if __name__ == "__main__":
    while True:
        q = input("Ask: ")
        if q.lower() == "exit":
            break
        print(json.dumps(nlpcall(q), indent=2))