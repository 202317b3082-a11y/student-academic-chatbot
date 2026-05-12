import json

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


FAISS_DIR = "faiss_index"


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.load_local(
    FAISS_DIR,
    embeddings,
    allow_dangerous_deserialization=True
)


def similarity_to_confidence(score: float) -> float:
    """
    Convert FAISS distance score to a confidence score between 0 and 100.

    Uses a scaled inverse formula to boost confidence values.
    Lower score => higher confidence.
    """
    confidence = 100 / (1 + score * 0.3)
    return max(0.0, min(100.0, confidence))


def nlpcall(query: str) -> dict:
    """
    Search FAISS index and return response with overall confidence.

    Returns:
        dict: {
            "response": list of matching document contents,
            "confidence": overall confidence percentage
        }
    """
    results = vectorstore.similarity_search_with_score(query, k=3)

    confidences = []
    content_parts = []

    for doc, score in results:
        confidence = similarity_to_confidence(score)
        confidences.append(confidence)
        content_parts.append(doc.page_content)

    overall_confidence = (
        sum(confidences) / len(confidences)
        if confidences
        else 0.0
    )

    return {
        "response": content_parts,
        "confidence": float(round(overall_confidence, 2))
    }


if __name__ == "__main__":
    while True:
        question = input("Ask a question (or type 'exit'): ")

        if question.lower() == "exit":
            break

        result = nlpcall(question)

        print(json.dumps(result, indent=2, ensure_ascii=False))