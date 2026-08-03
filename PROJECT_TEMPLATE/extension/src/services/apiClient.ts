import axios, { AxiosInstance, AxiosError } from 'axios';

export interface AnalysisResult {
  project: any;
  report: any;
}

export interface ChatResponse {
  assistantResponse: string;
  references: string[];
  confidence: string;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export class ApiClient {
  private client: AxiosInstance;
  
  constructor(private baseUrl: string) {
    this.client = axios.create({
      baseURL: baseUrl,
      timeout: 120000,
    });

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response) {
          const data = error.response.data as Record<string, any> | undefined;
          const message = typeof data === 'object' && data && 'detail' in data
            ? String((data as any).detail)
            : typeof data === 'object' && data && 'message' in data
              ? String((data as any).message)
              : error.message;
          throw new ApiError(message, error.response.status, data);
        } else if (error.request) {
          throw new ApiError('No response from backend', 0, { reason: 'network' });
        } else {
          throw new ApiError(error.message, 0, { reason: 'client' });
        }
      }
    );
  }
  
  async healthCheck(): Promise<{ status: string; version: string }> {
    const response = await this.client.get('/api/v1/health');
    return response.data;
  }
  
  async analyzeProject(projectPath: string): Promise<AnalysisResult> {
    const response = await this.client.post('/api/v1/project/analyze', {
      projectPath,
    });
    return response.data as AnalysisResult;
  }
  
  async analyzeDataset(datasetPath: string): Promise<any> {
    const response = await this.client.post('/api/v1/dataset/analyze', {
      datasetPath,
    });
    return response.data;
  }
  
  async sendChatMessage(message: string): Promise<ChatResponse> {
    const response = await this.client.post('/api/v1/chat/message', {
      message,
    });
    return response.data as ChatResponse;
  }
  
  async getReport(): Promise<any> {
    const response = await this.client.get('/api/v1/report');
    return response.data;
  }
  
  async getRecommendations(): Promise<{ recommendations: any[] }> {
    const response = await this.client.get('/api/v1/recommendations');
    return response.data;
  }
  
  async getConfig(): Promise<{ default_provider: string }> {
    const response = await this.client.get('/api/v1/config');
    return response.data;
  }
  
  async updateConfig(config: Record<string, any>): Promise<any> {
    const response = await this.client.put('/api/v1/config', config);
    return response.data;
  }
  
  async listProviders(): Promise<{ providers: string[] }> {
    const response = await this.client.get('/api/v1/providers');
    return response.data;
  }
}
