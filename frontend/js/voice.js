// Voice Module
class VoiceModule {
    constructor() {
        this.isVoiceEnabled = localStorage.getItem('voiceEnabled') === 'true';
        this.recognition = null;
        this.synth = window.speechSynthesis;
        this.isListening = false;
        this.speed = 1;
        this.pitch = 1;
        this.language = 'en-US';
        
        this.initSpeechRecognition();
    }
    
    initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = this.language;
            
            this.recognition.onstart = () => {
                this.isListening = true;
                console.log('Voice recognition started');
            };
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                if (this.onResultCallback) {
                    this.onResultCallback(transcript);
                }
            };
            
            this.recognition.onerror = (event) => {
                console.error('Recognition error:', event.error);
                this.isListening = false;
                if (this.onErrorCallback) {
                    this.onErrorCallback(event.error);
                }
            };
            
            this.recognition.onend = () => {
                this.isListening = false;
            };
            
            console.log('Speech recognition initialized');
        }
    }
    
    speakText(text) {
        if (!this.isVoiceEnabled) return;
        
        this.synth.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = this.speed;
        utterance.pitch = this.pitch;
        utterance.volume = 1;
        utterance.lang = this.language;
        
        this.synth.speak(utterance);
    }
    
    startListening() {
        if (!this.recognition) return false;
        if (this.isListening) this.stopListening();
        
        try {
            this.recognition.start();
            return true;
        } catch(e) {
            console.error('Failed to start:', e);
            return false;
        }
    }
    
    stopListening() {
        if (this.recognition && this.isListening) {
            try {
                this.recognition.stop();
            } catch(e) {}
            this.isListening = false;
        }
    }
    
    setCallbacks(onResult, onError) {
        this.onResultCallback = onResult;
        this.onErrorCallback = onError;
    }
    
    toggleVoice() {
        this.isVoiceEnabled = !this.isVoiceEnabled;
        localStorage.setItem('voiceEnabled', this.isVoiceEnabled);
        if (!this.isVoiceEnabled) {
            this.synth.cancel();
        }
        return this.isVoiceEnabled;
    }
    
    setSpeed(speed) {
        this.speed = speed;
        localStorage.setItem('voiceSpeed', speed);
    }
    
    setPitch(pitch) {
        this.pitch = pitch;
        localStorage.setItem('voicePitch', pitch);
    }
    
    setLanguage(lang) {
        this.language = lang;
        if (this.recognition) {
            this.recognition.lang = lang;
        }
        localStorage.setItem('voiceLang', lang);
    }
}

window.VoiceModule = VoiceModule;
