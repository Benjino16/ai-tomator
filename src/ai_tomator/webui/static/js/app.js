import { FilesUI } from "./ui/files_ui.js";
import { EndpointsUI } from "./ui/endpoints_ui.js";
import { RunsUI } from "./ui/batches_ui.js";

function init() {
    console.log("INIT");
    FilesUI.init();
    EndpointsUI.init();
    RunsUI.init();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
} else {
    init();
}
