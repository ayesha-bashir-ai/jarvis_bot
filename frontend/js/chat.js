class ChatModule {
    init() {
        this.container = document.getElementById('chatMessages');

        const welcome = document.getElementById('welcomeScreen');
        if (welcome) {
            this.welcomeHTML = welcome.outerHTML;
        }

        this.lastResponseTime = 0;
    }

    hideWelcome() {
        document.getElementById('welcomeScreen')?.style.setProperty('display', 'none');
    }

    showWelcome() {
        if (!this.container || !this.welcomeHTML) return;

        const existing = document.getElementById('welcomeScreen');

        if (existing) {
            existing.style.display = '';
            return;
        }

        this.container.innerHTML = "";

        this.container.insertAdjacentHTML('afterbegin', this.welcomeHTML);

        window.jarvis?.bindSuggestionCards?.();
    }

    addMessage(text, sender) {
        this.hideWelcome();

        const div = document.createElement("div");
        div.className = `message ${sender}`;

        const avatar = sender === "user" ? "👤" : "🤖";

        div.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content"></div>
        `;

        div.querySelector('.message-content').textContent = text;

        this.container.appendChild(div);

        this.smoothScroll();
    }

    // ⚡ improved typing indicator
    showTypingIndicator() {
        this.hideTypingIndicator();
        this.hideWelcome();

        const div = document.createElement("div");
        div.id = "typingIndicator";
        div.className = "message assistant";

        div.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <span class="typing-dots">Typing...</span>
            </div>
        `;

        this.container.appendChild(div);

        this.smoothScroll();
    }

    hideTypingIndicator() {
        document.getElementById("typingIndicator")?.remove();
    }

    // 🧠 response time tracking support
    setResponseStartTime() {
        this.lastStart = performance.now();
    }

    setResponseEndTime() {
        if (!this.lastStart) return;

        const time = Math.round(performance.now() - this.lastStart);
        this.lastResponseTime = time;

        window.jarvis?.ui?.updateResponseTime(time);
    }

    clearChat() {
        if (!this.container) return;

        this.hideTypingIndicator();

        this.container.innerHTML = "";

        this.showWelcome();
    }

    // ⚡ smoother scroll (prevents jitter)
    smoothScroll() {
        if (!this.container) return;

        requestAnimationFrame(() => {
            this.container.scrollTo({
                top: this.container.scrollHeight,
                behavior: "smooth"
            });
        });
    }
}
