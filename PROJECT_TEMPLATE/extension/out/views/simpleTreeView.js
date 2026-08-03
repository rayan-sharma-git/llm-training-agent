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
exports.SimpleTreeDataProvider = void 0;
exports.registerTreeView = registerTreeView;
const vscode = __importStar(require("vscode"));
/**
 * Simple tree item representing a single node in a view.
 */
class SimpleTreeItem extends vscode.TreeItem {
    constructor(label, collapsibleState, command) {
        super(label, collapsibleState);
        this.label = label;
        this.collapsibleState = collapsibleState;
        this.command = command;
    }
}
/**
 * A minimal TreeDataProvider that displays a list of string entries.
 * Used by the Overview, Chat, and Report sidebar views.
 */
class SimpleTreeDataProvider {
    constructor(entries = []) {
        this.entries = entries;
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
    }
    refresh(entries) {
        this.entries = entries;
        this._onDidChangeTreeData.fire();
    }
    getTreeItem(element) {
        return element;
    }
    getChildren() {
        if (this.entries.length === 0) {
            return [new SimpleTreeItem('No data available', vscode.TreeItemCollapsibleState.None)];
        }
        return this.entries.map((entry) => new SimpleTreeItem(entry.label, vscode.TreeItemCollapsibleState.None, entry.command));
    }
}
exports.SimpleTreeDataProvider = SimpleTreeDataProvider;
/**
 * Creates and registers a TreeDataProvider for a given view ID.
 * Returns the provider so the caller can refresh it later.
 */
function registerTreeView(context, viewId, entries = []) {
    const provider = new SimpleTreeDataProvider(entries);
    context.subscriptions.push(vscode.window.registerTreeDataProvider(viewId, provider));
    return provider;
}
