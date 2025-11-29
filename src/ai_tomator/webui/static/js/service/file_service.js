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

    async function getByTag(tag) {
        await ensureCache();
        return cache.filter(r => Array.isArray(r.tags) && r.tags.includes(tag));
    }

    return {
        async getAll() {
            await ensureCache();
            return cache;
        },

        async getStrListByTag(tag) {
            const list = await getByTag(tag)
            return list.flatMap(r => r.storage_name);
        },

        async getTags() {
            await ensureCache();
            return [...new Set(cache.flatMap(r => r.tags))];
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

        refresh,
        getByTag
    };
}
