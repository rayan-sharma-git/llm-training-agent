import * as vscode from 'vscode';
import { ApiClient, ChatResponse } from '../services/apiClient';
import { SettingsManager } from '../services/settings';

export function registerChatCommands(context: vscode.ExtensionContext, apiClient: ApiClient, settings: SettingsManager) {
  const openChatCommand = vscode.commands.registerCommand('llmTrainingAgent.openChat', async () => {
    const message = await vscode.window.showInputBox({
      prompt: 'Ask about your fine-tuning project',
      placeHolder: 'Why is my learning rate too high?',
    });
    
    if (!message) {
      return;
    }
    
    try {
      const response: ChatResponse = await apiClient.sendChatMessage(message);
      const confidence = response.confidence === 'high' ? '💚' : response.confidence === 'medium' ? '💛' : '❤️';
      const infoMessage = `${confidence} ${response.assistantResponse}`;
      vscode.window.showInformationMessage(infoMessage, 'Show Details').then(selection => {
        if (selection === 'Show Details') {
          vscode.window.showInformationMessage(JSON.stringify(response.references, null, 2));
        }
      });
    } catch (error) {
      vscode.window.showErrorMessage(`Chat failed: ${error}`);
    }
  });
  
  context.subscriptions.push(openChatCommand);
}