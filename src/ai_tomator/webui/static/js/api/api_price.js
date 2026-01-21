// js/api/endpoints.js

export function createPriceAPI(base) {
    return {
        calculatePrice(data) {
            return fetch(`${base}/price/calculate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            }).then(r => r.json());
        }
    };
}
