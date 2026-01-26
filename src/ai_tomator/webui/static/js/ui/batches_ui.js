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
        this.promptSelect = document.getElementById("prompt-select");

        this.openStartOverlayBtn = document.getElementById("open-start-overlay-btn");
        this.startOverlay = document.getElementById("batchStartOverlay");
        makeOverlayClosable(this.startOverlay);

        this.detailOverlay = document.getElementById("batchDetailOverlay");
        this.batchesDetailsTable = document.getElementById("batchDetailsTable");
        makeOverlayClosable(this.detailOverlay);

        this.logOverlay = document.getElementById("batchLogsOverlay");
        this.batchLogPre = document.getElementById("batch-logs");
        makeOverlayClosable(this.logOverlay);

        this.filesOverlay = document.getElementById("batchFilesOverlay");
        this.filesStatusPre = document.getElementById("batchFilesStatusPre");
        this.batchesFilesTable = document.getElementById("batchFileTable");
        makeOverlayClosable(this.filesOverlay);

        this.modelSelectDefault = "<option value=\"\">Modell auswählen</option>"
        this.modelSelect.innerHTML = this.modelSelectDefault;

        this.form = document.getElementById("runForm");

        this.openStartOverlayBtn.addEventListener("click", () => {
            this.startOverlay.classList.remove("hidden");
        });

        this.form.addEventListener("submit", async (e) => {
            e.preventDefault();

            if (!this.form.checkValidity()) {
                this.form.reportValidity();
                return;
            }
            await this.start();
            this.startOverlay.classList.add("hidden");
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

        this.startTimers();
        this.refresh();
    },

    async refresh() {
        const runs = await Service.Batches.getAll()
        const endpoints = await Service.Endpoints.getAll()
        const file_readers = await API.Pipeline.listFileReaders()
        file_readers.push("upload")
        const file_tags = await Service.Files.getTags()
        const prompts = await Service.Prompts.getAll()

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
        this.promptSelect.innerHTML = "<option value=\"\">Prompt auswählen</option>";
        for (const prompt of prompts) {
            const option = document.createElement("option");
            option.value = prompt.id;
            option.textContent = prompt.name;
            this.promptSelect.appendChild(option);
        }
        this.table.innerHTML = "";
        runs.forEach(r => this.addRow(r));
    },

    addRow(r) {
        const tr = document.createElement("tr");

        const statusClass = {
            "FAILED": "status-failed",
            "RUNNING": "status-running",
            "COMPLETED": "status-completed"
        }[r.status] || "status-unknown";

        const createdCell = (r.status === "RUNNING")
            ? `<td class="timer" data-start="${r.created_at}" data-id="${r.id}">${this.calculateTime(r.created_at)}</td>`
            : `<td class="text-grey">${r.updated_at}</td>`;


        tr.innerHTML = `
            <td>${r.id}</td>
            <td><span class="status-pill ${statusClass}">${r.status}</span></td>
            ${createdCell}
            <td>${r.model}</td>
            <td>${r.temperature}</td>
            <td>
                <button class="button button--grey" data-detail-id="${r.id}">Details</button>
                <button class="button button--grey" data-log-id="${r.id}">Logs</button>
                <button class="button button--grey" data-status-id="${r.id}">Status</button>
            </td>
        `;

        const batchDetailBtn = tr.querySelector("[data-detail-id]");
        batchDetailBtn.addEventListener("click", async () => {
            const batch_id = batchDetailBtn.getAttribute("data-detail-id");
            const batch = await Service.Batches.getById(batch_id)
            this.openBatchDetailOverlay(batch)
        })
        const batchLogBtn = tr.querySelector("[data-log-id]");
        batchLogBtn.addEventListener("click", async () => {
            const batch_id = batchLogBtn.getAttribute("data-log-id");
            this.openBatchLogOverlay(batch_id)
        })
        const batchStatusBtn = tr.querySelector("[data-status-id]");
        batchStatusBtn.addEventListener("click", async () => {
            const batch_id = batchStatusBtn.getAttribute("data-status-id");
            const files = await Service.Batches.getFileStatus(batch_id);
            this.openBatchFilesOverlay(files)
        })
        this.table.appendChild(tr);
    },


    openBatchDetailOverlay(batch) {
        this.detailOverlay.classList.remove("hidden");

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

    openBatchLogOverlay(batch_id) {
        this.logOverlay.classList.remove("hidden");

        this.batchLogPre.innerHTML = "";

        Service.Batches.getLogs(batch_id).then(logs => {
            const formattedLogs = logs.map(entry => {
                const date = new Date(entry.created_at).toLocaleString();
                let logText = entry.log;

                const maxLength = 80;
                if (logText.length > maxLength) {
                    logText = logText.slice(0, maxLength) + '…';
                }

                logText = logText.split('\n').map((line, index) => {
                    return index === 0 ? line : '    ' + line;
                }).join('\n');

                return `${date} - ${logText}`;
            });


            this.batchLogPre.textContent = formattedLogs.join("\n");
        }).catch(error => {
            console.log("Error while loading log for overlay: " + error);
        })
    },

    openBatchFilesOverlay(files) {
        this.filesOverlay.classList.remove("hidden");

        this.batchesFilesTable.innerHTML = "";
        this.filesStatusPre.innerHTML = "";

        const statusCounts = {};

        for (const file of files) {
            statusCounts[file.status] = (statusCounts[file.status] || 0) + 1;

            const statusClass = {
                FAILED: "status-failed",
                RUNNING: "status-running",
                COMPLETED: "status-completed"
            }[file.status] || "status-unknown";

            const tr = document.createElement("tr");
            tr.innerHTML = `
            <td>${file.display_name}</td>
            <td><span class="status-pill ${statusClass}">${file.status}</span></td>
        `;
            this.batchesFilesTable.appendChild(tr);
        }

        this.filesStatusPre.textContent = Object.entries(statusCounts)
            .map(([status, count]) => `${status}: ${count}`)
            .join("\n");
    },

    async start() {
        const data = {
            prompt_id: this.promptSelect.value,
            endpoint: this.endpointSelect.value,
            model: this.modelSelect.value,
            file_reader: this.fileReaderSelect.value,
            files: await Service.Files.getStrListByTag(this.fileTagSelect.value),
            delay: this.delayField.value,
            temperature: this.temperatureField.value,
        };

        const run = await Service.Batches.add(data);

        this.addRow(run);
    },

    startTimers() {
        setInterval(() => {
            const now = Date.now();
            document.querySelectorAll("td.timer").forEach(td => {
                td.textContent = this.calculateTime(td.dataset.start)
            });
        }, 1000);
    },

    calculateTime(start_date) {
        const now = Date.now();
        const start = new Date(start_date).getTime();
        const diff = Math.floor((now - start) / 1000) - 3600;

        const m = String(Math.floor(diff / 60)).padStart(2, '0');
        const s = String(diff % 60).padStart(2, '0');
        return `${m}:${s}`;
    },
};
