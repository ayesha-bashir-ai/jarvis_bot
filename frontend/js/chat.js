class ChatModule {
    init() {
        this.container = document.getElementById('chatMessages');

        const welcome = document.getElementById('welcomeScreen');

        if (welcome) {
            this.welcomeHTML = welcome.outerHTML;
        }
    }

    hideWelcome() {
        const welcome = document.getElementById('welcomeScreen');
        if (welcome) welcome.style.display = 'none';
    }

    // ✅ FIXED: no duplication + safe restore
    showWelcome() {
        let welcome = document.getElementById('welcomeScreen');

        if (welcome) {
            welcome.style.display = '';
            return;
        }

        if (!this.container || !this.welcomeHTML) return;

        this.container.innerHTML = '';

        this.container.insertAdjacentHTML('afterbegin', this.welcomeHTML);

        if (window.jarvis) {
            window.jarvis.bindSuggestionCards();
        }
    }

    addMessage(text, sender) {
        this.hideWelcome();

        const div = document.createElement("div");
        div.className = `message ${sender}`;

        div.innerHTML = `
            <div class="message-avatar">
                ${sender === "user" ? "👤" : "🤖"}
            </div>
            <div class="message-content"></div>
        `;

        div.querySelector('.message-content').textContent = text;

        this.container.appendChild(div);

        this.scroll();
    }

    showTypingIndicator() {
        this.hideTypingIndicator();
        this.hideWelcome();

        const div = document.createElement("div");
        div.id = "typing";
        div.className = "message assistant";
        div.innerHTML = "🤖 typing...";

        this.container.appendChild(div);

        this.scroll();
    }

    hideTypingIndicator() {
        document.getElementById("typing")?.remove();
    }

    // ✅ FIXED: full clean reset (no leftover DOM bugs)
    clearChat() {
        if (!this.container) return;

        this.container.innerHTML = "";

        this.hideTypingIndicator();

        this.showWelcome();
    }

    scroll() {
        if (!this.container) return;

        this.container.scrollTop = this.container.scrollHeight;
    }
}
