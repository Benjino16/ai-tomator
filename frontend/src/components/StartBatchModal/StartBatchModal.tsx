import { useState, useEffect } from "react";
import { Modal } from "../Modal/Modal.tsx";
import { BatchesAPI } from "../../api/batches.ts";
import { EndpointsAPI } from "../../api/endpoints.ts";
import { PipelineAPI } from "../../api/pipeline.ts";
import { FilesAPI } from "../../api/files.ts";
import { PromptsAPI } from "../../api/prompts.ts";
import type { Prompt } from "../../types/Prompt.ts";
import type { Batch } from "../../types/Batch.ts";
import styles from "./StartBatchModal.module.css"


type Props = {
    isOpen: boolean;
    onClose: () => void;
    onCreated: (batch: Batch) => void;
};

export function StartBatchModal({ isOpen, onClose, onCreated }: Props) {
    const [endpoint, setEndpoint] = useState("");
    const [endpoints, setEndpoints] = useState<string[]>([]);
    const [loadingEndpoints, setLoadingEndpoints] = useState(false);

    const [fileTag, setFileTag] = useState("");
    const [fileTags, setFileTags] = useState<string[]>([]);
    const [loadingFileTags, setLoadingFileTags] = useState(false);

    const [fileReader, setFileReader] = useState("");
    const [fileReaders, setFileReaders] = useState<string[]>([]);
    const [loadingFileReaders, setLoadingFileReaders] = useState(false);

    const [model, setModel] = useState("");
    const [models, setModels] = useState<string[]>([]);
    const [loadingModels, setLoadingModels] = useState(false);

    const [promptId, setPromptId] = useState<number | null>(null);
    const [prompts, setPrompts] = useState<Prompt[]>([]);
    const [loadingPrompts, setLoadingPrompts] = useState(false);

    const [temperature, setTemperature] = useState<number>(1);
    const [delay, setDelay] = useState<number>(10);

    useEffect(() => {
        if (!endpoint) {
            setModels([]);
            setModel("");
            return;
        }

        const loadModels = async () => {
            setLoadingModels(true);
            try {
                const mdls = await EndpointsAPI.getModels(endpoint);
                setModels(mdls);
            } catch (err) {
                console.error(err);
                alert("Error loading models: " + err);
            } finally {
                setLoadingModels(false);
            }
        };

        loadModels();
    }, [endpoint]);


    useEffect(() => {
        if (!isOpen) return;

        const fetchData = async () => {
            setLoadingEndpoints(true);
            setLoadingFileTags(true);
            setLoadingFileReaders(true);
            setLoadingPrompts(true);

            try {
                const [eps, fTags, fReaders, prms] = await Promise.all([
                    EndpointsAPI.getAll(),
                    FilesAPI.getFileTags(),
                    PipelineAPI.getFileReaders(),

                    PromptsAPI.getAll(),
                ]);

                setEndpoints(eps.map(ep => ep.name));
                setFileTags(fTags);
                setFileReaders(fReaders);
                setPrompts(prms);
            } catch (err) {
                console.error(err);
                alert("Error while fetching data: " + err);
            } finally {
                setLoadingEndpoints(false);
                setLoadingFileTags(false);
                setLoadingFileReaders(false);
                setLoadingModels(false);
                setLoadingPrompts(false);
            }
        };

        fetchData();
    }, [isOpen]);




    function handleSubmit(e: React.FormEvent) {
        e.preventDefault();

        FilesAPI.getFilesByTag(fileTag).then(r => {
            let files = r.map(f => f.storage_name)

            if (promptId === null) {
                alert("Please select a prompt");
                return;
            }


            BatchesAPI.create({
                prompt_id: promptId,
                files: files,
                endpoint: endpoint,
                file_reader: fileReader,
                model: model,
                delay: delay,
                temperature: temperature,

            }).then((data) => {
                onCreated(data)
            }).catch(error => {
                console.error(error);
                alert(error.detail);
            })
        })



        onClose();
    }

    return (
        <Modal isOpen={isOpen} onClose={onClose}>
            <h3>Start Batch</h3>

            <form onSubmit={handleSubmit} className={styles.batchStartForm}>

                <label>Endpoint</label>
                <select
                    required
                    value={endpoint}
                    onChange={(e) => setEndpoint(e.target.value)}
                    disabled={loadingEndpoints}
                >
                    <option value="" disabled>
                        {loadingEndpoints ? "Loading..." : "Please select"}
                    </option>

                    {endpoints.map((ep) => (
                        <option key={ep} value={ep}>
                            {ep}
                        </option>
                    ))}
                </select>

                <label>File-Tag</label>
                <select
                    required
                    value={fileTag}
                    onChange={(e) => setFileTag(e.target.value)}
                >
                    <option value="" disabled>
                        {loadingFileTags ? "Loading..." : "Please select"}
                    </option>

                    {fileTags.map((ft) => (
                        <option key={ft} value={ft}>
                            {ft}
                        </option>
                    ))}
                </select>

                <label>File Reader</label>
                <select
                    required
                    value={fileReader}
                    onChange={(e) => setFileReader(e.target.value)}

                >
                    <option value="" disabled>
                        {loadingFileReaders ? "Loading..." : "Please select"}
                    </option>

                    {fileReaders.map((fr) => (
                        <option key={fr} value={fr}>
                            {fr}
                        </option>
                    ))}
                </select>

                <label>Model</label>
                <select
                    required
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    disabled={!endpoint || loadingModels}
                >
                    <option value="" disabled>
                        {!endpoint
                            ? "Select endpoint first"
                            : loadingModels
                                ? "Loading..."
                                : "Please select"}
                    </option>

                    {models.map((md) => (
                        <option key={md} value={md}>
                            {md}
                        </option>
                    ))}
                </select>

                <label>Prompt</label>
                <select
                    required
                    value={promptId ?? ""}
                    onChange={(e) => setPromptId(parseInt(e.target.value))}
                >
                    <option value="" disabled>
                        {loadingPrompts ? "Loading..." : "Please select"}
                    </option>

                    {prompts.map((pr) => (
                        <option key={pr.id} value={pr.id}>
                            {pr.name}
                        </option>
                    ))}
                </select>

                <label>Temperature</label>
                <input
                    id="temperature-input"
                    placeholder="Temperature"
                    required
                    type="number"
                    value={temperature} min="0.0" max="3.0"
                    step="0.1"
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                />

                <label>API Request Delay</label>
                <input
                    placeholder="(seconds)"
                    required
                    type="number"
                    min="0" max="360" value={delay}
                    onChange={(e) => setDelay(parseInt(e.target.value))}
                />

                <button type="submit">Start</button>
            </form>
        </Modal>
    );
}
