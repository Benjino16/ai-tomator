import { createCachedService } from './cache_factory.js';

export function createBatchService(api) {
    return createCachedService({
        list: api.Batches.list,
        get: api.Batches.get,
        add: api.Batches.start,
        delete: api.Batches.stop,
        cacheKey: 'batches',
        extra: {
            getFileStatus: async (cache, batch_id) => api.Batches.get_files(batch_id),
            getLogs: async (cache, batch_id) => api.Batches.get_logs(batch_id),
        }
    });
}
