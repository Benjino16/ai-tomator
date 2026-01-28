import { useEffect, useState } from "react";
import { BatchesAPI } from "../../api/batches.ts";
import { type Batch } from "../../types/Batch.ts"
import {Button} from "../../components/Button/Button.tsx";
import {StartBatchModal} from "../../components/StartBatchModal/StartBatchModal.tsx";


export default function BatchesPage() {
    const [batches, setBatches] = useState<Batch[]>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);

    useEffect(() => {
        BatchesAPI.getAll().then(setBatches);
    }, []);

    return (
        <section>
            <h2>Batch Run</h2>
            <table>
                <thead>
                <tr>
                    <th>ID</th>
                    <th>Status</th>
                    <th>Model</th>
                    <th>Temperature</th>
                    <th>Endpoint</th>
                    <th>File Reader</th>
                </tr>
                </thead>
                <tbody>
                {batches.map((batch) => (
                    <tr key={batch.id}>
                        <td>{batch.id}</td>
                        <td>{batch.status}</td>
                        <td>{batch.model}</td>
                        <td>{batch.temperature}</td>
                        <td>{batch.endpoint}</td>
                        <td>{batch.file_reader}</td>
                    </tr>
                ))}
                </tbody>
            </table>
            <div style={{ textAlign: "center", marginTop: "1rem" }}>
                <Button
                    text="Start Batch"
                    onClick={() => setIsModalOpen(true)}
                />
            </div>

            <StartBatchModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onCreated={(newBatch: Batch) => {
                    setBatches(prev => [...prev, newBatch]);
                    console.log(newBatch);
                    }
                }
            />
        </section>
    );
}