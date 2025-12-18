import { API } from "../api/index.js";
import { Service } from "../service/index.js";
import { makeOverlayClosable} from "../utils/overlay.js";

export const FilesUI = {

    selectedFiles: [],

    init() {
        this.table = document.querySelector("#filesTable tbody");

        this.detailOverlay = document.getElementById("uploadOverlay");
        this.overlayDropzone = document.getElementById("overlayDropzone");
        this.overlayFileInput = document.getElementById("overlayFileInput");
        this.selectedFilesList = document.getElementById("selectedFilesList");
        this.tagInput = document.getElementById("uploadTag");

        this.openOverlayBtn = document.getElementById("openUploadOverlay");
        this.cancelOverlayBtn = document.getElementById("cancelUploadOverlay");
        this.uploadBtn = document.getElementById("uploadFilesBtn");

        makeOverlayClosable(this.detailOverlay)

        this.bindEvents();
        this.refresh();
    },

    bindEvents() {

        // open overlay
        this.openOverlayBtn.addEventListener("click", () => {
            this.selectedFiles = [];
            this.selectedFilesList.innerHTML = "";
            this.tagInput.value = "";
            this.detailOverlay.classList.remove("hidden");
        });

        // close overlay
        this.cancelOverlayBtn.addEventListener("click", () => {
            this.detailOverlay.classList.add("hidden");
        });

        // overlay: click on dropzone
        this.overlayDropzone.addEventListener("click", () => {
            this.overlayFileInput.click();
        });

        // overlay: files per FileInput
        this.overlayFileInput.addEventListener("change", e => {
            [...e.target.files].forEach(f => this.addLocalFile(f));
            this.overlayFileInput.value = "";
        });

        // overlay: drag & drop
        this.overlayDropzone.addEventListener("dragover", e => {
            e.preventDefault();
            this.overlayDropzone.classList.add("drag");
        });

        this.overlayDropzone.addEventListener("dragleave", () => {
            this.overlayDropzone.classList.remove("drag");
        });

        this.overlayDropzone.addEventListener("drop", e => {
            e.preventDefault();
            this.overlayDropzone.classList.remove("drag");
            [...e.dataTransfer.files].forEach(f => this.addLocalFile(f));
        });

        this.uploadBtn.addEventListener("click", () => this.uploadAll());
    },

    addLocalFile(file) {
        this.selectedFiles.push(file);
        const li = document.createElement("li");
        li.textContent = file.name;
        this.selectedFilesList.appendChild(li);
    },

    async uploadAll() {
        const tag = this.tagInput.value.trim();

        for (const file of this.selectedFiles) {
            await API.Files.upload(file, [tag]);
        }

        this.detailOverlay.classList.add("hidden");
        await this.refresh();
    },

    async refresh() {
        const files = await Service.Files.getAll();
        this.table.innerHTML = "";

        for (const f of files) {
            this.addRow(
                f.display_name,
                f.storage_name,
                f.size,
                f.mime_type,
                f.tags ?? ""
            );
        }
    },

    addRow(display_name, storage_name, size, mime_type, tags) {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${display_name}</td>
            <td>${storage_name}</td>
            <td>${size}</td>
            <td>${mime_type}</td>
            <td>${tags}</td>
            <td><button class="button button--red" data-delete="${storage_name}">Del</button></td>
        `;

        tr.querySelector("[data-delete]").addEventListener("click", async () => {
            tr.remove();
            try {
                await API.Files.delete(storage_name);
            } catch {
                await this.refresh();
            }
        });

        this.table.appendChild(tr);
    }
};
