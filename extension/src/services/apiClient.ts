import axios, { AxiosInstance } from 'axios';

export interface AnalysisResult {
  project: any;
  report: any;
}

export interface ChatResponse {
  assistantResponse: string;
  references: string[];
  confidence: string;
}

export class ApiClient {
  private client: AxiosInstance;
  
  constructor(private baseUrl: string) {
    this.client = axios.create({
      baseURL: baseUrl,
      timeout: 120000,
    });
  }
  
  async healthCheck() {
    const response = await this.client.get('/api/v1/health');
    return response.data;
  }
  
  async analyzeProject(projectPath: string): Promise<AnalysisResult> {
    const response = await this.client.post('/api/v1/project/analyze', {
      projectPath,
    });
    return response.data;
  }
  
  async sendChatMessage(message: string): Promise<ChatResponse> {
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
  
  async updateConfig(config: Record<string, any>) {
    const response = await this.client.put('/api/v1/config', config);
    return response.data;
  }
  
  async listProviders() {
    const response = await this.client.get('/api/v1/providers');
    return response.data;
  }
}