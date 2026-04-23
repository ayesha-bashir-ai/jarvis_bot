// JARVIS Main Application
class JARVISApp {
    constructor() {
        this.apiEndpoint = localStorage.getItem('apiEndpoint') ||
            "https://jarvisbot-production-5eb2.up.railway.app";

        this.sessionId = localStorage.getItem('sessionId') ||
            'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

        this.messageCount = parseInt(localStorage.getItem('messageCount') || '0');
        this.voiceEnabled = localStorage.getItem('voiceEnabled') === 'true';
        this.startTime = Date.now();

        this.init();
    }

    async init() {
        this.bindEvents();
        this.updateUI();
        await this.checkConnection();
        this.initVoice();
        this.startUptimeTimer();
        console.log('JARVIS Assistant Ready!');
    }

    bindEvents() {
        const sendBtn = document.getElementById('sendBtn');
        const messageInput = document.getElementById('messageInput');

        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }

        if (messageInput) {
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        const clearBtn = document.getElementById('clearChat');
        if (clearBtn) clearBtn.addEventListener('click', () => this.clearChat());

        const voiceToggle = document.getElementById('voiceToggle');
        if (voiceToggle) voiceToggle.addEventListener('click', () => this.toggleVoice());

        const micBtn = document.getElementById('micBtn');
        if (micBtn) micBtn.addEventListener('click', () => this.startVoiceInput());

        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) themeToggle.addEventListener('click', () => this.toggleTheme());

        const settingsBtn = document.getElementById('settingsBtn');
        if (settingsBtn) settingsBtn.addEventListener('click', () => this.openSettings());
    }

    updateUI() {
        const msgCount = document.getElementById('msgCount');
        if (msgCount) msgCount.textContent = this.messageCount;

        const sessionId = document.getElementById('sessionId');
        if (sessionId) sessionId.textContent = this.sessionId.slice(0, 8) + "...";

        const voiceStatus = document.getElementById('voiceStatus');
        if (voiceStatus) voiceStatus.textContent = this.voiceEnabled ? "Active" : "Ready";
    }

    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        if (!message) return;

        this.addMessage(message, 'user');
        input.value = '';
        this.showTyping();

        try {
            const response = await fetch(`${this.apiEndpoint}/api/v1/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message,
                    session_id: this.sessionId
                })
            });

            const data = await response.json();
            this.hideTyping();

            this.addMessage(data.message, 'assistant');

            // ✅ FIX: OPEN YOUTUBE / URL FROM BACKEND
            if (data.action === "open_url" && data.url) {
                window.open(data.url, "_blank");
            }

        } catch (error) {
            console.error(error);
            this.hideTyping();
            this.addMessage("Backend error. Please check server.", "assistant");
        }
    }

    addMessage(text, sender) {
        const chat = document.getElementById('chatMessages');

        const div = document.createElement('div');
        div.className = `message ${sender}`;

        const avatar = sender === 'user' ? '👤' : '🤖';

        div.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">${text}</div>
        `;

        chat.appendChild(div);

        const container = document.getElementById('chatContainer');
        if (container) container.scrollTop = container.scrollHeight;
    }

    showTyping() {
        const chat = document.getElementById('chatMessages');

        const div = document.createElement('div');
        div.id = "typing";
        div.className = "message assistant";
        div.innerHTML = "🤖 typing...";

        chat.appendChild(div);
    }

    hideTyping() {
        const t = document.getElementById('typing');
        if (t) t.remove();
    }

    async checkConnection() {
        try {
            const res = await fetch(`${this.apiEndpoint}/health`);
            console.log("Backend connected:", await res.json());
        } catch {
            console.log("Backend offline");
        }
    }

    toggleVoice() {
        this.voiceEnabled = !this.voiceEnabled;
        localStorage.setItem('voiceEnabled', this.voiceEnabled);
    }

    initVoice() {
        if (!('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) return;

        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SR();

        this.recognition.onresult = (e) => {
            const text = e.results[0][0].transcript;
            document.getElementById('messageInput').value = text;
            this.sendMessage();
        };
    }

    startVoiceInput() {
        if (this.recognition) this.recognition.start();
    }

    toggleTheme() {
        document.body.classList.toggle("light-theme");
    }

    openSettings() {
        alert("Settings opened");
    }

    startUptimeTimer() {
        setInterval(() => {
            const uptime = Math.floor((Date.now() - this.startTime) / 1000);
            const el = document.getElementById('uptime');
            if (el) el.textContent = uptime + "s";
        }, 1000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.jarvis = new JARVISApp();
});