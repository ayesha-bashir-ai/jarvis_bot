// JARVIS Main Application (PRODUCTION FIXED VERSION)
class JARVISApp {
    constructor() {
        this.apiEndpoint = localStorage.getItem('apiEndpoint') ||
            "https://jarvisbot-production-5eb2.up.railway.app";

        this.sessionId = localStorage.getItem('sessionId') ||
            'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

        this.messageCount = parseInt(localStorage.getItem('messageCount') || '0');
        this.voiceEnabled = localStorage.getItem('voiceEnabled') === 'true';
        this.startTime = Date.now();
    }

    async init() {
        this.bindEvents();
        this.updateUI();
        await this.checkConnection();
        this.startUptimeTimer();
        console.log("JARVIS Ready");
    }

    // ---------------- EVENTS (FIXED SAFE BINDING) ----------------
    bindEvents() {
        console.log("Binding events...");

        const sendBtn = document.getElementById('sendBtn');
        const input = document.getElementById('messageInput');
        const clearBtn = document.getElementById('clearChat');

        console.log("sendBtn:", sendBtn);
        console.log("messageInput:", input);

        if (sendBtn) {
            sendBtn.onclick = () => this.sendMessage();
        }

        if (input) {
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') this.sendMessage();
            });
        }

        if (clearBtn) {
            clearBtn.onclick = () => this.clearChat();
        }
    }

    // ---------------- UI ----------------
    updateUI() {
        const set = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };

        set('msgCount', this.messageCount);

        const sessionEl = document.getElementById('sessionId');
        if (sessionEl) sessionEl.textContent = this.sessionId.slice(0, 8) + "...";

        const api = document.getElementById('apiEndpoint');
        if (api) api.value = this.apiEndpoint;
    }

    // ---------------- CHAT ----------------
    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input?.value.trim();

        if (!message) return;

        this.addMessage(message, "user");
        input.value = "";
        this.showTyping();

        try {
            const res = await fetch(`${this.apiEndpoint}/api/v1/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message,
                    session_id: this.sessionId,
                    user_id: "user1"
                })
            });

            if (!res.ok) throw new Error("Server error");

            const data = await res.json();
            this.hideTyping();

            this.addMessage(data.message, "assistant");

            if (data.action === "open_url" && data.url) {
                window.open(data.url, "_blank");
            }

            this.messageCount++;
            localStorage.setItem("messageCount", this.messageCount);

        } catch (err) {
            console.error(err);
            this.hideTyping();
            this.addMessage("Backend error. Check server.", "assistant");
        }
    }

    // ---------------- MESSAGES ----------------
    addMessage(text, sender) {
        const chat = document.getElementById("chatMessages");
        if (!chat) return;

        const div = document.createElement("div");
        div.className = `message ${sender}`;

        const avatar = sender === "user" ? "👤" : "🤖";

        div.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">${text}</div>
        `;

        chat.appendChild(div);
        chat.scrollTop = chat.scrollHeight;
    }

    showTyping() {
        const chat = document.getElementById("chatMessages");
        if (!chat) return;

        const div = document.createElement("div");
        div.id = "typing";
        div.className = "message assistant";
        div.innerHTML = "🤖 typing...";
        chat.appendChild(div);
    }

    hideTyping() {
        const t = document.getElementById("typing");
        if (t) t.remove();
    }

    // ---------------- CONNECTION ----------------
    async checkConnection() {
        try {
            await fetch(`${this.apiEndpoint}/health`);
            console.log("Backend Connected");
        } catch {
            console.log("Backend Offline");
        }
    }

    // ---------------- CLEAR CHAT ----------------
    clearChat() {
        const chat = document.getElementById("chatMessages");
        if (chat) chat.innerHTML = "";

        this.messageCount = 0;
        localStorage.setItem("messageCount", "0");
        this.updateUI();
    }

    // ---------------- UPTIME ----------------
    startUptimeTimer() {
        setInterval(() => {
            const uptime = Math.floor((Date.now() - this.startTime) / 1000);
            const el = document.getElementById("uptime");
            if (el) el.textContent = uptime + "s";
        }, 1000);
    }
}

// ---------------- SAFE INIT (IMPORTANT FIX) ----------------
document.addEventListener("DOMContentLoaded", () => {
    window.jarvis = new JARVISApp();
    window.jarvis.init();
});