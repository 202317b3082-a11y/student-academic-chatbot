from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

FAISS_DIR = "faiss_index"
CACHE_DIR = "hf_cache"   # local folder for model caching

# Initialize embedding model with local cache
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder=CACHE_DIR
)

def load_text_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def split_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks

def create_embeddings_from_file(file_path):
    text = load_text_file(file_path)

    texts = split_text(text, chunk_size=500, overlap=50)

    vectorstore = FAISS.from_texts(texts, embeddings)

    vectorstore.save_local(FAISS_DIR)

    print(f"✅ Embeddings created from '{file_path}'")
    print(f"✅ FAISS saved to '{FAISS_DIR}'")
    print(f"✅ Model cached in '{CACHE_DIR}'")

if __name__ == "__main__":
    create_embeddings_from_file("college_policy.txt")