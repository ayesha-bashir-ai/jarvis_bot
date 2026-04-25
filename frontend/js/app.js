class JARVISApp {
    constructor() {
        const storedEndpoint = localStorage.getItem('apiEndpoint');

        // ✅ FIX 1: safe default backend (8000)
        this.apiEndpoint =
            storedEndpoint && storedEndpoint.trim() !== ""
                ? storedEndpoint.trim()
                : "http://localhost:8000";

        // ❌ removed broken railway auto-reset logic (it was causing empty API)

        this.sessionId =
            localStorage.getItem('sessionId') ||
            'session_' + Date.now();

        localStorage.setItem('sessionId', this.sessionId);

        this.messageCount =
            parseInt(localStorage.getItem('messageCount') || '0');

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
        console.log("API:", this.apiEndpoint);
    }

    // ✅ FIX 2: ALWAYS use backend URL (no relative path)
    async checkConnection() {
        const el = document.getElementById('connectionStatus');
        if (!el) return;

        const label = el.querySelector('span:last-child');
        const dot = el.querySelector('.status-dot');

        const base = this.apiEndpoint || "http://localhost:8000";

        try {
            const res = await fetch(`${base}/api/health`, {
                cache: 'no-store'
            });

            if (!res.ok) throw new Error('bad status');

            const data = await res.json();

            if (label)
                label.textContent = data.ai_enabled
                    ? 'Online'
                    : 'Online (offline AI)';

            if (dot) dot.style.background = '#22c55e';

        } catch (err) {
            if (label) label.textContent = 'Offline';
            if (dot) dot.style.background = '#ef4444';
        }
    }

    bindEvents() {
        document.getElementById('sendBtn')
            ?.addEventListener('click', () => this.sendMessage());

        document.getElementById('messageInput')
            ?.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') this.sendMessage();
            });

        document.getElementById('clearChat')
            ?.addEventListener('click', () => this.chat.clearChat());

        document.getElementById('themeToggle')
            ?.addEventListener('click', () => this.ui.toggleTheme());

        document.getElementById('micBtn')
            ?.addEventListener('click', () => this.voice.startListening());

        document.getElementById('voiceCommandBtn')
            ?.addEventListener('click', () => this.voice.startListening());

        document.getElementById('voiceToggle')
            ?.addEventListener('click', (e) => {
                this.voice.toggleVoice();

                const btn = e.currentTarget;
                const label = btn.querySelector('span');

                if (label)
                    label.textContent =
                        this.voice.isVoiceEnabled ? 'Voice On' : 'Voice Off';

                btn.classList.toggle('active', this.voice.isVoiceEnabled);
            });

        this.bindSuggestionCards();

        document.querySelectorAll('.theme-option').forEach((opt) => {
            opt.addEventListener('click', () => {
                const theme = opt.getAttribute('data-theme');
                if (theme) this.ui.applyTheme(theme);
            });
        });

        document.getElementById('mobileMenuBtn')
            ?.addEventListener('click', () => {
                document.querySelector('.sidebar')?.classList.toggle('open');
            });

        document.getElementById('emojiBtn')
            ?.addEventListener('click', () => {
                const input = document.getElementById('messageInput');
                if (input) {
                    input.value += ' 🙂';
                    input.focus();
                }
            });

        document.getElementById('attachBtn')
            ?.addEventListener('click', () => {
                this.chat.addMessage(
                    'Attachments are not supported yet.',
                    'assistant'
                );
            });

        const settingsModal = document.getElementById('settingsModal');

        const openSettings = () => {
            if (!settingsModal) return;

            const apiInput = document.getElementById('apiEndpoint');
            const sessionInput = document.getElementById('sessionIdInput');

            if (apiInput) apiInput.value = this.apiEndpoint;
            if (sessionInput) sessionInput.value = this.sessionId;

            settingsModal.classList.add('active');
        };

        const closeSettings = () => {
            settingsModal?.classList.remove('active');
        };

        document.getElementById('settingsBtn')
            ?.addEventListener('click', openSettings);

        document.getElementById('closeModalBtn')
            ?.addEventListener('click', closeSettings);

        document.getElementById('cancelSettingsBtn')
            ?.addEventListener('click', closeSettings);

        settingsModal?.addEventListener('click', (e) => {
            if (e.target === settingsModal) closeSettings();
        });

        document.getElementById('saveSettingsBtn')
            ?.addEventListener('click', () => {
                const apiInput = document.getElementById('apiEndpoint');

                if (apiInput && apiInput.value.trim() !== '') {
                    this.apiEndpoint = apiInput.value.trim();
                    localStorage.setItem('apiEndpoint', this.apiEndpoint);
                } else {
                    this.apiEndpoint = "http://localhost:8000";
                    localStorage.removeItem('apiEndpoint');
                }

                closeSettings();
                this.checkConnection();
            });

        document.getElementById('newSessionBtn')
            ?.addEventListener('click', () => {
                this.sessionId = 'session_' + Date.now();
                localStorage.setItem('sessionId', this.sessionId);

                const sessionInput = document.getElementById('sessionIdInput');
                if (sessionInput) sessionInput.value = this.sessionId;

                this.ui.updateSessionInfo();
            });
    }

    bindSuggestionCards() {
        document.querySelectorAll('.suggestion-card').forEach((card) => {
            if (card.dataset.bound === '1') return;
            card.dataset.bound = '1';

            card.addEventListener('click', () => {
                const msg = card.getAttribute('data-msg');
                if (!msg) return;

                const input = document.getElementById('messageInput');
                if (input) input.value = msg;

                this.sendMessage();
            });
        });
    }

    // ✅ FIX 3: safe API call always hits backend
    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();

        if (!message) return;

        this.chat.addMessage(message, "user");
        input.value = "";

        this.chat.showTypingIndicator();

        try {
            const base = this.apiEndpoint || "http://localhost:8000";

            const res = await fetch(`${base}/api/v1/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message,
                    session_id: this.sessionId
                })
            });

            if (!res.ok) throw new Error("API error");

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
            this.chat.addMessage(
                "Server error ❌ Check backend (port 8000)",
                "assistant"
            );
            console.error(err);
        }
    }

    startUptimeTimer() {
        setInterval(() => {
            const uptime = Math.floor((Date.now() - this.startTime) / 1000);
            const el = document.getElementById("uptime");
            if (el) el.textContent = uptime + "s";
        }, 1000);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    window.jarvis = new JARVISApp();
    window.jarvis.init();
});
