from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)
CORS(app)

try:
    model = genai.GenerativeModel("gemini-2.5-flash")
except Exception as e:
    print("Error initializing Gemini:", e)
    model = None

user_sessions = {}


@app.route("/interactive-chat", methods=["POST"])
def interactive_chat():
    data = request.get_json()

    session_id = data.get("sessionId", "default-session")
    incoming_text = data.get("message", "").strip()

    if session_id not in user_sessions:
        user_sessions[session_id] = {"question": "", "history": []}

    base_question = user_sessions[session_id]["question"]
    history = user_sessions[session_id]["history"]

    # If first message → treat it as main question → return short overview
    if base_question == "":
        user_sessions[session_id]["question"] = incoming_text
        prompt = f"""
Explain the following in **maximum 10 short lines**.
Only highlight key terms using **bold**.
Do not use bullet points or stars.

Topic: {incoming_text}
"""

    # If follow-up → continue conversation but keep it short and clean
    else:
        prompt = f"""
Base Question: {base_question}

Conversation History:
{json.dumps(history, indent=2)}

User asks: {incoming_text}

Respond in **maximum 10 short lines**.
Keep explanation clear and concise.
Use **bold** only for important terms. Do not use '*' anywhere else.
"""

        history.append({"user": incoming_text})

    try:
        response = model.generate_content(prompt)
        reply = response.candidates[0].content.parts[0].text.strip()
    except Exception as e:
        return jsonify({"error": f"Gemini Error: {str(e)}"}), 500

    history.append({"bot": reply})

    return jsonify({"response": reply})


@app.route("/api_chat", methods=["POST"])
def api_chat_alias():
    return interactive_chat()


@app.route("/reset-session", methods=["POST"])
def reset():
    sid = request.get_json().get("sessionId", "default-session")
    user_sessions.pop(sid, None)
    return jsonify({"message": "Session cleared"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
