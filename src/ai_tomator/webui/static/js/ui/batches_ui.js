import { API } from "../api/index.js";

export const RunsUI = {

    init() {
        this.table = document.querySelector("#runsTable tbody");
        this.startBtn = document.getElementById("startRunBtn");
        this.endpointSelect = document.getElementById("endpoint-select");
        this.fileSelect = document.getElementById("file-tag-select");
        this.fileReaderSelect = document.getElementById("file-reader-select");
        this.modelField = document.getElementById("model-input");
        this.temperatureField = document.getElementById("temperature-input");


        this.startBtn.onclick = () => this.start();
        console.log("Test")
        this.refresh();
    },

    async refresh() {
        const runs = await API.Batches.list()
        const endpoints = await API.Endpoints.list()
        const file_readers = await API.Pipeline.listFileReaders()
        const files = await API.Files.list()
        console.log(files)

        this.endpointSelect.innerHTML = "<option value=\"\">Endpoint auswählen</option>";
        for (const endpointsKey of endpoints) {
           const option = document.createElement("option");
           option.value = endpointsKey["name"];
           option.textContent = endpointsKey["name"];
           this.endpointSelect.appendChild(option);
        }
        this.fileSelect.innerHTML = "<option value=\"\">File Tag auswählen</option>";
        for (const file of files) {
            const option = document.createElement("option");
            option.value = file["storage_name"];
            option.textContent = file["display_name"];
            this.fileSelect.appendChild(option);
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
        this.table.appendChild(tr);
    },

    async start() {
        const data = {
            prompt: "bla bla",
            endpoint: this.endpointSelect.value,
            model: this.modelField.value,
            file_reader: "pypdf2",
            files: [this.fileSelect.value],
            delay: 5,
            temperature: this.temperatureField.value,
        };

        const run = await API.Batches.start(data);

        this.addRow(run);
    }
};
