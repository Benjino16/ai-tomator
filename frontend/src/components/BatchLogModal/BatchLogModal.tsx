import styles from "./BatchLogModal.module.css";
import { ACTIVE_STATUSES, type Batch } from "../../types/Batch.ts";
import { Modal } from "../Modal/Modal.tsx";
import { useEffect, useState } from "react";
import { BatchesAPI } from "../../api/batches.ts";
import type { BatchLogEntry } from "../../types/BatchLogEntry.ts";

type Props = {
    isOpen: boolean;
    onClose: () => void;
    batch: Batch;
};

function formatTimestamp(isoString: string): string {
    const date = new Date(isoString);
    const pad = (n: number) => String(n).padStart(2, "0");
    return (
        `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ` +
        `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
    );
}

export function BatchLogModal({ isOpen, onClose, batch }: Props) {
    const [batchLog, setBatchLog] = useState<BatchLogEntry[]>();
    const [fetchError, setFetchError] = useState<string>();

    const fetchLog = (id: number) =>
        BatchesAPI.getLogEntries(id)
            .then((entries) => {
                setFetchError(undefined);
                setBatchLog(entries);
            })
            .catch((err: unknown) => {
                setFetchError(err instanceof Error ? err.message : String(err));
            });

    useEffect(() => {
        fetchLog(batch.id);

        if (!ACTIVE_STATUSES.includes(batch.status)) return;

        const interval = setInterval(() => fetchLog(batch.id), 5000);

        return () => clearInterval(interval);
    }, [batch.id, batch.status]);

    return (
        <Modal isOpen={isOpen} onClose={onClose}>
            <div className={styles.container}>
                <h3 className={styles.title}>
                    <span className={styles.titleLabel}>Batch Log</span>
                    <span className={styles.titleName}>{batch.name}</span>
                </h3>
                {fetchError && (
                    <p className={styles.fetchError}>
                        fetching log error: {fetchError}
                    </p>
                )}
                <div className={styles.logContainer}>
                    {batchLog?.length === 0 && (
                        <p className={styles.empty}>Keine Einträge vorhanden.</p>
                    )}
                    {batchLog?.map((logEntry: BatchLogEntry) => (
                        <div
                            key={logEntry.id}
                            className={`${styles.logRow} ${styles[`level_${logEntry.level}`]}`}
                        >
                            <span className={styles.timestamp}>
                                {formatTimestamp(logEntry.created_at)}
                            </span>
                            <span className={styles.level}>{logEntry.level}</span>
                            <span className={styles.message}>{logEntry.message}</span>
                        </div>
                    ))}
                </div>
            </div>
        </Modal>
    );
}