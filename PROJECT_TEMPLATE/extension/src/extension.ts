import * as vscode from 'vscode';
import { SettingsManager } from './services/settings';
import { ApiClient } from './services/apiClient';
import { registerAnalyzerCommands } from './commands/analyzerCommands';
import { registerChatCommands } from './commands/chatCommands';
import { registerTreeView } from './views/simpleTreeView';
import { generateReportHtml } from './utils';


export function activate(context: vscode.ExtensionContext) {
  // --- Services ---
  const settings = new SettingsManager(context);
  const config = settings.getSettings();
  const apiClient = new ApiClient(config.backendUrl);

  // --- Commands (implemented) ---
  registerAnalyzerCommands(context, apiClient, settings);
  registerChatCommands(context, apiClient, settings);

  // --- Dataset & Report Commands ---
  const analyzeDatasetCmd = vscode.commands.registerCommand(
    'llmTrainingAgent.analyzeDataset',
    async () => {
      const workspaceFolders = vscode.workspace.workspaceFolders;
      if (!workspaceFolders) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
      }

      const datasetPath = await vscode.window.showOpenDialog({
        canSelectFiles: false,
        canSelectFolders: true,
        canSelectMany: false,
        title: 'Select Dataset Directory',
        openLabel: 'Analyze',
      });

      if (!datasetPath || datasetPath.length === 0) {
        return;
      }

      await vscode.window.withProgress(
        {
          location: vscode.ProgressLocation.Notification,
          title: 'Analyzing dataset...',
          cancellable: true,
        },
        async (progress, token) => {
          try {
            progress.report({ increment: 0, message: 'Starting analysis' });
            const result = await apiClient.analyzeDataset(datasetPath[0].fsPath);
            progress.report({ increment: 80, message: 'Analysis complete' });
            vscode.window.showInformationMessage('Dataset analysis complete');
          } catch (error) {
            vscode.window.showErrorMessage(`Dataset analysis failed: ${error}`);
          }
        }
      );
    }
  );
  context.subscriptions.push(analyzeDatasetCmd);

  const viewReportCmd = vscode.commands.registerCommand(
    'llmTrainingAgent.viewReport',
    async () => {
      try {
        const report = await apiClient.getReport();
        if (!report) {
          vscode.window.showInformationMessage('No report available');
          return;
        }
        const panel = vscode.window.createWebviewPanel(
          'llmTrainingAgent.report',
          'Report',
          vscode.ViewColumn.One,
          { enableScripts: true }
        );
        panel.webview.html = generateReportHtml(report);
      } catch (error) {
        vscode.window.showErrorMessage(`Failed to load report: ${error}`);
      }
    }
  );
  context.subscriptions.push(viewReportCmd);

  // --- Sidebar views ---
  registerTreeView(context, 'overview', [
    { label: 'Project: No project analyzed yet' },
    { label: 'Provider: ' + config.provider },
    { label: 'Model: ' + config.model },
  ]);

  registerTreeView(context, 'chat', [
    { label: 'Chat history is empty' },
  ]);

  registerTreeView(context, 'report', [
    { label: 'No report available' },
    {
      label: 'Generate a report',
      command: {
        command: 'llmTrainingAgent.analyzeProject',
        title: 'Analyze Project',
      },
    },
  ]);
}

export function deactivate() {}
