# AI Prepzone - Full-Stack Exam Assistant 🚀

AI Prepzone is an intelligent study platform designed to help students prepare for exams using AI-driven question paper analysis and interactive study sessions.

## 🌟 Key Features
* **AI Quiz Generator**: Generates dynamic quizzes based on custom topics and difficulty levels using Google Gemini AI.
* **Question Paper Chat**: An intelligent assistant capable of searching and retrieving information from a database of Past exam questions.
* **Interactive Study Explainer**: A session-based chat that provides concise (10-line) explanations of complex academic topics with conversation memory.

## 🛠️ Tech Stack
* **Frontend**: HTML5, CSS3 (Tailwind CSS), Vanilla JavaScript, Chart.js for data visualization.
* **Backend**: Python (Flask framework), Gunicorn (WSGI server).
* **AI Engine**: Google Gemini 1.5 Flash API.
* **Database**: CSV-based storage for question paper records.
* **Deployment**: Hosted on Render (Cloud PaaS).

## 🚀 Live Demo
The backend service is live and operational:
[https://ai-prepzone-backend.onrender.com](https://ai-prepzone-backend.onrender.com)

## 📁 Project Structure
* `app.py`: The "Mega-Backend" merging all AI and search logic.
* `QUESTIONPAPER.csv`: The primary database of 189 academic questions.
* `FrontEnd/`: Contains the interactive user interface and chat systems.
