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

        if (sendBtn) sendBtn.addEventListener('click', () => this.sendMessage());

        if (messageInput) {
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
    }

    updateUI() {
        document.getElementById('msgCount').textContent = this.messageCount;
        document.getElementById('sessionId').textContent = this.sessionId.substr(0, 8) + '...';
        document.getElementById('sessionIdInput').value = this.sessionId;
        document.getElementById('apiEndpoint').value = this.apiEndpoint;
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
                    session_id: this.sessionId,
                    user_id: 'user1'
                })
            });

            const data = await response.json();
            this.hideTyping();

            this.addMessage(data.message, 'assistant');

            // ✅ OPEN URL IN BROWSER (IMPORTANT FIX)
            if (data.action === 'open_url' && data.url) {
                window.open(data.url, '_blank');
            }

        } catch (error) {
            console.error(error);
            this.hideTyping();
            this.addMessage("Backend error. Check server.", 'assistant');
        }
    }

    addMessage(text, sender) {
        const chatMessages = document.getElementById('chatMessages');

        const div = document.createElement('div');
        div.className = `message ${sender}`;

        const avatar = sender === 'user' ? '👤' : '🤖';

        div.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">${text}</div>
        `;

        chatMessages.appendChild(div);
    }

    showTyping() {
        const chatMessages = document.getElementById('chatMessages');

        const div = document.createElement('div');
        div.id = "typing";
        div.className = "message assistant";
        div.innerHTML = "🤖 typing...";

        chatMessages.appendChild(div);
    }

    hideTyping() {
        const t = document.getElementById('typing');
        if (t) t.remove();
    }

    async checkConnection() {
        try {
            const res = await fetch(`${this.apiEndpoint}/health`);
            console.log("Backend OK");
        } catch {
            console.log("Backend offline");
        }
    }

    startUptimeTimer() {}
}

document.addEventListener('DOMContentLoaded', () => {
    window.jarvis = new JARVISApp();
});