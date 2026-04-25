class ChatModule {
    init() {
        this.container = document.getElementById('chatMessages');
        this.welcomeScreen = document.getElementById('welcomeScreen');
        if (this.welcomeScreen) {
            this.welcomeHTML = this.welcomeScreen.outerHTML;
        }
    }

    hideWelcome() {
        const welcome = document.getElementById('welcomeScreen');
        if (welcome) welcome.style.display = 'none';
    }

    showWelcome() {
        let welcome = document.getElementById('welcomeScreen');
        if (!welcome && this.welcomeHTML) {
            this.container.insertAdjacentHTML('afterbegin', this.welcomeHTML);
            welcome = document.getElementById('welcomeScreen');
            if (window.jarvis) window.jarvis.bindSuggestionCards();
        }
        if (welcome) welcome.style.display = '';
    }

    addMessage(text, sender) {
        this.hideWelcome();

        const div = document.createElement("div");
        div.className = `message ${sender}`;

        div.innerHTML = `
            <div class="message-avatar">${sender === "user" ? "👤" : "🤖"}</div>
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

    clearChat() {
        this.container.querySelectorAll('.message').forEach((el) => el.remove());
        this.showWelcome();
    }

    scroll() {
        this.container.scrollTop = this.container.scrollHeight;
    }
}
