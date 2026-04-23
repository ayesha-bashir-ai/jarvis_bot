// JARVIS Main Application
class JARVISApp {
    constructor() {
        this.apiEndpoint = localStorage.getItem('apiEndpoint') || 
"https://jarvisbot-production-5eb2.up.railway.app";
        this.sessionId = localStorage.getItem('sessionId') || 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
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
        // Send message
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
        
        // Clear chat
        const clearBtn = document.getElementById('clearChat');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearChat());
        }
        
        // Voice toggle
        const voiceToggle = document.getElementById('voiceToggle');
        if (voiceToggle) {
            voiceToggle.addEventListener('click', () => this.toggleVoice());
            if (this.voiceEnabled) {
                voiceToggle.classList.add('active');
                voiceToggle.innerHTML = '<i class="fas fa-volume-up"></i><span>Voice On</span>';
            }
        }
        
        // Voice command button
        const voiceCommandBtn = document.getElementById('voiceCommandBtn');
        if (voiceCommandBtn) {
            voiceCommandBtn.addEventListener('click', () => this.startVoiceInput());
        }
        
        // Mic button
        const micBtn = document.getElementById('micBtn');
        if (micBtn) {
            micBtn.addEventListener('click', () => this.startVoiceInput());
        }
        
        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
        
        // Settings
        const settingsBtn = document.getElementById('settingsBtn');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => this.openSettings());
        }
        
        // Modal close buttons
        const closeModalBtn = document.getElementById('closeModalBtn');
        const cancelSettingsBtn = document.getElementById('cancelSettingsBtn');
        const saveSettingsBtn = document.getElementById('saveSettingsBtn');
        
        if (closeModalBtn) closeModalBtn.addEventListener('click', () => this.closeSettings());
        if (cancelSettingsBtn) cancelSettingsBtn.addEventListener('click', () => this.closeSettings());
        if (saveSettingsBtn) saveSettingsBtn.addEventListener('click', () => this.saveSettings());
        
        // New session
        const newSessionBtn = document.getElementById('newSessionBtn');
        if (newSessionBtn) {
            newSessionBtn.addEventListener('click', () => this.newSession());
        }
        
        // Voice settings sliders
        const voiceSpeed = document.getElementById('voiceSpeed');
        const voicePitch = document.getElementById('voicePitch');
        
        if (voiceSpeed) {
            voiceSpeed.addEventListener('input', (e) => {
                const speedValue = document.getElementById('speedValue');
                if (speedValue) speedValue.textContent = e.target.value + 'x';
                localStorage.setItem('voiceSpeed', e.target.value);
            });
        }
        
        if (voicePitch) {
            voicePitch.addEventListener('input', (e) => {
                const pitchValue = document.getElementById('pitchValue');
                if (pitchValue) pitchValue.textContent = e.target.value + 'x';
                localStorage.setItem('voicePitch', e.target.value);
            });
        }
        
        // Theme options
        document.querySelectorAll('.theme-option').forEach(option => {
            option.addEventListener('click', () => {
                const theme = option.getAttribute('data-theme');
                this.applyTheme(theme);
            });
        });
        
        // Suggestions
        document.querySelectorAll('.suggestion-card').forEach(btn => {
            btn.addEventListener('click', () => {
                const msg = btn.getAttribute('data-msg');
                const input = document.getElementById('messageInput');
                if (input && msg) {
                    input.value = msg;
                    this.sendMessage();
                }
            });
        });
        
        // Voice cancel
        const voiceCancelBtn = document.getElementById('voiceCancelBtn');
        if (voiceCancelBtn) {
            voiceCancelBtn.addEventListener('click', () => {
                if (this.recognition) {
                    this.recognition.stop();
                }
                this.hideVoiceWave();
            });
        }
        
        // Close modal on outside click
        window.addEventListener('click', (e) => {
            const modal = document.getElementById('settingsModal');
            if (e.target === modal) {
                this.closeSettings();
            }
        });
    }
    
    updateUI() {
        document.getElementById('msgCount').textContent = this.messageCount;
        document.getElementById('sessionId').textContent = this.sessionId.substr(0, 8) + '...';
        document.getElementById('sessionIdInput').value = this.sessionId;
        document.getElementById('apiEndpoint').value = this.apiEndpoint;
        
        const voiceStatus = document.getElementById('voiceStatus');
        if (voiceStatus) {
            voiceStatus.textContent = this.voiceEnabled ? 'Active' : 'Ready';
        }
        
        // Load saved theme
        const savedTheme = localStorage.getItem('theme') || 'dark';
        this.applyTheme(savedTheme);
    }
    
    applyTheme(theme) {
        const body = document.body;
        const themeToggle = document.getElementById('themeToggle');
        const themeSelect = document.getElementById('themeSelect');
        
        body.classList.remove('dark-theme', 'light-theme', 'cyber-theme');
        body.classList.add(theme + '-theme');
        
        if (themeToggle) {
            if (theme === 'light') themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
            else if (theme === 'cyber') themeToggle.innerHTML = '<i class="fas fa-microchip"></i>';
            else themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        }
        
        if (themeSelect) themeSelect.value = theme;
        localStorage.setItem('theme', theme);
    }
    
    toggleTheme() {
        const themes = ['dark', 'light', 'cyber'];
        const current = localStorage.getItem('theme') || 'dark';
        const next = themes[(themes.indexOf(current) + 1) % themes.length];
        this.applyTheme(next);
    }
    
    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        if (!message) return;
        
        this.addMessage(message, 'user');
        input.value = '';
        this.showTyping();
        
        const startTime = performance.now();
        
        try {
            const response = await fetch(`${this.apiEndpoint}/api/v1/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId,
                    user_id: 'user1'
                })
            });
            
            const endTime = performance.now();
            const responseTime = Math.round(endTime - startTime);
            document.getElementById('responseTime').textContent = responseTime + 'ms';
            
            if (!response.ok) throw new Error('HTTP error');
            
            const data = await response.json();
            this.hideTyping();
            this.addMessage(data.message, 'assistant');
            
            // Handle URL opening
            if (data.action === 'open_url' && data.url) {
                window.open(data.url, '_blank');
            }
            
            // Speak response if voice enabled
            if (this.voiceEnabled && window.speechSynthesis) {
                const utterance = new SpeechSynthesisUtterance(data.message);
                utterance.rate = parseFloat(localStorage.getItem('voiceSpeed') || '1');
                utterance.pitch = parseFloat(localStorage.getItem('voicePitch') || '1');
                window.speechSynthesis.speak(utterance);
            }
            
            this.messageCount++;
            document.getElementById('msgCount').textContent = this.messageCount;
            localStorage.setItem('messageCount', this.messageCount);
            
        } catch (error) {
            console.error('Error:', error);
            this.hideTyping();
            this.addMessage('Sorry, I encountered an error. Please check if the backend is running.', 'assistant');
        }
    }
    
    addMessage(text, sender) {
        const chatMessages = document.getElementById('chatMessages');
        const welcomeScreen = document.getElementById('welcomeScreen');
        
        if (welcomeScreen && this.messageCount === 0) {
            welcomeScreen.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        const avatar = sender === 'user' ? '👤' : '🤖';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">${this.escapeHtml(text)}</div>
        `;
        
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        const chatContainer = document.getElementById('chatContainer');
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    showTyping() {
        const chatMessages = document.getElementById('chatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        `;
        chatMessages.appendChild(typingDiv);
        
        const chatContainer = document.getElementById('chatContainer');
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    hideTyping() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) indicator.remove();
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    clearChat() {
        if (confirm('Are you sure you want to clear the conversation history?')) {
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = `
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
                        <button class="suggestion-card" data-msg="Open YouTube">
                            <i class="fab fa-youtube"></i>
                            <span>Open YouTube</span>
                        </button>
                        <button class="suggestion-card" data-msg="Calculate 25 * 4">
                            <i class="fas fa-calculator"></i>
                            <span>Calculate 25 * 4</span>
                        </button>
                        <button class="suggestion-card" data-msg="Tell me a joke">
                            <i class="fas fa-laugh"></i>
                            <span>Tell me a joke</span>
                        </button>
                        <button class="suggestion-card" data-msg="What is AI?">
                            <i class="fas fa-brain"></i>
                            <span>What is AI?</span>
                        </button>
                    </div>
                </div>
            `;
            this.messageCount = 0;
            document.getElementById('msgCount').textContent = '0';
            localStorage.setItem('messageCount', '0');
            this.rebindSuggestions();
        }
    }
    
    rebindSuggestions() {
        document.querySelectorAll('.suggestion-card').forEach(btn => {
            btn.addEventListener('click', () => {
                const msg = btn.getAttribute('data-msg');
                const input = document.getElementById('messageInput');
                if (input && msg) {
                    input.value = msg;
                    this.sendMessage();
                }
            });
        });
    }
    
    newSession() {
        this.sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('sessionId', this.sessionId);
        document.getElementById('sessionId').textContent = this.sessionId.substr(0, 8) + '...';
        document.getElementById('sessionIdInput').value = this.sessionId;
        this.clearChat();
        this.addMessage("New session started! I'm ready to assist you, Commander.", 'assistant');
        this.showToast('New session created', 'success');
    }
    
    async checkConnection() {
        const connectionSpan = document.querySelector('#connectionStatus span:last-child');
        const statusDot = document.querySelector('.status-dot');
        const modelStatus = document.getElementById('modelStatus');
        
        try {
            const response = await fetch(`${this.apiEndpoint}/health`);
            if (response.ok) {
                if (connectionSpan) connectionSpan.textContent = 'Connected';
                if (statusDot) statusDot.style.background = '#10b981';
                if (modelStatus) modelStatus.textContent = 'JARVIS AI';
                console.log('Connected to backend');
            } else {
                throw new Error('Not connected');
            }
        } catch (error) {
            if (connectionSpan) connectionSpan.textContent = 'AI Mode';
            if (statusDot) statusDot.style.background = '#f59e0b';
            if (modelStatus) modelStatus.textContent = 'Local AI';
            console.log('Using local AI mode');
        }
    }
    
    toggleVoice() {
        this.voiceEnabled = !this.voiceEnabled;
        localStorage.setItem('voiceEnabled', this.voiceEnabled);
        
        const voiceToggle = document.getElementById('voiceToggle');
        const voiceStatus = document.getElementById('voiceStatus');
        
        if (this.voiceEnabled) {
            voiceToggle.classList.add('active');
            voiceToggle.innerHTML = '<i class="fas fa-volume-up"></i><span>Voice On</span>';
            voiceStatus.textContent = 'Active';
            this.showToast('Voice response enabled', 'success');
        } else {
            voiceToggle.classList.remove('active');
            voiceToggle.innerHTML = '<i class="fas fa-volume-mute"></i><span>Voice Off</span>';
            voiceStatus.textContent = 'Ready';
            if (window.speechSynthesis) window.speechSynthesis.cancel();
            this.showToast('Voice response disabled', 'info');
        }
    }
    
    initVoice() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = localStorage.getItem('voiceLang') || 'en-US';
            
            this.recognition.onstart = () => {
                this.showVoiceWave();
            };
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                const input = document.getElementById('messageInput');
                if (input) {
                    input.value = transcript;
                    this.sendMessage();
                }
                this.hideVoiceWave();
            };
            
            this.recognition.onerror = () => {
                this.hideVoiceWave();
                this.showToast('Voice recognition failed', 'error');
            };
            
            this.recognition.onend = () => {
                this.hideVoiceWave();
            };
        }
    }
    
    startVoiceInput() {
        if (!this.recognition) {
            this.showToast('Voice recognition not supported in this browser', 'error');
            return;
        }
        if (this.recognition.running) return;
        this.recognition.start();
    }
    
    showVoiceWave() {
        const overlay = document.getElementById('voiceWaveOverlay');
        if (overlay) overlay.classList.add('active');
        const micBtn = document.getElementById('micBtn');
        if (micBtn) micBtn.classList.add('listening');
    }
    
    hideVoiceWave() {
        const overlay = document.getElementById('voiceWaveOverlay');
        if (overlay) overlay.classList.remove('active');
        const micBtn = document.getElementById('micBtn');
        if (micBtn) micBtn.classList.remove('listening');
    }
    
    openSettings() {
        const modal = document.getElementById('settingsModal');
        if (modal) modal.classList.add('active');
        document.getElementById('apiEndpoint').value = this.apiEndpoint;
        document.getElementById('sessionIdInput').value = this.sessionId;
        
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.getElementById('themeSelect').value = savedTheme;
        
        const savedVoiceLang = localStorage.getItem('voiceLang') || 'en-US';
        document.getElementById('voiceSelect').value = savedVoiceLang;
        
        const savedSpeed = localStorage.getItem('voiceSpeed') || '1';
        document.getElementById('voiceSpeed').value = savedSpeed;
        document.getElementById('speedValue').textContent = savedSpeed + 'x';
        
        const savedPitch = localStorage.getItem('voicePitch') || '1';
        document.getElementById('voicePitch').value = savedPitch;
        document.getElementById('pitchValue').textContent = savedPitch + 'x';
    }
    
    closeSettings() {
        const modal = document.getElementById('settingsModal');
        if (modal) modal.classList.remove('active');
    }
    
    saveSettings() {
        const apiEndpoint = document.getElementById('apiEndpoint');
        if (apiEndpoint) {
            this.apiEndpoint = apiEndpoint.value;
            localStorage.setItem('apiEndpoint', this.apiEndpoint);
        }
        
        const voiceSelect = document.getElementById('voiceSelect');
        if (voiceSelect && this.recognition) {
            this.recognition.lang = voiceSelect.value;
            localStorage.setItem('voiceLang', voiceSelect.value);
        }
        
        const longTermMemory = document.getElementById('longTermMemory');
        if (longTermMemory) localStorage.setItem('longTermMemory', longTermMemory.checked);
        
        const contextAwareness = document.getElementById('contextAwareness');
        if (contextAwareness) localStorage.setItem('contextAwareness', contextAwareness.checked);
        
        this.closeSettings();
        this.checkConnection();
        this.showToast('Settings saved', 'success');
    }
    
    showToast(message, type = 'info') {
        const toast = document.getElementById('toastNotification');
        const toastMessage = document.getElementById('toastMessage');
        
        if (toast && toastMessage) {
            toastMessage.textContent = message;
            
            const icon = toast.querySelector('i');
            if (icon) {
                icon.className = '';
                if (type === 'success') icon.className = 'fas fa-check-circle';
                else if (type === 'error') icon.className = 'fas fa-exclamation-circle';
                else icon.className = 'fas fa-info-circle';
            }
            
            toast.classList.add('show');
            setTimeout(() => {
                toast.classList.remove('show');
            }, 3000);
        }
    }
    
    startUptimeTimer() {
        setInterval(() => {
            const uptime = Math.floor((Date.now() - this.startTime) / 1000);
            const hours = Math.floor(uptime / 3600);
            const minutes = Math.floor((uptime % 3600) / 60);
            const seconds = uptime % 60;
            const uptimeDisplay = document.getElementById('uptime');
            if (uptimeDisplay) {
                uptimeDisplay.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }
        }, 1000);
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.jarvis = new JARVISApp();
});