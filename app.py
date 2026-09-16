import uuid
from flask import Flask, jsonify, request
from chat_engine import ChatEngine

app = Flask(__name__)

# Initialize model once globally
Engine = ChatEngine(model_dir="onnx_chat_model")

# In-memory session store
CONVERSATION_SESSIONS = {}

@app.route("/", methods=["GET"])
def check():
    return jsonify({"status": "running"}), 200

@app.route("/chat", methods=["POST"])
def stateless_chat():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Request body must be valid JSON with 'Content-Type: application/json'"}), 400

    messages = data.get("messages")
    if not isinstance(messages, list) or len(messages) == 0:
        return jsonify({"error": "'messages' must be a non-empty list of role/content objects"}), 400

    max_tokens = int(data.get("max_tokens", 100))
    temperature = float(data.get("temperature", 0.7))

    try:
        reply = Engine.generate_response(
            messages=messages,
            max_new_tokens=max_tokens,
            temperature=temperature
        )
        return jsonify({"reply": reply, "role": "assistant"}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 422
    except Exception as e:
        return jsonify({"error": f"Inference failed: {str(e)}"}), 500

@app.route("/chat/session", methods=["POST"])
def session_chat():
    # silent=True prevents Flask from throwing 400 HTML page if JSON is malformed
    data = request.get_json(silent=True)

    # 1. Check if JSON body exists
    if not data or not isinstance(data, dict):
        return jsonify({
            "error": "Invalid request. Ensure body is JSON and Header 'Content-Type: application/json' is set."
        }), 400

    # 2. Extract and validate 'message' safely
    raw_message = data.get("message")
    if raw_message is None or not isinstance(raw_message, str) or not raw_message.strip():
        return jsonify({
            "error": "Field 'message' is required, must be a string, and cannot be empty."
        }), 400

    user_text = raw_message.strip()
    session_id = data.get("session_id")
    max_tokens = int(data.get("max_tokens", 120))
    temperature = float(data.get("temperature", 0.7))

    # 3. Handle session ID creation and memory
    if not session_id or session_id not in CONVERSATION_SESSIONS:
        session_id = str(uuid.uuid4())[:8]
        system_prompt = data.get("system_prompt", "You are a helpful customer service AI assistant.")
        CONVERSATION_SESSIONS[session_id] = [
            {"role": "system", "content": system_prompt}
        ]

    CONVERSATION_SESSIONS[session_id].append({"role": "user", "content": user_text})

    try:
        # 4. Generate response using the session's history
        reply = Engine.generate_response(
            messages=CONVERSATION_SESSIONS[session_id],
            max_new_tokens=max_tokens,
            temperature=temperature
        )
        CONVERSATION_SESSIONS[session_id].append({"role": "assistant", "content": reply})

        return jsonify({
            "session_id": session_id,
            "reply": reply,
            "turn_count": len(CONVERSATION_SESSIONS[session_id]) // 2
        }), 200

    except Exception as e:
        return jsonify({"error": f"Generation error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=False)