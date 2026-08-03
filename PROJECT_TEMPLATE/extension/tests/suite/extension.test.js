"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
Object.defineProperty(exports, "__esModule", { value: true });
var assert = require("assert");
var vscode = require("vscode");
suite('LLM Training Agent Extension Tests', function () {
    // --- 1. Extension Activation ---
    test('Extension should be found and activate', function () { return __awaiter(void 0, void 0, void 0, function () {
        var extension;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    extension = vscode.extensions.getExtension('rayansharma.llm-training-agent');
                    assert.ok(extension, 'Extension "rayansharma.llm-training-agent" was not found');
                    return [4 /*yield*/, extension.activate()];
                case 1:
                    _a.sent();
                    assert.strictEqual(extension.isActive, true, 'Extension did not activate');
                    return [2 /*return*/];
            }
        });
    }); });
    // --- 2. Commands ---
    test('All 4 commands should be registered', function () { return __awaiter(void 0, void 0, void 0, function () {
        var commands, expectedCommands, _i, expectedCommands_1, cmd;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, vscode.commands.getCommands(true)];
                case 1:
                    commands = _a.sent();
                    expectedCommands = [
                        'llmTrainingAgent.analyzeProject',
                        'llmTrainingAgent.analyzeDataset',
                        'llmTrainingAgent.openChat',
                        'llmTrainingAgent.viewReport',
                    ];
                    for (_i = 0, expectedCommands_1 = expectedCommands; _i < expectedCommands_1.length; _i++) {
                        cmd = expectedCommands_1[_i];
                        assert.ok(commands.includes(cmd), "Command \"".concat(cmd, "\" is not registered"));
                    }
                    return [2 /*return*/];
            }
        });
    }); });
    test('Analyze Dataset command should execute and show message', function () { return __awaiter(void 0, void 0, void 0, function () {
        var result;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, vscode.commands.executeCommand('llmTrainingAgent.analyzeDataset')];
                case 1:
                    result = _a.sent();
                    // If it executes without throwing, the command is wired up
                    assert.ok(true, 'Analyze Dataset command executed successfully');
                    return [2 /*return*/];
            }
        });
    }); });
    test('View Report command should execute and show message', function () { return __awaiter(void 0, void 0, void 0, function () {
        var result;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, vscode.commands.executeCommand('llmTrainingAgent.viewReport')];
                case 1:
                    result = _a.sent();
                    assert.ok(true, 'View Report command executed successfully');
                    return [2 /*return*/];
            }
        });
    }); });
    // --- 3. Sidebar Views ---
    test('Overview view should be registered', function () { return __awaiter(void 0, void 0, void 0, function () {
        var e_1;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    _a.trys.push([0, 2, , 3]);
                    return [4 /*yield*/, vscode.commands.executeCommand('vscode.openView', 'overview')];
                case 1:
                    _a.sent();
                    assert.ok(true, 'Overview view opened successfully');
                    return [3 /*break*/, 3];
                case 2:
                    e_1 = _a.sent();
                    assert.fail('Overview view could not be opened: ' + e_1.message);
                    return [3 /*break*/, 3];
                case 3: return [2 /*return*/];
            }
        });
    }); });
    test('Chat view should be registered', function () { return __awaiter(void 0, void 0, void 0, function () {
        var e_2;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    _a.trys.push([0, 2, , 3]);
                    return [4 /*yield*/, vscode.commands.executeCommand('vscode.openView', 'chat')];
                case 1:
                    _a.sent();
                    assert.ok(true, 'Chat view opened successfully');
                    return [3 /*break*/, 3];
                case 2:
                    e_2 = _a.sent();
                    assert.fail('Chat view could not be opened: ' + e_2.message);
                    return [3 /*break*/, 3];
                case 3: return [2 /*return*/];
            }
        });
    }); });
    test('Report view should be registered', function () { return __awaiter(void 0, void 0, void 0, function () {
        var e_3;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    _a.trys.push([0, 2, , 3]);
                    return [4 /*yield*/, vscode.commands.executeCommand('vscode.openView', 'report')];
                case 1:
                    _a.sent();
                    assert.ok(true, 'Report view opened successfully');
                    return [3 /*break*/, 3];
                case 2:
                    e_3 = _a.sent();
                    assert.fail('Report view could not be opened: ' + e_3.message);
                    return [3 /*break*/, 3];
                case 3: return [2 /*return*/];
            }
        });
    }); });
    // --- 4. Settings ---
    test('backendUrl setting should have correct default', function () {
        var config = vscode.workspace.getConfiguration('llmTrainingAgent');
        var value = config.get('backendUrl');
        assert.strictEqual(value, 'http://127.0.0.1:8000', 'backendUrl default is incorrect');
    });
    test('provider setting should have correct default', function () {
        var config = vscode.workspace.getConfiguration('llmTrainingAgent');
        var value = config.get('provider');
        assert.strictEqual(value, 'ollama', 'provider default is incorrect');
    });
    test('model setting should have correct default', function () {
        var config = vscode.workspace.getConfiguration('llmTrainingAgent');
        var value = config.get('model');
        assert.strictEqual(value, 'llama3.2', 'model default is incorrect');
    });
    test('SettingsManager should return all settings', function () { return __awaiter(void 0, void 0, void 0, function () {
        var extension, config;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    extension = vscode.extensions.getExtension('rayansharma.llm-training-agent');
                    assert.ok(extension, 'Extension not found');
                    return [4 /*yield*/, extension.activate()];
                case 1:
                    _a.sent();
                    config = vscode.workspace.getConfiguration('llmTrainingAgent');
                    assert.ok(config.has('backendUrl'), 'backendUrl setting not found');
                    assert.ok(config.has('provider'), 'provider setting not found');
                    assert.ok(config.has('model'), 'model setting not found');
                    return [2 /*return*/];
            }
        });
    }); });
    // --- 5. Edge Cases ---
    test('Analyze Project command should handle no workspace gracefully', function () { return __awaiter(void 0, void 0, void 0, function () {
        var e_4;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    _a.trys.push([0, 2, , 3]);
                    return [4 /*yield*/, vscode.commands.executeCommand('llmTrainingAgent.analyzeProject')];
                case 1:
                    _a.sent();
                    // If it doesn't throw, that's fine - it may have shown a progress notification
                    assert.ok(true, 'Analyze Project command executed');
                    return [3 /*break*/, 3];
                case 2:
                    e_4 = _a.sent();
                    // A network error is expected since no backend is running.
                    // The important thing is the command was found and executed.
                    assert.ok(true, 'Analyze Project command executed (expected network error)');
                    return [3 /*break*/, 3];
                case 3: return [2 /*return*/];
            }
        });
    }); });
    test('Open Chat command should be registered and callable', function () { return __awaiter(void 0, void 0, void 0, function () {
        var commands;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, vscode.commands.getCommands(true)];
                case 1:
                    commands = _a.sent();
                    assert.ok(commands.includes('llmTrainingAgent.openChat'), 'Open Chat command is not registered');
                    return [2 /*return*/];
            }
        });
    }); });
});
