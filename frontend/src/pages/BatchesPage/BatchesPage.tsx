import { useEffect, useState } from "react";
import { BatchesAPI } from "../../api/batches.ts";
import { type Batch } from "../../types/Batch.ts";
import { type BatchFile } from "../../types/BatchFile.ts";
import { Button } from "../../components/Button/Button.tsx";
import { StartBatchModal } from "../../components/StartBatchModal/StartBatchModal.tsx";
import { BatchStatusSymbol } from "../../components/BatchStatusSymbol/BatchStatusSymbol.tsx";
import { BatchTimer } from "../../components/BatchTimer/BatchTimer.tsx";
import { BatchDetailView } from "../../components/BatchDetailView/BatchDetailView.tsx";
import styles from "../../pages/BatchesPage/BatchesPage.module.css";

export default function BatchesPage() {
    const [batches, setBatches] = useState<Batch[]>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [expandedBatchId, setExpandedBatchId] = useState<number | null>(null);
    const [batchFiles, setBatchFiles] = useState<BatchFile[]>([]);

    useEffect(() => {
        BatchesAPI.getAll().then(setBatches);
    }, []);

    function handleStop(batch_id: number) {
        BatchesAPI.stop(batch_id).catch((err) => {
            alert(err);
            console.error(err);
        });
    }

    function toggleExpand(batch_id: number) {
        if (expandedBatchId === batch_id) {
            setExpandedBatchId(null);
            setBatchFiles([]);
        } else {
            setExpandedBatchId(batch_id);
            BatchesAPI.getBatchFilesById(batch_id).then(setBatchFiles);
        }
    }

    return (
        <section>
            <h2>Batch Run</h2>

            {/* Tabellen-Header */}
            <div className={styles.batchTableHeader}>
                <div className={styles.batchGrid}>
                    <div></div>
                    <div>ID</div>
                    <div>Status</div>
                    <div>Progress</div>
                    <div>Time</div>
                    <div>Costs</div>
                    <div>Model</div>
                    <div>Temp</div>
                    <div>Endpoint</div>
                    <div>File Reader</div>
                    <div>Action</div>
                </div>
            </div>

            <div className={styles.batchContainer}>
                {batches.map((batch) => (
                    <div key={batch.id} className={styles.batchRowWrapper}>

                        {/* Eine Tabellen-Zeile */}
                        <div
                            className={styles.batchRow}
                            onClick={() => toggleExpand(batch.id)}
                        >
                            <div className={styles.batchArrow}>
                                {expandedBatchId === batch.id ? "▼" : "▶"}
                            </div>

                            <div>{batch.id}</div>

                            <div>
                                <BatchStatusSymbol status={batch.status} />
                            </div>

                            <div>{batch.progress}</div>

                            <div>
                                {batch.started_at ? (
                                    <BatchTimer
                                        startTime={batch.started_at}
                                        stopTime={batch.stopped_at}
                                    />
                                ) : (
                                    "-"
                                )}
                            </div>

                            {batch.costs_in_usd && <div>${batch.costs_in_usd.toFixed(4)}</div>}

                            <div>{batch.model}</div>
                            <div>{batch.temperature}</div>
                            <div>{batch.endpoint}</div>
                            <div>{batch.file_reader}</div>

                            <div>
                                {batch.status === "RUNNING" ? (
                                    <button
                                        className={styles.logoutButton}
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            handleStop(batch.id);
                                        }}
                                    >
                                        Stop
                                    </button>
                                ) : (
                                    "-"
                                )}
                            </div>
                        </div>

                        {/* Expand-Area */}
                        {expandedBatchId === batch.id && (
                            <BatchDetailView files={batchFiles} />
                        )}

                    </div>
                ))}
            </div>

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
                }}
            />
        </section>
    );
}
