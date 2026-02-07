/**
 * ========================================
 * ⚙️ GLOBAL VARIABLES AND DOM ELEMENTS
 * ========================================
 */
const topic = sessionStorage.getItem("quizTopic");
const numQuestions = sessionStorage.getItem("numQuestions");
const difficulty = sessionStorage.getItem("difficulty");

const quizTopicTitle = document.getElementById("quiz-topic-title");
const questionContainer = document.getElementById("question-container");
const submitBtn = document.getElementById("submit-btn");
const resultArea = document.getElementById("result-area");
const scoreText = document.getElementById("score-text");

const quizWrapper = document.querySelector('.quiz-wrapper');
const initialLoadingDiv = document.getElementById('initial-loading'); 
const loadingMessage = document.getElementById('loading-message'); 

let currentQuestion = 0;
let questions = []; 
let score = 0;

//---

/**
 * ========================================
 * 🚀 QUIZ INITIALIZATION & VISIBILITY
 * ========================================
 */
document.addEventListener('DOMContentLoaded', () => {
    
    

    fetchQuiz();
});

//---

/**
 * ========================================
 * 🌐 QUIZ DATA FETCHING (Improved with Loading/Error Handling)
 * ========================================
 */
async function fetchQuiz() {
    quizTopicTitle.style.display = "none";

    try {
        const res = await fetch("/generate-questions", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                topic: topic,
                count: numQuestions,
                difficulty: difficulty,
            }),
        });
        
        if (!res.ok) {
            throw new Error(`Server responded with status: ${res.status}`);
        }

        const data = await res.json();
        
        if (!data.questions || data.questions.length === 0) {
            throw new Error("No questions were returned by the API.");
        }
        
        questions = data.questions;
        
        // --- SUCCESS: Hide loading, show quiz content ---
        if (initialLoadingDiv) initialLoadingDiv.style.display = 'none';
        if (quizWrapper) quizWrapper.style.display = 'block'; 
        
        displayQuestion();

    } catch (error) {
        console.error("Error fetching or starting quiz:", error);
        
        // --- ERROR: Hide loading, show error message in the quiz area ---
        if (initialLoadingDiv) initialLoadingDiv.style.display = 'none';
        if (quizWrapper) quizWrapper.style.display = 'block';

        questionContainer.innerHTML = `
            <div style="text-align: center; color: #ff5252; padding: 50px;">
                <h2>⚠️ Error Loading Quiz</h2>
                <p>Could not fetch questions. Please ensure your backend server is running and accessible.</p>
                <p>Details: ${error.message}</p>
            </div>
        `;
        document.getElementById("quiz-area").style.display = 'block';
        submitBtn.style.display = "none";
    }
}

//---

/**
 * ========================================
 * ❓ QUESTION DISPLAY LOGIC
 * ========================================
 */
function displayQuestion() {
    const q = questions[currentQuestion];

    // ✅ NEW: Update progress display
    document.getElementById("quiz-progress").textContent =
      `Question ${currentQuestion + 1} of ${questions.length}`;

    questionContainer.innerHTML = `
        <div class="question">
            <h2>${q.question}</h2>
            ${q.options
                .map(
                    (opt, i) =>
                        `<div class="option" data-index="${i}">${opt}</div>`
                )
                .join("")}
        </div>
    `;

    submitBtn.textContent = "Submit"; 
    submitBtn.style.display = "block";
    addOptionListeners();
}


function addOptionListeners() {
    const options = document.querySelectorAll(".option");
    options.forEach((opt) => {
        opt.addEventListener("click", () => {
            options.forEach((o) => o.classList.remove("selected"));
            opt.classList.add("selected");
        });
    });

    submitBtn.onclick = handleSubmit;
}

//---

/**
 * ========================================
 * ✍️ ANSWER SUBMISSION & NAVIGATION
 * ========================================
 */
function handleSubmit() {
    const selected = document.querySelector(".option.selected");
    if (!selected) {
        alert("Please select an answer!");
        return;
    }

    document.querySelectorAll(".option").forEach(opt => opt.style.pointerEvents = 'none');

    const chosenText = selected.textContent.trim();
    const q = questions[currentQuestion];
    
    q.userAnswer = chosenText;

    const feedback = document.createElement("div");
    feedback.classList.add("feedback");

    if (chosenText === q.answer.trim()) {
        feedback.textContent = "✅ Correct!";
        feedback.classList.add("correct");
        score++;
    } else {
        feedback.textContent = "❌ Wrong! Correct answer was: " + q.answer;
        feedback.classList.add("wrong");
    }

    const explanation = document.createElement("p");
explanation.textContent = `Explanation: ${
    q.explanation ? q.explanation : "No explanation provided."
}`;
explanation.classList.add("explanation");

questionContainer.appendChild(feedback);
questionContainer.appendChild(explanation);


    submitBtn.textContent =
        currentQuestion + 1 < questions.length
            ? "Next Question"
            : "Finish Quiz";

    submitBtn.onclick = () => {
        currentQuestion++;
        if (currentQuestion < questions.length) {
            displayQuestion();
        } else {
            showResults();
        }
    };
}

//---

/**
 * ========================================
 * 📈 RESULT & REVIEW LOGIC
 * ========================================
 */
function showResults() {
    document.getElementById("quiz-area").style.display = "none";
    resultArea.style.display = "block";
    const percentage = (score / questions.length) * 100;
    scoreText.textContent = `You scored ${score} out of ${questions.length}! (${percentage.toFixed(0)}%)`;

    const ctx = document.getElementById("result-chart");
    new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Correct", "Wrong"],
            datasets: [
                {
                    data: [score, questions.length - score],
                    backgroundColor: ["#00e676", "#ff5252"],
                },
            ],
        },
        options: {
            animation: { animateRotate: true, duration: 1500 },
        },
    });

    document.getElementById("review-btn").onclick = showReview;
    document.getElementById("play-again-btn").onclick = () =>
        location.reload(); 
    document.getElementById("back-btn").onclick = () =>
        (window.location.href = "index.html"); 
}

function showReview() {
    resultArea.style.display = "none";
    const reviewArea = document.getElementById("review-area");
    const reviewContainer = document.getElementById("review-container");
    reviewContainer.innerHTML = "";

    questions.forEach((q, i) => {
        const div = document.createElement("div");
        div.classList.add("review-item");
        const isCorrect = q.userAnswer === q.answer;
        div.classList.add(isCorrect ? "correct" : "wrong");
        div.innerHTML = `
            <h3>Q${i + 1}: ${q.question}</h3>
            <p><strong>Your Answer:</strong> ${q.userAnswer || "Not answered"}</p>
            <p><strong>Correct Answer:</strong> ${q.answer}</p>
            <p><em>${q.explanation}</em></p>
        `;
        reviewContainer.appendChild(div);
    });

    reviewArea.style.display = "block";
    document.getElementById("back-to-results-btn").onclick = () => {
        reviewArea.style.display = "none";
        resultArea.style.display = "block";
    };
}