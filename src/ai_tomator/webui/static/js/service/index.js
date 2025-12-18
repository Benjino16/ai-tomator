import { createFilesService } from "./file_service.js";
import { createBatchService } from "./batch_service.js";
import { createEndpointService } from "./endpoint_service.js";
import {createPromptService} from "./prompt_service.js";
import { API } from "../api/index.js";

export const Service = {
    Files: createFilesService(API),
    Batches: createBatchService(API),
    Endpoints: createEndpointService(API),
    Prompts: createPromptService(API)
};
