import json
import os
import csv
import html
from typing import Dict, List

try:
    from langchain_community.vectorstores import FAISS
    from langchain_huggingface import HuggingFaceEmbeddings
    FAISS_DIR = "faiss_feedback_index"
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = None
    if os.path.isdir(os.path.join(os.path.dirname(__file__), FAISS_DIR)):
        vectorstore = FAISS.load_local(FAISS_DIR, embeddings, allow_dangerous_deserialization=True)
        use_faiss = True
    else:
        use_faiss = False
except Exception:
    use_faiss = False
    vectorstore = None

FB_CSV = os.path.join(os.path.dirname(__file__), 'feedback.csv')


def similarity_to_confidence(score: float) -> float:
    """
    Convert FAISS distance score to confidence (0–100).

    FAISS distance logic:
    - Lower score = higher similarity
    - Scaled inverse to avoid overly low confidence
    """
    confidence = 100 / (1 + score * 0.3)
    return round(max(0.0, min(100.0, confidence)), 2)


def _fallback_hint(query: str, limit: int = 5) -> str:
    if not os.path.exists(FB_CSV):
        return ""

    query_l = query.strip().lower()
    matches = []

    with open(FB_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            q = row.get('user_query') or row.get('query') or ''
            if query_l in q.lower():
                matches.append((q, row.get('user_email', '')))
            if len(matches) >= limit:
                break

    if not matches:
        return ""

    items = []
    for q, email in matches:
        safe_q = html.escape(q)
        safe_email = html.escape(email)
        items.append(f"<li>{safe_q} <span style='color:#94a3b8;font-size:12px'>(from {safe_email})</span></li>")

    return f"<ul>{''.join(items)}</ul>"


def hint(query: str) -> str:
    if not query:
        return ""

    if use_faiss and vectorstore is not None:
        try:
            results = vectorstore.similarity_search_with_score(query, k=5)
            items = []
            for doc, score in results:
                content = getattr(doc, 'page_content', str(doc))
                safe_content = html.escape(content)
                items.append(f"<li>{safe_content} <span style='color:#94a3b8;font-size:12px'>(score: {round(score,2)})</span></li>")
            if items:
                return f"<ul>{''.join(items)}</ul>"
        except Exception:
            pass

    return _fallback_hint(query)


if __name__ == "__main__":
    while True:
        question = input("Ask a question (or type 'exit'): ").strip()

        if question.lower() == "exit":
            break

        result = hint(question)
        print(json.dumps(result, indent=2, ensure_ascii=False))