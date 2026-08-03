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
exports.registerAnalyzerCommands = registerAnalyzerCommands;
const vscode = __importStar(require("vscode"));
const simpleTreeView_1 = require("../views/simpleTreeView");
function registerAnalyzerCommands(context, apiClient, settings) {
    const analyzeCommand = vscode.commands.registerCommand('llmTrainingAgent.analyzeProject', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }
        const projectPath = workspaceFolders[0].uri.fsPath;
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Analyzing project...',
            cancellable: true,
        }, async (progress, token) => {
            try {
                progress.report({ increment: 0, message: 'Scanning project' });
                const result = await apiClient.analyzeProject(projectPath);
                progress.report({ increment: 80, message: 'Generating report' });
                vscode.window.showInformationMessage('Analysis complete');
                // Update overview tree view with analysis results
                const overviewProvider = (0, simpleTreeView_1.registerTreeView)(context, 'overview', [
                    { label: 'Project: ' + projectPath },
                    { label: 'Provider: ' + settings.getSettings().provider },
                    { label: 'Model: ' + settings.getSettings().model },
                ]);
                // Store the result for report view
                context.globalState.update('lastAnalysisResult', result);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Analysis failed: ${error}`);
            }
        });
    });
    context.subscriptions.push(analyzeCommand);
}
