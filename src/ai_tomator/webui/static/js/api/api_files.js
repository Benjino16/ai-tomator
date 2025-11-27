export function createFilesAPI(base) {
    return {
        upload(file) {
            const formData = new FormData();
            formData.append("file", file);

            return fetch(`${base}/files/upload`, {
                method: "POST",
                body: formData
            }).then(r => r.json());
        },

        list() {
            return fetch(`${base}/files`).then(r => r.json());
        },

        delete(name) {
            return fetch(`${base}/files/delete/${name}`, {
                method: "DELETE"
            }).then(r => r.json());
        }
    };
}
