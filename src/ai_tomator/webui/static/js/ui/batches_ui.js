import { API } from "../api/index.js";
import { Service } from "../service/index.js";
import { makeOverlayClosable} from "../utils/overlay.js";

export const RunsUI = {

    init() {
        this.table = document.querySelector("#runsTable tbody");
        this.startBtn = document.getElementById("startRunBtn");
        this.endpointSelect = document.getElementById("endpoint-select");
        this.fileTagSelect = document.getElementById("file-tag-select");
        this.fileReaderSelect = document.getElementById("file-reader-select");
        this.modelSelect = document.getElementById("model-select");
        this.temperatureField = document.getElementById("temperature-input");
        this.delayField = document.getElementById("delay-input");
        this.promptField = document.getElementById("prompt-input");


        this.overlay = document.getElementById("batchOverlay");
        makeOverlayClosable(this.overlay);
        this.batchesDetailsTable = document.getElementById("batchDetailsTable");

        this.modelSelectDefault = "<option value=\"\">Modell auswählen</option>"
        this.modelSelect.innerHTML = this.modelSelectDefault;

        this.form = document.getElementById("runForm");

        this.form.addEventListener("submit", async (e) => {
            e.preventDefault();

            if (!this.form.checkValidity()) {
                this.form.reportValidity();
                return;
            }

            await this.start();
        });

        this.endpointSelect.addEventListener("change", async () => {
            if (this.endpointSelect.value === "") {
                this.modelSelect.innerHTML = this.modelSelectDefault;
                return;
            }
            this.modelSelect.innerHTML = "<option>Lädt…</option>";
            const models = await API.Endpoints.get_models(this.endpointSelect.value);

            this.modelSelect.innerHTML = this.modelSelectDefault;
            for (const model of models) {
                const option = document.createElement("option");
                option.value = model;
                option.textContent = model;
                this.modelSelect.appendChild(option);
            }
        });

        this.refresh();
    },

    async refresh() {
        const runs = await API.Batches.list()
        const endpoints = await API.Endpoints.list()
        const file_readers = await API.Pipeline.listFileReaders()
        file_readers.push("upload")
        const file_tags = await Service.Files.getTags()

        this.endpointSelect.innerHTML = "<option value=\"\">Endpoint auswählen</option>";
        for (const endpointsKey of endpoints) {
           const option = document.createElement("option");
           option.value = endpointsKey["name"];
           option.textContent = endpointsKey["name"];
           this.endpointSelect.appendChild(option);
        }
        console.log(file_tags)
        this.fileTagSelect.innerHTML = "<option value=\"\">File Tag auswählen</option>";
        for (const tag of file_tags) {
            const option = document.createElement("option");
            option.value = tag;
            option.textContent = tag;
            this.fileTagSelect.appendChild(option);
        }
        this.fileReaderSelect.innerHTML = "<option value=\"\">File Reader auswählen</option>";
        for (const reader of file_readers) {
            const option = document.createElement("option");
            option.value = reader;
            option.textContent = reader;
            this.fileReaderSelect.appendChild(option);
        }
        console.log(runs);
        this.table.innerHTML = "";
        runs.forEach(r => this.addRow(r));
    },

    addRow(r) {
        const tr = document.createElement("tr");
        tr.innerHTML = `
        <td>${r.id}</td>
        <td>${r.status}</td>
        <td>${r.endpoint}</td>
        <td>${r.file_reader}</td>
    `;

        tr.addEventListener("click", () => {
            console.log("Batch element clicked:", r.id);
            this.openBatchDetailOverlay(r)
        });

        this.table.appendChild(tr);
    },

    openBatchDetailOverlay(batch) {
        this.overlay.classList.remove("hidden");

        this.batchesDetailsTable.innerHTML = "";

        for (const [key, value] of Object.entries(batch)) {
            const tr = document.createElement("tr");
            tr.innerHTML = `
            <td>${key}</td>
            <td>${value}</td>
        `;
            this.batchesDetailsTable.appendChild(tr);
        }
    },

    async start() {
        const data = {
            prompt: this.promptField.value,
            endpoint: this.endpointSelect.value,
            model: this.modelSelect.value,
            file_reader: this.fileReaderSelect.value,
            files: await Service.Files.getStrListByTag(this.fileTagSelect.value),
            delay: this.delayField.value,
            temperature: this.temperatureField.value,
        };

        const run = await API.Batches.start(data);

        this.addRow(run);
    }
};
