import { createFilesService } from "./file_service.js";
import { API } from "../api/index.js";

export const Service = {
    Files: createFilesService(API),
};
