// UI management module
class UIModule {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'dark';
        this.apiEndpoint = localStorage.getItem('apiEndpoint') || 'http://127.0.0.1:8000';
        this.sessionId = localStorage.getItem('sessionId') || this.generateSessionId();
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    applyTheme(theme) {
        const body = document.body;
        const themeToggle = document.getElementById('themeToggle');
        
        // Remove all theme classes
        body.classList.remove('dark-theme', 'light-theme', 'cyber-theme');
        
        // Apply new theme
        if (theme === 'light') {
            body.classList.add('light-theme');
            if (themeToggle) themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        } else if (theme === 'cyber') {
            body.classList.add('cyber-theme');
            if (themeToggle) themeToggle.innerHTML = '<i class="fas fa-microchip"></i>';
        } else {
            body.classList.add('dark-theme');
            if (themeToggle) themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        }
        
        this.currentTheme = theme;
        localStorage.setItem('theme', theme);
        console.log('Theme applied:', theme);
    }
    
    toggleTheme() {
        const themes = ['dark', 'light', 'cyber'];
        const currentIndex = themes.indexOf(this.currentTheme);
        const nextTheme = themes[(currentIndex + 1) % themes.length];
        this.applyTheme(nextTheme);
    }
    
    showVoiceWave() {
        const wave = document.getElementById('voiceWave');
        if (wave) wave.classList.add('active');
        const micBtn = document.getElementById('micBtn');
        if (micBtn) micBtn.classList.add('listening');
    }
    
    hideVoiceWave() {
        const wave = document.getElementById('voiceWave');
        if (wave) wave.classList.remove('active');
        const micBtn = document.getElementById('micBtn');
        if (micBtn) micBtn.classList.remove('listening');
    }
    
    updateStatus(message, isError = false) {
        const connectionStatus = document.querySelector('.connection-status span:last-child');
        const statusDot = document.querySelector('.status-dot');
        
        if (connectionStatus) {
            connectionStatus.textContent = message;
        }
        
        if (isError && statusDot) {
            statusDot.classList.add('disconnected');
            statusDot.classList.remove('connected');
        } else if (statusDot) {
            statusDot.classList.remove('disconnected');
            statusDot.classList.add('connected');
        }
    }
    
    updateResponseTime(time) {
        const responseTime = document.getElementById('responseTime');
        if (responseTime) {
            responseTime.textContent = time === 0 ? 'N/A' : `${time}ms`;
        }
    }
    
    updateSessionInfo() {
        const sessionDisplay = document.getElementById('sessionId');
        if (sessionDisplay) {
            sessionDisplay.textContent = this.sessionId.substr(0, 8) + '...';
        }
        
        const sessionInput = document.getElementById('sessionIdInput');
        if (sessionInput) {
            sessionInput.value = this.sessionId;
        }
    }
    
    openSettings() {
        const modal = document.getElementById('settingsModal');
        if (modal) {
            modal.style.display = 'flex';
            modal.classList.add('active');
            
            // Populate settings
            const apiEndpoint = document.getElementById('apiEndpoint');
            if (apiEndpoint) apiEndpoint.value = this.apiEndpoint;
            
            const themeSelect = document.getElementById('themeSelect');
            if (themeSelect) themeSelect.value = this.currentTheme;
            
            const sessionInput = document.getElementById('sessionIdInput');
            if (sessionInput) sessionInput.value = this.sessionId;
        }
    }
    
    closeSettings() {
        const modal = document.getElementById('settingsModal');
        if (modal) {
            modal.style.display = 'none';
            modal.classList.remove('active');
        }
    }
    
    saveSettings() {
        const apiEndpoint = document.getElementById('apiEndpoint');
        if (apiEndpoint) {
            this.apiEndpoint = apiEndpoint.value;
            localStorage.setItem('apiEndpoint', this.apiEndpoint);
        }
        
        const themeSelect = document.getElementById('themeSelect');
        if (themeSelect) {
            this.applyTheme(themeSelect.value);
        }
        
        const voiceSelect = document.getElementById('voiceSelect');
        if (voiceSelect) {
            localStorage.setItem('voiceLang', voiceSelect.value);
        }
        
        this.closeSettings();
    }
    
    newSession() {
        this.sessionId = this.generateSessionId();
        localStorage.setItem('sessionId', this.sessionId);
        this.updateSessionInfo();
        return this.sessionId;
    }
}

window.UIModule = UIModule;