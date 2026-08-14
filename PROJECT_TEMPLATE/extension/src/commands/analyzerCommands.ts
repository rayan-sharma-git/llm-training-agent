import * as vscode from 'vscode';
import { ApiClient } from '../services/apiClient';
import { SettingsManager } from '../services/settings';
import { SimpleTreeDataProvider } from '../views/simpleTreeView';

/**
 * Registers the project analysis command.
 * - llmTrainingAgent.analyzeProject : scans the workspace and refreshes the Overview view.
 */
export function registerAnalyzerCommands(
  context: vscode.ExtensionContext,
  apiClient: ApiClient,
  settings: SettingsManager,
  overviewProvider: SimpleTreeDataProvider,
  startupPromise?: Promise<boolean>
): void {
  const analyzeCommand = vscode.commands.registerCommand(
    'llmTrainingAgent.analyzeProject',
    async () => {
      const workspaceFolders = vscode.workspace.workspaceFolders;
      if (!workspaceFolders || workspaceFolders.length === 0) {
        vscode.window.showErrorMessage(
          'No project/workspace is currently open. Please open a folder first.'
        );
        return;
      }

      // Ensure the path exists before sending to the backend.
      const projectPath = workspaceFolders[0].uri.fsPath;
      const fs = require('fs') as typeof import('fs');
      if (!fs.existsSync(projectPath)) {
        vscode.window.showErrorMessage(
          `Project path does not exist: ${projectPath}`
        );
        return;
      }

      // Wait for the backend to be ready before sending the request.
      if (startupPromise) {
        const ok = await startupPromise;
        if (!ok) {
          vscode.window.showErrorMessage(
            'Python backend could not be started. ' +
            'Check the "LLM Training Agent: Backend" output channel, or start it manually: ' +
            'cd backend && python -m uvicorn main:app --port 8000'
          );
          return;
        }
      }

      await vscode.window.withProgress(
        {
          location: vscode.ProgressLocation.Notification,
          title: 'Analyzing project...',
          cancellable: true,
        },
        async (progress, token) => {
          try {
            progress.report({ increment: 0, message: 'Contacting backend' });
            if (token.isCancellationRequested) {
              return;
            }
            progress.report({ increment: 20, message: 'Scanning project' });
            const result = await apiClient.analyzeProject(projectPath);
            progress.report({ increment: 80, message: 'Generating report' });
            vscode.window.showInformationMessage('Analysis complete');

            // Refresh the overview tree view with analysis results.
            overviewProvider.refresh([
              { label: 'Project: ' + projectPath },
              { label: 'Provider: ' + settings.getSettings().provider },
              { label: 'Model: ' + settings.getSettings().model },
            ]);

            // Store the result for the report view.
            await context.globalState.update('lastAnalysisResult', result);
          } catch (error) {
            // Use the ApiError message (already human-friendly).
            const err = error instanceof Error ? error : new Error(String(error));
            vscode.window.showErrorMessage(`Analysis failed: ${err.message}`);
            console.error('Analyze project error:', err);
          }
        }
      );
    }
  );

  context.subscriptions.push(analyzeCommand);
}