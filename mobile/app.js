// PREPP-Lingo Mobile App - JavaScript

// Game State
let gameState = {
    isPlaying: false,
    currentWord: null,
    currentAudio: null,
    words: [],
    sessionWords: [],
    currentIndex: 0,
    hearts: 3,
    score: 0,
    correctCount: 0,
    totalWords: 0,
    streak: 0,
    // Timer state
    timerActive: false,
    timerDuration: 10,
    timerInterval: null,
    remainingTime: 0, // For carrying over time in action mode
    // Missed words tracking
    missedWords: [],
    settings: {
        gameMode: 'practice',
        difficulty: 'medium',
        wordCount: 10,
        showTranslation: true,
        currentChapter: 'capital_one'
    },
    chapterProgress: {
        'capital_one': { unlocked: true, completed: false, bestScore: 0 },
        'capital_two': { unlocked: false, completed: false, bestScore: 0 },
        'capital_three': { unlocked: false, completed: false, bestScore: 0 }
    }
};

// Norwegian Words Data - Loaded from selected chapter
let wordsDatabase = {
    easy: [],
    medium: [],
    hard: []
};

// Load words from selected chapter
async function loadChapterWords(chapterId) {
    console.log('📚 Loading words for chapter:', chapterId);
    
    try {
        const response = await fetch(`words_${chapterId}.json`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        wordsDatabase = data;
        console.log('✅ Loaded words from chapter system:', {
            chapter: chapterId,
            easy: data.easy.length,
            medium: data.medium.length,
            hard: data.hard.length,
            total: data.easy.length + data.medium.length + data.hard.length
        });
        
        return data;
    } catch (error) {
        console.error('❌ Error loading words for chapter', chapterId, ':', error);
        // Fallback to basic words if file not found
        wordsDatabase = {
            easy: [
                { word: "hei", translation: "hello", audio: null },
                { word: "takk", translation: "thanks", audio: null }
            ],
            medium: [
                { word: "velkommen", translation: "welcome", audio: null }
            ],
            hard: [
                { word: "Innsatsfaktorer", translation: "input factors", audio: null }
            ]
        };
        return wordsDatabase;
    }
}

// Initialize App
window.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 PREPP-Lingo Mobile App v2.0 - REAL AUDIO VERSION LOADED!');
    console.log('📱 DOM Content Loaded - Starting initialization...');
    
    try {
        console.log('🔧 Loading settings...');
        loadSettings();
        console.log('✅ Settings loaded');
        
        console.log('📊 Loading game stats...');
        loadGameStats();
        console.log('✅ Game stats loaded');
        
        // Load words for the current chapter and wait for completion
        const currentChapter = gameState.settings.currentChapter;
        console.log('⏳ Loading chapter words for:', currentChapter);
        
        const words = await loadChapterWords(currentChapter);
        console.log('✅ Chapter words loaded successfully!', words);
        
        console.log('🎨 Hiding loading screen...');
        hideLoading();
        console.log('✅ Loading screen hidden');
        
        console.log('🔗 Setting up event listeners...');
        setupEventListeners();
        console.log('✅ Event listeners set up');
        
        console.log('🎉 App initialization complete!');
        
    } catch (error) {
        console.error('❌ Initialization failed:', error);
        console.log('🆘 Hiding loading screen anyway...');
        hideLoading();
    }
});

function hideLoading() {
    console.log('🎨 hideLoading() called');
    setTimeout(() => {
        const loadingScreen = document.getElementById('loading-screen');
        const app = document.getElementById('app');
        
        if (loadingScreen) {
            loadingScreen.style.display = 'none';
            console.log('✅ Loading screen hidden');
        } else {
            console.error('❌ Loading screen element not found');
        }
        
        if (app) {
            app.style.display = 'block';
            console.log('✅ App displayed');
        } else {
            console.error('❌ App element not found');
        }
    }, 1000);
}

// Emergency timeout to prevent infinite loading
setTimeout(() => {
    console.log('⚠️ Emergency timeout triggered - forcing app to show');
    hideLoading();
}, 10000); // 10 second timeout

function setupEventListeners() {
    // Enter key to submit - with better error handling
    const answerInput = document.getElementById('answer-input');
    if (answerInput) {
        answerInput.addEventListener('keypress', (e) => {
            console.log('🔑 Key pressed:', e.key);
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                console.log('✅ Enter key detected - submitting answer');
                submitAnswer();
            }
        });
        console.log('✅ Enter key listener attached');
    } else {
        console.error('❌ Answer input element not found!');
    }
}

// Settings Management
function loadSettings() {
    const saved = localStorage.getItem('preppLingoSettings');
    if (saved) {
        gameState.settings = JSON.parse(saved);
    }
    updateSettingsUI();
}

function saveSettings() {
    console.log('💾 saveSettings() called');
    
    try {
        const oldChapter = gameState.settings.currentChapter;
        
        gameState.settings.gameMode = document.getElementById('game-mode').value;
        gameState.settings.difficulty = document.getElementById('difficulty').value;
        gameState.settings.wordCount = parseInt(document.getElementById('word-count').value);
        gameState.settings.showTranslation = document.getElementById('show-translation').checked;
        gameState.settings.currentChapter = document.getElementById('chapter-select').value;
        
        console.log('💾 Settings updated:', gameState.settings);
        
        // If chapter changed, reload words
        if (oldChapter !== gameState.settings.currentChapter) {
            console.log(`🔄 Chapter changed from ${oldChapter} to ${gameState.settings.currentChapter}`);
            loadChapterWords(gameState.settings.currentChapter).then(() => {
                console.log('✅ New chapter words loaded!');
            }).catch(error => {
                console.error('❌ Failed to load new chapter words:', error);
            });
        }
        
        localStorage.setItem('preppLingoSettings', JSON.stringify(gameState.settings));
        console.log('💾 Settings saved to localStorage');
        
        closeSettings();
        console.log('💾 Settings modal closed');
        
        showNotification('✅ Innstillinger lagret!', 'success');
        console.log('💾 Notification shown');
        
    } catch (error) {
        console.error('❌ Error in saveSettings:', error);
        showNotification('❌ Feil ved lagring av innstillinger', 'error');
    }
}

function updateSettingsUI() {
    document.getElementById('game-mode').value = gameState.settings.gameMode;
    document.getElementById('difficulty').value = gameState.settings.difficulty;
    document.getElementById('word-count').value = gameState.settings.wordCount;
    document.getElementById('show-translation').checked = gameState.settings.showTranslation;
    document.getElementById('chapter-select').value = gameState.settings.currentChapter;
    
    // Update chapter selector with locked/unlocked status
    updateChapterSelector();
}

function openSettings() {
    document.getElementById('settings-modal').style.display = 'block';
}

function closeSettings() {
    document.getElementById('settings-modal').style.display = 'none';
}

// Game Stats
function loadGameStats() {
    const saved = localStorage.getItem('preppLingoStats');
    if (saved) {
        const stats = JSON.parse(saved);
        gameState.streak = stats.streak || 0;
        document.getElementById('streak-count').textContent = gameState.streak;
    }
    
    // Load chapter progress
    const chapterProgress = localStorage.getItem('preppLingoChapterProgress');
    if (chapterProgress) {
        gameState.chapterProgress = JSON.parse(chapterProgress);
    }
}

function saveGameStats() {
    const stats = {
        streak: gameState.streak,
        lastPlayed: new Date().toISOString()
    };
    localStorage.setItem('preppLingoStats', JSON.stringify(stats));
}

// Start Session
function startSession() {
    const gameMode = gameState.settings.gameMode;
    const difficulty = gameState.settings.difficulty;
    const wordCount = gameState.settings.wordCount;
    
    console.log('🎯 Starting session with gameMode:', gameMode, 'difficulty:', difficulty);
    console.log('📚 Available words:', wordsDatabase);
    
    if (gameMode === 'action') {
        // Aksjon mode: Load ALL words from current chapter (all difficulties)
        const allWords = [
            ...wordsDatabase.easy,
            ...wordsDatabase.medium,
            ...wordsDatabase.hard
        ];
        console.log('📝 Aksjon mode: Loading ALL words from current chapter:', {
            chapter: gameState.settings.currentChapter,
            easy: wordsDatabase.easy.length,
            medium: wordsDatabase.medium.length,
            hard: wordsDatabase.hard.length,
            total: allWords.length
        });
        gameState.words = allWords;
        gameState.sessionWords = shuffleArray(allWords); // Use ALL words in Aksjon mode
    } else {
        // Øvelse mode: Load words based on difficulty only
        console.log('📝 Øvelse mode: Loading words for difficulty:', difficulty, 'from chapter:', gameState.settings.currentChapter);
        gameState.words = [...wordsDatabase[difficulty]];
        gameState.sessionWords = shuffleArray(gameState.words).slice(0, wordCount);
    }
    gameState.currentIndex = 0;
    gameState.hearts = 3;
    gameState.correctCount = 0;
    gameState.totalWords = 0;
    gameState.missedWords = []; // Reset missed words
    gameState.remainingTime = 0; // Reset remaining time
    gameState.isPlaying = true;
    
    console.log('🎮 Session words selected:', gameState.sessionWords);
    
    // Update UI
    document.getElementById('start-btn').style.display = 'none';
    enableGameControls();
    updateHeartsDisplay();
    
    // Load first word
    loadNextWord();
}

function loadNextWord() {
    console.log('🔄 Loading next word...', {
        currentIndex: gameState.currentIndex,
        totalWords: gameState.sessionWords.length
    });
    
    if (gameState.currentIndex >= gameState.sessionWords.length) {
        console.log('🏁 Session ended - calling endSession()');
        endSession();
        return;
    }
    
    gameState.currentWord = gameState.sessionWords[gameState.currentIndex];
    gameState.totalWords++;
    console.log('📝 Current word:', gameState.currentWord);
    
    // Update UI
    updateWordCounter();
    clearInput();
    clearResult();
    
    // Show instruction
    const instruction = gameState.settings.showTranslation 
        ? `Skriv: "${gameState.currentWord.translation}"`
        : "Lytt og skriv ordet";
    document.getElementById('instruction-text').textContent = instruction;
    
    // Auto-play audio
    setTimeout(() => playAudio(), 500);
    
    // Start timer for action mode
    startTimer();
}

function playAudio() {
    console.log('🎵🎵🎵 REAL AUDIO FUNCTION CALLED - NO ROBOTIC VOICE! 🎵🎵🎵');
    console.log('Current word:', gameState.currentWord);
    console.log('Game state:', gameState);
    
    // Stop any existing audio first
    if (gameState.currentAudio) {
        console.log('🛑 Stopping existing audio');
        gameState.currentAudio.pause();
        gameState.currentAudio.currentTime = 0;
        gameState.currentAudio = null;
    }
    
    // Play real MP3 audio file
    if (gameState.currentWord && gameState.currentWord.audio) {
        console.log('🎵 Playing REAL MP3 file:', gameState.currentWord.audio);
        console.log('Word object:', gameState.currentWord);
        
        // Create NEW audio element every time to avoid caching issues
        gameState.currentAudio = new Audio();
        gameState.currentAudio.src = gameState.currentWord.audio;
        console.log('🎵 Audio element created with src:', gameState.currentAudio.src);
        
        // Add event listeners for debugging
        gameState.currentAudio.addEventListener('loadstart', () => {
            console.log('🔄 Audio loading started');
        });
        
        gameState.currentAudio.addEventListener('canplay', () => {
            console.log('✅ Audio can play');
        });
        
        gameState.currentAudio.addEventListener('error', (e) => {
            console.error('❌ Audio error:', e);
            console.error('❌ Audio src was:', gameState.currentAudio.src);
        });
        
        // Play the audio
        gameState.currentAudio.play().then(() => {
            console.log('🎵✅ REAL MP3 AUDIO PLAYING SUCCESSFULLY!');
        }).catch(error => {
            console.error('❌ Audio playback failed:', error);
            console.error('❌ Audio src was:', gameState.currentAudio.src);
            showNotification('⚠️ Kunne ikke spille lyd', 'warning');
        });
        
        // Visual feedback
        const btn = document.getElementById('play-audio-btn');
        if (btn) {
            btn.style.background = 'var(--success)';
            setTimeout(() => {
                btn.style.background = 'var(--primary)';
            }, 1000);
        }
    } else {
        console.log('❌ No audio available for word:', gameState.currentWord);
        console.log('❌ Current word exists:', !!gameState.currentWord);
        console.log('❌ Audio property exists:', !!(gameState.currentWord && gameState.currentWord.audio));
        showNotification('⚠️ Ingen lydfil tilgjengelig', 'warning');
    }
}

function submitAnswer() {
    if (!gameState.isPlaying) return;
    
    const input = document.getElementById('answer-input').value.trim();
    if (!input) {
        showNotification('⚠️ Skriv et svar først!', 'warning');
        return;
    }
    
    const correct = input.toLowerCase() === gameState.currentWord.word.toLowerCase();
    const gameMode = gameState.settings.gameMode;
    
    if (correct) {
        // Stop timer and audio
        stopTimer();
        if (gameState.currentAudio) {
            gameState.currentAudio.pause();
            gameState.currentAudio.currentTime = 0;
            gameState.currentAudio = null;
        }
        
        gameState.correctCount++;
        gameState.score += 10;
        showResult(true, gameState.currentWord.word);
        showNotification('🎉 Riktig!', 'success');
        
        // In action mode, save remaining time for next word
        if (gameMode === 'action') {
            gameState.remainingTime = gameState.timerDuration;
            console.log(`💾 Saved remaining time: ${gameState.remainingTime} seconds`);
        }
        
        // Move to next word after delay
        setTimeout(() => {
            gameState.currentIndex++;
            if (gameState.currentIndex < gameState.sessionWords.length) {
                loadNextWord();
            } else {
                endSession();
            }
        }, 2000);
    } else {
        // Wrong answer - handle differently for practice vs action
        if (gameMode === 'practice') {
            // Practice mode: Show wrong message but allow immediate retry
            // DO NOT restart timer - keep the same 20 seconds for the question
            showResult(false, gameState.currentWord.word);
            showNotification('❌ Feil! Prøv igjen.', 'warning');
            
            // Clear input and focus back for retry
            document.getElementById('answer-input').value = '';
            document.getElementById('answer-input').focus();
        } else {
            // Action mode: Lose heart immediately for wrong answer
            // Stop timer and audio first
            stopTimer();
            if (gameState.currentAudio) {
                gameState.currentAudio.pause();
                gameState.currentAudio.currentTime = 0;
                gameState.currentAudio = null;
            }
            
            gameState.hearts--;
            updateHeartsDisplay();
            showResult(false, gameState.currentWord.word);
            showNotification('❌ Feil! Mistet et hjerte.', 'error');
            
            if (gameState.hearts <= 0) {
                setTimeout(() => endSession(), 2000);
            } else {
                // Move to next word after delay
                setTimeout(() => {
                    gameState.currentIndex++;
                    if (gameState.currentIndex < gameState.sessionWords.length) {
                        loadNextWord();
                    } else {
                        endSession();
                    }
                }, 2000);
            }
        }
    }
}

function useHint() {
    if (!gameState.currentWord) return;
    
    const word = gameState.currentWord.word;
    const input = document.getElementById('answer-input');
    const currentValue = input.value;
    
    if (currentValue.length < word.length) {
        input.value = word.substring(0, currentValue.length + 1);
        showNotification('💡 Hint lagt til!', 'success');
    } else {
        showNotification('💡 Ingen flere hint!', 'warning');
    }
}

function showResult(correct, correctAnswer) {
    const resultDiv = document.getElementById('result-display');
    resultDiv.className = 'result-display ' + (correct ? 'correct' : 'incorrect');
    
    if (correct) {
        resultDiv.innerHTML = `✅ Riktig!<br><strong>${correctAnswer}</strong>`;
    } else {
        const userAnswer = document.getElementById('answer-input').value;
        resultDiv.innerHTML = `❌ Feil!<br>Du skrev: <strong>${userAnswer}</strong><br>Riktig: <strong>${correctAnswer}</strong>`;
    }
}

function clearResult() {
    document.getElementById('result-display').innerHTML = '';
    document.getElementById('result-display').className = 'result-display';
}

function endSession() {
    gameState.isPlaying = false;
    
    // Stop timer
    stopTimer();
    
    // Stop any playing audio
    if (gameState.currentAudio) {
        gameState.currentAudio.pause();
        gameState.currentAudio.currentTime = 0;
        gameState.currentAudio = null;
    }
    
    const accuracy = Math.round((gameState.correctCount / gameState.sessionWords.length) * 100);
    
    // Update streak
    if (accuracy >= 70) {
        gameState.streak++;
    } else {
        gameState.streak = 0;
    }
    
    // Update chapter progress
    updateChapterProgress(accuracy);
    
    saveGameStats();
    
    // Show results
    const resultDiv = document.getElementById('result-display');
    resultDiv.className = 'result-display';
    
    let missedWordsHtml = '';
    if (gameState.missedWords.length > 0) {
        missedWordsHtml = `
            <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 10px;">
                <h3 style="color: var(--error); margin-bottom: 10px;">📝 Ord du mistet:</h3>
                ${gameState.missedWords.map(missed => 
                    `<div style="margin: 8px 0; padding: 8px; background: white; border-radius: 5px;">
                        <strong>${missed.word}</strong> - ${missed.translation}
                    </div>`
                ).join('')}
            </div>
        `;
    }
    
    // Chapter progression message
    let chapterMessage = '';
    const currentChapter = gameState.settings.currentChapter;
    const chapterName = currentChapter.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    
    if (accuracy >= 70) {
        chapterMessage = `
            <div style="margin: 15px 0; padding: 15px; background: var(--success); color: white; border-radius: 10px;">
                <h3>🏆 Kapitel ${chapterName} fullført!</h3>
                <p>Du har oppnådd ${accuracy}% nøyaktighet!</p>
                ${getNextChapterMessage()}
            </div>
        `;
    } else {
        chapterMessage = `
            <div style="margin: 15px 0; padding: 15px; background: var(--warning); color: white; border-radius: 10px;">
                <h3>📚 Fortsett å øve!</h3>
                <p>Du trenger 70% for å låse opp neste kapittel.</p>
                <p>Nåværende resultat: ${accuracy}%</p>
            </div>
        `;
    }

    resultDiv.innerHTML = `
        <h2>🎉 Økten fullført!</h2>
        <p style="font-size: 24px; margin: 20px 0;">
            ${gameState.correctCount} / ${gameState.sessionWords.length}
        </p>
        <p style="font-size: 18px; color: var(--primary);">
            Nøyaktighet: ${accuracy}%
        </p>
        <p style="margin-top: 20px;">
            Poeng: ${gameState.score}
        </p>
        ${chapterMessage}
        ${missedWordsHtml}
    `;
    
    document.getElementById('instruction-text').textContent = 'Trykk "Start" for å prøve igjen';
    document.getElementById('start-btn').style.display = 'block';
    document.getElementById('streak-count').textContent = gameState.streak;
    
    disableGameControls();
}

// UI Helpers
function enableGameControls() {
    document.getElementById('play-audio-btn').disabled = false;
    document.getElementById('answer-input').disabled = false;
    document.getElementById('submit-btn').disabled = false;
    document.getElementById('hint-btn').disabled = false;
}

function disableGameControls() {
    document.getElementById('play-audio-btn').disabled = true;
    document.getElementById('answer-input').disabled = true;
    document.getElementById('submit-btn').disabled = true;
    document.getElementById('hint-btn').disabled = true;
}

function clearInput() {
    document.getElementById('answer-input').value = '';
}

function updateHeartsDisplay() {
    const hearts = '❤️'.repeat(gameState.hearts) + '🖤'.repeat(3 - gameState.hearts);
    document.getElementById('hearts-display').textContent = hearts;
}

function updateWordCounter() {
    document.getElementById('word-counter').textContent = 
        `${gameState.currentIndex + 1}/${gameState.sessionWords.length}`;
}

function showNotification(message, type) {
    // Simple toast notification
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: ${type === 'success' ? 'var(--success)' : type === 'warning' ? 'var(--warning)' : 'var(--error)'};
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        font-weight: 600;
        z-index: 10000;
        animation: slideDown 0.3s;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideUp 0.3s';
        setTimeout(() => toast.remove(), 300);
    }, 2000);
}

// Utility Functions
function shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

// Timer Functions
function startTimer() {
    // CRITICAL: Stop any existing timer first to prevent multiple timers running
    stopTimer();
    
    const gameMode = gameState.settings.gameMode;
    
    // Set timer duration based on game mode
    if (gameMode === 'action') {
        // Action mode: difficulty-based timing + carry over remaining time
        const difficulty = gameState.settings.difficulty;
        const baseTime = {
            'easy': 10,    // 5 + 5
            'medium': 15,  // 10 + 5
            'hard': 20     // 15 + 5
        }[difficulty];
        
        // Add remaining time from previous word (if any)
        gameState.timerDuration = baseTime + gameState.remainingTime;
        console.log(`⏰ Aksjon timer: base=${baseTime}, carryover=${gameState.remainingTime}, total=${gameState.timerDuration}`);
        gameState.remainingTime = 0; // Reset for next word
    } else if (gameMode === 'practice') {
        // Practice mode: always 20 seconds
        gameState.timerDuration = 20;
        gameState.remainingTime = 0; // Reset for practice mode
    }
    
    // Show timer display for both modes
    const timerDisplay = document.getElementById('timer-display');
    const timerCountdown = document.getElementById('timer-countdown');
    
    if (timerDisplay && timerCountdown) {
        timerDisplay.style.display = 'block';
        timerCountdown.textContent = gameState.timerDuration;
        console.log('✅ Timer display shown:', gameState.timerDuration);
    } else {
        console.error('❌ Timer elements not found!');
    }
    
    gameState.timerActive = true;
    
    // Store the gameMode in a variable to avoid issues with closure
    const currentGameMode = gameState.settings.gameMode;
    
    gameState.timerInterval = setInterval(() => {
        gameState.timerDuration--;
        const timerCountdown = document.getElementById('timer-countdown');
        if (timerCountdown) {
            timerCountdown.textContent = gameState.timerDuration;
        }
        
        // Change color when time is running low
        const timerElement = document.getElementById('timer-countdown');
        if (gameState.timerDuration <= 3) {
            timerElement.style.color = 'var(--error)';
        } else {
            timerElement.style.color = 'var(--primary)';
        }
        
        if (gameState.timerDuration <= 0) {
            stopTimer();
            // Time's up - handle differently for practice vs action
            if (currentGameMode === 'practice') {
                // In practice mode, lose a heart when time runs out and track missed word
                gameState.hearts--;
                updateHeartsDisplay();
                showResult(false, gameState.currentWord.word);
                showNotification('⏰ Tiden er ute! Mistet et hjerte.', 'error');
                
                // Track missed word
                gameState.missedWords.push({
                    word: gameState.currentWord.word,
                    translation: gameState.currentWord.translation,
                    reason: 'timeout'
                });
                
                // Move to next word after delay
                setTimeout(() => {
                    gameState.currentIndex++;
                    if (gameState.currentIndex < gameState.sessionWords.length) {
                        loadNextWord();
                    } else {
                        endSession();
                    }
                }, 2000);
            } else {
                // In action mode, handle timeout directly (don't call submitAnswer with empty input)
                console.log('⏰ Aksjon mode timeout - no answer submitted');
                
                // Stop audio
                if (gameState.currentAudio) {
                    gameState.currentAudio.pause();
                    gameState.currentAudio.currentTime = 0;
                    gameState.currentAudio = null;
                }
                
                // Show timeout result
                showResult(false, gameState.currentWord.word);
                showNotification('⏰ Tiden er ute! Ingen svar gitt.', 'error');
                
                // Track missed word
                gameState.missedWords.push({
                    word: gameState.currentWord.word,
                    translation: gameState.currentWord.translation,
                    reason: 'timeout'
                });
                
                // Move to next word after delay
                setTimeout(() => {
                    gameState.currentIndex++;
                    if (gameState.currentIndex < gameState.sessionWords.length) {
                        loadNextWord();
                    } else {
                        endSession();
                    }
                }, 2000);
            }
        }
    }, 1000);
}

function stopTimer() {
    console.log('🛑 stopTimer() called');
    
    if (gameState.timerInterval) {
        console.log('🛑 Clearing existing timer interval');
        clearInterval(gameState.timerInterval);
        gameState.timerInterval = null;
    }
    
    gameState.timerActive = false;
    
    const timerDisplay = document.getElementById('timer-display');
    if (timerDisplay) {
        timerDisplay.style.display = 'none';
        console.log('🛑 Timer display hidden');
    } else {
        console.error('❌ Timer display element not found');
    }
}

// Chapter progression functions
function updateChapterProgress(accuracy) {
    const currentChapter = gameState.settings.currentChapter;
    const gameMode = gameState.settings.gameMode;
    
    console.log(`📊 Updating chapter progress:`, {
        currentChapter,
        gameMode,
        accuracy,
        currentBestScore: gameState.chapterProgress[currentChapter].bestScore
    });
    
    // Update best score for current chapter
    if (accuracy > gameState.chapterProgress[currentChapter].bestScore) {
        gameState.chapterProgress[currentChapter].bestScore = accuracy;
        console.log(`📈 New best score for ${currentChapter}: ${accuracy}%`);
    }
    
    // Check if chapter is completed (70% threshold) - ONLY in Aksjon mode
    if (accuracy >= 70 && gameMode === 'action') {
        console.log(`🎯 Chapter completion threshold reached in Aksjon mode: ${accuracy}% >= 70%`);
        gameState.chapterProgress[currentChapter].completed = true;
        
        // Unlock next chapter
        const chapterOrder = ['capital_one', 'capital_two', 'capital_three'];
        const currentIndex = chapterOrder.indexOf(currentChapter);
        if (currentIndex < chapterOrder.length - 1) {
            const nextChapter = chapterOrder[currentIndex + 1];
            gameState.chapterProgress[nextChapter].unlocked = true;
            console.log(`🔓 Unlocked chapter: ${nextChapter} (from Aksjon mode)`);
            
            // Update chapter selector immediately
            setTimeout(() => {
                updateChapterSelector();
                console.log(`🔄 Chapter selector updated`);
            }, 100);
        } else {
            console.log(`🏆 All chapters completed!`);
        }
    } else if (accuracy >= 70 && gameMode === 'practice') {
        console.log(`✅ Good score in Øvelse mode: ${accuracy}%, but chapters only unlock in Aksjon mode`);
    } else {
        console.log(`❌ Chapter completion threshold not reached: ${accuracy}% < 70% or not Aksjon mode`);
    }
    
    // Save chapter progress to localStorage
    localStorage.setItem('preppLingoChapterProgress', JSON.stringify(gameState.chapterProgress));
    console.log(`💾 Chapter progress saved to localStorage`);
}

function getNextChapterMessage() {
    const chapterOrder = ['capital_one', 'capital_two', 'capital_three'];
    const currentChapter = gameState.settings.currentChapter;
    const gameMode = gameState.settings.gameMode;
    const currentIndex = chapterOrder.indexOf(currentChapter);
    
    // Only show chapter progression messages in Aksjon mode
    if (gameMode === 'action') {
        if (currentIndex < chapterOrder.length - 1) {
            const nextChapter = chapterOrder[currentIndex + 1];
            const isUnlocked = gameState.chapterProgress[nextChapter].unlocked;
            
            if (isUnlocked) {
                const nextChapterName = nextChapter.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
                return `<p>🎉 Neste kapittel "${nextChapterName}" er nå tilgjengelig!</p>`;
            } else {
                return `<p>💡 Oppnå 70% nøyaktighet i Aksjon-modus for å låse opp neste kapittel.</p>`;
            }
        } else {
            return `<p>🏆 Gratulerer! Du har fullført alle kapitler!</p>`;
        }
    } else {
        // In Øvelse mode, show a different message
        return `<p>💡 Bytte til Aksjon-modus for å låse opp nye kapitler.</p>`;
    }
}

// Chapter selector functions
function updateChapterSelector() {
    console.log('🔄 updateChapterSelector() called');
    
    const chapterSelect = document.getElementById('chapter-select');
    if (!chapterSelect) {
        console.error('❌ Chapter select element not found');
        return;
    }
    
    const chapterOrder = ['capital_one', 'capital_two', 'capital_three'];
    const chapterNames = {
        'capital_one': 'Kapitel 1 - Grunnleggende',
        'capital_two': 'Kapitel 2 - Middels',
        'capital_three': 'Kapitel 3 - Avansert'
    };
    
    console.log('📊 Current chapter progress:', gameState.chapterProgress);
    
    // Clear existing options
    chapterSelect.innerHTML = '';
    
    // Add options based on unlock status
    chapterOrder.forEach(chapterId => {
        const option = document.createElement('option');
        option.value = chapterId;
        
        const isUnlocked = gameState.chapterProgress[chapterId].unlocked;
        const isCompleted = gameState.chapterProgress[chapterId].completed;
        const bestScore = gameState.chapterProgress[chapterId].bestScore;
        
        console.log(`📝 Chapter ${chapterId}:`, {
            isUnlocked,
            isCompleted,
            bestScore
        });
        
        let displayName = chapterNames[chapterId];
        
        if (isCompleted) {
            displayName += ` ✅ (${bestScore}%)`;
        } else if (isUnlocked) {
            displayName += ` 🔓 (Tilgjengelig)`;
        } else {
            displayName += ` 🔒 (Låst)`;
        }
        
        option.textContent = displayName;
        option.disabled = !isUnlocked;
        
        chapterSelect.appendChild(option);
    });
    
    console.log('✅ Chapter selector updated');
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('settings-modal');
    if (event.target === modal) {
        closeSettings();
    }
}

// PWA Service Worker Registration
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('sw.js').catch(() => {
        console.log('Service worker registration failed');
    });
}
