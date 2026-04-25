class UIModule {
    constructor() {
        this.theme = localStorage.getItem("theme") || "dark";
        this.applyTheme(this.theme);
    }

    // ✅ FIXED: preserve other body classes
    applyTheme(theme) {
        document.body.classList.remove("dark-theme", "light-theme", "cyber-theme");
        document.body.classList.add(`${theme}-theme`);

        this.theme = theme;
        localStorage.setItem("theme", theme);
    }

    toggleTheme() {
        const themes = ["dark", "light", "cyber"];
        const current = themes.indexOf(this.theme);

        const nextTheme = themes[(current + 1) % themes.length];

        this.applyTheme(nextTheme);
    }

    // ✅ FIXED: safe session handling
    updateSessionInfo() {
        const el = document.getElementById("sessionId");

        const session = window.jarvis?.sessionId;

        if (el && session) {
            el.textContent = session.slice(0, 8);
        }
    }
}
