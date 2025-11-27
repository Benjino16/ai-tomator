// js/api/endpoints.js

export function createEndpointsAPI(base) {
    return {
        list() {
            return fetch(`${base}/endpoints`)
                .then(r => r.json());
        },

        add(data) {
            return fetch(`${base}/endpoints/add`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            }).then(r => r.json());
        },

        delete(name) {
            return fetch(`${base}/endpoints/delete/${name}`, {
                method: "DELETE"
            }).then(r => r.json());
        }
    };
}
