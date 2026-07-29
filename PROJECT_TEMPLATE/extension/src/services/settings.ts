import * as vscode from 'vscode';

export interface Settings {
  backendUrl: string;
  provider: string;
  model: string;
}

export class SettingsManager {
  private context: vscode.ExtensionContext;
  
  constructor(context: vscode.ExtensionContext) {
    this.context = context;
    this.initializeDefaults();
  }
  
  private initializeDefaults() {
    const config = vscode.workspace.getConfiguration('llmTrainingAgent');
    if (!config.has('backendUrl')) {
      config.update('backendUrl', 'http://127.0.0.1:8000', vscode.ConfigurationTarget.Global);
    }
    if (!config.has('provider')) {
      config.update('provider', 'ollama', vscode.ConfigurationTarget.Global);
    }
    if (!config.has('model')) {
      config.update('model', 'llama3.2', vscode.ConfigurationTarget.Global);
    }
  }
  
  getSettings(): Settings {
    const config = vscode.workspace.getConfiguration('llmTrainingAgent');
    return {
      backendUrl: config.get<string>('backendUrl', 'http://127.0.0.1:8000'),
      provider: config.get<string>('provider', 'ollama'),
      model: config.get<string>('model', 'llama3.2'),
    };
  }
  
  async updateSettings(settings: Partial<Settings>): Promise<void> {
    const config = vscode.workspace.getConfiguration('llmTrainingAgent');
    for (const [key, value] of Object.entries(settings)) {
      await config.update(key as any, value, vscode.ConfigurationTarget.Global);
    }
  }
}