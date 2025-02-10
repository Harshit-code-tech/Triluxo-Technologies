from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os
import tensorflow as tf
tf.config.set_visible_devices([], 'GPU')
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

# Load the BGE-base-en embedding model
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en")

# Initialize ChromaDB
def get_chroma_vector_store(persist_directory="db"):
    # Returns a Chroma vector store instance with the embedding model.
    if not os.path.exists(persist_directory):
        os.makedirs(persist_directory)

    vector_store = Chroma(persist_directory=persist_directory, embedding_function=embedding_model)

    # Debugging: Check stored embeddings count
    total_embeddings = len(vector_store.get(include=["metadatas"]))
    print(f"✅ Total embeddings stored: {total_embeddings}")

    return vector_store

# Run only if this script is executed directly
if __name__ == "__main__":
    vector_store = get_chroma_vector_store()
    print(f"✅ Total embeddings stored at start: {len(vector_store.get(include=['metadatas']))}")

    # Dynamic user input for query
    query = input("🔍 Enter your search query: ").strip().lower()

    # Perform similarity search
    docs = vector_store.similarity_search(query, k=10)  # Get more results initially

    # Filter results that explicitly contain the query in title or content
    filtered_docs = [
        doc for doc in docs if query in doc.metadata.get("title", "").lower() or query in doc.page_content.lower()
    ]

    # Display results
    if filtered_docs:
        print(f"🔎 Filtered search results for '{query}':")
        for doc in filtered_docs[:5]:  # Show only top 5 relevant ones
            title = doc.metadata.get("title", "No Title")
            course_link = doc.metadata.get("course_link", "No Link")
            print(f"📌 {title} | {course_link} - {doc.page_content[:150]}...")
    else:
        print(f"⚠️ No results found specifically containing '{query}', showing top semantic matches:")
        for doc in docs[:5]:  # Fallback: Show semantic matches
            title = doc.metadata.get("title", "No Title")
            course_link = doc.metadata.get("course_link", "No Link")
            print(f"📌 {title} | {course_link} - {doc.page_content[:150]}...")
