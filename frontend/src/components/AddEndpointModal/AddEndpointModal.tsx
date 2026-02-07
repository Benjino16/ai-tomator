import { useState } from "react";
import { Modal } from "../Modal/Modal.tsx";
import { EndpointsAPI } from "../../api/endpoints.ts";
import type { Endpoint } from "../../types/Endpoint.ts";


type Props = {
    isOpen: boolean;
    onClose: () => void;
    onCreated: (endpoint: Endpoint) => void;
};

export function AddEndpointModal({ isOpen, onClose, onCreated }: Props) {
    const [name, setName] = useState("");
    const [client, setClient] = useState("test");
    const [baseUrl, setBaseUrl] = useState("");
    const [token, setToken] = useState("");



    function handleSubmit(e: React.FormEvent) {
        e.preventDefault();

        const payload: Record<string, string> = {
            name: name,
            engine: client,
        };
        if (baseUrl) payload.url = baseUrl;
        if (token) payload.token = token;

        EndpointsAPI.create(payload)
            .then((data) => {
                onCreated(data);
                console.log(data);
            }).catch((err) => {
                console.log(err);
                alert(err);
            });
        onClose();
    }


    return (
        <Modal isOpen={isOpen} onClose={onClose}>
            <h3>Add Endpoint</h3>

            <form onSubmit={handleSubmit} className="styles.promptForm">
                <input
                    type="text"
                    placeholder="Name"
                    required
                    minLength={3}
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                />
                <select
                    required
                    value={client}
                    onChange={(e) => setClient(e.target.value)}
                >
                    <option value="openai">OpenAI</option>
                    <option value="gemini">Gemini</option>
                    <option value="ollama">Ollama</option>
                    <option value="test">Test-Client</option>
                </select>
                <input
                    type="url"
                    placeholder="Base URL"
                    minLength={3}
                    value={baseUrl}
                    onChange={(e) => setBaseUrl(e.target.value)}
                />
                <input
                    type="text"
                    placeholder="API-Token"
                    minLength={3}
                    value={token}
                    onChange={(e) => setToken(e.target.value)}
                />


                <button type="submit">Add</button>
            </form>
        </Modal>
    );
}
