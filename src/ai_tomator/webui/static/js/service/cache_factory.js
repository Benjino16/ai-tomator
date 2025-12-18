// cache_factory.js
// einfacher Memory-Cache für späteren Austausch
const memoryCache = {
    get: (key) => memoryCache.store?.[key] ?? null,
    set: (key, value) => { memoryCache.store = memoryCache.store || {}; memoryCache.store[key] = value; },
    clear: (key) => { if (memoryCache.store) delete memoryCache.store[key]; },
    store: {}
};

/**
 * Generic cached service factory
 * @param {Object} options
 * @param {Function} options.list - Pflicht: Funktion, die alle Items abruft
 * @param {Function} [options.get] - Optional: Funktion, um einzelnes Item zu laden
 * @param {Function} [options.add] - Optional: Funktion, um Item hinzuzufügen
 * @param {Function} [options.delete] - Optional: Funktion, um Item zu löschen
 * @param {Function} [options.extra] - Optional: zusätzliche Hilfsfunktionen (cache-basiert)
 * @param {string} options.cacheKey - Speicher-Key im Cache
 * @param {Object} [options.storage] - Cache-Backend, Default memoryCache
 */
export function createCachedService({ list, get, add, delete: remove, extra, cacheKey, storage = memoryCache }) {
    let refreshPromise = null;

    async function refresh() {
        try {
            const data = await list();
            storage.set(cacheKey, data);
            return data;
        } catch (e) {
            console.error(`${cacheKey} Service refresh failed`, e);
            throw e;
        }
    }

    async function ensureCache() {
        let cached = storage.get(cacheKey);
        if (cached) return cached;
        if (!refreshPromise) {
            refreshPromise = refresh().finally(() => { refreshPromise = null; });
        }
        return refreshPromise;
    }

    const service = {
        getAll: async () => await ensureCache(),
        refresh
    };

    if (get) {
        service.getById = async (id) => {
            const cache = await ensureCache();
            const cachedItem = cache.find(r => String(r.id) === String(id));
            if (cachedItem) return cachedItem;
            return await get(id);
        };
    }

    if (add) {
        service.add = async (data) => {
            const result = await add(data);
            await refresh();
            return result;
        };
    }

    if (remove) {
        service.delete = async (id) => {
            const result = await remove(id);
            await refresh();
            return result;
        };
    }

    if (extra) {
        for (const [name, fn] of Object.entries(extra)) {
            service[name] = async (...args) => {
                const cache = await ensureCache();
                return fn(cache, ...args);
            };
        }
    }

    return service;
}
