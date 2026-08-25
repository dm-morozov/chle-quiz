document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const screens = {
        loading: document.getElementById('loading-screen'),
        start: document.getElementById('start-screen'),
        quiz: document.getElementById('quiz-screen'),
        result: document.getElementById('result-screen')
    };

    const ui = {
        totalQuestions: document.getElementById('total-questions'),
        sectionSelect: document.getElementById('section-select'),
        questionCount: document.getElementById('question-count'),
        btnStart: document.getElementById('btn-start'),
        
        progressBarFill: document.getElementById('progress-bar-fill'),
        currentQuestionNum: document.getElementById('current-question-num'),
        scoreDisplay: document.getElementById('score'),
        questionSection: document.getElementById('question-section'),
        questionText: document.getElementById('question-text'),
        optionsContainer: document.getElementById('options-container'),
        btnNext: document.getElementById('btn-next'),

        finalScoreValue: document.getElementById('final-score-value'),
        finalScoreTotal: document.getElementById('final-score-total'),
        resultMessage: document.getElementById('result-message'),
        btnRestart: document.getElementById('btn-restart')
    };

    // State
    let allQuestions = windowQuestions || [];
    let currentQuizQuestions = [];
    let currentQuestionIndex = 0;
    let score = 0;

    // Initialize App directly since data is already loaded
    if (allQuestions.length > 0) {
        initApp();
    } else {
        ui.loading.innerHTML = '<h2>Ошибка загрузки вопросов. Проверьте questions.js</h2>';
    }

    function initApp() {
        ui.totalQuestions.textContent = allQuestions.length;
        
        // Extract unique sections
        const sections = [...new Set(allQuestions.map(q => q.section))].filter(Boolean);
        sections.forEach(sec => {
            const option = document.createElement('option');
            option.value = sec;
            option.textContent = sec;
            ui.sectionSelect.appendChild(option);
        });

        switchScreen('start');
    }

    function switchScreen(screenName) {
        Object.values(screens).forEach(s => s.classList.remove('active'));
        screens[screenName].classList.add('active');
    }

    // Event Listeners
    ui.btnStart.addEventListener('click', startQuiz);
    ui.btnNext.addEventListener('click', handleNext);
    ui.btnRestart.addEventListener('click', () => switchScreen('start'));

    function startQuiz() {
        const selectedSection = ui.sectionSelect.value;
        let count = parseInt(ui.questionCount.value) || 20;

        let filtered = allQuestions;
        if (selectedSection !== 'all') {
            filtered = allQuestions.filter(q => q.section === selectedSection);
        }

        // Shuffle and slice
        currentQuizQuestions = [...filtered].sort(() => 0.5 - Math.random()).slice(0, count);
        
        if (currentQuizQuestions.length === 0) {
            alert('Нет вопросов по выбранным критериям!');
            return;
        }

        currentQuestionIndex = 0;
        score = 0;
        ui.scoreDisplay.textContent = '0';
        
        loadQuestion();
        switchScreen('quiz');
    }

    function loadQuestion() {
        const q = currentQuizQuestions[currentQuestionIndex];
        
        ui.currentQuestionNum.textContent = `Вопрос ${currentQuestionIndex + 1} из ${currentQuizQuestions.length}`;
        ui.progressBarFill.style.width = `${((currentQuestionIndex) / currentQuizQuestions.length) * 100}%`;
        
        ui.questionSection.textContent = q.section || 'Общий раздел';
        ui.questionText.textContent = q.question;
        
        ui.optionsContainer.innerHTML = '';
        ui.btnNext.disabled = true;

        for (const [letter, text] of Object.entries(q.options)) {
            const optDiv = document.createElement('div');
            optDiv.className = 'option';
            optDiv.innerHTML = `<span class="letter">${letter}.</span><span class="text">${text}</span>`;
            
            optDiv.addEventListener('click', () => handleOptionClick(optDiv, letter, q.correct_answer));
            ui.optionsContainer.appendChild(optDiv);
        }
    }

    function handleOptionClick(optDiv, selectedLetter, correctLetter) {
        if (!ui.btnNext.disabled) return; // already answered

        const options = ui.optionsContainer.children;
        for (let opt of options) {
            opt.classList.add('answered');
            const letter = opt.querySelector('.letter').textContent[0];
            if (letter === correctLetter) {
                opt.classList.add('correct');
            }
        }

        if (selectedLetter === correctLetter) {
            score++;
            ui.scoreDisplay.textContent = score;
        } else {
            optDiv.classList.add('wrong');
        }

        ui.btnNext.disabled = false;
        
        if (currentQuestionIndex === currentQuizQuestions.length - 1) {
            ui.btnNext.textContent = 'Завершить';
        } else {
            ui.btnNext.textContent = 'Далее';
        }
    }

    function handleNext() {
        currentQuestionIndex++;
        if (currentQuestionIndex < currentQuizQuestions.length) {
            loadQuestion();
        } else {
            showResult();
        }
    }

    function showResult() {
        ui.progressBarFill.style.width = '100%';
        ui.finalScoreValue.textContent = score;
        ui.finalScoreTotal.textContent = currentQuizQuestions.length;
        
        const percentage = score / currentQuizQuestions.length;
        let msg = 'Отличный результат!';
        if (percentage < 0.5) msg = 'Нужно еще потренироваться.';
        else if (percentage < 0.8) msg = 'Хороший результат, но есть куда расти.';
        
        ui.resultMessage.textContent = msg;
        switchScreen('result');
    }
});
