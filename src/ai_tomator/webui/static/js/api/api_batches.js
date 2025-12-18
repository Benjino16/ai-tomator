// js/api/runs.js

export function createBatchesAPI(base) {
    return {
        start(data) {
            return fetch(`${base}/batches/start/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            }).then(r => r.json());
        },

        list() {
            return fetch(`${base}/batches/`)
                .then(r => r.json());
        },

        get(batcheId) {
            return fetch(`${base}/batches/${batcheId}/`)
                .then(r => r.json());
        },
        get_files(batcheId) {
            return fetch(`${base}/batches/files/${batcheId}/`)
                .then(r => r.json());
        },
        get_logs(batcheId) {
            return fetch(`${base}/batches/log/${batcheId}/`)
                .then(r => r.json());
        },

        stop(name) {
            return fetch(`${base}/batches/stop/${name}/`, {
                method: "POST"
            }).then(r => r.json());
        }
    };
}
