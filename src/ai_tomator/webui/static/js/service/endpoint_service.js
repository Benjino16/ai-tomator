export function createEndpointService(api) {
    let cache = null;

    async function refresh() {
        try {
            cache = await api.Endpoints.list();
        } catch (e) {
            console.error("EndpointService.refresh failed", e);
            throw e;
        }
    }
    async function ensureCache() {
        if (cache === null) {
            await refresh();
        }
    }

    return {
        async getAll() {
            await ensureCache();
            return cache;
        },

        async add(data) {
            try {
                const result = await api.Endpoints.add(data);
                await refresh();
                return result
            }
            catch (error) {
                console.error(error)
            }
        },
        async delete(endpoint_id) {
            try {
                const result = await api.Endpoints.delete(endpoint_id);
                await refresh();
                return result
            }
            catch (error) {
                console.error(error)
            }
        },

        refresh,
    };
}
