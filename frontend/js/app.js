class JARVISApp {
    constructor() {
        const storedEndpoint = localStorage.getItem('apiEndpoint') || "";
        if (storedEndpoint.includes('railway.app') || storedEndpoint.includes('jarvisbot-production')) {
            localStorage.removeItem('apiEndpoint');
            this.apiEndpoint = "";
        } else {
            this.apiEndpoint = storedEndpoint;
        }

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
        this.checkConnection();
        setInterval(() => this.checkConnection(), 15000);
        console.log("JARVIS Ready");
    }

    async checkConnection() {
        const el = document.getElementById('connectionStatus');
        if (!el) return;
        const label = el.querySelector('span:last-child');
        const dot = el.querySelector('.status-dot');
        try {
            const res = await fetch(`${this.apiEndpoint}/api/health`, { cache: 'no-store' });
            if (!res.ok) throw new Error('bad status');
            const data = await res.json();
            if (label) label.textContent = data.ai_enabled ? 'Online' : 'Online (offline AI)';
            if (dot) dot.style.background = '#22c55e';
        } catch (err) {
            if (label) label.textContent = 'Offline';
            if (dot) dot.style.background = '#ef4444';
        }
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

        document.getElementById('voiceCommandBtn')?.addEventListener('click', () => {
            this.voice.startListening();
        });

        document.getElementById('voiceToggle')?.addEventListener('click', (e) => {
            this.voice.toggleVoice();
            const btn = e.currentTarget;
            const label = btn.querySelector('span');
            if (label) label.textContent = this.voice.isVoiceEnabled ? 'Voice On' : 'Voice Off';
            btn.classList.toggle('active', this.voice.isVoiceEnabled);
        });

        document.querySelectorAll('.suggestion-card').forEach((card) => {
            card.addEventListener('click', () => {
                const msg = card.getAttribute('data-msg');
                if (!msg) return;
                const input = document.getElementById('messageInput');
                if (input) input.value = msg;
                this.sendMessage();
            });
        });

        document.querySelectorAll('.theme-option').forEach((opt) => {
            opt.addEventListener('click', () => {
                const theme = opt.getAttribute('data-theme');
                if (theme) this.ui.applyTheme(theme);
            });
        });

        document.getElementById('mobileMenuBtn')?.addEventListener('click', () => {
            document.querySelector('.sidebar')?.classList.toggle('open');
        });

        document.getElementById('emojiBtn')?.addEventListener('click', () => {
            const input = document.getElementById('messageInput');
            if (input) {
                input.value += ' 🙂';
                input.focus();
            }
        });

        document.getElementById('attachBtn')?.addEventListener('click', () => {
            this.chat.addMessage('Attachments are not supported yet.', 'assistant');
        });

        document.getElementById('settingsBtn')?.addEventListener('click', () => {
            const modal = document.getElementById('settingsModal');
            if (modal) modal.classList.toggle('open');
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