from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pickle

# =========================
# CONFIG
# =========================
MODEL_NAME = "all-MiniLM-L6-v2"
INDEX_FILE = "memory.index"
TEXT_FILE = "memory.pkl"

# =========================
# LOAD MODEL
# =========================
model = SentenceTransformer(MODEL_NAME)

# =========================
# LOAD / CREATE INDEX
# =========================
dimension = 384

if os.path.exists(INDEX_FILE):
    index = faiss.read_index(INDEX_FILE)
    with open(TEXT_FILE, "rb") as f:
        memory_texts = pickle.load(f)
else:
    index = faiss.IndexFlatL2(dimension)
    memory_texts = []

# =========================
# FUNCTIONS
# =========================

def add_memory(text):
    vector = model.encode([text])
    index.add(np.array(vector).astype("float32"))
    memory_texts.append(text)
    print(f"[+] Memory added: {text}")


def search_memory(query, k=3):
    if len(memory_texts) == 0:
        return []

    query_vec = model.encode([query])
    D, I = index.search(np.array(query_vec).astype("float32"), k)

    results = []
    for i in I[0]:
        if i < len(memory_texts):
            results.append(memory_texts[i])
    return results


def save_memory():
    faiss.write_index(index, INDEX_FILE)
    with open(TEXT_FILE, "wb") as f:
        pickle.dump(memory_texts, f)
    print("[+] Memory saved!")


# =========================
# DEMO LOOP
# =========================
print("=== AI Memory System (FAISS) ===")

while True:
    user_input = input("\nYou: ")

    if user_input.lower() == "exit":
        save_memory()
        break

    elif user_input.startswith("add:"):
        add_memory(user_input.replace("add:", "").strip())

    else:
        results = search_memory(user_input)
        print("\n🔍 Relevant Memories:")
        for r in results:
            print("-", r)