/**
 * JARVIS AI Assistant - Chat Module
 * Handles all chat-related functionality
 */

class ChatModule {
    constructor() {
        this.messageCount = 0;
        this.isTyping = false;
        this.messagesContainer = document.getElementById('chatMessages');
        this.typingIndicator = null;
    }
    
    addMessage(text, sender) {
        const welcomeScreen = document.getElementById('welcomeScreen');
        
        // Remove welcome screen if it exists and it's the first message
        if (welcomeScreen && this.messageCount === 0) {
            welcomeScreen.remove();
        }
        
        const messageDiv = this.createMessageElement(text, sender);
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageDiv;
    }
    
    createMessageElement(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatar = sender === 'user' ? '👤' : '🤖';
        const avatarClass = sender === 'user' ? 'user-avatar' : 'assistant-avatar';
        
        const formattedText = this.formatMessage(text);
        
        messageDiv.innerHTML = `
            <div class="message-avatar ${avatarClass}">${avatar}</div>
            <div class="message-content">
                ${formattedText}
                <div class="message-time">${this.getFormattedTime()}</div>
            </div>
        `;
        
        return messageDiv;
    }
    
    formatMessage(text) {
        // Convert URLs to clickable links
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        text = text.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer" class="message-link">$1</a>');
        
        // Convert code blocks
        text = text.replace(/`([^`]+)`/g, '<code class="message-code">$1</code>');
        
        // Convert bold text
        text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        
        // Convert italic text
        text = text.replace(/\*([^*]+)\*/g, '<em>$1</em>');
        
        // Convert line breaks
        text = text.replace(/\n/g, '<br>');
        
        // Convert emoji shortcodes (basic)
        const emojis = {
            ':smile:': '😊',
            ':laugh:': '😂',
            ':thinking:': '🤔',
            ':robot:': '🤖',
            ':rocket:': '🚀'
        };
        
        for (const [code, emoji] of Object.entries(emojis)) {
            text = text.replace(new RegExp(code, 'g'), emoji);
        }
        
        return text;
    }
    
    getFormattedTime() {
        const now = new Date();
        return now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    }
    
    showTypingIndicator() {
        if (this.isTyping) return;
        
        this.typingIndicator = document.createElement('div');
        this.typingIndicator.className = 'message assistant typing';
        this.typingIndicator.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        this.messagesContainer.appendChild(this.typingIndicator);
        this.scrollToBottom();
        this.isTyping = true;
    }
    
    hideTypingIndicator() {
        if (this.typingIndicator && this.typingIndicator.parentNode) {
            this.typingIndicator.remove();
        }
        this.isTyping = false;
    }
    
    clearChat() {
        // Clear messages container
        this.messagesContainer.innerHTML = `
            <div class="welcome-screen" id="welcomeScreen">
                <div class="welcome-animation">
                    <div class="hologram-circle"></div>
                    <div class="hologram-circle delay-1"></div>
                    <div class="hologram-circle delay-2"></div>
                    <div class="welcome-icon">
                        <i class="fas fa-robot"></i>
                    </div>
                </div>
                <h2>Conversation Cleared</h2>
                <p class="welcome-text">How can I assist you, Commander?</p>
                <div class="suggestions-grid">
                    <button class="suggestion-card" data-msg="What time is it?">
                        <i class="fas fa-clock"></i>
                        <span>What time is it?</span>
                    </button>
                    <button class="suggestion-card" data-msg="Tell me a joke">
                        <i class="fas fa-laugh"></i>
                        <span>Tell me a joke</span>
                    </button>
                    <button class="suggestion-card" data-msg="Calculate 100 / 4">
                        <i class="fas fa-calculator"></i>
                        <span>Calculate 100 / 4</span>
                    </button>
                    <button class="suggestion-card" data-msg="Open YouTube">
                        <i class="fab fa-youtube"></i>
                        <span>Open YouTube</span>
                    </button>
                </div>
            </div>
        `;
        
        // Re-bind suggestion events
        this.rebindSuggestions();
        
        this.messageCount = 0;
    }
    
    rebindSuggestions() {
        document.querySelectorAll('.suggestion-card').forEach(btn => {
            btn.addEventListener('click', () => {
                const msg = btn.getAttribute('data-msg');
                const input = document.getElementById('messageInput');
                if (input && msg) {
                    input.value = msg;
                    if (window.jarvis) {
                        window.jarvis.sendMessage();
                    }
                }
            });
        });
    }
    
    scrollToBottom() {
        const chatContainer = document.getElementById('chatContainer');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }
    
    incrementMessageCount() {
        this.messageCount++;
    }
    
    updateMessageCount(count) {
        this.messageCount = count;
    }
}