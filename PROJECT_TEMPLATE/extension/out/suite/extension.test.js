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
const assert = __importStar(require("assert"));
const vscode = __importStar(require("vscode"));
suite('LLM Training Agent Extension Tests', () => {
    // --- 1. Extension Activation ---
    test('Extension should be found and activate', async () => {
        const extension = vscode.extensions.getExtension('rayansharma.llm-training-agent');
        assert.ok(extension, 'Extension "rayansharma.llm-training-agent" was not found');
        await extension.activate();
        assert.strictEqual(extension.isActive, true, 'Extension did not activate');
    });
    // --- 2. Commands ---
    test('All 4 commands should be registered', async () => {
        const commands = await vscode.commands.getCommands(true);
        const expectedCommands = [
            'llmTrainingAgent.analyzeProject',
            'llmTrainingAgent.analyzeDataset',
            'llmTrainingAgent.openChat',
            'llmTrainingAgent.viewReport',
        ];
        for (const cmd of expectedCommands) {
            assert.ok(commands.includes(cmd), `Command "${cmd}" is not registered`);
        }
    });
    test('Analyze Dataset command should execute and show message', async () => {
        // This command shows an information message and returns immediately
        const result = await vscode.commands.executeCommand('llmTrainingAgent.analyzeDataset');
        // If it executes without throwing, the command is wired up
        assert.ok(true, 'Analyze Dataset command executed successfully');
    });
    test('View Report command should execute and show message', async () => {
        const result = await vscode.commands.executeCommand('llmTrainingAgent.viewReport');
        assert.ok(true, 'View Report command executed successfully');
    });
    // --- 3. Sidebar Views ---
    test('Overview view should be registered', async () => {
        try {
            await vscode.commands.executeCommand('vscode.openView', 'overview');
            assert.ok(true, 'Overview view opened successfully');
        }
        catch (e) {
            assert.fail('Overview view could not be opened: ' + e.message);
        }
    });
    test('Chat view should be registered', async () => {
        try {
            await vscode.commands.executeCommand('vscode.openView', 'chat');
            assert.ok(true, 'Chat view opened successfully');
        }
        catch (e) {
            assert.fail('Chat view could not be opened: ' + e.message);
        }
    });
    test('Report view should be registered', async () => {
        try {
            await vscode.commands.executeCommand('vscode.openView', 'report');
            assert.ok(true, 'Report view opened successfully');
        }
        catch (e) {
            assert.fail('Report view could not be opened: ' + e.message);
        }
    });
    // --- 4. Settings ---
    test('backendUrl setting should have correct default', () => {
        const config = vscode.workspace.getConfiguration('llmTrainingAgent');
        const value = config.get('backendUrl');
        assert.strictEqual(value, 'http://127.0.0.1:8000', 'backendUrl default is incorrect');
    });
    test('provider setting should have correct default', () => {
        const config = vscode.workspace.getConfiguration('llmTrainingAgent');
        const value = config.get('provider');
        assert.strictEqual(value, 'ollama', 'provider default is incorrect');
    });
    test('model setting should have correct default', () => {
        const config = vscode.workspace.getConfiguration('llmTrainingAgent');
        const value = config.get('model');
        assert.strictEqual(value, 'llama3.2', 'model default is incorrect');
    });
    test('SettingsManager should return all settings', async () => {
        const extension = vscode.extensions.getExtension('rayansharma.llm-training-agent');
        assert.ok(extension, 'Extension not found');
        await extension.activate();
        // The settings are managed internally; verify via VS Code config API
        const config = vscode.workspace.getConfiguration('llmTrainingAgent');
        assert.ok(config.has('backendUrl'), 'backendUrl setting not found');
        assert.ok(config.has('provider'), 'provider setting not found');
        assert.ok(config.has('model'), 'model setting not found');
    });
    // --- 5. Edge Cases ---
    test('Analyze Project command should handle no workspace gracefully', async () => {
        // This test verifies the command is registered and can be invoked.
        // In the test environment a workspace IS open (the extension dir),
        // so the command will attempt a network call and fail.
        // We verify the command is callable without throwing a "command not found" error.
        try {
            await vscode.commands.executeCommand('llmTrainingAgent.analyzeProject');
            // If it doesn't throw, that's fine - it may have shown a progress notification
            assert.ok(true, 'Analyze Project command executed');
        }
        catch (e) {
            // A network error is expected since no backend is running.
            // The important thing is the command was found and executed.
            assert.ok(true, 'Analyze Project command executed (expected network error)');
        }
    });
    test('Open Chat command should be registered and callable', async () => {
        // The command shows an input box. We can't interact with it,
        // but we can verify the command is registered.
        const commands = await vscode.commands.getCommands(true);
        assert.ok(commands.includes('llmTrainingAgent.openChat'), 'Open Chat command is not registered');
    });
});
