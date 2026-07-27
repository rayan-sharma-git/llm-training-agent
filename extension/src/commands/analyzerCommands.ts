import * as vscode from 'vscode';
import { ApiClient } from '../services/apiClient';
import { SettingsManager } from '../services/settings';

export function registerAnalyzerCommands(context: vscode.ExtensionContext, apiClient: ApiClient, settings: SettingsManager) {
  const analyzeCommand = vscode.commands.registerCommand('llmTrainingAgent.analyzeProject', async () => {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders) {
      vscode.window.showErrorMessage('No workspace folder open');
      return;
    }
    
    const projectPath = workspaceFolders[0].uri.fsPath;
    await vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: 'Analyzing project...',
        cancellable: true,
      },
      async (progress, token) => {
        try {
          const result = await apiClient.analyzeProject(projectPath);
          vscode.window.showInformationMessage('Analysis complete');
          // TODO: display report in sidebar
        } catch (error) {
          vscode.window.showErrorMessage(`Analysis failed: ${error}`);
        }
      }
    );
  });
  
  context.subscriptions.push(analyzeCommand);
}