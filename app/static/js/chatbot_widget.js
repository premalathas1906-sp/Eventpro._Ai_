/**
 * ============================================================
 *  AI Event Planner — Global Chatbot Widget & Voice Assistant
 * ============================================================
 */
document.addEventListener('DOMContentLoaded', () => {
    const widgetBtn = document.getElementById('chatWidgetBtn');
    const widgetWindow = document.getElementById('chatWidgetWindow');
    const closeBtn = document.getElementById('chatWidgetCloseBtn');
    const clearBtn = document.getElementById('chatWidgetClearBtn');
    const volumeBtn = document.getElementById('chatWidgetVolumeBtn');
    const messageBody = document.getElementById('chatWidgetBody');
    const chatForm = document.getElementById('chatWidgetForm');
    const chatInput = document.getElementById('chatWidgetInput');
    const micBtn = document.getElementById('chatWidgetMicBtn');
    const typingIndicator = document.getElementById('chatWidgetTyping');
    const suggestionContainer = document.getElementById('chatWidgetSuggestions');
    const badge = document.getElementById('chatWidgetBadge');

    if (!widgetBtn || !widgetWindow) return;

    // Volume state (default unmuted, read from localstorage)
    let isMuted = localStorage.getItem('chatWidgetMuted') === 'true';
    updateVolumeIcon();

    // Active speech recognition instance
    let recognition = null;
    let isListening = false;

    // Speech synthesis instance
    const synth = window.speechSynthesis;
    let currentUtterance = null;

    // Initialize Speech Recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = 'en-US';
        recognition.interimResults = false;

        recognition.onstart = () => {
            isListening = true;
            micBtn.classList.add('listening');
            chatInput.placeholder = 'Listening...';
        };

        recognition.onend = () => {
            isListening = false;
            micBtn.classList.remove('listening');
            chatInput.placeholder = 'Ask AI Assistant...';
        };

        recognition.onerror = (e) => {
            console.error('[ChatWidget Voice] Recognition error:', e.error);
            showToast(`Voice error: ${e.error}`, 'error');
            isListening = false;
            micBtn.classList.remove('listening');
            chatInput.placeholder = 'Ask AI Assistant...';
        };

        recognition.onresult = (e) => {
            const transcript = e.results[0][0].transcript;
            if (transcript && transcript.trim()) {
                chatInput.value = transcript;
                sendMessage(transcript);
            }
        };
    } else {
        micBtn.style.display = 'none'; // Hide mic if not supported
    }

    // Toggle widget window
    widgetBtn.addEventListener('click', () => {
        widgetWindow.classList.toggle('collapsed');
        if (!widgetWindow.classList.contains('collapsed')) {
            // Clear badge
            badge.style.display = 'none';
            // Focus input
            chatInput.focus();
            scrollToBottom();
        }
    });

    // Close button
    closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        widgetWindow.classList.add('collapsed');
        stopSpeaking();
    });

    // Mute/Unmute toggle
    volumeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        isMuted = !isMuted;
        localStorage.setItem('chatWidgetMuted', isMuted);
        updateVolumeIcon();
        if (isMuted) {
            stopSpeaking();
        }
        showToast(isMuted ? 'Voice output muted' : 'Voice output unmuted', 'info');
    });

    // Clear history
    clearBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (confirm('Clear chat history?')) {
            stopSpeaking();
            // Keep only welcoming message
            const welcome = messageBody.querySelector('.chat-message.bot:first-child');
            messageBody.innerHTML = '';
            if (welcome) messageBody.appendChild(welcome);
            messageBody.appendChild(suggestionContainer);
            messageBody.appendChild(typingIndicator);
            scrollToBottom();
            showToast('Chat history cleared', 'success');
        }
    });

    // Suggestion chips handler
    suggestionContainer.addEventListener('click', (e) => {
        const chip = e.target.closest('.chat-suggestion-chip');
        if (chip) {
            const query = chip.dataset.query;
            sendMessage(query);
        }
    });

    // Form submission
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = chatInput.value.trim();
        if (text) {
            sendMessage(text);
        }
    });

    // Mic button toggle listener
    micBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (!recognition) return;

        if (isListening) {
            recognition.stop();
        } else {
            stopSpeaking();
            recognition.start();
        }
    });

    /* --- Core logic functions --- */

    async function sendMessage(text) {
        if (!text.trim()) return;

        // Add user bubble
        appendMessage(text, 'user');
        chatInput.value = '';

        // Show typing indicator
        showTyping();

        try {
            const response = await fetch('/api/chatbot', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ message: text })
            });

            const data = await response.json();
            hideTyping();

            const botReply = data.reply || data.response || "I couldn't get a response. Please try again.";
            appendMessage(botReply, 'bot');

            // Speak response
            speak(botReply);

        } catch (err) {
            console.error('[ChatWidget] Error posting message:', err);
            hideTyping();
            appendMessage("Offline. I couldn't connect to the server.", 'bot');
        }
    }

    function appendMessage(text, sender) {
        // Create wrapper
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-message ${sender}`;

        // Create bubble content
        const bubble = document.createElement('div');
        bubble.className = 'chat-message-content';
        bubble.innerHTML = text; // allow HTML structure like list cards
        msgDiv.appendChild(bubble);

        // Create timestamp
        const timeDiv = document.createElement('div');
        timeDiv.className = 'chat-message-time';
        timeDiv.textContent = getTimestamp();
        msgDiv.appendChild(timeDiv);

        // Insert before typing indicator
        typingIndicator.before(msgDiv);
        scrollToBottom();
    }

    function showTyping() {
        typingIndicator.style.display = 'block';
        scrollToBottom();
    }

    function hideTyping() {
        typingIndicator.style.display = 'none';
    }

    function scrollToBottom() {
        messageBody.scrollTop = messageBody.scrollHeight;
    }

    function getTimestamp() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function updateVolumeIcon() {
        const icon = volumeBtn.querySelector('i');
        if (icon) {
            if (isMuted) {
                icon.className = 'bi bi-volume-mute-fill text-white';
            } else {
                icon.className = 'bi bi-volume-up-fill text-white';
            }
        }
    }

    /* --- Speech Synthesis (Text-to-Speech) --- */
    function speak(text) {
        if (isMuted || !synth) return;

        stopSpeaking();

        // Strip HTML tags from speech synthesis text
        const plainText = text.replace(/<[^>]*>/g, '');

        currentUtterance = new SpeechSynthesisUtterance(plainText);
        currentUtterance.rate = 1.05; // Slightly faster for natural chat responsiveness

        // Select a premium English voice if available
        const voices = synth.getVoices();
        const preferredVoice = voices.find(v => v.lang.includes('en') && (v.name.includes('Google') || v.name.includes('Natural')));
        if (preferredVoice) {
            currentUtterance.voice = preferredVoice;
        }

        synth.speak(currentUtterance);
    }

    function stopSpeaking() {
        if (synth && synth.speaking) {
            synth.cancel();
        }
    }
});
