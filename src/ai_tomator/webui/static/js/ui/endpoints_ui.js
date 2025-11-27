// js/endpoints_ui.js

import { API } from "../api/index.js";

export const EndpointsUI = {

    init() {
        this.table = document.querySelector("#endpointsTable tbody");
        this.nameInput = document.getElementById("endpointName");
        this.select = document.getElementById("endpointEngine");
        this.urlInput = document.getElementById("endpointUrl");
        this.tokenInput = document.getElementById("endpointToken");
        this.addBtn = document.getElementById("addEndpointBtn");

        this.addBtn.onclick = () => this.add();

        this.refresh();
    },

    async refresh() {
        const endpoints = await API.Endpoints.list()
        const engines = await API.Pipeline.listEngines()
        console.log(endpoints)

        this.select.innerHTML = "<option value=\"\">Engine auswählen</option>";
        for (const engine of engines) {
            const option = document.createElement("option");
            option.value = engine;
            option.textContent = engine;
            this.select.appendChild(option);
        }

        this.table.innerHTML = "";
        endpoints.forEach(ep => this.addRow(ep));
    },

    async add() {
        const data = {
            name: this.nameInput.value,
            engine: this.select.value,
            url: this.urlInput.value,
            token: this.tokenInput.value,
        };

        await API.Endpoints.add(data);
        this.refresh();
    },

    addRow(ep) {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${ep.name}</td>
            <td>${ep.engine}</td>
            <td>${ep.url}</td>
            <td>${ep.token}</td>
            <td><button data-delete="${ep.name}">Löschen</button></td>
        `;

        const endpointDeleteBtn = tr.querySelector("[data-delete]");

        endpointDeleteBtn.addEventListener("click", async () => {
            const name = endpointDeleteBtn.getAttribute("data-delete");
            console.log("Delete clicked for:", name);

            tr.remove();

            try {
                await API.Endpoints.delete(name);
            } catch (err) {
                console.error("Delete failed:", err);
                await this.refresh();
            }
        });

        this.table.appendChild(tr);}
};
