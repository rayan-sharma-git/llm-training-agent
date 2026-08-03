export const mock = {};

export const workspace = {
  workspaceFolders: {
    at: (_index: number) => ({ uri: { fsPath: '/dummy/workspace' } }),
  },
  getConfiguration: (_section?: string) => ({
    get: (_key: string, defaultValue?: any) => defaultValue,
    has: (_key: string) => false,
    update: vi.fn(() => Promise.resolve()),
  }),
};

export const window = {
  showInformationMessage: vi.fn(),
  showErrorMessage: vi.fn(),
  showInputBox: vi.fn(),
  showOpenDialog: vi.fn(),
  withProgress: (_options: any, task: any) => task({ report: vi.fn() }, { isCancellationRequested: false }),
  createWebviewPanel: vi.fn(() => ({ webview: { html: '' } })),
};

export const commands = {
  registerCommand: vi.fn((_id: string, _handler: any) => ({ dispose: vi.fn() })),
  getCommands: vi.fn(() => Promise.resolve([])),
  executeCommand: vi.fn(() => Promise.resolve(undefined)),
};

export const TreeItemCollapsibleState = {
  None: 0,
};

export class TreeItem {
  constructor(public label: string, public collapsibleState: number = 0, public command?: any) {}
}

export const EventEmitter = () => ({
  event: undefined,
  fire: vi.fn(),
});

export class TreeDataProvider {
  onDidChangeTreeData = { event: undefined };
  getTreeItem = vi.fn(() => new TreeItem(''));
  getChildren = vi.fn(() => []);
}

export const TreeDataProvider = TreeDataProvider as any;

export const windowState = {
  registerTreeDataProvider: vi.fn((_id: string, provider: any) => provider),
};

export const globalState = {
  update: vi.fn(() => Promise.resolve()),
};

export const ExtensionContext = function ExtensionContext() {
  return { subscriptions: [], globalState: globalState };
} as any;

export const ConfigurationTarget = {
  Global: 1,
};

export const ProgressLocation = {
  Notification: 2,
};

export const ViewColumn = {
  One: 1,
};

export default mock;