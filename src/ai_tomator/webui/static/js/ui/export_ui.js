import { API } from "../api/index.js";
import { Service } from "../service/index.js";

export const ExportUI = {

    init() {
        const tableEl = document.getElementById("batchTableExport");
        this.table = tableEl.querySelector("tbody");

        this.headerCheckbox = document.getElementById("select-all-checkbox");
        this.exportModeSelect = document.getElementById("export-mode-select");
        this.exportButton = document.getElementById("export-button");

        this.headerCheckbox.addEventListener("change", () => this.toggleAll());
        this.exportButton.addEventListener("click", () => this.export());

        this.refresh();
    },

    async refresh() {
        const runs = await Service.Batches.getAll();
        this.table.innerHTML = "";
        runs.forEach(r => this.addRow(r));
    },

    addRow(r) {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><input type="checkbox" class="batch-checkbox" data-id="${r.id}"></td>
            <td>${r.id}</td>
            <td>${r.status}</td>
            <td>${r.endpoint}</td>
            <td>${r.file_reader}</td>
        `;
        this.table.appendChild(tr);
    },

    toggleAll() {
        const checked = this.headerCheckbox.checked;
        const boxes = this.table.querySelectorAll(".batch-checkbox");
        boxes.forEach(cb => cb.checked = checked);
    },

    async export() {
        const mode = this.exportModeSelect.value;

        const batch_ids = [...this.table.querySelectorAll(".batch-checkbox")]
            .filter(cb => cb.checked)
            .map(cb => parseInt(cb.dataset.id));

        if (batch_ids.length === 0) {
            console.warn("No batches selected");
            return;
        }

        const blob = await API.Export.batches(mode, batch_ids);

        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "export.csv";
        a.click();
        URL.revokeObjectURL(url);
    }
};