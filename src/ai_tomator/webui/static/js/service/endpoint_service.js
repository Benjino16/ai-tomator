import { createCachedService } from './cache_factory.js';

export function createEndpointService(api) {
    return createCachedService({
        list: api.Endpoints.list,
        add: api.Endpoints.add,
        delete: api.Endpoints.delete,
        cacheKey: 'endpoints'
    });
}
