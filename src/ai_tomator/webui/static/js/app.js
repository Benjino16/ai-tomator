import { FilesUI } from "./ui/files_ui.js";
import { EndpointsUI } from "./ui/endpoints_ui.js";
import { RunsUI } from "./ui/batches_ui.js";

function init() {
    console.log("INIT");
    FilesUI.init();
    EndpointsUI.init();
    RunsUI.init();
}

export function makeOverlayClosable(overlay) {
    const content = overlay.querySelector(".overlay-content");

    overlay.addEventListener("click", () => {
        overlay.classList.add("hidden");
    });

    content.addEventListener("click", (e) => {
        e.stopPropagation();
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
} else {
    init();
}
