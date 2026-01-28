import { useEffect, useState } from "react";
import { PromptsAPI } from "../../api/prompts.ts";
import { type Prompt } from "../../types/Prompt.ts"
import { Button } from "../../components/Button/Button";
import { AddPromptModal } from "../../components/AddPromptModal/AddPromptModal";
import styles from "./PromptsPage.module.css";

export default function PromptsPage() {
    const [prompts, setPrompts] = useState<Prompt[]>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);

    useEffect(() => {
        PromptsAPI.getAll().then(setPrompts);
    }, []);

    function handleDeletePrompt(prompt_id: number): void {
        PromptsAPI.delete(prompt_id).then(() => {
            setPrompts(prev => prev.filter(prompt => prompt.id !== prompt_id));
        });
    }

    return (
        <section>
            <h2>Prompts</h2>
            <table>
                <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Content</th>
                    <th>Action</th>
                </tr>
                </thead>
                <tbody>
                {prompts.map((prompt) => (
                    <tr key={prompt.id}>
                        <td>{prompt.id}</td>
                        <td>{prompt.name}</td>
                        <td>
                            <div className={styles.promptPreview}>{prompt.content}</div>
                        </td>
                        <td>
                            <button onClick={() => handleDeletePrompt(prompt.id)}>Del</button>
                        </td>
                    </tr>
                ))}
                </tbody>
            </table>
            <div style={{ textAlign: "center", marginTop: "1rem" }}>
                <Button
                    text="Add Prompt"
                    onClick={() => setIsModalOpen(true)}
                />
            </div>

            <AddPromptModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onCreated={(newPrompt: Prompt) =>
                    setPrompts(prev => [...prev, newPrompt])
                }
            />
        </section>
    );
}
