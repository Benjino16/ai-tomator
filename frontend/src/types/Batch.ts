export interface Batch {
    id: number;
    name: string;
    status: "RUNNING" | "FAILED" | "COMPLETED";
    prompt: string;
    prompt_id: number;
    endpoint: string;
    files: string[];
    file_reader: string;
    model: string;
    temperature: number;
    delay: number;
    created_at: string;
    updated_at: string;
    started_at?: string;
    stopped_at?: string;
}