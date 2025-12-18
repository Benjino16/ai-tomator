
export function createBatchService(api) {
    let cache = null;
    let refreshPromise = null;

    async function refresh() {
        try {
            console.log("Refreshing batch service...");
            const result = await api.Batches.list();
            cache = result;
            return result;
        } catch (e) {
            console.error("BatchService.refresh failed", e);
            throw e;
        }
    }

    async function ensureCache() {
        if (cache !== null) {
            return cache;
        }
        if (!refreshPromise) {
            refreshPromise = refresh().finally(() => {
                refreshPromise = null;
            });
        }
        return refreshPromise;
    }



    return {
        async getAll() {
            await ensureCache();
            return cache;
        },

        async getById(batch_id) {
            await ensureCache();
            const cachedBatch = cache.find(r => String(r.id) === String(batch_id));
            if(!cachedBatch) {
                return await api.Batches.get(batch_id);
            }
            console.log("Cached batch found for batch_id", batch_id);
            return cachedBatch;
        },

        async getFileStatus(batch_id) {
            return await api.Batches.get_files(batch_id);
            //todo: cache the output
        },

        async getLogs(batch_id) {
            return await api.Batches.get_logs(batch_id);
            //todo: cache the output
        },

        async start(data) {
            try {
                const result = await api.Batches.start(data);
                await refresh();
                return result
            }
            catch (error) {
                console.error(error)
            }
        },

        async stop(batch_id) {
            try {
                const result = await api.Batches.stop(batch_id);
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
