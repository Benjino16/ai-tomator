import { FilesUI } from "./ui/files_ui.js";
import { EndpointsUI } from "./ui/endpoints_ui.js";
import { RunsUI } from "./ui/batches_ui.js";
import { ExportUI } from "./ui/export_ui.js";
import { PromptsUI as PromptUI } from "./ui/prompts_ui.js";
import { PriceUI } from "./ui/price_ui.js";
import { setupLogin } from "./login.js";  // Login importieren
import { setupNavigation, showSection } from "./navigation.js";

function init() {
    setupNavigation()
    FilesUI.init();
    EndpointsUI.init();
    RunsUI.init();
    ExportUI.init();
    PriceUI.init();
    PromptUI.init();

    showSection("batch-run")
}

function loginSuccess() {
    document.getElementById('authOverlay').style.display = 'none';
    document.querySelector('.layout').style.display = 'flex';

    const warningOverlay = document.getElementById("warning-overlay");
    const understandWarningBtn = document.getElementById("understand-warning-btn");

    if (!sessionStorage.getItem("understoodWarning")) {
        warningOverlay.classList.remove("hidden");
    }

    understandWarningBtn.addEventListener("click", () => {
        warningOverlay.classList.add("hidden");
        sessionStorage.setItem("understoodWarning", "true");
    });

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
}

// Login einrichten, Callback übergeben
setupLogin(loginSuccess);
