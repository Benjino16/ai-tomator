import { api } from "./client";
import type { Batch } from "../types/Batch";



export const BatchesAPI = {
    getAll: (): Promise<Batch[]> => api.get("/batches/").then(r => r.data),
    getById: (id: number): Promise<Batch> => api.get(`/batches/${id}`).then(r => r.data),
    create: (payload: Partial<Batch>): Promise<Batch> => api.post("/batches/start", payload).then(r => r.data),
    stop: (id: number): Promise<Batch> => api.post(`/batches/stop/${id}`).then(r => r.data),
};
