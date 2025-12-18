import { API } from "../api/index.js";
import { Service } from "../service/index.js";

export const PromptsUI = {

    init() {
        this.table = document.querySelector("#promptsTable tbody");
        this.nameInput = document.getElementById("promptName");
        this.promptInput = document.getElementById("promptInput");
        this.fileInput = document.getElementById("promptTXTFileInput");


        this.form = document.getElementById("promptsForm");

        this.form.addEventListener("submit", async (e) => {
            e.preventDefault();

            if (!this.form.checkValidity()) {
                this.form.reportValidity();
                return;
            }

            await this.add();
        });

        this.fileInput.addEventListener("change", e => {
            [...e.target.files].forEach(f => this.addLocalFile(f));
            this.overlayFileInput.value = "";
        });

        this.refresh();
    },

    async refresh() {
        const prompts = await Service.Prompts.getAll()
        this.table.innerHTML = "";
        prompts.forEach(ep => this.addRow(ep));
    },

    async add() {
        await Service.Prompts.add(this.nameInput.value, this.promptInput.value);
        this.refresh();
    },

    async addLocalFile(file) {
        const fileContent = await new Promise((resolve, reject) => {
            const reader = new FileReader();

            reader.onload = () => resolve(reader.result);
            reader.onerror = () => reject(reader.error);

            reader.readAsText(file);
        });

        this.nameInput.value = file.name;
        this.promptInput.value = fileContent;
    },


    addRow(pr) {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${pr.id}</td>
            <td>${pr.name}</td>
            <td>${pr.prompt}</td>
            <td><button class="button button--red" data-delete="${pr.id}">Del</button></td>
        `;

        const promptDeleteBtn = tr.querySelector("[data-delete]");

        promptDeleteBtn.addEventListener("click", async () => {
            const id = promptDeleteBtn.getAttribute("data-delete");
            console.log("Delete clicked for:", id);

            try {
                await Service.Prompts.delete(id);
                tr.remove();
            } catch (err) {
                console.error("Delete failed:", err);
                alert("Delete failed: \n" + err)
                await this.refresh();
            }
        });

        this.table.appendChild(tr);}
};
