const FALLBACK_ENDPOINTS = [
    '',
    'https://jarvisbot-production-5eb2.up.railway.app',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
];

function defaultStartingEndpoint() {
    try {
        if (window.location.protocol === 'file:') return 'http://localhost:8000';
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

        this.sessionId = localStorage.getItem('sessionId') || 'session_' + Date.now();
        localStorage.setItem('sessionId', this.sessionId);
        this.messageCount = parseInt(localStorage.getItem('messageCount') || '0');

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

    // Try the currently chosen endpoint first, then walk the fallbacks.
    // Auto-switches `this.apiEndpoint` to the first one that responds.
    async _findWorkingEndpoint() {
        const seen = new Set();
        const ordered = [];
        const add = (e) => {
            const v = e || "";
            if (seen.has(v)) return;
            seen.add(v);
            ordered.push(v);
        };
        add(this.apiEndpoint || "");
        for (const c of FALLBACK_ENDPOINTS) add(c);

        for (const candidate of ordered) {
            const result = await this._probeEndpoint(candidate);
            if (result) {
                if (candidate !== (this.apiEndpoint || "")) {
                    console.log("API switched to:", candidate || "(same origin)");
                    this.apiEndpoint = candidate;
                }
                return result;
            }
        }
        return null;
    }

    async checkConnection() {
        const el = document.getElementById('connectionStatus');
        if (!el) return;
        const label = el.querySelector('span:last-child');
        const dot = el.querySelector('.status-dot');

        const data = await this._findWorkingEndpoint();

        if (data) {
            if (label) label.textContent = data.ai_enabled ? 'Online' : 'Online (offline AI)';
            if (dot) dot.style.background = '#22c55e';
        } else {
            if (label) label.textContent = 'Offline';
            if (dot) dot.style.background = '#ef4444';
        }
    }

    bindEvents() {
        document.getElementById('sendBtn')?.addEventListener('click', () => this.sendMessage());
        document.getElementById('messageInput')?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        document.getElementById('clearChat')?.addEventListener('click', () => this.chat.clearChat());
        document.getElementById('themeToggle')?.addEventListener('click', () => this.ui.toggleTheme());
        document.getElementById('micBtn')?.addEventListener('click', () => this.voice.startListening());
        document.getElementById('voiceCommandBtn')?.addEventListener('click', () => this.voice.startListening());
        document.getElementById('voiceCancelBtn')?.addEventListener('click', () => this.voice.stopListening());

        document.getElementById('voiceToggle')?.addEventListener('click', (e) => {
            this.voice.toggleVoice();
            const btn = e.currentTarget;
            const label = btn.querySelector('span');
            if (label) label.textContent = this.voice.isVoiceEnabled ? 'Voice On' : 'Voice Off';
            btn.classList.toggle('active', this.voice.isVoiceEnabled);
        });

        this.bindSuggestionCards();

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
            if (input) { input.value += ' 🙂'; input.focus(); }
        });

        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/*,text/*,.txt,.md,.csv,.json,.yaml,.yml,.xml,.html,.css,.js,.ts,.py,.log,.ini,.toml';
        fileInput.style.display = 'none';
        document.body.appendChild(fileInput);
        this._fileInput = fileInput;

        document.getElementById('attachBtn')?.addEventListener('click', () => {
            if (this._uploading) return;
            fileInput.value = '';
            fileInput.click();
        });

        fileInput.addEventListener('change', () => {
            const file = fileInput.files && fileInput.files[0];
            if (file) this.uploadFile(file);
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
        const closeSettings = () => settingsModal?.classList.remove('active');

        document.getElementById('settingsBtn')?.addEventListener('click', openSettings);
        document.getElementById('closeModalBtn')?.addEventListener('click', closeSettings);
        document.getElementById('cancelSettingsBtn')?.addEventListener('click', closeSettings);
        settingsModal?.addEventListener('click', (e) => {
            if (e.target === settingsModal) closeSettings();
        });

        document.getElementById('saveSettingsBtn')?.addEventListener('click', () => {
            const apiInput = document.getElementById('apiEndpoint');
            if (apiInput && apiInput.value.trim() !== '') {
                this.apiEndpoint = apiInput.value.trim();
                this.userConfiguredEndpoint = true;
                localStorage.setItem('apiEndpoint', this.apiEndpoint);
            } else {
                this.apiEndpoint = "";
                this.userConfiguredEndpoint = false;
                localStorage.removeItem('apiEndpoint');
            }
            closeSettings();
            this.checkConnection();
        });

        document.getElementById('newSessionBtn')?.addEventListener('click', () => {
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

    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        if (!message) return;

        this.chat.addMessage(message, "user");
        input.value = "";
        this.chat.showTypingIndicator();

        try {
            // Make sure we're pointed at a backend that's actually up.
            await this._findWorkingEndpoint();
            const BASE_URL = this.apiEndpoint || "";

            const res = await fetch(`${BASE_URL}/api/v1/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message, session_id: this.sessionId })
            });
            if (!res.ok) throw new Error("API error");
            const data = await res.json();

            this.chat.hideTypingIndicator();
            this.chat.addMessage(data.message, "assistant");

            if (this.voice.isVoiceEnabled) this.voice.speakText(data.message);

            if (data.action === "open_url" && data.url) {
                const opened = window.open(data.url, "_blank", "noopener,noreferrer");
                if (!opened) {
                    this.chat.addMessage(
                        `Your browser blocked the popup. Open it manually: ${data.url}`,
                        "assistant"
                    );
                }
            }

            this.messageCount++;
            localStorage.setItem("messageCount", this.messageCount);
        } catch (err) {
            this.chat.hideTypingIndicator();
            this.chat.addMessage(
                `Server error ❌ Could not reach backend at "${this.apiEndpoint || window.location.origin}". Check the backend is running, or update the API endpoint in Settings.`,
                "assistant"
            );
            console.error(err);
        }
    }

    async uploadFile(file) {
        if (!file) return;
        const sizeKb = (file.size / 1024).toFixed(1);
        this.chat.addMessage(`📎 ${file.name} (${sizeKb} KB)`, "user");
        this.chat.showTypingIndicator();
        this._uploading = true;

        try {
            await this._findWorkingEndpoint();
            const BASE_URL = this.apiEndpoint || "";

            const form = new FormData();
            form.append("file", file);
            form.append("session_id", this.sessionId);

            const res = await fetch(`${BASE_URL}/api/v1/upload`, { method: "POST", body: form });
            const data = await res.json().catch(() => ({}));

            this.chat.hideTypingIndicator();
            const reply = data.message || (res.ok ? "File uploaded." : `Upload failed (status ${res.status}).`);
            this.chat.addMessage(reply, "assistant");

            if (this.voice.isVoiceEnabled && reply) this.voice.speakText(reply);

            this.messageCount++;
            localStorage.setItem("messageCount", this.messageCount);
        } catch (err) {
            this.chat.hideTypingIndicator();
            this.chat.addMessage("Upload error ❌ Could not reach the server.", "assistant");
            console.error(err);
        } finally {
            this._uploading = false;
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
