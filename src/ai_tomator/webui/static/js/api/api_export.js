export function createExportAPI(base) {
    return {
        async batches(mode, batch_ids) {
            const url = new URL(`${base}/export/batches/`, window.location.origin);
            url.searchParams.set("mode", mode);

            batch_ids.forEach(id => url.searchParams.append("batch_ids", id));

            const res = await fetch(url, { method: "GET" });
            if (!res.ok) throw new Error("Request failed");

            return await res.blob();
        },
    };
}
