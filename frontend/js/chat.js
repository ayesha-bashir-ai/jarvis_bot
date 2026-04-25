class ChatModule {
    init() {
        this.container = document.getElementById('chatMessages');
    }

    addMessage(text, sender) {
        const div = document.createElement("div");
        div.className = `message ${sender}`;

        div.innerHTML = `
            <div class="message-avatar">${sender === "user" ? "👤" : "🤖"}</div>
            <div class="message-content">${text}</div>
        `;

        this.container.appendChild(div);
        this.scroll();
    }

    showTypingIndicator() {
        this.hideTypingIndicator();

        const div = document.createElement("div");
        div.id = "typing";
        div.className = "message assistant";
        div.innerHTML = "🤖 typing...";
        this.container.appendChild(div);
    }

    hideTypingIndicator() {
        document.getElementById("typing")?.remove();
    }

    clearChat() {
        this.container.innerHTML = "";
    }

    scroll() {
        this.container.scrollTop = this.container.scrollHeight;
    }
}