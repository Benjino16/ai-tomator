export function createPipelineAPI(base) {
    return {
        listFileReaders() {
            return fetch(`${base}/pipeline/file_readers`)
                .then(r => r.json());
        },

        listEngines() {
            return fetch(`${base}/pipeline/engines`)
                .then(r => r.json());
        },
    };
}
