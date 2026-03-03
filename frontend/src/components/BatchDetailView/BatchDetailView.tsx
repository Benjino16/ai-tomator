import { type BatchFile } from "../../types/BatchFile.ts";
import styles from "./BatchDetailView.module.css";

interface BatchDetailViewProps {
    files: BatchFile[];
}

export function BatchDetailView({ files }: BatchDetailViewProps) {
    const getStatusStyle = (status: BatchFile["status"]) => {
        switch (status) {
            case "COMPLETED":
                return { backgroundColor: "#e6f7e6", symbol: "✓" };
            case "FAILED":
                return { backgroundColor: "#ffe6e6", symbol: "✗" };
            case "RUNNING":
                return { backgroundColor: "#e6f0ff", symbol: "→" };
            case "QUEUED":
            default:
                return { backgroundColor: "#f5f5f5", symbol: "•" };
        }
    };

    return (
        <div className={styles.batchDetails}>
            <h4>Batch Files:</h4>
            <div className={styles.batchFilesList}>
                {files.map((file) => {
                    const { backgroundColor, symbol } = getStatusStyle(file.status);
                    return (
                        <div
                            key={file.id}
                            className={styles.batchFileItem}
                            style={{ backgroundColor }}
                        >
                            <div>{file.display_name}</div>
                            {file.costs_in_usd && <div>${file.costs_in_usd.toFixed(4)}</div>}
                            {file.seed && <div>{file.seed}</div>}
                            <div className={styles.statusContainer}>
                                <span>{file.status}</span>
                                <span className={styles.statusSymbol}>{symbol}</span>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
