import * as vscode from 'vscode';
import { ApiClient } from '../services/apiClient';
import { SettingsManager } from '../services/settings';
import { registerTreeView } from '../views/simpleTreeView';

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
          progress.report({ increment: 0, message: 'Scanning project' });
          const result = await apiClient.analyzeProject(projectPath);
          progress.report({ increment: 80, message: 'Generating report' });
          vscode.window.showInformationMessage('Analysis complete');
          
          // Update overview tree view with analysis results
          const overviewProvider = registerTreeView(context, 'overview', [
            { label: 'Project: ' + projectPath },
            { label: 'Provider: ' + settings.getSettings().provider },
            { label: 'Model: ' + settings.getSettings().model },
          ]);
          
          // Store the result for report view
          context.globalState.update('lastAnalysisResult', result);
        } catch (error) {
          vscode.window.showErrorMessage(`Analysis failed: ${error}`);
        }
      }
    );
  });
  
  context.subscriptions.push(analyzeCommand);
}