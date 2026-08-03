"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerChatCommands = registerChatCommands;
const vscode = __importStar(require("vscode"));
function registerChatCommands(context, apiClient, settings) {
    const openChatCommand = vscode.commands.registerCommand('llmTrainingAgent.openChat', async () => {
        const message = await vscode.window.showInputBox({
            prompt: 'Ask about your fine-tuning project',
            placeHolder: 'Why is my learning rate too high?',
        });
        if (!message) {
            return;
        }
        try {
            const response = await apiClient.sendChatMessage(message);
            const confidence = response.confidence === 'high' ? '💚' : response.confidence === 'medium' ? '💛' : '❤️';
            const infoMessage = `${confidence} ${response.assistantResponse}`;
            vscode.window.showInformationMessage(infoMessage, 'Show Details').then(selection => {
                if (selection === 'Show Details') {
                    vscode.window.showInformationMessage(JSON.stringify(response.references, null, 2));
                }
            });
        }
        catch (error) {
            vscode.window.showErrorMessage(`Chat failed: ${error}`);
        }
    });
    context.subscriptions.push(openChatCommand);
}
