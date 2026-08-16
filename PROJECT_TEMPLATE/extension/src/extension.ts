import * as vscode from 'vscode';
import { SettingsManager } from './services/settings';
import { ApiClient } from './services/apiClient';
import { BackendManager } from './services/backendManager';
import { registerAnalyzerCommands } from './commands/analyzerCommands';
import { registerChatCommands } from './commands/chatCommands';
import { registerTreeView } from './views/simpleTreeView';
import { ChatWebviewProvider } from './views/chatWebviewProvider';
import { SettingsWebviewProvider } from './views/settingsWebviewProvider';
import { generateReportHtml, formatError } from './utils';
import { OVERVIEW_VIEW_ID, CHAT_VIEW_ID, REPORTS_VIEW_ID, SETTINGS_VIEW_ID } from './views/viewIds';

export async function activate(context: vscode.ExtensionContext) {
  try {
    // --- Services ---
    const settings = new SettingsManager(context);
    const config = settings.getSettings();

    // BackendManager auto-starts the Python backend and waits for it to be ready.
    const backendManager = new BackendManager(context);
    const apiClient = new ApiClient(config.backendUrl, () => backendManager.getBaseUrl(), context);

    // Kick off automatic startup in the background (non-blocking).
    const startupPromise = backendManager.ensureRunning().then((ok) => {
      if (!ok) {
        vscode.window.showWarningMessage(
          'LLM Training Agent: The Python backend could not be started automatically. ' +
          'Please start it manually (uvicorn main:app --port 8000) from the backend folder.'
        );
      }
      return ok;
    });

    // Register shutdown so the child process is cleaned up when VS Code closes.
    context.subscriptions.push({
      dispose: () => {
        backendManager.shutdown();
      },
    });

    // Ensure the backend is ready before the first API call from commands.
    // We store the promise on the context so commands can await it.
    context.globalState.update('_backendReadyPromise', undefined);
    (apiClient as any)._ensureBackendReady = async () => {
      await startupPromise;
    };

    // --- Overview tree view ---
    const overviewProvider = registerTreeView(context, OVERVIEW_VIEW_ID, [
      { label: 'Project: No project analyzed yet' },
      { label: 'Provider: ' + config.provider },
      { label: 'Model: ' + config.model },
    ]);

    // --- Reports tree view ---
    registerTreeView(context, REPORTS_VIEW_ID, [
      { label: 'No report available' },
      {
        label: 'Generate a report',
        command: {
          command: 'llmTrainingAgent.analyzeProject',
          title: 'Analyze Project',
        },
      },
    ]);

    // --- Chat webview view ---
    const chatProvider = new ChatWebviewProvider(context.extensionUri, apiClient);
    context.subscriptions.push(
      vscode.window.registerWebviewViewProvider(ChatWebviewProvider.viewType, chatProvider, {
        webviewOptions: { retainContextWhenHidden: true },
      })
    );

    // --- Settings webview view ---
    const settingsProvider = new SettingsWebviewProvider(context.extensionUri, apiClient, settings);
    context.subscriptions.push(
      vscode.window.registerWebviewViewProvider(SettingsWebviewProvider.viewType, settingsProvider, {
        webviewOptions: { retainContextWhenHidden: true },
      })
    );

    // --- Commands ---
    registerAnalyzerCommands(context, apiClient, settings, overviewProvider, chatProvider, startupPromise);
    registerChatCommands(context, apiClient, settings, startupPromise);
    context.subscriptions.push(
      vscode.commands.registerCommand('llmTrainingAgent.configureProvider', async () => {
        await settingsProvider.reveal();
      })
    );

    // Analyze Dataset command.
    const analyzeDatasetCmd = vscode.commands.registerCommand(
      'llmTrainingAgent.analyzeDataset',
      async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders) {
          vscode.window.showErrorMessage('No workspace folder open');
          return;
        }

        // Wait for backend before performing work.
        await startupPromise;

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
          async (_progress, token) => {
            try {
              _progress.report({ increment: 0, message: 'Starting analysis' });
              if (token.isCancellationRequested) {
                return;
              }
              await apiClient.analyzeDataset(datasetPath[0].fsPath);
              _progress.report({ increment: 80, message: 'Analysis complete' });
              vscode.window.showInformationMessage('Dataset analysis complete');
            } catch (error) {
              vscode.window.showErrorMessage(`Dataset analysis failed: ${formatError(error)}`);
            }
          }
        );
      }
    );
    context.subscriptions.push(analyzeDatasetCmd);

    // View Report command.
    const viewReportCmd = vscode.commands.registerCommand(
      'llmTrainingAgent.viewReport',
      async () => {
        try {
          await startupPromise;
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
          vscode.window.showErrorMessage(`Failed to load report: ${formatError(error)}`);
        }
      }
    );
    context.subscriptions.push(viewReportCmd);
  } catch (error) {
    vscode.window.showErrorMessage(`Failed to activate LLM Training Agent: ${formatError(error)}`);
    console.error('Extension activation failed:', error);
  }
}

export function deactivate() {}