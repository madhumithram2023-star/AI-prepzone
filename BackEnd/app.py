import os
import re
import json
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.oauth2 import service_account
from google.cloud import dialogflow_v2 as dialogflow
import google.generativeai as genai
from dotenv import load_dotenv

# --- INITIAL SETUP & COFIGURATION ---
load_dotenv()

# Load Google Credentials for Dialogflow
if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in os.environ:
    try:
        cred_data = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
        with open("service-account.json", "w") as f:
            json.dump(cred_data, f)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account.json"
        print("Service account loaded from environment.")
    except json.JSONDecodeError:
        print("Invalid GOOGLE_APPLICATION_CREDENTIALS_JSON format.")
else:
    print("GOOGLE_APPLICATION_CREDENTIALS_JSON not found.")

# Initialize Dialogflow
try:
    project_id = "questionbot-lbwk"   
    credentials = service_account.Credentials.from_service_account_file("service-account.json")
    session_client = dialogflow.SessionsClient(credentials=credentials)
except Exception as e:
    print(f"Dialogflow Client Error: {e}")
    session_client = None

# Initialize Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

try:
    # Using gemini-1.5-flash as 2.5 is not a standard release yet
    model = genai.GenerativeModel("gemini-1.5-flash") 
except Exception as e:
    print("Error initializing Gemini:", e)
    model = None

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Global session tracker for Interactive Chat
user_sessions = {}

# Load Question Paper Data
try:
    df = pd.read_csv("QUESTIONPAPER.csv", encoding="latin1")
    df.columns = df.columns.str.lower()
    if 'year' in df.columns:
        df["year"] = df["year"].astype(str)
    print(f"CSV Loaded: {len(df)} questions")
except Exception as e:
    df = pd.DataFrame()
    print(f"CSV Load Failed: {e}")

# --- HELPER FUNCTIONS ---

def format_questions(questions, limit=None):
    if questions.empty:
        return None
    if limit:
        questions = questions.head(limit)
    formatted_list = []
    for row in questions.itertuples(index=False):
        year = getattr(row, 'year', 'N/A')
        sub = getattr(row, 'sub', 'N/A')
        examtype = getattr(row, 'examtype', 'N/A')
        question = getattr(row, 'question', 'No question provided.')
        formatted_list.append(f"<b>[{year}] {sub} ({examtype})</b><br>Q: {question}")
    return "\n\n".join(formatted_list)

def detect_intent_and_get_params(text, session_id="12345", language_code="en"):
    if not session_client:
        return None
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    try:
        response = session_client.detect_intent(request={"session": session, "query_input": query_input})
        return response.query_result
    except Exception as e:
        print(f"Dialogflow API Error: {e}")
        return None

def get_csv_questions(params):
    year = str(params.get("Year", "")).strip()
    limit = int(params.get("number", 2)) if params.get("number") else 2
    exam_type = str(params.get("Exam_Type", "")).strip()
    subject = str(params.get("Subject", "")).strip()
    topic = str(params.get("Topic", "")).strip()
    repeated = str(params.get("Repeatation", "")).strip()

    filtered = df.copy()
    if year: filtered = filtered[filtered["year"] == year]
    if exam_type: filtered = filtered[filtered["examtype"].str.contains(exam_type, case=False, na=False)]
    if subject: filtered = filtered[filtered["sub"].str.contains(subject, case=False, na=False)]
    if repeated: 
        filtered = filtered[pd.to_numeric(filtered["repeatation"], errors="coerce") > 1]
        limit = 1

    if filtered.empty:
        return "I couldn't find any questions matching those criteria. Try being less specific!"
    return format_questions(filtered, limit)

# --- ROUTES ---

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "AI Prepzone Mega-Backend is running 🚀",
        "active_file": "app.py (Merged)",
        "endpoints": {
            "question_analysis": "/chat (POST)",
            "simple_ai_chat": "/api_chat (POST)",
            "interactive_session_chat": "/interactive-chat (POST)",
            "reset_session": "/reset-session (POST)"
        }
    })

# Route for Dialogflow / CSV Analysis
@app.route("/chat", methods=["POST"])
def chat():
    req = request.get_json()
    user_message = req.get("message")
    session_id = req.get("sessionId", "12345")
    if not user_message:
        return jsonify({"fulfillmentText": "No message received."})
    
    query_result = detect_intent_and_get_params(user_message, session_id)
    if not query_result:
        return jsonify({"fulfillmentText": "Connection Error."})

    intent = query_result.intent.display_name
    params = dict(query_result.parameters)

    if intent.lower() == "get_questions_by_intent":
        csv_response = get_csv_questions(params)
        return jsonify({"fulfillmentText": csv_response})
    return jsonify({"fulfillmentText": query_result.fulfillment_text})

# Route for Simple AI Chat (One-off)
@app.route("/api_chat", methods=["POST"])
def api_chat():
    req = request.get_json()
    user_message = req.get("message")
    if not user_message:
        return jsonify({"response": "No message received"})
    try:
        response = model.generate_content(user_message)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": f"AI Error: {str(e)}"})


@app.route("/generate-questions", methods=["POST"])
def generate_questions():
    data = request.get_json()

    topic = data.get("topic")
    count = int(data.get("count", 5))
    difficulty = data.get("difficulty", "medium")

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    prompt = f"""
Generate {count} multiple-choice questions on the topic "{topic}".
Difficulty level: {difficulty}.

Each question must include:
- question
- 4 options
- correct answer
- short explanation

Return STRICT JSON in this format:
{{
  "questions": [
    {{
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "answer": "A",
      "explanation": "..."
    }}
  ]
}}
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Extract JSON safely
        json_text = text[text.find("{"): text.rfind("}") + 1]
        quiz_data = json.loads(json_text)

        return jsonify(quiz_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Route for Interactive Session-based Chat
@app.route("/interactive-chat", methods=["POST"])
def interactive_chat():
    data = request.get_json()
    if model is None:
        return jsonify({"error": "AI model not initialized"}), 500
        
    session_id = data.get("sessionId", "default-session")
    incoming_text = data.get("message", "").strip()

    if session_id not in user_sessions:
        user_sessions[session_id] = {"question": "", "history": []}

    base_question = user_sessions[session_id]["question"]
    history = user_sessions[session_id]["history"]

    if base_question == "":
        user_sessions[session_id]["question"] = incoming_text
        prompt = f"Explain the following in **maximum 10 short lines**. Bold key terms. Topic: {incoming_text}"
    else:
        prompt = f"Base Question: {base_question}\nHistory: {json.dumps(history)}\nUser: {incoming_text}\nRespond in 10 short lines, use bold for key terms."
        history.append({"user": incoming_text})

    try:
        response = model.generate_content(prompt)
        reply = response.text.strip()
        history.append({"bot": reply})
        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"error": f"Gemini Error: {str(e)}"}), 500

@app.route("/reset-session", methods=["POST"])
def reset():
    sid = request.get_json().get("sessionId", "default-session")
    user_sessions.pop(sid, None)
    return jsonify({"message": "Session cleared"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)