export function createFilesService(api) {
    let cache = null;

    async function refresh() {
        try {
            cache = await api.Files.list();
        } catch (e) {
            console.error("FilesService.refresh failed", e);
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

        async getByTag(tag) {
            await ensureCache();
            return cache.filter(r => r.tag === tag);
        },

        async getTags() {
            await ensureCache();
            return [...new Set(cache.map(r => r.tag))];
        },

        async delete(storage_name) {
            try {
                const result = await api.Files.delete(storage_name);
                await refresh();
                return result
            }
            catch (error) {
                console.error(error)
            }
        },

        refresh
    };
}
