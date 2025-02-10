from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os
import tensorflow as tf
import random
import re

# Disable GPU for compatibility
tf.config.set_visible_devices([], 'GPU')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
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


# Function to handle queries with strict filtering and refined responses
def handle_query(query, vector_store, k=20):
    # Handles user queries while returning only relevant results, with conversational improvements.
    query = query.lower().strip()

    # Predefined responses for common interactions
    predefined_responses = {
        r"\bhi\b|\bhello\b": [
            "Hello! How can I assist you?",
            "Hi there! What can I help you with?",
            "Hey! Need any help?"
        ],
        r"are you a robot\??|are you an ai\??": [
            "Yes! I’m an AI assistant here to help answer your questions. 😊",
            "A robot? Not quite! I don’t have wheels or arms (yet!), but I do have plenty of knowledge to share. 🤖"
        ],
        r"what is ai\??|what is an ai\??": [
            "Artificial Intelligence (AI) is the simulation of human intelligence in machines that can think, learn, and adapt.",
            "AI enables machines to perform tasks that typically require human intelligence, like problem-solving and decision-making."
        ],
        r"\bcourses?\b|\bavailable courses\??": [
            "I can provide a list of available courses. Try searching for a specific topic like 'Python' or 'AI'.",
            "We offer courses on AI, coding, and business applications. Let me know if you need details!"
        ]
    }

    # Check for predefined responses
    for pattern, responses in predefined_responses.items():
        if re.search(pattern, query):
            return random.choice(responses)

    # Identify category (kids, business, coding)
    category_keywords = ["kids", "business", "coding"]
    category_filter = next((cat for cat in category_keywords if cat in query), None)

    # Ensure the database is not empty before searching
    total_embeddings = len(vector_store.get(include=["metadatas"]))
    if total_embeddings == 0:
        return "⚠️ No courses available at the moment. Please check back later."

    # Perform similarity search in vector store
    docs = vector_store.similarity_search(query, k=k)

    # Filter only highly relevant results
    relevant_docs = [
        doc for doc in docs
        if re.search(re.escape(query), doc.page_content.lower()) or
           re.search(re.escape(query), doc.metadata.get("title", "").lower())
    ]

    # Apply category filtering if specified
    if category_filter:
        relevant_docs = [doc for doc in relevant_docs if doc.metadata.get("category", "").lower() == category_filter]

    if not relevant_docs:
        return "I couldn't find any relevant courses for your query. Try rephrasing or searching for a broader topic."

    # Format the response
    response = "📚 **Here are some courses related to your query:**\n\n"
    for doc in relevant_docs:
        title = doc.metadata.get("title", "No Title")
        course_link = doc.metadata.get("course_link", "No Link")
        price = doc.metadata.get("price", "$30")
        content_preview = doc.page_content[:200]  # Show first 200 chars

        response += f"📌 **{title}**\n🔗 [View Course]({course_link})\n💰 Price: {price}\n🔹 *{content_preview}...*\n\n"

    response += "⚠️ (These are the most relevant results I could find for now.)\n"
    return response



# Run only if this script is executed directly
if __name__ == "__main__":
    vector_store = get_chroma_vector_store()
    print(f"✅ Total embeddings stored at start: {len(vector_store.get(include=['metadatas']))}")

    while True:
        query = input("🔍 Enter your search query: ")
        if query.lower() in ["exit", "quit"]:
            print("👋 Exiting query system. Have a great day!")
            break
        response = handle_query(query, vector_store)
        print(response)
