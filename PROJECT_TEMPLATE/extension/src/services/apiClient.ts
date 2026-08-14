import axios, { AxiosInstance, AxiosError } from 'axios';
import * as vscode from 'vscode';

export interface AnalysisResult {
  project: any;
  report: any;
}

export interface ChatResponse {
  assistantResponse: string;
  references: string[];
  confidence: string;
}

export interface ProviderInfo {
  requiresKey: boolean;
  models: string[];
  description: string;
  configured: boolean;
}

export interface TestConnectionResult {
  success: boolean;
  message: string;
  provider?: string;
  model?: string;
  error?: string;
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

const SECRET_KEY_PREFIX = 'llmTrainingAgent.apiKey.';

export class ApiClient {
  private client: AxiosInstance;
  private getDynamicBaseUrl?: () => string;
  private context: vscode.ExtensionContext | undefined;

  constructor(
    private baseUrl: string,
    getDynamicBaseUrl?: () => string,
    context?: vscode.ExtensionContext
  ) {
    this.getDynamicBaseUrl = getDynamicBaseUrl;
    this.context = context;
    this.client = axios.create({
      baseURL: baseUrl,
      timeout: 120000,
    });

    if (getDynamicBaseUrl) {
      this.client.interceptors.request.use((config) => {
        config.baseURL = getDynamicBaseUrl();
        return config;
      });
    }

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.code === 'ECONNREFUSED') {
          throw new ApiError(
            'Could not connect to the backend. The Python backend may not be running. ' +
            'Try reloading the VS Code window, or start it manually: ' +
            'cd backend && python -m uvicorn main:app --port 8000',
            0,
            { reason: 'connection_refused' }
          );
        }
        if (error.response) {
          const data = error.response.data as Record<string, any> | undefined;
          const apiError = data as { detail?: any; message?: string; errorCode?: string } | undefined;
          let message: string;
          if (apiError?.detail) {
            message = typeof apiError.detail === 'object' ? JSON.stringify(apiError.detail) : String(apiError.detail);
          } else if (apiError?.message) {
            message = String(apiError.message);
          } else {
            message = error.message;
          }
          throw new ApiError(message, error.response.status, data);
        } else if (error.request) {
          throw new ApiError(
            'No response from backend — the backend may still be starting. ' +
            'Check the Output panel (LLM Training Agent: Backend) for details.',
            0,
            { reason: 'network' }
          );
        } else {
          throw new ApiError(error.message, 0, { reason: 'client' });
        }
      }
    );
  }

  // ------------------------------------------------------------------
  // SecretStorage-backed API-key helpers
  // ------------------------------------------------------------------

  private getSecretStorage(): vscode.SecretStorage | undefined {
    return this.context?.secrets;
  }

  private getSecretKey(provider: string): string {
    return `${SECRET_KEY_PREFIX}${provider}`;
  }

  /**
   * Retrieve a stored API key for *provider* from VS Code SecretStorage.
   * Never logs or returns the key to the user interface directly.
   */
  async getApiKey(provider: string): Promise<string | undefined> {
    try {
      const secretStore = this.getSecretStorage();
      if (!secretStore) return undefined;
      const secret = await secretStore.get(this.getSecretKey(provider));
      return secret ?? undefined;
    } catch {
      return undefined;
    }
  }

  /**
   * Store an API key for *provider* in VS Code SecretStorage.
   */
  async setApiKey(provider: string, apiKey: string): Promise<void> {
    const secretStore = this.getSecretStorage();
    if (!secretStore) {
      throw new ApiError('VS Code SecretStorage is not available.', 0);
    }
    await secretStore.store(this.getSecretKey(provider), apiKey);
  }

  /**
   * Remove a stored API key for *provider* from VS Code SecretStorage.
   */
  async removeApiKey(provider: string): Promise<void> {
    const secretStore = this.getSecretStorage();
    if (!secretStore) {
      throw new ApiError('VS Code SecretStorage is not available.', 0);
    }
    await secretStore.delete(this.getSecretKey(provider));
  }

  // ------------------------------------------------------------------
  // API methods
  // ------------------------------------------------------------------

  async healthCheck(): Promise<{ status: string; version: string }> {
    const response = await this.client.get('/api/v1/health');
    return response.data;
  }

  async analyzeProject(projectPath: string): Promise<AnalysisResult> {
    if (!projectPath || !projectPath.trim()) {
      throw new ApiError('No project/workspace is currently open. Please open a folder first.', 0);
    }
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

  async listProviders(): Promise<{ providers: Record<string, ProviderInfo> }> {
    const response = await this.client.get('/api/v1/providers');
    return response.data;
  }

  async getProviderModels(provider: string): Promise<{ provider: string; models: string[]; error?: string }> {
    const response = await this.client.get('/api/v1/provider/models', {
      params: { provider },
    });
    return response.data;
  }

  async selectProvider(provider: string, model: string): Promise<any> {
    const response = await this.client.post('/api/v1/provider/select', {
      provider,
      model,
    });
    return response.data;
  }

  async testConnection(config: {
    provider: string;
    model?: string;
    apiKey?: string;
    baseUrl?: string;
  }): Promise<TestConnectionResult> {
    const response = await this.client.post('/api/v1/provider/test', config);
    return response.data as TestConnectionResult;
  }

  async removeApiKeyBackend(provider: string): Promise<any> {
    const response = await this.client.delete('/api/v1/config/key', {
      params: { provider },
    });
    return response.data;
  }
}