// js/api/endpoints.js

export function createLoginAPI(base) {
    return {
        login(username, password) {
            const payload = {
                username: username,
                password: password
            }
            return fetch(`${base}/authentication/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            }).then(r => r.json());
        },

        register(username, password) {
            const payload = {
                username: username,
                password: password
            }
            return fetch(`${base}/authentication/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            }).then(r => r.json());
        },

        authme() {
            return fetch(`${base}/authentication/me`, {
                method: "GET"
            }).then(r => r.json());
        },

        logout() {
            return fetch(`${base}/authentication/logout`, {
                method: "POST"
            }).then(r => r.json());
        },
    };
}
