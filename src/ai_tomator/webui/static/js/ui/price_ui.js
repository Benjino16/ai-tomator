import {API} from "../api/index.js";
import {Service} from "../service/index.js";

export const PriceUI = {

    init() {
        this.providerSelect = document.getElementById("price-provider-select");
        this.modelInput = document.getElementById("price-model-input");
        this.fileTagSelect = document.getElementById("price-file-tag-select");
        this.fileReaderSelect = document.getElementById("price-file-reader-select");
        this.promptSelect = document.getElementById("price-prompt-select");
        this.exampleOutputInput = document.getElementById("price-example-output");

        this.priceResultHeader = document.getElementById("price-result-header");


        this.form = document.getElementById("priceForm");


        this.form.addEventListener("submit", async (e) => {
            e.preventDefault();

            if (!this.form.checkValidity()) {
                this.form.reportValidity();
                return;
            }

            const submitButton = this.form.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;

            submitButton.disabled = true;
            submitButton.textContent = "Loading…";

            try {
                let price = await this.priceCalculation();

                if (price > 0 && price < 0.01) {
                    price = 0.01;
                } else {
                    price = Math.round(price * 100) / 100;
                }

                this.priceResultHeader.textContent =
                    "Calculated Price: " + price.toFixed(2) + "$";
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            }
        });


        this.refresh();
    },

    async refresh() {
        const file_readers = await API.Pipeline.listFileReaders()
        const file_tags = await Service.Files.getTags()
        const prompts = await Service.Prompts.getAll()

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
        this.promptSelect.innerHTML = "<option value=\"\">Prompt auswählen (Optional)</option>";
        for (const prompt of prompts) {
            const option = document.createElement("option");
            option.value = prompt.prompt;
            option.textContent = prompt.name;
            this.promptSelect.appendChild(option);
        }
    },

    async priceCalculation() {
        const data = {
            provider: this.providerSelect.value,
            model: this.modelInput.value,
            file_reader: this.fileReaderSelect.value,
            file_ids: await Service.Files.getStrListByTag(this.fileTagSelect.value),
            prompt: this.promptSelect.value,
            output: this.exampleOutputInput.value,
        };

        return await API.Price.calculatePrice(data);
    },
};
