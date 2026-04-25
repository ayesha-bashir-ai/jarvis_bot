class VoiceModule {
    constructor() {
        this.synth = window.speechSynthesis;

        // ✅ FIX 1: restore saved state properly
        this.isVoiceEnabled =
            localStorage.getItem("voiceEnabled") === "true";
    }

    startListening() {
        console.log("Voice not fully implemented yet");
    }

    speakText(text) {
        if (!this.isVoiceEnabled) return;
        if (!this.synth) return;

        // stop previous speech (prevents overlap)
        this.synth.cancel();

        const utter = new SpeechSynthesisUtterance(text);

        // optional safe defaults
        utter.lang = "en-US";
        utter.rate = 1;
        utter.pitch = 1;

        this.synth.speak(utter);
    }

    toggleVoice() {
        this.isVoiceEnabled = !this.isVoiceEnabled;

        // ✅ FIX 2: store as string safely
        localStorage.setItem(
            "voiceEnabled",
            this.isVoiceEnabled.toString()
        );
    }
}
