document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('questionnaireForm');
    if (!form) return;

    const questions = document.querySelectorAll('.question-container');
    const progress = document.querySelector('.progress');
    const btnPrev = document.querySelector('.btn-prev');
    const btnNext = document.querySelector('.btn-next');
    const btnSubmit = document.querySelector('.btn-submit');
    
    let currentQuestion = 1;
    const totalQuestions = questions.length;

    function updateProgress() {
        const percentage = ((currentQuestion - 1) / totalQuestions) * 100;
        progress.style.width = `${percentage}%`;
    }

    function showQuestion(questionNumber) {
        questions.forEach(q => {
            q.classList.add('hidden');
        });
        document.querySelector(`[data-question="${questionNumber}"]`).classList.remove('hidden');
        
        // Update buttons
        btnPrev.classList.toggle('hidden', questionNumber === 1);
        btnNext.classList.toggle('hidden', questionNumber === totalQuestions);
        btnSubmit.classList.toggle('hidden', questionNumber !== totalQuestions);
        
        updateProgress();
    }

    btnNext.addEventListener('click', () => {
        if (currentQuestion < totalQuestions) {
            currentQuestion++;
            showQuestion(currentQuestion);
        }
    });

    btnPrev.addEventListener('click', () => {
        if (currentQuestion > 1) {
            currentQuestion--;
            showQuestion(currentQuestion);
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        
        try {
            const response = await fetch('/generate-message', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                window.location.href = data.preview_url;
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while generating the message');
        }
    });
});