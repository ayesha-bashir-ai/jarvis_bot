class VoiceModule {
    constructor() {
        this.isVoiceEnabled = localStorage.getItem('voiceEnabled') === 'true';
        this.synth = window.speechSynthesis;
        this.lang = localStorage.getItem('voiceLang') || 'en-US';
        this.rate = parseFloat(localStorage.getItem('voiceRate') || '1');
        this.pitch = parseFloat(localStorage.getItem('voicePitch') || '1');

        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = null;
        this.isListening = false;

        if (SR) {
            this.recognition = new SR();
            this.recognition.lang = this.lang;
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.maxAlternatives = 1;

            this.recognition.onresult = (e) => {
                const transcript = e.results[0][0].transcript;
                const input = document.getElementById('messageInput');
                if (input) input.value = transcript;
                this.hideOverlay();
                if (window.jarvis) window.jarvis.sendMessage();
            };

            this.recognition.onerror = (e) => {
                console.error('Speech recognition error:', e.error);
                this.hideOverlay();
                if (window.jarvis && window.jarvis.chat) {
                    const msg = e.error === 'not-allowed'
                        ? 'Microphone permission denied. Please allow microphone access in your browser.'
                        : `Voice input error: ${e.error}`;
                    window.jarvis.chat.addMessage(msg, 'assistant');
                }
            };

            this.recognition.onend = () => {
                this.isListening = false;
                this.hideOverlay();
            };
        }
    }

    showOverlay() {
        const overlay = document.getElementById('voiceWaveOverlay');
        if (overlay) overlay.classList.add('active');
    }

    hideOverlay() {
        const overlay = document.getElementById('voiceWaveOverlay');
        if (overlay) overlay.classList.remove('active');
    }

    startListening() {
        if (!this.recognition) {
            if (window.jarvis && window.jarvis.chat) {
                window.jarvis.chat.addMessage(
                    'Voice input is not supported in this browser. Try Chrome or Edge.',
                    'assistant'
                );
            }
            return;
        }

        if (this.isListening) {
            this.stopListening();
            return;
        }

        try {
            this.recognition.lang = this.lang;
            this.recognition.start();
            this.isListening = true;
            this.showOverlay();
        } catch (err) {
            console.error('Could not start speech recognition:', err);
            this.hideOverlay();
        }
    }

    stopListening() {
        if (this.recognition && this.isListening) {
            try { this.recognition.stop(); } catch (_) {}
        }
        this.isListening = false;
        this.hideOverlay();
    }

    speakText(text) {
        if (!this.isVoiceEnabled || !this.synth) return;
        try { this.synth.cancel(); } catch (_) {}
        const utter = new SpeechSynthesisUtterance(text);
        utter.lang = this.lang;
        utter.rate = this.rate;
        utter.pitch = this.pitch;
        this.synth.speak(utter);
    }

    toggleVoice() {
        this.isVoiceEnabled = !this.isVoiceEnabled;
        localStorage.setItem('voiceEnabled', this.isVoiceEnabled);
        if (!this.isVoiceEnabled && this.synth) {
            try { this.synth.cancel(); } catch (_) {}
        }
    }

    setLanguage(lang) {
        if (!lang) return;
        this.lang = lang;
        localStorage.setItem('voiceLang', lang);
        if (this.recognition) this.recognition.lang = lang;
    }

    setRate(rate) {
        const r = parseFloat(rate);
        if (!isNaN(r)) {
            this.rate = r;
            localStorage.setItem('voiceRate', String(r));
        }
    }

    setPitch(pitch) {
        const p = parseFloat(pitch);
        if (!isNaN(p)) {
            this.pitch = p;
            localStorage.setItem('voicePitch', String(p));
        }
    }
}
