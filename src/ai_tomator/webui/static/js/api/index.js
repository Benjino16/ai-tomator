import { createFilesAPI } from "./api_files.js";
import { createEndpointsAPI } from "./api_endpoints.js";
import { createBatchesAPI } from "./api_batches.js";
import { createPipelineAPI } from "./api_pipeline.js";
import {createExportAPI} from "./api_export.js";
import {createPromptsAPI} from "./api_prompts.js";
import {createLoginAPI} from "./api_login.js";
import {createPriceAPI} from "./api_price.js";

export const API_BASE = "/api";

export const API = {
    Files: createFilesAPI(API_BASE),
    Endpoints: createEndpointsAPI(API_BASE),
    Batches: createBatchesAPI(API_BASE),
    Pipeline: createPipelineAPI(API_BASE),
    Export: createExportAPI(API_BASE),
    Prompts: createPromptsAPI(API_BASE),
    Login: createLoginAPI(API_BASE),
    Price: createPriceAPI(API_BASE),
};
