export function createPromptsAPI(base) {
    return {
        list() {
            return fetch(`${base}/prompts/`)
                .then(r => r.json());
        },

        add(data) {
            return fetch(`${base}/prompts/add`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            }).then(r => r.json());
        },

        get_content_by_id(id) {
            const prompts = this.list()
            return prompts.filter(r => r.id === id)[0]["prompt"];
        },

        delete(id) {
            return fetch(`${base}/prompts/delete/${id}/`, {
                method: "DELETE"
            }).then(r => r.json());
        }
    };
}
