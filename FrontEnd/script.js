function startQuizNavigation() {
    // Optional: You can collect form data here before navigating
    
    // Directs the browser to the quizpage.html file
    window.location.href = 'quizpage.html';
}

document.addEventListener("DOMContentLoaded", () => {
  const backBtn = document.getElementById("back-btn");
  if (backBtn) {
    backBtn.onclick = () => {
      window.location.href = "chat.html";
    };
  }
});


document.addEventListener('DOMContentLoaded', () => {
    // 1. Apply the 'animate-fade-in' class to trigger the hero section animation
    const heroSection = document.getElementById('fade-in-element');
    if (heroSection) {
        // A small timeout ensures the fade-in occurs *after* the DOM is fully painted
        // for a smoother effect, mimicking the component's original intent.
        setTimeout(() => {
            heroSection.classList.add('animate-fade-in');
        }, 50);
    }

    // 2. Add an event listener to the logo container for the cursor change
    const logoContainer = document.querySelector('.logo-container');
    if (logoContainer) {
        // While the hover styles are in CSS, we can ensure the group class is present
        // for any potential JS interactions, though in this case, it's just a visual trigger.
        logoContainer.classList.add('group');
    }

    // 3. Optional: Add click handlers for buttons (since they don't navigate yet)
    const ctaButtons = document.querySelectorAll('.cta-button');
    ctaButtons.forEach(button => {
        button.addEventListener('click', () => {
            console.log(`Button clicked: ${button.querySelector('span').textContent}`);
            // You can implement actual navigation here if needed
            // e.g., window.location.href = '/quiz-generator';
        });
    });
});
document.addEventListener('DOMContentLoaded', () => {
    // 1. Get a reference to the main container
    const quizWrapper = document.querySelector('.quiz-wrapper');
    
    // 2. Make the container visible by removing the 'display: none;' style
    if (quizWrapper) {
        quizWrapper.style.display = 'block'; // Or 'flex', 'grid', etc., depending on your layout needs
    }
    
    // 3. (You would add logic here to fetch questions 
    //    based on the form data and start the quiz)
    console.log("Quiz Page Loaded and Visible!");
});


document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. Hero Section Animation ---
    const heroSection = document.getElementById('fade-in-element');
    if (heroSection) {
        setTimeout(() => {
            heroSection.classList.add('animate-fade-in');
        }, 50);
    }

    // --- 2. Logo Container Interaction ---
    const logoContainer = document.querySelector('.logo-container');
    if (logoContainer) {
        logoContainer.classList.add('group');
    }

    // --- 3. Form Submission & Navigation Logic ---
    const quizForm = document.getElementById('quiz-params-form');
    
    if (quizForm) {
        quizForm.addEventListener('submit', function(event) {
            event.preventDefault(); // Stop default refresh

            const topic = document.getElementById('topic-title').value;
            const numQuestions = document.getElementById('num-questions').value;
            const difficulty = document.getElementById('difficulty').value;

            // Save data before navigation
            sessionStorage.setItem("quizTopic", topic); 
            sessionStorage.setItem("numQuestions", numQuestions);
            sessionStorage.setItem("difficulty", difficulty);

            // Show loading state (assuming IDs are present)
            const startBtn = document.getElementById('startQuizBtn');
            const loadingDiv = document.getElementById('loadingIndicator');

            if (startBtn && loadingDiv) {
                startBtn.style.display = 'none';
                loadingDiv.style.display = 'block';
            }

            // Navigate to the quiz page
            setTimeout(() => {
                window.location.href = 'quizpage.html'; 
            }, 500); 
        });
    }

    // --- 4. Generic CTA Button Handlers (Optional) ---
    const ctaButtons = document.querySelectorAll('.cta-button');
    ctaButtons.forEach(button => {
        button.addEventListener('click', () => {
            console.log(`Generic button clicked: ${button.querySelector('span').textContent}`);
        });
    });
});