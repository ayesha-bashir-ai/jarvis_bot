// ===============================
// ENDPOINTS
// ===============================
const FALLBACK_ENDPOINTS = [
    'https://jarvisbot-production-5eb2.up.railway.app',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
];

function defaultStartingEndpoint() {
    try {
        if (window.location.protocol === 'file:') {
            return 'http://localhost:8000';
        }
    } catch (_) {}
    return '';
}

// ===============================
// MAIN APP
// ===============================
class JARVISApp {
    constructor() {
        const storedEndpoint = localStorage.getItem('apiEndpoint');

        this.userConfiguredEndpoint = !!(storedEndpoint && storedEndpoint.trim());

        this.apiEndpoint = this.userConfiguredEndpoint
            ? storedEndpoint.trim()
            : defaultStartingEndpoint();

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

        this._sending = false;
        this._suggestionsBound = false;
    }

    // ===============================
    // INIT
    // ===============================
    async init() {
        this.chat.init();
        this.bindEvents();
        this.ui.updateSessionInfo();

        const msgEl = document.getElementById("msgCount");
        if (msgEl) msgEl.textContent = this.messageCount;

        this.startUptimeTimer();
        this.checkConnection();

        setInterval(() => this.checkConnection(), 15000);

        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape") this.closeSettings();
        });

        console.log("JARVIS Ready");
    }

    // ===============================
    // API CHECK
    // ===============================
    async _probeEndpoint(base) {
        try {
            const res = await fetch(`${base}/api/health`, { cache: 'no-store' });
            if (!res.ok) return null;
            return await res.json();
        } catch (_) {
            return null;
        }
    }

    async checkConnection() {
        const el = document.getElementById('connectionStatus');
        if (!el) return;

        const label = el.querySelector('span:last-child');
        const dot = el.querySelector('.status-dot');

        let data = await this._probeEndpoint(this.apiEndpoint || "");

        if (!data && !this.userConfiguredEndpoint) {
            for (const candidate of FALLBACK_ENDPOINTS) {
                const result = await this._probeEndpoint(candidate);
                if (result) {
                    this.apiEndpoint = candidate;
                    data = result;
                    break;
                }
            }
        }

        if (data) {
            if (label)
                label.textContent = data.ai_enabled
                    ? 'Online'
                    : 'Online (offline AI)';
            if (dot) dot.style.background = '#22c55e';
        } else {
            if (label) label.textContent = 'Offline';
            if (dot) dot.style.background = '#ef4444';
        }
    }

    getBaseURL() {
        return this.apiEndpoint?.trim()
            ? this.apiEndpoint
            : 'https://jarvisbot-production-5eb2.up.railway.app';
    }

    // ===============================
    // EVENTS
    // ===============================
    bindEvents() {
        document.getElementById('sendBtn')
            ?.addEventListener('click', () => this.sendMessage());

        document.getElementById('messageInput')
            ?.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

        document.getElementById('clearChat')
            ?.addEventListener('click', () => this.chat.clearChat());

        document.getElementById('themeToggle')
            ?.addEventListener('click', () => this.ui.toggleTheme());

        document.getElementById('micBtn')
            ?.addEventListener('click', () => this.voice.startListening());

        document.getElementById('voiceCommandBtn')
            ?.addEventListener('click', () => this.voice.startListening());

        document.getElementById('voiceCancelBtn')
            ?.addEventListener('click', () => this.voice.stopListening());

        document.getElementById('settingsBtn')
            ?.addEventListener('click', () => this.openSettings());

        document.getElementById('closeModalBtn')
            ?.addEventListener('click', () => this.closeSettings());

        document.getElementById('cancelSettingsBtn')
            ?.addEventListener('click', () => this.closeSettings());

        document.getElementById('saveSettingsBtn')
            ?.addEventListener('click', () => this.saveSettings());

        // voice toggle
        document.getElementById('voiceToggle')
            ?.addEventListener('click', () => this.toggleVoiceUI());

        this.bindSuggestionCards();
    }

    // ===============================
    // SUGGESTIONS
    // ===============================
    bindSuggestionCards() {
        if (this._suggestionsBound) return;
        this._suggestionsBound = true;

        document.addEventListener('click', (e) => {
            const card = e.target.closest('.suggestion-card');
            if (!card) return;

            const value =
                card.getAttribute('data-msg') ||
                card.querySelector("span")?.textContent?.trim();

            const input = document.getElementById('messageInput');

            if (input && value) {
                input.value = value;
                input.focus();
            }
        });
    }

    // ===============================
    // SETTINGS
    // ===============================
    openSettings() {
        document.getElementById("settingsModal")?.classList.add("active");
    }

    closeSettings() {
        document.getElementById("settingsModal")?.classList.remove("active");
    }

    saveSettings() {
        const apiInput = document.getElementById('apiEndpoint');

        if (apiInput && apiInput.value.trim()) {
            this.apiEndpoint = apiInput.value.trim();
            this.userConfiguredEndpoint = true;
            localStorage.setItem('apiEndpoint', this.apiEndpoint);
        } else {
            this.apiEndpoint = "";
            this.userConfiguredEndpoint = false;
            localStorage.removeItem('apiEndpoint');
        }

        this.checkConnection();
        this.closeSettings();
    }

    // ===============================
    // VOICE UI TOGGLE
    // ===============================
    toggleVoiceUI() {
        if (!this.voice) return;

        this.voice.toggleVoice();

        const btn = document.getElementById('voiceToggle');
        const icon = btn?.querySelector('i');

        if (this.voice.isVoiceEnabled) {
            icon?.classList.replace("fa-volume-mute", "fa-volume-up");
            this.ui.showToast("Voice Enabled");
        } else {
            icon?.classList.replace("fa-volume-up", "fa-volume-mute");
            this.ui.showToast("Voice Disabled");
        }
    }

    // ===============================
    // CHAT SEND
    // ===============================
    async sendMessage() {
        if (this._sending) return;
        this._sending = true;

        const input = document.getElementById('messageInput');
        const message = input.value.trim();

        if (!message) {
            this._sending = false;
            return;
        }

        this.chat.setResponseStartTime?.();

        this.chat.addMessage(message, "user");
        input.value = "";

        this.chat.showTypingIndicator();

        try {
            const res = await fetch(`${this.getBaseURL()}/api/v1/chat`, {
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

            this.chat.setResponseEndTime?.();

            if (this.voice.isVoiceEnabled) {
                this.voice.speakText(data.message);
            }

            this.messageCount++;
            localStorage.setItem("messageCount", this.messageCount);

            document.getElementById("msgCount")
                ?.textContent = this.messageCount;

            this.ui?.showToast("Message sent");

        } catch (err) {
            this.chat.hideTypingIndicator();
            this.chat.addMessage("Server error ❌", "assistant");
            console.error(err);
        }

        this._sending = false;
    }

    // ===============================
    // UPTIME
    // ===============================
    startUptimeTimer() {
        setInterval(() => {
            const uptime = Math.floor((Date.now() - this.startTime) / 1000);
            const el = document.getElementById("uptime");
            if (el) el.textContent = uptime + "s";
        }, 1000);
    }
}

// ===============================
// BOOT
// ===============================
document.addEventListener("DOMContentLoaded", () => {
    window.jarvis = new JARVISApp();
    window.jarvis.init();
});
