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
exports.SettingsManager = void 0;
const vscode = __importStar(require("vscode"));
class SettingsManager {
    constructor(context) {
        this.context = context;
        this.initializeDefaults();
    }
    initializeDefaults() {
        const config = vscode.workspace.getConfiguration('llmTrainingAgent');
        if (!config.has('backendUrl')) {
            config.update('backendUrl', 'http://127.0.0.1:8000', vscode.ConfigurationTarget.Global);
        }
        if (!config.has('provider')) {
            config.update('provider', 'ollama', vscode.ConfigurationTarget.Global);
        }
        if (!config.has('model')) {
            config.update('model', 'llama3.2', vscode.ConfigurationTarget.Global);
        }
    }
    getSettings() {
        const config = vscode.workspace.getConfiguration('llmTrainingAgent');
        return {
            backendUrl: config.get('backendUrl', 'http://127.0.0.1:8000'),
            provider: config.get('provider', 'ollama'),
            model: config.get('model', 'llama3.2'),
        };
    }
    async updateSettings(settings) {
        const config = vscode.workspace.getConfiguration('llmTrainingAgent');
        for (const [key, value] of Object.entries(settings)) {
            await config.update(key, value, vscode.ConfigurationTarget.Global);
        }
    }
}
exports.SettingsManager = SettingsManager;
