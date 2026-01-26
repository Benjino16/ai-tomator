import { API } from "../api/index.js";
import { Service } from "../service/index.js";
import {makeOverlayClosable} from "../utils/overlay.js";

export const PromptsUI = {

    init() {
        this.table = document.querySelector("#promptsTable tbody");
        this.nameInput = document.getElementById("promptName");
        this.promptInput = document.getElementById("promptInput");
        this.fileInput = document.getElementById("promptTXTFileInput");

        this.promptsOverlay = document.getElementById("promptAddOverlay");
        this.openPromptOverlayBtn = document.getElementById("open-prompt-overlay-btn");
        makeOverlayClosable(this.promptsOverlay);

        this.nameDisplay = document.getElementById("promptDisplayName");
        this.promptDisplay = document.getElementById("promptDisplayInput");
        this.promptsDisplayOverlay = document.getElementById("promptDisplayOverlay");
        makeOverlayClosable(this.promptsDisplayOverlay);

        this.form = document.getElementById("promptForm");
        this.form.addEventListener("submit", async (e) => {
            e.preventDefault();

            if (!this.form.checkValidity()) {
                this.form.reportValidity();
                return;
            }

            const isValid = await this.add();
            if(isValid) {
                this.form.reset()
                this.promptsOverlay.classList.add("hidden");
            }
        });

        this.openPromptOverlayBtn.addEventListener("click", () => {
            this.promptsOverlay.classList.remove("hidden");
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
        const data = {
            name: this.nameInput.value,
            content: this.promptInput.value,
        }
        try {
            const response = await Service.Prompts.add(data);
            if (!response.ok) {
                if (response.status === 409) {
                    const result = await response.json()
                    throw "Name already exists: " + JSON.stringify(result.detail)
                }
            }
            else {
                return true
            }
        }
        catch (e) {
            console.error(e);
            alert(e)
            return false
        } finally {
            this.refresh();
        }
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

        const shorten_prompt =
            pr.content.length > 50
                ? pr.content.slice(0, 50) + "..."
                : pr.content;

        tr.innerHTML = `
            <td>${pr.id}</td>
            <td>${pr.name}</td>
            <td>${shorten_prompt}</td>
            <td>
                <div>
                    <button class="button button--grey">Show</button>
                    <button class="button button--red" data-delete="${pr.id}">Del</button>
                </div>
            </td>
            
            
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

        const promptShowBtn = tr.querySelector(".button--grey");

        promptShowBtn.addEventListener("click", () => {
            this.nameDisplay.value = pr.name;
            this.promptDisplay.value = pr.content;
            this.promptsDisplayOverlay.classList.remove("hidden");
        });




        this.table.appendChild(tr);}
};
