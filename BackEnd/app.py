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
if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in os.environ:
    try:
        cred_data = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
        with open("service-account.json", "w") as f:
            json.dump(cred_data, f)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account.json"
        print("Service account loaded from environment.")
    except json.JSONDecodeError:
        print(" Invalid GOOGLE_APPLICATION_CREDENTIALS_JSON format.")
else:
    print(" GOOGLE_APPLICATION_CREDENTIALS_JSON not found.")


try:
    project_id = "questionbot-lbwk"   
    credentials = service_account.Credentials.from_service_account_file("service-account.json")
    session_client = dialogflow.SessionsClient(credentials=credentials)
except Exception as e:
    print(f"Dialogflow Client Error: {e}")
    session_client = None



load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

try:
    model = genai.GenerativeModel("gemini-2.5-flash")
except Exception as e:
    print("Error initializing Gemini:", e)
    model = None

user_sessions = {}
app = Flask(__name__)
CORS(app)


try:
    df = pd.read_csv("QUESTIONPAPER.csv", encoding="latin1")
    df.columns = df.columns.str.lower()

    if 'year' in df.columns:
        df["year"] = df["year"].astype(str)

    if 'sub' not in df.columns or 'question' not in df.columns:
        raise ValueError("CSV missing required columns: sub, question")

    print(f" CSV Loaded: {len(df)} questions")
except Exception as e:
    df = pd.DataFrame()
    print(f" CSV Load Failed: {e}")


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

        formatted_list.append(
            f"<b>[{year}] {sub} ({examtype})</b><br>Q: {question}"
        )
    return "\n\n".join(formatted_list)

def detect_intent_and_get_params(text, session_id="12345", language_code="en"):
    if not session_client:
        return {"intent": {"displayName": "Error"}, "parameters": {}}

    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    try:
        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )
        return response.query_result
    except Exception as e:
        print(f"Dialogflow API Error: {e}")
        return {"intent": {"displayName": "Error"}, "parameters": {}}

def get_csv_questions(params):

    year = str(params.get("Year", "")).strip()
    limit = int(params.get("number", 2)) if params.get("number") else 2
    exam_type = str(params.get("Exam_Type", "")).strip()
    subject = str(params.get("Subject", "")).strip()
    topic = str(params.get("Topic", "")).strip()
    any_param = str(params.get("any", "")).strip()
    q_type = str(params.get("Type", "")).strip()
    difficulty = str(params.get("Difficulty", "")).strip()
    repeated = str(params.get("Repeatation", "")).strip()

    filtered = df.copy()
    print(filtered.columns)

    if year:
        filtered = filtered[filtered["year"] == year]

    if exam_type:
        filtered = filtered[filtered["examtype"].str.contains(exam_type, case=False, na=False, regex=False)]

    if subject:
        filtered = filtered[filtered["sub"].str.contains(subject, case=False, na=False, regex=False)]

    if q_type:
        filtered = filtered[filtered["type"].str.contains(q_type, case=False, na=False, regex=False)]

    if difficulty:
        filtered = filtered[filtered["difficulty"].str.lower().str.contains(difficulty, na=False, regex=False, case=False)]
        print(filtered.columns)

    if repeated:
        filtered = filtered[pd.to_numeric(filtered["repeatation"], errors="coerce") > 1]
        limit = 1

    search_query = topic or any_param
    if search_query and "topic" in filtered.columns:
        keywords = re.split(r'\s+or\s+|\s+', search_query, flags=re.IGNORECASE)
        keywords = [kw for kw in keywords if kw]
        if keywords:
            regex_query = "|".join(re.escape(s) for s in keywords)
            filtered = filtered[filtered["topic"].str.contains(regex_query, case=False, na=False)]

    if filtered.empty:
        filters_used = [f"{k}: {v}" for k, v in params.items() if v and k not in ('number', 'sessionId')]
        filter_str = ", ".join(filters_used)
        return f"I couldn't find any questions matching the criteria ({filter_str}). Try being less specific!"

    return format_questions(filtered, limit)

@app.route("/api_chat", methods=["POST"])
def api_chat():
    req = request.get_json()
    user_message = req.get("message")

    if not user_message:
        return jsonify({"response": "No message received"})

    try:
        response = model.generate_content(user_message)
        return jsonify({
            "response": response.text
        })
    except Exception as e:
        return jsonify({
            "response": f"AI Error: {str(e)}"
        })

@app.route("/chat", methods=["POST"])
def chat():
    req = request.get_json()
    user_message = req.get("message")
    session_id = req.get("sessionId")

    if not user_message:
        return jsonify({"fulfillmentText": "No message received."})

    query_result = detect_intent_and_get_params(user_message, session_id)

    if isinstance(query_result, dict) and query_result.get("intent", {}).get("displayName") == "Error":
        return jsonify({"fulfillmentText": "Dialogflow Connection Error."})

    intent = query_result.intent.display_name
    params = dict(query_result.parameters)

    if intent.lower() == "get_questions_by_intent":
        csv_response = get_csv_questions(params)
        return jsonify({"fulfillmentText": csv_response})

    return jsonify({"fulfillmentText": query_result.fulfillment_text})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
