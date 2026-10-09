/**
 * MedMate Senior Voice Interface Controller
 */

const state = {
    isListening: false,
    currentMedicationHistoryId: null,
    recognition: null,
    synthesis: window.speechSynthesis,
    isSpeaking: false,
    userName: 'Alex'
};

const elements = {
    greetingText: document.getElementById('greeting-text'),
    greetingEmoji: document.getElementById('greeting-emoji'),
    navUserLabel: document.getElementById('nav-user-label'),
    footerUsername: document.getElementById('footer-username'),
    aiStateLabel: document.getElementById('ai-state-label'),
    aiStateSub: document.getElementById('ai-state-sub'),
    aiStatusCard: document.getElementById('ai-status-card'),
    lastCommandHint: document.getElementById('last-command-hint'),
    micOrbWrapper: document.getElementById('mic-orb-wrapper'),
    studioMicBtn: document.getElementById('studio-mic-btn'),
    tapSpeakCaption: document.getElementById('tap-speak-caption'),
    waveformVisualizer: document.getElementById('waveform-visualizer'),
    transcriptArea: document.getElementById('transcript-area'),
    queryTextInput: document.getElementById('query-text-input'),
    sendPillBtn: document.getElementById('send-pill-btn'),
    toast: document.getElementById('toast-msg')
};

function initApp() {
    loadUserProfile();
    updateGreeting();
    setupSpeechRecognition();
    setupEventListeners();
    checkDueMedications();

    setInterval(checkDueMedications, 60000);
    setInterval(updateGreeting, 1800000);
}

function loadUserProfile() {
    const savedProfile = localStorage.getItem('medmate-user-profile');
    if (savedProfile) {
        try {
            const data = JSON.parse(savedProfile);
            if (data.name) {
                state.userName = data.name;
            }
        } catch (e) {
            console.error('Error loading profile', e);
        }
    }
    if (elements.navUserLabel) elements.navUserLabel.textContent = `Profile (${state.userName})`;
    if (elements.footerUsername) elements.footerUsername.textContent = `${state.userName}...`;
}

function updateGreeting() {
    const hour = new Date().getHours();
    let timeGreeting = 'Good Morning';
    let emoji = '☀️';

    if (hour < 12) {
        timeGreeting = 'Good Morning';
        emoji = '☀️';
    } else if (hour < 17) {
        timeGreeting = 'Good Afternoon';
        emoji = '🌤️';
    } else {
        timeGreeting = 'Good Evening';
        emoji = '🌙';
    }

    if (elements.greetingText) elements.greetingText.textContent = `${timeGreeting}, ${state.userName}`;
    if (elements.greetingEmoji) elements.greetingEmoji.textContent = emoji;
}

function setupSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        console.warn('Speech recognition not supported in this browser.');
        setAIStatus('READY', 'Voice recognition not available. Please type query below.');
        return;
    }

    state.recognition = new SpeechRecognition();
    state.recognition.lang = 'en-IN';
    state.recognition.continuous = false;
    state.recognition.interimResults = false;
    state.recognition.maxAlternatives = 1;

    state.recognition.onstart = () => {
        state.isListening = true;
        if (elements.micOrbWrapper) elements.micOrbWrapper.classList.add('listening');
        if (elements.waveformVisualizer) elements.waveformVisualizer.classList.add('active');
        if (elements.studioMicBtn) elements.studioMicBtn.setAttribute('aria-expanded', 'true');
        setAIStatus('LISTENING...', 'Capturing voice input... Speak now.');
        if (elements.tapSpeakCaption) elements.tapSpeakCaption.textContent = 'LISTENING...';
    };

    state.recognition.onend = () => {
        state.isListening = false;
        if (elements.micOrbWrapper) elements.micOrbWrapper.classList.remove('listening');
        if (!state.isSpeaking) {
            if (elements.waveformVisualizer) elements.waveformVisualizer.classList.remove('active');
            setAIStatus('READY', 'Connected | Awaiting input. Tap microphone or speak naturally');
            if (elements.tapSpeakCaption) elements.tapSpeakCaption.textContent = 'TAP TO SPEAK';
        }
    };

    state.recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        if (text && text.trim()) {
            handleUserInput(text.trim());
        }
    };

    state.recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        state.isListening = false;
        if (elements.micOrbWrapper) elements.micOrbWrapper.classList.remove('listening');
        if (elements.waveformVisualizer) elements.waveformVisualizer.classList.remove('active');

        if (event.error === 'no-speech') {
            setAIStatus('READY', 'No speech detected. Tap microphone to try again.');
        } else if (event.error === 'not-allowed' || event.error === 'permission-denied') {
            setAIStatus('BLOCKED', 'Microphone blocked. Allow microphone access in browser.');
        } else {
            setAIStatus('READY', 'Tap microphone to speak or type query below.');
        }
        if (elements.tapSpeakCaption) elements.tapSpeakCaption.textContent = 'TAP TO SPEAK';
    };
}

function setupEventListeners() {
    if (elements.studioMicBtn) {
        elements.studioMicBtn.addEventListener('click', toggleListening);
        elements.studioMicBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            toggleListening();
        });
    }

    if (elements.sendPillBtn) {
        elements.sendPillBtn.addEventListener('click', sendTextMessage);
    }

    if (elements.queryTextInput) {
        elements.queryTextInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendTextMessage();
            }
        });
    }
}

function toggleListening() {
    if (!state.recognition) {
        showToast('Microphone not supported. Please type your query.');
        return;
    }

    if (state.isListening) {
        state.recognition.stop();
    } else {
        if (state.isSpeaking) {
            state.synthesis.cancel();
            state.isSpeaking = false;
        }
        try {
            state.recognition.start();
        } catch (e) {
            console.error('Could not start recognition:', e);
            setAIStatus('ERROR', 'Error starting microphone. Tap again.');
        }
    }

    if (navigator.vibrate) {
        navigator.vibrate(35);
    }
}

window.triggerPreset = function(text) {
    if (elements.queryTextInput) {
        elements.queryTextInput.value = text;
    }
    handleUserInput(text);
};

async function checkDueMedications() {
    try {
        const response = await fetch('/api/medications/due');
        if (!response.ok) return;

        const medications = await response.json();
        if (Array.isArray(medications) && medications.length > 0) {
            const med = medications[0];

            try {
                const triggerRes = await fetch('/api/trigger-reminder', { method: 'POST' });
                const triggerData = await triggerRes.json();
                if (triggerData.history_id) {
                    state.currentMedicationHistoryId = triggerData.history_id;
                }
            } catch (err) {
                console.error('Error triggering reminder:', err);
            }

            const instruction = med.instruction || '';
            const dosage = med.dosage || '';
            const message = `It is time to take ${med.name}. ${instruction} ${dosage}`.trim();

            setAIStatus('REMINDER DUE ⚠️', `Time for ${med.name} - ${instruction} (${dosage})`);
            if (elements.aiStatusCard) elements.aiStatusCard.classList.add('active-reminder');

            speakText(message);

            if (navigator.vibrate) {
                navigator.vibrate([200, 100, 200, 100, 200]);
            }
        }
    } catch (error) {
        console.error('Error checking medications:', error);
    }
}

async function handleUserInput(text) {
    addToTranscript('user', text);
    if (elements.lastCommandHint) {
        elements.lastCommandHint.textContent = `...processing user query... (command: "${text}")...`;
    }
    setAIStatus('PROCESSING...', 'Analyzing natural language intent...');

    try {
        const response = await fetch('/api/interact', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                medication_history_id: state.currentMedicationHistoryId
            })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        if (data.response) {
            addToTranscript('sys', data.response);
            speakText(data.response);

            if (data.intent === 'MEDICINE_TAKEN') {
                setAIStatus('CONFIRMED ✓', 'Medication recorded as taken. Great job!');
                if (elements.aiStatusCard) elements.aiStatusCard.classList.remove('active-reminder');
                state.currentMedicationHistoryId = null;

                if (navigator.vibrate) navigator.vibrate([100, 50, 100]);

            } else if (data.intent === 'REMIND_LATER') {
                const minutes = data.delay_minutes || 10;
                setAIStatus('SNOOZED ⏰', `Reminder postponed for ${minutes} minutes.`);
                if (elements.aiStatusCard) elements.aiStatusCard.classList.remove('active-reminder');

                setTimeout(() => {
                    checkDueMedications();
                }, minutes * 60 * 1000);

            } else if (data.intent === 'NOT_TAKEN') {
                setAIStatus('NOTED ⚠️', 'Please take your medication as soon as possible.');
            } else {
                setAIStatus('READY', 'Connected | Awaiting input. Tap microphone or speak naturally');
            }
        }
    } catch (error) {
        console.error('Interaction error:', error);
        setAIStatus('CONNECTION ERROR', 'Could not reach server. Please try again.');
    }
}

function speakText(text) {
    if (!state.synthesis) return;

    state.synthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1.0;

    const voices = state.synthesis.getVoices();
    if (voices.length > 0) {
        const hasTamil = /[\u0B80-\u0BFF]/.test(text);
        let selectedVoice = null;

        if (hasTamil) {
            selectedVoice = voices.find(v => v.lang.includes('ta'));
        }
        if (!selectedVoice) {
            selectedVoice = voices.find(v => v.lang.includes('en-IN') || v.lang.includes('en_IN'));
        }
        if (!selectedVoice) {
            selectedVoice = voices.find(v => v.lang.startsWith('en'));
        }
        if (selectedVoice) {
            utterance.voice = selectedVoice;
        }
    }

    utterance.onstart = () => {
        state.isSpeaking = true;
        if (elements.waveformVisualizer) elements.waveformVisualizer.classList.add('active');
        setAIStatus('SPEAKING 🔊', text.substring(0, 48) + '...');
    };

    utterance.onend = () => {
        state.isSpeaking = false;
        if (elements.waveformVisualizer) elements.waveformVisualizer.classList.remove('active');
        if (!state.isListening) {
            setAIStatus('READY', 'Connected | Awaiting input. Tap microphone or speak naturally');
        }
    };

    utterance.onerror = () => {
        state.isSpeaking = false;
        if (elements.waveformVisualizer) elements.waveformVisualizer.classList.remove('active');
    };

    state.synthesis.speak(utterance);
}

function setAIStatus(statusText, subText) {
    if (elements.aiStateLabel) elements.aiStateLabel.textContent = statusText;
    if (elements.aiStateSub) elements.aiStateSub.textContent = subText || '';
}

function addToTranscript(sender, message) {
    if (!elements.transcriptArea) return;
    const div = document.createElement('div');
    div.className = `msg msg-${sender}`;
    div.textContent = message;
    elements.transcriptArea.appendChild(div);
    elements.transcriptArea.scrollTop = elements.transcriptArea.scrollHeight;
}

function sendTextMessage() {
    if (!elements.queryTextInput) return;
    const text = elements.queryTextInput.value.trim();
    if (text) {
        handleUserInput(text);
        elements.queryTextInput.value = '';
        elements.queryTextInput.blur();
    }
}

function showToast(message) {
    if (!elements.toast) return;
    elements.toast.textContent = message;
    elements.toast.classList.add('show');
    setTimeout(() => {
        elements.toast.classList.remove('show');
    }, 3000);
}

if (window.speechSynthesis) {
    window.speechSynthesis.onvoiceschanged = () => {};
    window.speechSynthesis.getVoices();
}

document.addEventListener('DOMContentLoaded', initApp);
