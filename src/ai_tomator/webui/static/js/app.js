import { FilesUI } from "./ui/files_ui.js";
import { EndpointsUI } from "./ui/endpoints_ui.js";
import { RunsUI } from "./ui/batches_ui.js";
import { ExportUI } from "./ui/export_ui.js";
import {PromptsUI as PromptUI} from "./ui/prompts_ui.js";

function init() {
    console.log("INIT");
    FilesUI.init();
    EndpointsUI.init();
    RunsUI.init();
    ExportUI.init();
    PromptUI.init();
}



const warningOverlay = document.getElementById("warning-overlay");
const understandWarningBtn = document.getElementById("understand-warning-btn");

const understoodWarning = sessionStorage.getItem("understoodWarning");
if (!understoodWarning) {
    warningOverlay.classList.remove("hidden");
}

understandWarningBtn.addEventListener("click", function() {
    warningOverlay.classList.add("hidden");
    sessionStorage.setItem("understoodWarning", "true");
})

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
} else {
    init();
}
