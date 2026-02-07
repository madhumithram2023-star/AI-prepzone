function startQuizNavigation() {
   
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
   
    const heroSection = document.getElementById('fade-in-element');
    if (heroSection) {
      
        setTimeout(() => {
            heroSection.classList.add('animate-fade-in');
        }, 50);
    }

 
    const logoContainer = document.querySelector('.logo-container');
    if (logoContainer) {
        logoContainer.classList.add('group');
    }

  
    const ctaButtons = document.querySelectorAll('.cta-button');
    ctaButtons.forEach(button => {
        button.addEventListener('click', () => {
            console.log(`Button clicked: ${button.querySelector('span').textContent}`);
         
        });
    });
});
document.addEventListener('DOMContentLoaded', () => {
   
    const quizWrapper = document.querySelector('.quiz-wrapper');
    

    if (quizWrapper) {
        quizWrapper.style.display = 'block'; 
    }
    
    
    console.log("Quiz Page Loaded and Visible!");
});


document.addEventListener('DOMContentLoaded', () => {
    

    const heroSection = document.getElementById('fade-in-element');
    if (heroSection) {
        setTimeout(() => {
            heroSection.classList.add('animate-fade-in');
        }, 50);
    }

    const logoContainer = document.querySelector('.logo-container');
    if (logoContainer) {
        logoContainer.classList.add('group');
    }

    const quizForm = document.getElementById('quiz-params-form');
    
    if (quizForm) {
        quizForm.addEventListener('submit', function(event) {
            event.preventDefault(); 

            const topic = document.getElementById('topic-title').value;
            const numQuestions = document.getElementById('num-questions').value;
            const difficulty = document.getElementById('difficulty').value;

        
            sessionStorage.setItem("quizTopic", topic); 
            sessionStorage.setItem("numQuestions", numQuestions);
            sessionStorage.setItem("difficulty", difficulty);

            const startBtn = document.getElementById('startQuizBtn');
            const loadingDiv = document.getElementById('loadingIndicator');

            if (startBtn && loadingDiv) {
                startBtn.style.display = 'none';
                loadingDiv.style.display = 'block';
            }

            setTimeout(() => {
                window.location.href = 'quizpage.html'; 
            }, 500); 
        });
    }

    const ctaButtons = document.querySelectorAll('.cta-button');
    ctaButtons.forEach(button => {
        button.addEventListener('click', () => {
            console.log(`Generic button clicked: ${button.querySelector('span').textContent}`);
        });
    });
});