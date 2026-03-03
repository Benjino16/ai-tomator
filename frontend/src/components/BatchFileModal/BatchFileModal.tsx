import { Modal } from "../Modal/Modal.tsx";
import type { BatchFile } from "../../types/BatchFile.ts";
import styles from "./BatchFileModal.module.css";

type Props = {
    isOpen: boolean;
    onClose: () => void;
    file: BatchFile;
};

export function BatchFileModal({ isOpen, onClose, file }: Props) {
    let content;
    try {
        const parsedOutput = JSON.parse(file.output);
        content = typeof parsedOutput === "string"
            ? parsedOutput
            : JSON.stringify(parsedOutput, null, 2);
    } catch {
        content = file.output;
    }

    return (
        <Modal isOpen={isOpen} onClose={onClose}>
            <h3>{file.display_name}</h3>
            <p>Kosten: {file.costs_in_usd} USD</p>
            <p>Output:</p>
            <div className={styles.fileOutput}>
                <pre>{content}</pre>
            </div>
        </Modal>
    );
}
