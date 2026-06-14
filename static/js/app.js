// ==========================================
// SarkariPrep - Frontend Application Logic
// ==========================================

// Trusted Types Policy for compatibility with strict browser environments
if (window.trustedTypes && window.trustedTypes.createPolicy) {
    try {
        window.trustedTypes.createPolicy("default", {
            createHTML: (string) => string,
            createScript: (string) => string,
            createScriptURL: (string) => string
        });
    } catch (e) {
        console.warn("Trusted Types default policy registration skipped: ", e);
    }
}

// Global Application State
let activeUser = null;
let authMode = 'login'; // 'login' or 'signup'
let currentPanel = 'home';
let currentQuestion = null;
let hasAnswered = false;
let selectedExam = 'General';
let selectedSubject = '';
let historyData = [];
let historyFilter = 'all';
let optionsTimeout = null;

// Initialize App on DOM Load
document.addEventListener('DOMContentLoaded', () => {
    // Check if user has an active session
    checkAuthSession();
});

// --- VIEW & PANEL ROUTING ---

function switchView(viewId) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById(viewId).classList.add('active');
}

function switchPanel(panelId) {
    if (!activeUser && panelId !== 'auth') {
        switchView('auth-view');
        return;
    }
    
    // Clear options delay timeout if navigating away from practice panel
    if (panelId !== 'practice') {
        if (optionsTimeout) {
            clearTimeout(optionsTimeout);
            optionsTimeout = null;
        }
    }
    
    // Switch active panel classes
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.getElementById(`${panelId}-panel`).classList.add('active');
    currentPanel = panelId;

    // Update bottom navigation active tab
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    
    // Settings panel is accessed via gear icon, doesn't have tab highlight
    if (panelId === 'home') {
        document.getElementById('tab-home').classList.add('active');
        initializeDashboard();
    } else if (panelId === 'history') {
        document.getElementById('tab-history').classList.add('active');
        loadHistory();
    } else if (panelId === 'stats') {
        document.getElementById('tab-stats').classList.add('active');
        loadStatsDashboard();
    } else if (panelId === 'settings') {
        loadSettings();
    }
}

// --- AUTHENTICATION HANDLERS ---

function switchAuthMode(mode) {
    authMode = mode;
    const slider = document.getElementById('auth-slider');
    const tabs = document.querySelectorAll('.auth-tab');
    const submitBtn = document.getElementById('auth-btn');
    const footerText = document.getElementById('auth-footer-text');
    const errorMsg = document.getElementById('auth-error-msg');
    
    errorMsg.innerText = '';
    
    if (mode === 'login') {
        slider.style.transform = 'translateX(0)';
        tabs[0].classList.add('active');
        tabs[1].classList.remove('active');
        submitBtn.innerText = 'Log in';
        footerText.innerText = 'New here? Tap Sign up to begin.';
    } else {
        slider.style.transform = 'translateX(100%)';
        tabs[0].classList.remove('active');
        tabs[1].classList.add('active');
        submitBtn.innerText = 'Sign up';
        footerText.innerText = 'Already have an account? Tap Log in to begin.';
    }
}

function toggleAuthMode() {
    if (authMode === 'login') {
        switchAuthMode('signup');
    } else {
        switchAuthMode('login');
    }
}

function togglePasswordVisibility() {
    const passInput = document.getElementById('auth-password');
    const eyeIcon = document.getElementById('password-eye-icon');
    
    if (passInput.type === 'password') {
        passInput.type = 'text';
        eyeIcon.classList.remove('fa-eye');
        eyeIcon.classList.add('fa-eye-slash');
    } else {
        passInput.type = 'password';
        eyeIcon.classList.remove('fa-eye-slash');
        eyeIcon.classList.add('fa-eye');
    }
}

function handleAuthSubmit(event) {
    event.preventDefault();
    
    const name = document.getElementById('auth-name').value.trim();
    const password = document.getElementById('auth-password').value;
    const errorMsg = document.getElementById('auth-error-msg');
    
    if (!name || !password) {
        errorMsg.innerText = 'Name and Password are required.';
        return;
    }
    
    const endpoint = authMode === 'login' ? '/api/auth/login' : '/api/auth/signup';
    
    fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, password })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // Logged in successfully
            checkAuthSession();
            // Reset fields
            document.getElementById('auth-name').value = '';
            document.getElementById('auth-password').value = '';
        } else {
            errorMsg.innerText = data.message || 'An error occurred during authentication.';
        }
    })
    .catch(err => {
        console.error(err);
        errorMsg.innerText = 'Could not connect to the server. Try running python app.py.';
    });
}

function checkAuthSession() {
    fetch('/api/auth/me')
    .then(res => res.json())
    .then(data => {
        if (data.authenticated) {
            activeUser = data.user;
            document.getElementById('home-user-name').innerText = activeUser.name;
            document.getElementById('settings-username').innerText = activeUser.name;
            switchView('app-view');
            switchPanel('home');
        } else {
            activeUser = null;
            switchView('auth-view');
            switchAuthMode('login');
        }
    })
    .catch(err => {
        console.error("Session check failed: ", err);
        switchView('auth-view');
    });
}

function handleLogout() {
    fetch('/api/auth/logout', { method: 'POST' })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            activeUser = null;
            switchView('auth-view');
            switchAuthMode('login');
        }
    })
    .catch(err => console.error("Logout error: ", err));
}

// --- HOME PANEL DASHBOARD INITIALIZER ---

function initializeDashboard() {
    if (!activeUser) return;
    
    fetch('/api/user/stats')
    .then(res => res.json())
    .then(data => {
        if (data.success && data.stats) {
            const stats = data.stats;
            // Update stats row numbers
            document.getElementById('home-attempted-count').innerText = stats.total_attempted;
            document.getElementById('home-correct-count').innerText = stats.total_correct;
            document.getElementById('home-wrong-count').innerText = stats.total_wrong;
            
            // Update streak flame text
            document.getElementById('badge-streak-text').innerText = `${stats.streak} day streak`;
            // Update accuracy text
            document.getElementById('badge-accuracy-text').innerText = `${stats.accuracy}% accuracy`;
            
            // Sync user streak locally
            activeUser.streak = stats.streak;
        }
    })
    .catch(err => console.error("Error loading home stats: ", err));
}

// --- QUIZ AND PRACTICE ENGINE ---

function startGeneralQuiz() {
    startQuiz('General');
}

function startQuiz(examCategory) {
    selectedExam = examCategory;
    selectedSubject = ''; // Mixed
    
    document.getElementById('quiz-header-title').innerText = `${selectedExam} Exam Prep`;
    document.getElementById('quiz-header-subject').innerText = 'Mixed Subjects';
    
    // Switch to practice panel
    switchPanel('practice');
    
    // Fetch first question
    fetchQuestion();
}

function fetchQuestion() {
    hasAnswered = false;
    currentQuestion = null;
    
    // Clear any pending options timeout
    if (optionsTimeout) {
        clearTimeout(optionsTimeout);
        optionsTimeout = null;
    }
    
    // Immediately hide the options container to avoid showing old options or loading state
    const optionsContainer = document.querySelector('.options-container');
    if (optionsContainer) {
        optionsContainer.classList.add('delayed-hide');
    }
    
    // Reset buttons and feedback drawer
    const optButtons = document.querySelectorAll('.option-btn');
    optButtons.forEach(btn => {
        btn.className = 'option-btn';
        btn.querySelector('.option-letter').style.backgroundColor = '';
        btn.querySelector('.option-letter').style.color = '';
    });
    
    document.getElementById('explanation-drawer').style.display = 'none';
    document.getElementById('ai-pill-indicator').style.display = 'none';
    
    // Show loading shimmers / loader
    document.getElementById('quiz-question-text').innerText = 'Searching for standard question details...';
    document.getElementById('opt-A-text').innerText = 'Loading Option A...';
    document.getElementById('opt-B-text').innerText = 'Loading Option B...';
    document.getElementById('opt-C-text').innerText = 'Loading Option C...';
    document.getElementById('opt-D-text').innerText = 'Loading Option D...';
    
    // Disable clicks during load
    optButtons.forEach(btn => btn.classList.add('disabled'));
    
    // Check settings if AI is active and show loading text appropriately
    fetch('/api/user/settings')
    .then(res => res.json())
    .then(data => {
        if (data.success && data.settings && data.settings.use_ai_generation && data.settings.has_api_key) {
            document.getElementById('quiz-question-text').innerText = 'AI model is constructing a customized MCQ question...';
        }
    })
    .catch(() => {});

    // Request actual question
    let url = `/api/quiz/question?category=${encodeURIComponent(selectedExam)}`;
    if (selectedSubject) {
        url += `&subject=${encodeURIComponent(selectedSubject)}`;
    }
    
    fetch(url)
    .then(res => res.json())
    .then(data => {
        optButtons.forEach(btn => btn.classList.remove('disabled'));
        
        if (data.success && data.question) {
            currentQuestion = data.question;
            
            // Update question text and headers
            document.getElementById('quiz-question-text').innerText = currentQuestion.question_text;
            document.getElementById('quiz-header-subject').innerText = currentQuestion.subject;
            
            // Set option values
            document.getElementById('opt-A-text').innerText = currentQuestion.option_a;
            document.getElementById('opt-B-text').innerText = currentQuestion.option_b;
            document.getElementById('opt-C-text').innerText = currentQuestion.option_c;
            document.getElementById('opt-D-text').innerText = currentQuestion.option_d;
            
            // Toggle AI indicator badge
            if (currentQuestion.is_ai_generated) {
                document.getElementById('ai-pill-indicator').style.display = 'flex';
            }
            
            // Set bookmark icon status
            updateBookmarkIcon(currentQuestion.is_bookmarked === 1);
            
            // Show options after a 2-second delay to discourage immediate guessing and foster active recall
            optionsTimeout = setTimeout(() => {
                const container = document.querySelector('.options-container');
                if (container) {
                    container.classList.remove('delayed-hide');
                }
            }, 2000);
        } else {
            document.getElementById('quiz-question-text').innerText = data.message || 'No questions available. Try different category.';
        }
    })
    .catch(err => {
        console.error("Fetch question error: ", err);
        optButtons.forEach(btn => btn.classList.remove('disabled'));
        document.getElementById('quiz-question-text').innerText = 'Failed to load question. Please verify your connection or try again.';
    });
}

function selectOption(letter) {
    if (hasAnswered || !currentQuestion) return;
    hasAnswered = true;
    
    // Disable option clicks
    const optButtons = document.querySelectorAll('.option-btn');
    optButtons.forEach(btn => btn.classList.add('disabled'));
    
    // Submit answer to backend to record progress and get explanation details
    fetch('/api/quiz/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            question_id: currentQuestion.id,
            selected_option: letter
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // Apply visual styles to option buttons based on response
            optButtons.forEach(btn => {
                const btnLetter = btn.id.replace('opt-', '');
                if (btnLetter === data.correct_option) {
                    btn.classList.add('show-correct');
                }
            });
            
            const selectedBtn = document.getElementById(`opt-${letter}`);
            selectedBtn.classList.remove('disabled'); // Allow selecting click animation to show
            
            const feedbackHeader = document.getElementById('feedback-header');
            const feedbackIcon = document.getElementById('feedback-icon');
            const feedbackTitle = document.getElementById('feedback-title');
            
            if (data.is_correct) {
                selectedBtn.classList.add('selected-correct');
                feedbackHeader.className = 'feedback-header correct';
                feedbackIcon.className = 'fa-solid fa-circle-check';
                feedbackTitle.innerText = 'Correct Answer!';
            } else {
                selectedBtn.classList.add('selected-wrong');
                feedbackHeader.className = 'feedback-header wrong';
                feedbackIcon.className = 'fa-solid fa-circle-xmark';
                feedbackTitle.innerText = `Incorrect. The correct option is ${data.correct_option}.`;
            }
            
            // Show explanation text
            document.getElementById('explanation-text').innerText = data.explanation;
            
            // Slide up the explanation drawer
            document.getElementById('explanation-drawer').style.display = 'block';
        }
    })
    .catch(err => {
        console.error("Answer submission failed: ", err);
        hasAnswered = false; // Allow retrying on network failure
        optButtons.forEach(btn => btn.classList.remove('disabled'));
    });
}

function loadNextQuestion() {
    fetchQuestion();
}

function exitQuiz() {
    // Clear any pending options timeout
    if (optionsTimeout) {
        clearTimeout(optionsTimeout);
        optionsTimeout = null;
    }
    // Back to dashboard
    switchPanel('home');
}

// --- BOOKMARK CONTROLLERS ---

function toggleBookmarkCurrentQuestion() {
    if (!currentQuestion) return;
    
    const isBookmarked = currentQuestion.is_bookmarked === 1;
    const endpoint = isBookmarked ? '/api/quiz/unbookmark' : '/api/quiz/bookmark';
    
    fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question_id: currentQuestion.id })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            currentQuestion.is_bookmarked = isBookmarked ? 0 : 1;
            updateBookmarkIcon(!isBookmarked);
        }
    })
    .catch(err => console.error("Error bookmarking question: ", err));
}

function updateBookmarkIcon(active) {
    const bookmarkIcon = document.getElementById('quiz-bookmark-btn').querySelector('i');
    if (active) {
        bookmarkIcon.className = 'fa-solid fa-bookmark';
        bookmarkIcon.style.color = 'var(--primary)';
    } else {
        bookmarkIcon.className = 'fa-regular fa-bookmark';
        bookmarkIcon.style.color = '';
    }
}

// --- HISTORY LOG PANEL CONTROLLER ---

function loadHistory() {
    const historyList = document.getElementById('history-list');
    const emptyState = document.getElementById('history-empty');
    
    historyList.innerHTML = '<div class="quiz-loader"><div class="spinner"></div><p>Fetching your study log history...</p></div>';
    emptyState.style.display = 'none';
    
    fetch('/api/user/history')
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            historyData = data.history;
            renderHistoryCards();
        }
    })
    .catch(err => {
        console.error("History fetch error: ", err);
        historyList.innerHTML = '<p class="error-message">Could not load history. Please try again.</p>';
    });
}

function renderHistoryCards() {
    const historyList = document.getElementById('history-list');
    const emptyState = document.getElementById('history-empty');
    historyList.innerHTML = '';
    
    // Filter the items according to current historyFilter selection
    let filtered = historyData;
    if (historyFilter === 'correct') {
        filtered = historyData.filter(h => h.is_correct === 1);
    } else if (historyFilter === 'wrong') {
        filtered = historyData.filter(h => h.is_correct === 0);
    } else if (historyFilter === 'bookmarked') {
        filtered = historyData.filter(h => h.is_bookmarked === 1);
    }
    
    if (filtered.length === 0) {
        emptyState.style.display = 'flex';
        return;
    }
    
    emptyState.style.display = 'none';
    
    filtered.forEach(item => {
        const dateObj = new Date(item.attempted_at + "Z"); // SQLite dates are UTC
        const formattedDate = dateObj.toLocaleDateString(undefined, {month: 'short', day: 'numeric', hour: '2-digit', minute:'2-digit'});
        
        const card = document.createElement('div');
        card.className = 'history-card';
        card.id = `history-card-${item.attempt_id}`;
        card.onclick = () => toggleHistoryCardExpand(item.attempt_id);
        
        const isCorrect = item.is_correct === 1;
        const iconClass = isCorrect ? 'fa-circle-check text-correct' : 'fa-circle-xmark text-wrong';
        const statusClass = isCorrect ? 'correct' : 'wrong';
        const statusText = isCorrect ? 'Correct' : 'Incorrect';
        
        card.innerHTML = `
            <div class="history-card-header">
                <span class="history-category-badge">${item.category} • ${item.subject}</span>
                <span class="history-status-indicator ${statusClass}">
                    <i class="fa-solid ${iconClass}"></i> ${statusText}
                </span>
            </div>
            <div class="history-card-body">
                <p>${item.question_text}</p>
            </div>
            <div class="history-card-expanded" id="history-expanded-${item.attempt_id}">
                <p class="full-question">${item.question_text}</p>
                
                <div class="history-option-detail ${item.correct_option === 'A' ? 'correct-opt' : ''} ${item.selected_option === 'A' && !isCorrect ? 'selected-wrong-opt' : ''}">
                    <span>A. ${item.option_a}</span>
                    ${item.selected_option === 'A' ? '<strong>(Your Choice)</strong>' : ''}
                </div>
                <div class="history-option-detail ${item.correct_option === 'B' ? 'correct-opt' : ''} ${item.selected_option === 'B' && !isCorrect ? 'selected-wrong-opt' : ''}">
                    <span>B. ${item.option_b}</span>
                    ${item.selected_option === 'B' ? '<strong>(Your Choice)</strong>' : ''}
                </div>
                <div class="history-option-detail ${item.correct_option === 'C' ? 'correct-opt' : ''} ${item.selected_option === 'C' && !isCorrect ? 'selected-wrong-opt' : ''}">
                    <span>C. ${item.option_c}</span>
                    ${item.selected_option === 'C' ? '<strong>(Your Choice)</strong>' : ''}
                </div>
                <div class="history-option-detail ${item.correct_option === 'D' ? 'correct-opt' : ''} ${item.selected_option === 'D' && !isCorrect ? 'selected-wrong-opt' : ''}">
                    <span>D. ${item.option_d}</span>
                    ${item.selected_option === 'D' ? '<strong>(Your Choice)</strong>' : ''}
                </div>
                
                <div class="history-exp-section">
                    <strong>Explanation:</strong> ${item.explanation}
                </div>
                <div style="font-size: 11px; color: var(--text-muted); margin-top:10px; text-align:right;">
                    Attempted on: ${formattedDate}
                </div>
            </div>
        `;
        
        historyList.appendChild(card);
    });
}

function filterHistory(filterType) {
    historyFilter = filterType;
    
    // Toggle active classes on filter pills
    const pills = document.querySelectorAll('.filter-pill');
    pills.forEach(pill => pill.classList.remove('active'));
    
    event.currentTarget.classList.add('active');
    
    renderHistoryCards();
}

function toggleHistoryCardExpand(attemptId) {
    // Stop event bubbling if click lands on internal spans
    const details = document.getElementById(`history-expanded-${attemptId}`);
    const card = document.getElementById(`history-card-${attemptId}`);
    
    const isShowing = details.style.display === 'block';
    
    // Close other expanded cards first
    document.querySelectorAll('.history-card-expanded').forEach(el => el.style.display = 'none');
    
    if (!isShowing) {
        details.style.display = 'block';
        card.style.borderColor = 'var(--primary)';
        // Scroll to card smoothly
        card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } else {
        details.style.display = 'none';
        card.style.borderColor = '';
    }
}

// --- STATS PANEL DASHBOARD ENGINE ---

function loadStatsDashboard() {
    fetch('/api/user/stats')
    .then(res => res.json())
    .then(data => {
        if (data.success && data.stats) {
            const stats = data.stats;
            
            // Streak Flame and stats box numbers
            document.getElementById('stats-streak-num').innerText = stats.streak;
            document.getElementById('stats-total-attempted').innerText = stats.total_attempted;
            document.getElementById('stats-total-correct').innerText = stats.total_correct;
            document.getElementById('stats-total-wrong').innerText = stats.total_wrong;
            document.getElementById('stats-overall-accuracy').innerText = `${stats.accuracy}%`;
            
            // Build subject accuracy list
            const subjectContainer = document.getElementById('stats-subject-list');
            subjectContainer.innerHTML = '';
            
            const SUBJECTS = ['History', 'Geography', 'Polity', 'Economy', 'Science', 'Current Affairs', 'General Knowledge'];
            SUBJECTS.forEach(subject => {
                const subStat = stats.subject_stats[subject] || { attempted: 0, correct: 0 };
                const pct = subStat.attempted > 0 ? Math.round((subStat.correct / subStat.attempted) * 100) : 0;
                
                const progressRow = document.createElement('div');
                progressRow.className = 'progress-row';
                progressRow.innerHTML = `
                    <div class="progress-row-header">
                        <span>${subject}</span>
                        <span>${pct}% (${subStat.correct}/${subStat.attempted})</span>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar-fill" id="subject-bar-${subject.replace(/\s+/g, '')}" style="width: 0%"></div>
                    </div>
                `;
                subjectContainer.appendChild(progressRow);
                
                // Animate expansion after painting DOM
                setTimeout(() => {
                    const bar = document.getElementById(`subject-bar-${subject.replace(/\s+/g, '')}`);
                    if (bar) bar.style.width = `${pct}%`;
                }, 100);
            });
            
            // Build category accuracy list
            const categoryContainer = document.getElementById('stats-category-list');
            categoryContainer.innerHTML = '';
            
            const CATEGORIES = ['General', 'UPSC', 'SSC', 'Banking', 'Railways', 'State PSC'];
            CATEGORIES.forEach(category => {
                const catStat = stats.category_stats[category] || { attempted: 0, correct: 0 };
                const pct = catStat.attempted > 0 ? Math.round((catStat.correct / catStat.attempted) * 100) : 0;
                
                const progressRow = document.createElement('div');
                progressRow.className = 'progress-row';
                progressRow.innerHTML = `
                    <div class="progress-row-header">
                        <span>${category} Exam</span>
                        <span>${pct}% (${catStat.correct}/${catStat.attempted})</span>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar-fill" id="category-bar-${category.replace(/\s+/g, '')}" style="width: 0%"></div>
                    </div>
                `;
                categoryContainer.appendChild(progressRow);
                
                // Animate expansion after painting DOM
                setTimeout(() => {
                    const bar = document.getElementById(`category-bar-${category.replace(/\s+/g, '')}`);
                    if (bar) bar.style.width = `${pct}%`;
                }, 100);
            });
        }
    })
    .catch(err => console.error("Stats load error: ", err));
}

// --- SETTINGS PANEL CONTROLLER ---

function loadSettings() {
    fetch('/api/user/settings')
    .then(res => res.json())
    .then(data => {
        if (data.success && data.settings) {
            const settings = data.settings;
            document.getElementById('settings-ai-toggle').checked = settings.use_ai_generation;
            
            const geminiInput = document.getElementById('settings-gemini-key');
            if (settings.has_api_key) {
                geminiInput.placeholder = `Masked key: ${settings.masked_api_key}`;
                geminiInput.value = ''; // Don't write masked placeholder to value
            } else {
                geminiInput.placeholder = 'Enter Gemini API Key';
                geminiInput.value = '';
            }
            
            toggleAIFieldVisibility();
        }
    })
    .catch(err => console.error("Settings load error: ", err));
}

function toggleAIFieldVisibility() {
    const isChecked = document.getElementById('settings-ai-toggle').checked;
    const keyContainer = document.getElementById('gemini-key-container');
    if (isChecked) {
        keyContainer.style.display = 'flex';
    } else {
        keyContainer.style.display = 'none';
    }
}

function toggleSettingsKeyVisibility() {
    const keyInput = document.getElementById('settings-gemini-key');
    const eyeIcon = document.getElementById('settings-key-eye-icon');
    
    if (keyInput.type === 'password') {
        keyInput.type = 'text';
        eyeIcon.classList.remove('fa-eye');
        eyeIcon.classList.add('fa-eye-slash');
    } else {
        keyInput.type = 'password';
        eyeIcon.classList.remove('fa-eye-slash');
        eyeIcon.classList.add('fa-eye');
    }
}

function saveSettings() {
    const use_ai_generation = document.getElementById('settings-ai-toggle').checked;
    let gemini_api_key = document.getElementById('settings-gemini-key').value.trim();
    
    const saveBtn = document.querySelector('.settings-save-row button');
    saveBtn.innerText = 'Saving...';
    saveBtn.disabled = true;

    // Check if key is left blank but had a value previously
    // The endpoint will not overwrite key with blank if not input
    fetch('/api/user/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            use_ai_generation,
            gemini_api_key
        })
    })
    .then(res => res.json())
    .then(data => {
        saveBtn.innerText = 'Save Settings';
        saveBtn.disabled = false;
        if (data.success) {
            // Success alert message or animation
            alert('Settings saved successfully!');
            switchPanel('home');
        } else {
            alert('Error saving settings: ' + data.message);
        }
    })
    .catch(err => {
        console.error(err);
        saveBtn.innerText = 'Save Settings';
        saveBtn.disabled = false;
        alert('Could not save settings. Verify that Flask is running.');
    });
}
