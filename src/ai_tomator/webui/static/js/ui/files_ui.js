import { API } from "../api/index.js";

export const FilesUI = {

    init() {
        this.table = document.querySelector("#filesTable tbody");
        this.dropzone = document.getElementById("dropzone");
        this.fileInput = document.getElementById("fileInput");
        this.bindEvents();
        this.refresh();
    },

    bindEvents() {
        this.dropzone.addEventListener("click", () => {
            this.fileInput.click();
        });

        this.fileInput.addEventListener("change", (e) => {
            [...e.target.files].forEach(file => this.upload(file));
            this.fileInput.value = "";
        });

        this.dropzone.addEventListener("dragover", e => {
            e.preventDefault();
            this.dropzone.classList.add("drag");
        });

        this.dropzone.addEventListener("dragleave", () => {
            this.dropzone.classList.remove("drag");
        });

        this.dropzone.addEventListener("drop", e => {
            e.preventDefault();
            this.dropzone.classList.remove("drag");
            [...e.dataTransfer.files].forEach(file => this.upload(file));
        });
    },

    async refresh() {
        const files = await API.Files.list();
        console.log("Files from API:", files);
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

    async upload(file) {
        const saved = await API.Files.upload(file);
        await this.refresh(); //todo: if the api returns the file instead of status, then directly add it
    },

    addRow(display_name, storage_name, size, mime_type, tags) {
        const tr = document.createElement("tr");
        tr.dataset.storageName = storage_name;

        tr.innerHTML = `
            <td>${display_name}</td>
            <td>${storage_name}</td>
            <td>${size}</td>
            <td>${mime_type}</td>
            <td>${tags ?? ""}</td>
            <td>
                <button data-delete="${storage_name}">Löschen</button>
            </td>
        `;

        const deleteBtn = tr.querySelector("[data-delete]");

        deleteBtn.addEventListener("click", async () => {
            const name = deleteBtn.getAttribute("data-delete");
            console.log("Delete clicked for:", name);

            tr.remove();

            try {
                await API.Files.delete(name);
            } catch (err) {
                console.error("Delete failed:", err);
                await this.refresh();
            }
        });

        this.table.appendChild(tr);
    }
};
