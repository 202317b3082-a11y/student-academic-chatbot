import json
import os

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

FAISS_DIR = "faiss_index"
POLICY_FILE = "college_policy.txt"


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


# Load full paragraphs from policy file
def load_policy_paragraphs():
    """Load full paragraphs from college_policy.txt"""
    if not os.path.exists(POLICY_FILE):
        return []
    
    with open(POLICY_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by double newlines to get paragraphs
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    return paragraphs


embeddings = get_embeddings()
vectorstore = load_vectorstore(embeddings)
policy_paragraphs = load_policy_paragraphs()


def similarity_to_confidence(score: float) -> float:
    confidence = 100 / (1 + score * 0.3)
    return max(0.0, min(100.0, confidence))



def find_full_paragraph(chunk_text: str) -> str:
    """Find and return the full paragraph containing the chunk text."""
    for para in policy_paragraphs:
        if chunk_text in para or para in chunk_text:
            return para
    return chunk_text


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
        responses.append(doc.page_content)

    overall_confidence = sum(confidences) / len(confidences)

    return {
        "response": responses,
        "confidence": round(overall_confidence, 2)
    }



# CLI test
if __name__ == "__main__":
    print("Academic Chatbot - Logic Response Test")
    print("=" * 50)
    print("Type 'exit' to quit\n")
    
    while True:
        q = input("Ask: ").strip()
        if q.lower() == "exit":
            break
        if not q:
            continue
            
        result = nlpcall(q)
        print(f"\nConfidence: {result['confidence']}")
        print(f"Response Count: {len(result['response'])}")
        print("\nResponses:")
        for i, resp in enumerate(result['response'], 1):
            print(f"\n{i}. {resp[:200]}..." if len(resp) > 200 else f"\n{i}. {resp}")
        print("\n" + "=" * 50 + "\n")

        q = input("Ask: ")
        if q.lower() == "exit":
            break
        print(json.dumps(nlpcall(q), indent=2))