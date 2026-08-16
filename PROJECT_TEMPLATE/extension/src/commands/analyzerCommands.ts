import * as vscode from 'vscode';
import { ApiClient } from '../services/apiClient';
import { SettingsManager } from '../services/settings';
import { SimpleTreeDataProvider } from '../views/simpleTreeView';
import { ChatWebviewProvider } from '../views/chatWebviewProvider';

/**
 * Formats and displays GPU training estimate in the chat.
 */
function formatGpuEstimateForChat(gpuEstimate: any): string {
  if (!gpuEstimate) {
    return '';
  }
  const lines: string[] = [];
  lines.push('## 🎮 GPU TRAINING ESTIMATE');
  lines.push('');

  const gpuInfo = gpuEstimate.gpu_info || {};
  const gpus = gpuInfo.gpus || [];
  if (gpus.length > 0) {
    for (const gpu of gpus) {
      lines.push(`**GPU ${gpu.index}:** ${gpu.name || 'Unknown'}`);
      if (gpu.vram_gb) {
        lines.push(`**VRAM:** ${gpu.vram_gb} GB`);
      }
      if (gpu.cuda_version) {
        lines.push(`**CUDA:** ${gpu.cuda_version}`);
      }
    }
  } else {
    lines.push('⚠ No supported GPU detected. GPU time estimation may be unavailable or less accurate.');
  }

  lines.push('');
  lines.push(`**Estimated training time:** ~${gpuEstimate.estimated_time || 'unknown'}`);
  if (gpuEstimate.range) {
    lines.push(`**Likely range:** ${gpuEstimate.range}`);
  }
  lines.push(`**Confidence:** ${gpuEstimate.confidence || 'low'}`);
  if (gpuEstimate.mode) {
    lines.push(`**Mode:** ${gpuEstimate.mode === 'calibrated' ? 'Calibrated' : 'Quick'} estimate`);
  }
  if (gpuEstimate.throughput_steps_per_sec) {
    lines.push(`**Throughput:** ${gpuEstimate.throughput_steps_per_sec.toFixed(2)} steps/sec`);
  }
  if (gpuEstimate.total_steps) {
    lines.push(`**Total steps:** ${gpuEstimate.total_steps}`);
  }
  lines.push(`**VRAM:** ${gpuEstimate.vram_feasible ? '✓ Likely sufficient' : '⚠ May exceed available VRAM'}`);

  if (gpuEstimate.warnings && gpuEstimate.warnings.length > 0) {
    lines.push('');
    lines.push('**Warnings:**');
    for (const w of gpuEstimate.warnings) {
      lines.push(`- ${w}`);
    }
  }

  if (gpuEstimate.assumptions && gpuEstimate.assumptions.length > 0) {
    lines.push('');
    lines.push('**Assumptions:**');
    for (const a of gpuEstimate.assumptions) {
      lines.push(`- ${a}`);
    }
  }

  return lines.join('\n');
}

/**
 * Registers the project analysis command.
 * - llmTrainingAgent.analyzeProject : scans the workspace and refreshes the Overview view.
 */
export function registerAnalyzerCommands(
  context: vscode.ExtensionContext,
  apiClient: ApiClient,
  settings: SettingsManager,
  overviewProvider: SimpleTreeDataProvider,
  chatProvider: ChatWebviewProvider | null = null,
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

            // Post GPU training estimate to chat if available
            if (chatProvider && result && result.report) {
              const gpuEstimates = [
                result.report.gpu_time_estimate,
                result.report.hardware_detection
              ];
              // Check report for GPU estimation
              const gpuEstimate = result.report.gpu_time_estimate;
              if (gpuEstimate) {
                const formatted = formatGpuEstimateForChat(gpuEstimate);
                if (formatted) {
                  chatProvider.postAssistantMessage(formatted);
                }
              }
            }
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