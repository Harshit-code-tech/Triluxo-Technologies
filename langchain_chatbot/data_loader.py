from langchain.schema import Document
from embedding_store import get_chroma_vector_store
from selenium_script import extract_courses
import os

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

def process_courses():
    # Extracts courses and converts them into documents with title and course link metadata.
    courses = extract_courses()

    if not courses:
        print("❌ No courses extracted.")
        return []

    documents = []
    for course in courses:
        print(f"🔍 Raw Course Data: {course}")  # Debugging print

        description = course.get("description", "").strip()
        title = course.get("title", "Untitled Course").strip()
        course_link = course.get("course_link", "No Link").strip()

        if not description:
            print(f"⚠️ Skipping course '{title}' due to missing description.")
            continue

        documents.append(Document(
            page_content=description,
            metadata={
                "title": title,
                "course_link": course_link  # Ensure link is stored
            }
        ))

    return documents

def store_embeddings():
    # Processes courses and stores extracted documents in ChromaDB."
    documents = process_courses()
    if not documents:
        print("❌ No valid documents to store.")
        return

    # Debugging: Print extracted course descriptions before storing
    print("\n📌 Extracted Documents:")
    for doc in documents:
        print(f"Title: {doc.metadata['title']}\nLink: {doc.metadata['course_link']}\nDescription: {doc.page_content[:100]}...\n")

    try:
        vector_store = get_chroma_vector_store()
        vector_store.add_documents(documents)

        total_embeddings = len(vector_store.get(include=['metadatas']))
        print(f"✅ Total embeddings stored: {total_embeddings}")

        print("✅ Courses successfully embedded and stored!")
    except Exception as e:
        print(f"❌ Error while storing embeddings: {e}")

if __name__ == "__main__":
    store_embeddings()
