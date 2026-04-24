class VoiceModule {
    constructor() {
        this.isVoiceEnabled = false;
        this.synth = window.speechSynthesis;
    }

    startListening() {
        console.log("Voice not fully implemented yet");
    }

    speakText(text) {
        if (!this.isVoiceEnabled) return;

        const utter = new SpeechSynthesisUtterance(text);
        this.synth.speak(utter);
    }

    toggleVoice() {
        this.isVoiceEnabled = !this.isVoiceEnabled;
        localStorage.setItem("voiceEnabled", this.isVoiceEnabled);
    }
}