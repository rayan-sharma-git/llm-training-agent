"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ApiClient = exports.ApiError = void 0;
const axios_1 = __importDefault(require("axios"));
class ApiError extends Error {
    constructor(message, statusCode, details) {
        super(message);
        this.statusCode = statusCode;
        this.details = details;
        this.name = 'ApiError';
    }
}
exports.ApiError = ApiError;
class ApiClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
        this.client = axios_1.default.create({
            baseURL: baseUrl,
            timeout: 120000,
        });
        this.client.interceptors.response.use((response) => response, (error) => {
            if (error.response) {
                const data = error.response.data;
                const message = typeof data === 'object' && data && 'detail' in data
                    ? String(data.detail)
                    : typeof data === 'object' && data && 'message' in data
                        ? String(data.message)
                        : error.message;
                throw new ApiError(message, error.response.status, data);
            }
            else if (error.request) {
                throw new ApiError('No response from backend', 0, { reason: 'network' });
            }
            else {
                throw new ApiError(error.message, 0, { reason: 'client' });
            }
        });
    }
    async healthCheck() {
        const response = await this.client.get('/api/v1/health');
        return response.data;
    }
    async analyzeProject(projectPath) {
        const response = await this.client.post('/api/v1/project/analyze', {
            projectPath,
        });
        return response.data;
    }
    async analyzeDataset(datasetPath) {
        const response = await this.client.post('/api/v1/dataset/analyze', {
            datasetPath,
        });
        return response.data;
    }
    async sendChatMessage(message) {
        const response = await this.client.post('/api/v1/chat/message', {
            message,
        });
        return response.data;
    }
    async getReport() {
        const response = await this.client.get('/api/v1/report');
        return response.data;
    }
    async getRecommendations() {
        const response = await this.client.get('/api/v1/recommendations');
        return response.data;
    }
    async getConfig() {
        const response = await this.client.get('/api/v1/config');
        return response.data;
    }
    async updateConfig(config) {
        const response = await this.client.put('/api/v1/config', config);
        return response.data;
    }
    async listProviders() {
        const response = await this.client.get('/api/v1/providers');
        return response.data;
    }
}
exports.ApiClient = ApiClient;
