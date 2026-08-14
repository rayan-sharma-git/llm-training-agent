/**
 * BackendManager: Starts, stops, and manages the Python FastAPI backend process.
 */
import * as vscode from 'vscode';
import { spawn, ChildProcess } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';
import * as net from 'net';
import * as http from 'http';

const DEFAULT_PORT = 8000;
const STARTUP_TIMEOUT_MS = 30000;
const POLL_INTERVAL_MS = 1000;

let backendProcess: ChildProcess | null = null;
let isBackendRunning = false;

function getBackendDir(context: vscode.ExtensionContext): string {
  // Prefer the packaged backend inside the extension
  const packaged = path.join(context.extensionPath, 'backend');
  if (fs.existsSync(path.join(packaged, 'main.py'))) {
    return packaged;
  }
  // Dev fallback: sibling backend folder
  const dev = path.join(context.extensionPath, '..', 'backend');
  if (fs.existsSync(path.join(dev, 'main.py'))) {
    return path.resolve(dev);
  }
  return packaged;
}

function findPython(backendDir: string): string {
  // Prefer venv inside backend or workspace
  const candidates = [
    path.join(backendDir, 'venv310', 'Scripts', 'python.exe'),
    path.join(backendDir, 'venv', 'Scripts', 'python.exe'),
    path.join(backendDir, '..', '..', 'venv310', 'Scripts', 'python.exe'),
    path.join(backendDir, '..', '..', 'venv', 'Scripts', 'python.exe'),
    'python',
    'python3',
  ];
  for (const c of candidates) {
    if (c === 'python' || c === 'python3') {
      return c;
    }
    if (fs.existsSync(c)) {
      return c;
    }
  }
  return 'python';
}

export async function isPortOpen(port: number = DEFAULT_PORT): Promise<boolean> {
  return new Promise((resolve) => {
    const socket = net.createConnection({ port, host: '127.0.0.1' }, () => {
      socket.destroy();
      resolve(true);
    });
    socket.on('error', () => resolve(false));
    socket.setTimeout(1000, () => {
      socket.destroy();
      resolve(false);
    });
  });
}

export async function healthCheck(port: number = DEFAULT_PORT): Promise<boolean> {
  return new Promise((resolve) => {
    const req = http.get(
      { hostname: '127.0.0.1', port, path: '/api/v1/health', timeout: 2000 },
      (res) => {
        let data = '';
        res.on('data', (c) => (data += c));
        res.on('end', () => {
          try {
            const j = JSON.parse(data);
            resolve(j.status === 'ok' || j.status === 'healthy');
          } catch {
            resolve(res.statusCode === 200);
          }
        });
      }
    );
    req.on('error', () => resolve(false));
    req.on('timeout', () => {
      req.destroy();
      resolve(false);
    });
  });
}

export async function waitForHealth(timeoutMs: number = STARTUP_TIMEOUT_MS): Promise<boolean> {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    if (await healthCheck()) {
      isBackendRunning = true;
      return true;
    }
    await new Promise((r) => setTimeout(r, POLL_INTERVAL_MS));
  }
  return false;
}

export async function startBackend(context: vscode.ExtensionContext): Promise<boolean> {
  // Already healthy?
  if (await healthCheck()) {
    isBackendRunning = true;
    return true;
  }

  // Port occupied by something else?
  if (await isPortOpen()) {
    // Wait a bit for health
    if (await waitForHealth(5000)) {
      return true;
    }
  }

  const backendDir = getBackendDir(context);
  const mainPy = path.join(backendDir, 'main.py');
  if (!fs.existsSync(mainPy)) {
    vscode.window.showErrorMessage(
      'Python backend not found. Expected main.py at: ' + backendDir
    );
    return false;
  }

  const python = findPython(backendDir);
  const logChannel = vscode.window.createOutputChannel('LLM Training Agent Backend');
  logChannel.appendLine('Starting backend with: ' + python);
  logChannel.appendLine('Backend dir: ' + backendDir);

  try {
    backendProcess = spawn(
      python,
      ['-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', String(DEFAULT_PORT)],
      {
        cwd: backendDir,
        env: { ...process.env, PYTHONUNBUFFERED: '1' },
        stdio: ['ignore', 'pipe', 'pipe'],
      }
    );

    backendProcess.stdout?.on('data', (d) => logChannel.append(d.toString()));
    backendProcess.stderr?.on('data', (d) => logChannel.append(d.toString()));
    backendProcess.on('exit', (code) => {
      logChannel.appendLine('Backend exited with code ' + code);
      isBackendRunning = false;
      backendProcess = null;
    });
    backendProcess.on('error', (err) => {
      logChannel.appendLine('Backend spawn error: ' + err.message);
      isBackendRunning = false;
    });

    const ok = await waitForHealth(STARTUP_TIMEOUT_MS);
    if (!ok) {
      vscode.window.showWarningMessage(
        'Backend started but health check timed out. Analyze Project may fail until the backend is ready.'
      );
    } else {
      logChannel.appendLine('Backend is healthy.');
    }
    return ok;
  } catch (err: any) {
    vscode.window.showErrorMessage('Failed to start Python backend: ' + (err?.message || err));
    return false;
  }
}

export async function stopBackend(): Promise<void> {
  if (backendProcess && !backendProcess.killed) {
    backendProcess.kill();
    backendProcess = null;
  }
  isBackendRunning = false;
}

export function getIsBackendRunning(): boolean {
  return isBackendRunning;
}

export function getBackendBaseUrl(): string {
  return 'http://127.0.0.1:' + DEFAULT_PORT;
}
