import { api } from "./client";
import type { Endpoint } from "../types/Endpoint";



export const EndpointsAPI = {
    getAll: (): Promise<Endpoint[]> => api.get("/endpoints/").then(r => r.data),
    create: (payload: Partial<Endpoint>): Promise<Endpoint> => api.post("/endpoints/add", payload).then(r => r.data),
    delete: (name: string): Promise<Endpoint> => api.delete(`/endpoints/delete/${name}`).then(r => r.data),
    getModels: (endpoint_name: string): Promise<string[]> => api.get(`/endpoints/models/${endpoint_name}`).then(r => r.data),
};
