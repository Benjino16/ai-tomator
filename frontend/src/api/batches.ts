import { api } from "./client";
import type { Batch } from "../types/Batch";



export const BatchesAPI = {
    getAll: (): Promise<Batch[]> => api.get("/batches/").then(r => r.data),
    getById: (id: string): Promise<Batch> => api.get(`/batches/${id}`).then(r => r.data),
    create: (payload: Partial<Batch>): Promise<Batch> => api.post("/batches/start", payload).then(r => r.data),
};
