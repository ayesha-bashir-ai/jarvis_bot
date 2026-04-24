class UIModule {
    constructor() {
        this.theme = localStorage.getItem("theme") || "dark";
        this.applyTheme(this.theme);
    }

    applyTheme(theme) {
        document.body.className = `${theme}-theme`;
        localStorage.setItem("theme", theme);
    }

    toggleTheme() {
        const themes = ["dark", "light", "cyber"];
        const current = themes.indexOf(this.theme);
        this.theme = themes[(current + 1) % themes.length];
        this.applyTheme(this.theme);
    }

    updateSessionInfo() {
        const el = document.getElementById("sessionId");
        if (el && window.jarvis) {
            el.textContent = window.jarvis.sessionId.slice(0, 8);
        }
    }
}