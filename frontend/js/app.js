// Endpoints we will try (production-safe order)
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
                if (candidate === (this.apiEndpoint || "")) continue;

                const result = await this._probeEndpoint(candidate);
                if (result) {
                    this.apiEndpoint = candidate;
                    data = result;
                    console.log("API switched to:", candidate);
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

        document.getElementById('voiceCancelBtn')
            ?.addEventListener('click', () => this.voice.stopListening());

        document.getElementById('settingsBtn')
            ?.addEventListener('click', () => this.openSettings());

        document.getElementById('saveSettingsBtn')
            ?.addEventListener('click', () => this.saveSettings());

        // ✅ FIXED: safe suggestion binding
        this.bindSuggestionCards();
    }

    // ✅ FIXED + IMPROVED (no rebind issues)
    bindSuggestionCards() {
        document.addEventListener('click', (e) => {
            const card = e.target.closest('.suggestion-card');
            if (!card) return;

            const value =
                card.getAttribute('data-value') ||
                card.textContent?.trim();

            const input = document.getElementById('messageInput');

            if (input && value) {
                input.value = value;
                input.focus();
            }

            // optional auto-send:
            // this.sendMessage();
        });
    }

    getBaseURL() {
        return this.apiEndpoint?.trim()
            ? this.apiEndpoint
            : 'https://jarvisbot-production-5eb2.up.railway.app';
    }

    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();

        if (!message) return;

        this.chat.addMessage(message, "user");
        input.value = "";

        this.chat.showTypingIndicator();

        try {
            const BASE_URL = this.getBaseURL();

            const res = await fetch(`${BASE_URL}/api/v1/chat`, {
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
                `Server error ❌ Could not reach backend.`,
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
    }
}

document.addEventListener("DOMContentLoaded", () => {
    window.jarvis = new JARVISApp();
    window.jarvis.init();
});
