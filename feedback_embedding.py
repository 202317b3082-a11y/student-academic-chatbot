import os
import pandas as pd
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

CSV_PATH = "feedback.csv"
FAISS_DIR = "faiss_feedback_index"


def safe_get(row, key, default=""):
    """Safely get column value"""
    return row[key] if key in row and pd.notna(row[key]) else default


def build_and_store_feedback_embeddings():
    # 1. Load CSV
    if not os.path.exists(CSV_PATH):
        print("❌ feedback.csv not found")
        return

    df = pd.read_csv(CSV_PATH)

    if df.empty:
        print("❌ CSV is empty")
        return

    print(f"📊 Loaded {len(df)} rows")

    documents = []

    # 2. Convert rows → Documents (user_query only)
    for i, row in df.iterrows():
        try:
            user_query = safe_get(row, "user_query")

            # Skip if no user query
            if not user_query:
                continue

            # Generate embedding only from user_query
            content = user_query

            metadata = {}

            documents.append(
                Document(
                    page_content=content,
                    metadata=metadata
                )
            )

        except Exception as e:
            print(f"⚠️ Skipping row {i}: {e}")

    if not documents:
        print("❌ No valid documents found")
        return

    print(f"✅ Processed {len(documents)} valid documents")

    # 3. Create embeddings directly (no splitting needed for user queries only)
    print("🧠 Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # 4. Create OR update FAISS index
    if os.path.exists(FAISS_DIR):
        print("📂 Existing index found → updating...")
        vectorstore = FAISS.load_local(
            FAISS_DIR,
            embeddings,
            allow_dangerous_deserialization=True
        )
        vectorstore.add_documents(documents)
    else:
        print("🆕 Creating new index...")
        vectorstore = FAISS.from_documents(documents, embeddings)

    # 5. Save index
    vectorstore.save_local(FAISS_DIR)

    print("✅ Feedback embeddings created/updated successfully!")


if __name__ == "__main__":
    build_and_store_feedback_embeddings()