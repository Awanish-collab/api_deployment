from flask import Flask, request, jsonify
from agent_runner import chat_with_agent

app = Flask(__name__)

# ✅ Root GET route to verify server is running in browser
@app.route("/", methods=["GET"])
def home():
    return "✅ AutoGen Agent API is running! Use POST /chat with JSON to query."

# ✅ POST endpoint to interact with agent
@app.route("/chat", methods=["POST"])  # Changed from GET to POST
def chat():
    data = request.json
    query = data.get("query", "")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    print(f"📥 Received query: {query}")  # Log incoming request

    try:
        result = chat_with_agent(query)
        print("✅ Agent response ready")
        return jsonify({"response": result})
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ✅ Optional: Add a GET version for testing via browser
@app.route("/chat", methods=["GET"])
def chat_get():
    query = request.args.get("query", "")
    if not query:
        return jsonify({"error": "No query provided. Use ?query=your_question"}), 400

    print(f"📥 Received GET query: {query}")

    try:
        result = chat_with_agent(query)
        print("✅ Agent response ready")
        return jsonify({"response": result})
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ✅ Run app on port 5000 (default) or 10000 if needed
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)