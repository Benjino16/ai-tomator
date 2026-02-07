import { useEffect, useState } from "react";
import { FilesAPI } from "../../api/files.ts";
import { type FileData } from "../../types/FileData.ts"
import {Button} from "../../components/Button/Button.tsx";
import {AddFileModal} from "../../components/AddFileModal/AddFileModal.tsx";

export default function FilesPage() {
    const [files, setFiles] = useState<FileData[]>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [modalKey, setModalKey] = useState(0);

    function loadFiles() {
        FilesAPI.getAll().then(setFiles);
    }

    useEffect(() => {
        loadFiles();
    }, []);


    function handleDeleteFile(filename: string): void {
        FilesAPI.delete(filename).then(() => {
            setFiles(prev => prev.filter(file => file.storage_name !== filename));
        });
    }

    return (
        <section>
            <h2>Files</h2>
            <table>
                <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Tags</th>
                    <th>Actions</th>
                </tr>
                </thead>
                <tbody>
                {files.map((file) => (
                    <tr key={file.storage_name}>
                        <td>{file.storage_name}</td>
                        <td>{file.display_name}</td>
                        <td>{file.tags}</td>
                        <td>
                            <button onClick={() => handleDeleteFile(file.storage_name)}>Del</button>
                        </td>
                    </tr>
                ))}
                </tbody>
            </table>
            <div style={{textAlign: "center", marginTop: "1rem"}}>
                <Button
                    text="Upload Files"
                    onClick={() =>
                    {
                        setModalKey(prev => prev + 1)
                        setIsModalOpen(true);
                    }}
                />
            </div>
            <AddFileModal
                key={modalKey}
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onUploaded={
                (success) => {
                    console.log(success)
                    loadFiles();
                }
            }
            />
        </section>
    );
}