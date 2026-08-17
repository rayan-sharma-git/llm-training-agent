import * as vscode from 'vscode';
import { ApiClient } from '../services/apiClient';
import { formatError } from '../utils';

/**
 * A WebviewViewProvider that renders a functional chat interface
 * in the sidebar. Messages are sent to the backend API and the
 * assistant's response is displayed in a scrollable conversation view.
 *
 * Supports action cards — interactive messages that present the user
 * with buttons (e.g. [Install Dependencies] [Cancel]).
 */
export class ChatWebviewProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = 'llmTrainingAgent.chat';

  private _view?: vscode.WebviewView;
  private _disposables: vscode.Disposable[] = [];
  /** Resolve a pending action-button promise, keyed by action id. */
  private _actionResolvers: Map<string, (action: string) => void> = new Map();

  constructor(
    private readonly _extensionUri: vscode.Uri,
    private readonly _apiClient: ApiClient
  ) {}

  resolveWebviewView(
    webviewView: vscode.WebviewView,
    _context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken
  ): void {
    this._view = webviewView;

    webviewView.webview.options = {
      // Allow scripts so the chat UI can send messages.
      enableScripts: true,
      localResourceRoots: [this._extensionUri],
    };

    webviewView.webview.html = this._getHtml(webviewView.webview);

    // Handle messages coming from the webview.
    webviewView.webview.onDidReceiveMessage(
      async (message) => {
        switch (message.command) {
          case 'sendMessage': {
            const text = message.text as string;
            if (!text || !text.trim()) {
              return;
            }
            await this._handleSendMessage(text);
            break;
          }
          case 'actionButtonClicked': {
            const actionId = message.actionId as string;
            const action = message.action as string;
            const resolver = this._actionResolvers.get(actionId);
            if (resolver) {
              resolver(action);
              this._actionResolvers.delete(actionId);
            }
            break;
          }
        }
      },
      null,
      this._disposables
    );
  }

  /**
   * Post an assistant message to the chat view (used by other commands).
   */
  public postAssistantMessage(text: string): void {
    if (!this._view) {
      return;
    }
    this._view.webview.postMessage({
      command: 'appendMessage',
      role: 'assistant',
      text,
    });
  }

  /**
   * Post an action card — a message with clickable buttons — to the chat view.
   * Returns a promise that resolves to the action label the user clicked.
   * If the view is not available, the promise resolves to an empty string.
   */
  public postActionCard(options: {
    text: string;
    actionId: string;
    buttons: Array<{ label: string; action: string }>;
  }): Promise<string> {
    return new Promise((resolve) => {
      if (!this._view) {
        resolve('');
        return;
      }

      // Store the resolver so the webview message handler can call it.
      this._actionResolvers.set(options.actionId, resolve);

      this._view.webview.postMessage({
        command: 'showActionCard',
        actionId: options.actionId,
        text: options.text,
        buttons: options.buttons,
      });
    });
  }

  private async _handleSendMessage(text: string): Promise<void> {
    if (!this._view) {
      return;
    }

    // Append the user's message to the chat.
    this._view.webview.postMessage({
      command: 'appendMessage',
      role: 'user',
      text,
    });

    try {
      const response = await this._apiClient.sendChatMessage(text);
      this._view.webview.postMessage({
        command: 'appendMessage',
        role: 'assistant',
        text: response.assistantResponse,
        confidence: response.confidence,
        references: response.references,
      });
    } catch (error) {
      this._view.webview.postMessage({
        command: 'appendMessage',
        role: 'assistant',
        text: `⚠️ Failed to get a response from the backend: ${formatError(error)}`,
      });
    }
  }

  private _getHtml(webview: vscode.Webview): string {
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chat</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: var(--vscode-font-family);
      font-size: var(--vscode-font-size);
      color: var(--vscode-foreground);
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
    }
    #messages {
      flex: 1;
      overflow-y: auto;
      padding: 8px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .message {
      padding: 8px 10px;
      border-radius: 6px;
      max-width: 90%;
      word-wrap: break-word;
      white-space: pre-wrap;
      line-height: 1.4;
    }
    .message.user {
      align-self: flex-end;
      background: var(--vscode-button-background);
      color: var(--vscode-button-foreground);
    }
    .message.assistant {
      align-self: flex-start;
      background: var(--vscode-editor-inlineValues-background, var(--vscode-editor-background));
      color: var(--vscode-foreground);
      border: 1px solid var(--vscode-panel-border);
    }
    .message .meta {
      font-size: 0.8em;
      opacity: 0.7;
      margin-bottom: 4px;
    }
    .message .refs {
      margin-top: 6px;
      font-size: 0.85em;
      opacity: 0.8;
    }
    .action-card {
      align-self: flex-start;
      background: var(--vscode-editor-inlineValues-background, var(--vscode-editor-background));
      color: var(--vscode-foreground);
      border: 1px solid var(--vscode-panel-border);
      border-radius: 6px;
      padding: 10px;
      max-width: 95%;
      word-wrap: break-word;
      white-space: pre-wrap;
      line-height: 1.4;
    }
    .action-card .card-text {
      margin-bottom: 10px;
    }
    .action-card .card-buttons {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    .action-card .card-buttons button {
      padding: 6px 14px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-family: inherit;
      font-size: var(--vscode-font-size);
    }
    .action-card .card-buttons .primary-btn {
      background: var(--vscode-button-background);
      color: var(--vscode-button-foreground);
    }
    .action-card .card-buttons .primary-btn:hover {
      background: var(--vscode-button-hoverBackground);
    }
    .action-card .card-buttons .secondary-btn {
      background: var(--vscode-button-secondaryBackground, var(--vscode-editor-background));
      color: var(--vscode-button-secondaryForeground, var(--vscode-foreground));
      border: 1px solid var(--vscode-panel-border);
    }
    .action-card .card-buttons .secondary-btn:hover {
      background: var(--vscode-button-secondaryHoverBackground, var(--vscode-list-hoverBackground));
    }
    #input-row {
      display: flex;
      gap: 6px;
      padding: 8px;
      border-top: 1px solid var(--vscode-panel-border);
    }
    #input {
      flex: 1;
      padding: 6px 8px;
      border: 1px solid var(--vscode-input-border, transparent);
      background: var(--vscode-input-background);
      color: var(--vscode-input-foreground);
      border-radius: 4px;
      resize: none;
      font-family: inherit;
    }
    #send {
      padding: 6px 12px;
      border: none;
      border-radius: 4px;
      background: var(--vscode-button-background);
      color: var(--vscode-button-foreground);
      cursor: pointer;
    }
    #send:hover { background: var(--vscode-button-hoverBackground); }
    #send:disabled { opacity: 0.5; cursor: default; }
    .placeholder {
      color: var(--vscode-descriptionForeground);
      text-align: center;
      margin-top: 40px;
      font-style: italic;
    }
  </style>
</head>
<body>
  <div id="messages">
    <div class="placeholder">Ask about your fine-tuning project…</div>
  </div>
  <div id="input-row">
    <textarea id="input" rows="2" placeholder="Type a message…"></textarea>
    <button id="send">Send</button>
  </div>
  <script>
    const vscode = acquireVsCodeApi();
    const messagesEl = document.getElementById('messages');
    const input = document.getElementById('input');
    const sendBtn = document.getElementById('send');

    function appendMessage(role, text, meta) {
      const placeholder = document.querySelector('.placeholder');
      if (placeholder) placeholder.remove();
      const div = document.createElement('div');
      div.className = 'message ' + role;
      if (meta) {
        const parts = [];
        if (meta.confidence) parts.push('Confidence: ' + meta.confidence);
        if (meta.refs && meta.refs.length) parts.push('References: ' + meta.refs.join(', '));
        if (parts.length) {
          const m = document.createElement('div');
          m.className = 'meta';
          m.textContent = parts.join(' · ');
          div.appendChild(m);
        }
      }
      const body = document.createElement('div');
      body.textContent = text;
      div.appendChild(body);
      messagesEl.appendChild(div);
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function showActionCard(actionId, text, buttons) {
      const placeholder = document.querySelector('.placeholder');
      if (placeholder) placeholder.remove();
      const card = document.createElement('div');
      card.className = 'action-card';
      card.dataset.actionId = actionId;

      const textDiv = document.createElement('div');
      textDiv.className = 'card-text';
      textDiv.textContent = text;
      card.appendChild(textDiv);

      const btnRow = document.createElement('div');
      btnRow.className = 'card-buttons';
      buttons.forEach(function(btn, index) {
        const button = document.createElement('button');
        button.textContent = btn.label;
        button.className = index === 0 ? 'primary-btn' : 'secondary-btn';
        button.addEventListener('click', function() {
          // Disable all buttons to prevent double-clicks
          const allBtns = btnRow.querySelectorAll('button');
          allBtns.forEach(function(b) { b.disabled = true; });
          vscode.postMessage({
            command: 'actionButtonClicked',
            actionId: actionId,
            action: btn.action
          });
        });
        btnRow.appendChild(button);
      });
      card.appendChild(btnRow);
      messagesEl.appendChild(card);
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function send() {
      const text = input.value.trim();
      if (!text) return;
      appendMessage('user', text);
      input.value = '';
      sendBtn.disabled = true;
      vscode.postMessage({ command: 'sendMessage', text });
    }

    sendBtn.addEventListener('click', send);
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        send();
      }
    });

    window.addEventListener('message', (event) => {
      const message = event.data;
      switch (message.command) {
        case 'appendMessage':
          const meta = message.role === 'assistant'
            ? {
                confidence: message.confidence,
                refs: message.references,
              }
            : undefined;
          appendMessage(message.role, message.text, meta);
          sendBtn.disabled = false;
          break;
        case 'showActionCard':
          showActionCard(message.actionId, message.text, message.buttons);
          sendBtn.disabled = false;
          break;
      }
    });
  </script>
</body>
</html>`;
  }
}