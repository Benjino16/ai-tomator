import { createCachedService } from './cache_factory.js';

export function createPromptService(api) {
    return createCachedService({
        list: api.Prompts.list,
        add: api.Prompts.add,
        delete: api.Prompts.delete,
        cacheKey: 'prompts',
    });
}
