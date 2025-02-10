from flask import Flask, request, render_template
from flask_restful import Api, Resource
from .query_engine import get_chroma_vector_store, handle_query
import traceback

app = Flask(__name__, template_folder="templates", static_folder="static")
api = Api(app)

# Load ChromaDB vector store
try:
    vector_store = get_chroma_vector_store()
    print(f"✅ Vector store loaded with {len(vector_store.get(include=['metadatas']))} embeddings.")
except Exception as e:
    print(f"❌ Error loading vector store: {e}")
    traceback.print_exc()

# Serve the chatbot UI
@app.route("/")
def index():
    return render_template("index.html")

class Chat(Resource):
    def post(self):
        try:
            if not request.is_json:
                return {"error": "Invalid content type. Use 'application/json'."}, 415

            data = request.get_json()
            if not data:
                return {"error": "No JSON data received"}, 400

            user_message = data.get("message")
            if not user_message:
                return {"error": "Missing 'message' key in request data"}, 400

            response_message = handle_query(user_message, vector_store)


            return {"response": response_message}, 200

        except Exception as e:
            traceback.print_exc()
            return {"error": f"Internal Server Error: {str(e)}"}, 500

class HealthCheck(Resource):
    def get(self):
        return {"status": "Chatbot is running"}, 200

api.add_resource(Chat, "/chat")
api.add_resource(HealthCheck, "/health")

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=10000)

