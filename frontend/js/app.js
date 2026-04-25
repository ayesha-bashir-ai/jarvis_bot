class JARVISApp {
    constructor() {
        this.apiEndpoint = localStorage.getItem('apiEndpoint') || "";

        this.sessionId = localStorage.getItem('sessionId') ||
            'session_' + Date.now();

        this.messageCount = parseInt(localStorage.getItem('messageCount') || '0');

        // MODULES
        this.chat = new ChatModule();
        this.ui = new UIModule();
        this.voice = new VoiceModule();

        this.startTime = Date.now();
    }

    async init() {
        this.chat.init();
        this.bindEvents();
        this.ui.updateSessionInfo();
        this.startUptimeTimer();
        console.log("JARVIS Ready");
    }

    bindEvents() {
        document.getElementById('sendBtn')?.addEventListener('click', () => this.sendMessage());

        document.getElementById('messageInput')?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });

        document.getElementById('clearChat')?.addEventListener('click', () => {
            this.chat.clearChat();
        });

        document.getElementById('themeToggle')?.addEventListener('click', () => {
            this.ui.toggleTheme();
        });

        document.getElementById('micBtn')?.addEventListener('click', () => {
            this.voice.startListening();
        });
    }

    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        if (!message) return;

        this.chat.addMessage(message, "user");
        input.value = "";

        this.chat.showTypingIndicator();

        try {
            const res = await fetch(`${this.apiEndpoint}/api/v1/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message,
                    session_id: this.sessionId
                })
            });

            const data = await res.json();

            this.chat.hideTypingIndicator();
            this.chat.addMessage(data.message, "assistant");

            if (this.voice.isVoiceEnabled) {
                this.voice.speakText(data.message);
            }

            this.messageCount++;
            localStorage.setItem("messageCount", this.messageCount);

        } catch (err) {
            this.chat.hideTypingIndicator();
            this.chat.addMessage("Server error ❌", "assistant");
        }
    }

    startUptimeTimer() {
        setInterval(() => {
            const uptime = Math.floor((Date.now() - this.startTime) / 1000);
            document.getElementById("uptime").textContent = uptime + "s";
        }, 1000);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    window.jarvis = new JARVISApp();
    window.jarvis.init();
});