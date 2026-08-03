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
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const settings_1 = require("./services/settings");
const apiClient_1 = require("./services/apiClient");
const analyzerCommands_1 = require("./commands/analyzerCommands");
const chatCommands_1 = require("./commands/chatCommands");
const simpleTreeView_1 = require("./views/simpleTreeView");
const utils_1 = require("./utils");
function activate(context) {
    // --- Services ---
    const settings = new settings_1.SettingsManager(context);
    const config = settings.getSettings();
    const apiClient = new apiClient_1.ApiClient(config.backendUrl);
    // --- Commands (implemented) ---
    (0, analyzerCommands_1.registerAnalyzerCommands)(context, apiClient, settings);
    (0, chatCommands_1.registerChatCommands)(context, apiClient, settings);
    // --- Dataset & Report Commands ---
    const analyzeDatasetCmd = vscode.commands.registerCommand('llmTrainingAgent.analyzeDataset', async () => {
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
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Analyzing dataset...',
            cancellable: true,
        }, async (progress, token) => {
            try {
                progress.report({ increment: 0, message: 'Starting analysis' });
                const result = await apiClient.analyzeDataset(datasetPath[0].fsPath);
                progress.report({ increment: 80, message: 'Analysis complete' });
                vscode.window.showInformationMessage('Dataset analysis complete');
            }
            catch (error) {
                vscode.window.showErrorMessage(`Dataset analysis failed: ${error}`);
            }
        });
    });
    context.subscriptions.push(analyzeDatasetCmd);
    const viewReportCmd = vscode.commands.registerCommand('llmTrainingAgent.viewReport', async () => {
        try {
            const report = await apiClient.getReport();
            if (!report) {
                vscode.window.showInformationMessage('No report available');
                return;
            }
            const panel = vscode.window.createWebviewPanel('llmTrainingAgent.report', 'Report', vscode.ViewColumn.One, { enableScripts: true });
            panel.webview.html = (0, utils_1.generateReportHtml)(report);
        }
        catch (error) {
            vscode.window.showErrorMessage(`Failed to load report: ${error}`);
        }
    });
    context.subscriptions.push(viewReportCmd);
    // --- Sidebar views ---
    (0, simpleTreeView_1.registerTreeView)(context, 'overview', [
        { label: 'Project: No project analyzed yet' },
        { label: 'Provider: ' + config.provider },
        { label: 'Model: ' + config.model },
    ]);
    (0, simpleTreeView_1.registerTreeView)(context, 'chat', [
        { label: 'Chat history is empty' },
    ]);
    (0, simpleTreeView_1.registerTreeView)(context, 'report', [
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
function deactivate() { }
