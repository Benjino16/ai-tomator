import { useEffect, useState } from "react";
import { EndpointsAPI } from "../../api/endpoints.ts";
import { type Endpoint } from "../../types/Endpoint.ts"
import { Button } from "../../components/Button/Button";
import { AddEndpointModal } from "../../components/AddEndpointModal/AddEndpointModal.tsx";


export default function EndpointsPage() {
    const [endpoints, setEndpoints] = useState<Endpoint[]>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);

    useEffect(() => {
        EndpointsAPI.getAll().then(setEndpoints);
    }, []);

    function handleDeleteEndpoint(ep_name: string): void {
        EndpointsAPI.delete(ep_name).then(() => {
            setEndpoints(prev => prev.filter(ep => ep.name !== ep_name));
        });
    }

    return (
        <section>
            <h2>Endpoints</h2>
            <table>
                <thead>
                <tr>
                    <th>Name</th>
                    <th>Client</th>
                    <th>Base-URL</th>
                    <th>API-Token</th>
                    <th>Action</th>
                </tr>
                </thead>
                <tbody>
                {endpoints.map((ep) => (
                    <tr key={ep.name}>
                        <td>{ep.name}</td>
                        <td>{ep.engine}</td>
                        <td>{ep.url}</td>
                        <td>{ep.token}</td>
                        <td>
                            <button onClick={() => handleDeleteEndpoint(ep.name)}>Del</button>
                        </td>
                    </tr>
                ))}
                </tbody>
            </table>
            <div style={{ textAlign: "center", marginTop: "1rem" }}>
                <Button
                    text="Add Endpoint"
                    onClick={() => setIsModalOpen(true)}
                />
            </div>
            <AddEndpointModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onCreated={(newEndpoint: Endpoint) =>
                    setEndpoints(prev => [...prev, newEndpoint])
                }
            />
        </section>
    );
}
