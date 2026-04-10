(function () {
    const STORAGE_KEY = "dashboard-theme";

    function getTheme() {
        return document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
    }

    function updateButtonLabel() {
        const button = document.getElementById("theme-toggle");
        if (!button) {
            return;
        }

        button.textContent = getTheme() === "dark" ? "Light Theme" : "Dark Theme";
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem(STORAGE_KEY, theme);
        updateButtonLabel();
    }

    document.addEventListener("DOMContentLoaded", () => {
        updateButtonLabel();

        const button = document.getElementById("theme-toggle");
        if (!button) {
            return;
        }

        button.addEventListener("click", () => {
            const nextTheme = getTheme() === "dark" ? "light" : "dark";
            applyTheme(nextTheme);
            window.location.reload();
        });
    });
}());
