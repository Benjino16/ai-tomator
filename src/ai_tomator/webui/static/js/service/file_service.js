import { createCachedService } from './cache_factory.js';

export function createFilesService(api) {
    return createCachedService({
        list: api.Files.list,
        delete: api.Files.delete,
        cacheKey: 'files',
        extra: {
            getByTag: (cache, tag) => cache.filter(r => Array.isArray(r.tags) && r.tags.includes(tag)),
            getStrListByTag: (cache, tag) => {
                const list = cache.filter(r => Array.isArray(r.tags) && r.tags.includes(tag));
                return list.flatMap(r => r.storage_name);
            },
            getTags: (cache) => [...new Set(cache.flatMap(r => r.tags))]
        }
    });
}
