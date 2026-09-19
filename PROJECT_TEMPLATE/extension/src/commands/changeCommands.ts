import * as vscode from 'vscode';
import { ApiClient } from '../services/apiClient';
import { formatError } from '../utils';

const VIEW_CHANGES_SCHEME = 'llm-training-agent-changes';

interface PendingChangeEntry {
  changeId: string;
  filePath: string;
  status: string;
  createdAt: string;
}

/**
 * Virtual-document provider that surfaces the original and proposed file
 * contents in VS Code's native diff editor.
 */
class ChangeContentProvider implements vscode.TextDocumentContentProvider {
  private readonly contents = new Map<string, string>();

  provideTextDocumentContent(uri: vscode.Uri): string {
    return this.contents.get(uri.toString()) ?? '';
  }

  set(uri: vscode.Uri, content: string): void {
    this.contents.set(uri.toString(), content);
  }
}

function projectRoot(): string | undefined {
  return vscode.workspace.workspaceFolders?.[0]?.uri.fsPath;
}

/**
 * Registers the "View Changes" workflow:
 * list pending agent-made changes → inspect each as a native diff →
 * apply, discard, or roll back.
 */
export function registerChangeCommands(
  context: vscode.ExtensionContext,
  apiClient: ApiClient
): void {
  const provider = new ChangeContentProvider();
  context.subscriptions.push(
    vscode.workspace.registerTextDocumentContentProvider(VIEW_CHANGES_SCHEME, provider)
  );

  const viewChanges = vscode.commands.registerCommand(
    'llmTrainingAgent.viewChanges',
    async () => {
      let changes: PendingChangeEntry[];
      try {
        changes = (await apiClient.listFileChanges(projectRoot())).changes ?? [];
      } catch (error) {
        vscode.window.showErrorMessage(`Could not list pending changes: ${formatError(error)}`);
        return;
      }

      if (changes.length === 0) {
        vscode.window.showInformationMessage(
          'No pending changes. The agent has not proposed any file modifications.'
        );
        return;
      }

      const picked = await vscode.window.showQuickPick(
        changes.map((change) => ({
          label: change.filePath,
          description: change.status,
          detail: change.createdAt,
          change,
        })),
        { placeHolder: 'View Changes — select a proposed change to inspect' }
      );
      if (!picked) {
        return;
      }

      let detail: any;
      try {
        detail = await apiClient.getFileChange(picked.change.changeId, projectRoot());
      } catch (error) {
        vscode.window.showErrorMessage(`Could not load the change: ${formatError(error)}`);
        return;
      }

      // Show the proposal in VS Code's native diff editor (before vs. proposed).
      const originalUri = vscode.Uri.parse(
        `${VIEW_CHANGES_SCHEME}:${picked.change.filePath}.original?${encodeURIComponent(picked.change.changeId + ':original')}`
      );
      const proposedUri = vscode.Uri.parse(
        `${VIEW_CHANGES_SCHEME}:${picked.change.filePath}.proposed?${encodeURIComponent(picked.change.changeId + ':proposed')}`
      );
      provider.set(originalUri, detail.originalContent ?? '');
      provider.set(proposedUri, detail.proposedContent ?? '');

      const title = `View Changes — ${picked.change.filePath} (proposed vs. current)`;
      await vscode.commands.executeCommand(
        'vscode.diff',
        originalUri,
        proposedUri,
        title,
        { preview: true }
      );

      const action = await vscode.window.showInformationMessage(
        `Apply proposed changes to ${picked.change.filePath}?`,
        { modal: false },
        'Apply',
        'Discard',
        'Rollback'
      );
      try {
        if (action === 'Apply') {
          await apiClient.applyFileChange(picked.change.changeId, projectRoot());
          vscode.window.showInformationMessage(`Changes applied to ${picked.change.filePath}. You can roll back later via View Changes.`);
        } else if (action === 'Discard') {
          await apiClient.discardFileChange(picked.change.changeId, projectRoot());
          vscode.window.showInformationMessage(`Change discarded. ${picked.change.filePath} was not modified.`);
        } else if (action === 'Rollback') {
          await apiClient.rollbackFileChange(picked.change.changeId, projectRoot());
          vscode.window.showInformationMessage(`Change rolled back. ${picked.change.filePath} restored to its previous content.`);
        }
      } catch (error) {
        vscode.window.showErrorMessage(`Operation failed: ${formatError(error)}`);
      }
    }
  );

  context.subscriptions.push(viewChanges);
}
