/**
 * ============================================================
 *  AI Event Planner — Voice Assistant Module
 *  Provides speech-to-text input and text-to-speech output
 *  using the Web Speech API.
 * ============================================================
 */

class VoiceAssistant {
    /* -------------------------------------------------------
     * Constructor
     * @param {object} options
     *   onResult(transcript)  — called when speech is recognised
     *   onError(error)        — called on recognition error
     *   onStart()             — called when listening begins
     *   onEnd()               — called when listening ends
     *   lang        {string}  — BCP-47 language tag (default 'en-US')
     *   continuous  {boolean} — keep mic open (default false)
     * ------------------------------------------------------ */
    constructor(options = {}) {
        // Callbacks
        this._onResult = options.onResult || (() => {});
        this._onError  = options.onError  || (() => {});
        this._onStart  = options.onStart  || (() => {});
        this._onEnd    = options.onEnd    || (() => {});

        // Settings
        this._lang       = options.lang       || 'en-US';
        this._continuous  = options.continuous  || false;

        // Internal state
        this._listening = false;
        this._speaking  = false;
        this._recognition = null;
        this._synth       = window.speechSynthesis || null;

        // Browser support check
        const SpeechRecognition =
            window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            console.warn('[VoiceAssistant] SpeechRecognition not supported in this browser.');
            this._supported = false;
            return;
        }

        this._supported = true;

        // Create recognition instance
        this._recognition                = new SpeechRecognition();
        this._recognition.lang           = this._lang;
        this._recognition.continuous     = this._continuous;
        this._recognition.interimResults = false;
        this._recognition.maxAlternatives = 1;

        // --- Recognition Event Handlers ---

        this._recognition.onstart = () => {
            this._listening = true;
            this._onStart();
        };

        this._recognition.onresult = (event) => {
            const last       = event.results[event.results.length - 1];
            const transcript = last[0].transcript.trim();
            if (transcript) {
                this._onResult(transcript);
            }
        };

        this._recognition.onerror = (event) => {
            // 'no-speech' and 'aborted' are non-critical
            if (event.error === 'no-speech' || event.error === 'aborted') {
                console.info(`[VoiceAssistant] Recognition info: ${event.error}`);
            } else {
                console.error(`[VoiceAssistant] Recognition error: ${event.error}`);
                this._onError(event.error);
            }
        };

        this._recognition.onend = () => {
            this._listening = false;
            this._onEnd();
        };
    }

    /* -------------------------------------------------------
     * Public API
     * ------------------------------------------------------ */

    /** Start listening for speech input. */
    startListening() {
        if (!this._supported) {
            this._showUnsupportedAlert();
            return;
        }
        if (this._listening) return; // already active

        // Cancel any ongoing speech so mic doesn't pick it up
        this.stopSpeaking();

        try {
            this._recognition.start();
        } catch (err) {
            // Can throw if called twice before onend fires
            console.warn('[VoiceAssistant] Recognition start failed:', err);
        }
    }

    /** Stop listening. */
    stopListening() {
        if (!this._supported || !this._listening) return;
        try {
            this._recognition.stop();
        } catch {
            // Swallow if already stopped
        }
    }

    /**
     * Speak the given text aloud using SpeechSynthesis.
     * @param {string} text — text to speak
     */
    speak(text) {
        if (!this._synth) {
            console.warn('[VoiceAssistant] SpeechSynthesis not supported.');
            return;
        }

        // Cancel any in-progress utterance
        this.stopSpeaking();

        const utterance  = new SpeechSynthesisUtterance(text);
        utterance.lang   = this._lang;
        utterance.rate   = 1;
        utterance.pitch  = 1;
        utterance.volume = 1;

        // Try to pick a natural-sounding voice
        const voices = this._synth.getVoices();
        const preferred = voices.find(
            (v) => v.lang.startsWith(this._lang.split('-')[0]) && v.localService
        );
        if (preferred) utterance.voice = preferred;

        utterance.onstart = () => {
            this._speaking = true;
        };
        utterance.onend = () => {
            this._speaking = false;
        };
        utterance.onerror = () => {
            this._speaking = false;
        };

        this._synth.speak(utterance);
    }

    /** Stop any in-progress speech output. */
    stopSpeaking() {
        if (this._synth && this._synth.speaking) {
            this._synth.cancel();
            this._speaking = false;
        }
    }

    /** @returns {boolean} Whether the mic is currently active. */
    isListening() {
        return this._listening;
    }

    /** @returns {boolean} Whether speech output is playing. */
    isSpeaking() {
        return this._speaking;
    }

    /** @returns {boolean} Whether the browser supports speech APIs. */
    isSupported() {
        return this._supported;
    }

    /* -------------------------------------------------------
     * Private helpers
     * ------------------------------------------------------ */

    /** Display a user-friendly alert when APIs are unavailable. */
    _showUnsupportedAlert() {
        if (typeof showToast === 'function') {
            showToast(
                'Voice input is not supported in this browser. Please try Chrome or Edge.',
                'warning',
                5000,
            );
        } else {
            alert('Voice input is not supported in this browser. Please try Chrome or Edge.');
        }
    }
}

/* ===========================================================
 * Pulse animation CSS — injected once
 * ========================================================= */
(function injectVoiceStyles() {
    if (document.getElementById('voice-assistant-style')) return;
    const style = document.createElement('style');
    style.id = 'voice-assistant-style';
    style.textContent = `
        /* Mic button states */
        .voice-mic-btn {
            position: relative;
            transition: all 0.3s ease;
        }
        .voice-mic-btn.listening {
            color: #ef4444 !important;
            animation: micPulse 1.2s ease-in-out infinite;
        }
        .voice-mic-btn.listening::after {
            content: '';
            position: absolute;
            inset: -4px;
            border-radius: 50%;
            border: 2px solid #ef4444;
            animation: micRing 1.2s ease-in-out infinite;
            pointer-events: none;
        }
        .voice-mic-btn.speaking {
            color: #6c63ff !important;
        }

        /* Speaker button on bot messages */
        .voice-speak-btn {
            transition: color 0.3s ease;
        }
        .voice-speak-btn.speaking {
            color: #6c63ff !important;
            animation: speakerPulse 0.8s ease-in-out infinite alternate;
        }

        @keyframes micPulse {
            0%, 100% { transform: scale(1);   }
            50%      { transform: scale(1.1); }
        }
        @keyframes micRing {
            0%   { opacity: 1; transform: scale(1);   }
            100% { opacity: 0; transform: scale(1.5); }
        }
        @keyframes speakerPulse {
            from { opacity: 1;   }
            to   { opacity: 0.5; }
        }
    `;
    document.head.appendChild(style);
})();

/* ===========================================================
 * Global Initialization
 * Wire up #voiceMicBtn and .voice-speak-btn elements.
 * ========================================================= */
document.addEventListener('DOMContentLoaded', () => {
    const micBtn = document.getElementById('voiceMicBtn');
    if (!micBtn) return; // Voice UI not present on this page

    const assistant = new VoiceAssistant({
        lang      : 'en-US',
        continuous: false,

        /* --- Callback: recognition started --- */
        onStart() {
            micBtn.classList.add('listening');
            micBtn.setAttribute('aria-label', 'Listening… click to stop');
            const icon = micBtn.querySelector('i');
            if (icon) icon.className = 'bi bi-mic-fill';
        },

        /* --- Callback: recognition ended --- */
        onEnd() {
            micBtn.classList.remove('listening');
            micBtn.setAttribute('aria-label', 'Click to speak');
            const icon = micBtn.querySelector('i');
            if (icon) icon.className = 'bi bi-mic';
        },

        /* --- Callback: transcript received --- */
        async onResult(transcript) {
            // Populate chatbot input if it exists
            const chatInput = document.getElementById('chatInput');
            if (chatInput) {
                chatInput.value = transcript;
            }

            // Send to chatbot API and speak the response
            try {
                const data = await apiRequest('/api/chatbot', 'POST', {
                    message: transcript,
                });
                if (data && data.reply) {
                    assistant.speak(data.reply);

                    // Append to chat UI if present
                    appendBotMessage(data.reply);
                }
            } catch (err) {
                console.error('[VoiceAssistant] Chatbot request failed:', err);
            }
        },

        /* --- Callback: error --- */
        onError(error) {
            if (typeof showToast === 'function') {
                showToast(`Voice error: ${error}`, 'error');
            }
        },
    });

    // Expose globally for other scripts
    window.voiceAssistant = assistant;

    /* --- Mic button click handler --- */
    micBtn.addEventListener('click', () => {
        if (assistant.isListening()) {
            assistant.stopListening();
        } else {
            assistant.startListening();
        }
    });

    /* --- Speaker buttons on bot messages --- */
    document.addEventListener('click', (e) => {
        const speakBtn = e.target.closest('.voice-speak-btn');
        if (!speakBtn) return;

        // If already speaking this message, stop
        if (speakBtn.classList.contains('speaking')) {
            assistant.stopSpeaking();
            speakBtn.classList.remove('speaking');
            return;
        }

        // Stop any other speaking button
        document.querySelectorAll('.voice-speak-btn.speaking').forEach((btn) => {
            btn.classList.remove('speaking');
        });

        const text = speakBtn.dataset.text ||
                     speakBtn.closest('.chat-message')?.querySelector('.message-text')?.textContent;

        if (text) {
            speakBtn.classList.add('speaking');
            assistant.speak(text);

            // Remove class when speech ends
            const checkInterval = setInterval(() => {
                if (!assistant.isSpeaking()) {
                    speakBtn.classList.remove('speaking');
                    clearInterval(checkInterval);
                }
            }, 300);
        }
    });
});

/* ===========================================================
 * Helper: Append a bot message to the chat container
 * (Safe no-op if the chat UI is not on the current page.)
 * ========================================================= */
function appendBotMessage(text) {
    const chatContainer = document.getElementById('chatMessages');
    if (!chatContainer) return;

    const wrapper = document.createElement('div');
    wrapper.className = 'chat-message bot-message d-flex align-items-start gap-2 mb-3';
    wrapper.innerHTML = `
        <div class="avatar-sm rounded-circle d-flex align-items-center justify-content-center"
             style="background:linear-gradient(135deg,#6c63ff,#3b82f6);min-width:32px;
                    height:32px">
            <i class="bi bi-robot text-white" style="font-size:0.85rem"></i>
        </div>
        <div>
            <div class="message-text bg-white p-3 rounded-3 shadow-sm"
                 style="border-radius:12px !important;max-width:420px">
                ${escapeHtml(text)}
            </div>
            <button class="btn btn-link btn-sm voice-speak-btn p-0 mt-1 text-secondary"
                    data-text="${escapeAttr(text)}" title="Read aloud">
                <i class="bi bi-volume-up"></i>
            </button>
        </div>`;

    chatContainer.appendChild(wrapper);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

/** Escape HTML entities for safe DOM insertion. */
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/** Escape a string for use inside an HTML attribute. */
function escapeAttr(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}
