/**
 * BackendManager — manages the Python backend subprocess lifecycle.
 *
 * Responsibilities:
 *   - Auto-start the FastAPI backend when the extension activates.
 *   - Poll the /health endpoint until the backend is ready.
 *   - Provide the base URL for the ApiClient.
 *   - Gracefully shut down the process on extension deactivation.
 *
 * The backend is launched with the project's venv Python interpreter.
 * If the venv is not found, the system Python is used as a fallback.
 */
import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { spawn, ChildProcess } from 'child_process';

export interface BackendStatus {
  status: 'starting' | 'running' | 'stopped' | 'failed';
  url?: string;
  error?: string;
}

export class BackendManager {
  private context: vscode.ExtensionContext;
  private backendProcess: ChildProcess | null = null;
  private backendUrl: string = 'http://127.0.0.1:8000';
  private healthCheckTimer: NodeJS.Timeout | null = null;
  private resolveReady: (() => void) | null = null;
  private readyPromise: Promise<void> | null = null;
  private startingPromise: Promise<boolean> | null = null;
  private shutdownRequested = false;
  private outputChannel: vscode.OutputChannel;

  constructor(context: vscode.ExtensionContext) {
    this.context = context;
    this.backendUrl = context.globalState.get<string>('backendUrl') || 'http://127.0.0.1:8000';
    this.outputChannel = vscode.window.createOutputChannel('LLM Training Agent: Backend');
  }

  /**
   * Log a message to the backend output channel.
   */
  private log(message: string): void {
    this.outputChannel.appendLine(`[${new Date().toISOString()}] ${message}`);
  }

  /**
   * Ensure the backend is running. If it is not, start it.
   * Returns a promise that resolves once the backend health check passes.
   */
  async ensureRunning(): Promise<boolean> {
    // If already running, verify health
    if (this.backendProcess && this.backendProcess.exitCode === null) {
      if (await this.checkHealth()) {
        return true;
      }
    }

    // Reuse an in-progress startup to avoid duplicate backend processes.
    if (this.startingPromise) {
      return this.startingPromise;
    }

    // Start fresh
    this.startingPromise = this.start();
    try {
      return await this.startingPromise;
    } finally {
      this.startingPromise = null;
    }
  }

  /**
   * Start the backend subprocess and wait for it to become healthy.
   */
  async start(): Promise<boolean> {
    this.shutdownRequested = false;
    this.readyPromise = new Promise<void>((resolve) => {
      this.resolveReady = resolve;
    });

    const backendPath = this.findBackendPath();
    if (!backendPath) {
      vscode.window.showWarningMessage(
        'LLM Training Agent: Backend path not found. Please ensure the Python backend exists.'
      );
      this.cleanupProcess();
      return false;
    }

    const pythonExe = this.findPythonExecutable();
    const cwd = path.dirname(backendPath);

    try {
      // Quick dependency sanity check so a backend with missing dependencies
      // fails fast with a useful message instead of silently crashing.
      const { execFileSync } = require('child_process') as typeof import('child_process');
      try {
        execFileSync(
          pythonExe,
          ['-c', 'import fastapi, uvicorn, pydantic, pydantic_settings'],
          { cwd, stdio: 'ignore', timeout: 15000 }
        );
      } catch (depError) {
        this.log(`Dependency check failed: ${depError instanceof Error ? depError.message : String(depError)}`);
        vscode.window.showWarningMessage(
          'LLM Training Agent: Python backend dependencies are missing. ' +
          `Please run "pip install -r requirements.txt" using "${pythonExe}".`
        );
        this.cleanupProcess();
        return false;
      }

      this.log(`Starting backend: ${pythonExe} -m uvicorn main:app --host 127.0.0.1 --port 8000`);
      this.backendProcess = spawn(
        pythonExe,
        ['-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8000', '--no-server-header'],
        {
          cwd,
          stdio: ['ignore', 'pipe', 'pipe'],
          env: { ...process.env, PYTHONPATH: cwd },
        }
      );

      this.backendProcess.stdout?.on('data', (data: Buffer) => {
        const output = stripAnsi(data.toString());
        this.log(`[stdout] ${output.trimEnd()}`);
      });

      this.backendProcess.stderr?.on('data', (data: Buffer) => {
        const output = stripAnsi(data.toString());
        this.log(`[stderr] ${output.trimEnd()}`);
        if (output.includes('Uvicorn running')) {
          // Backend is starting up; health check will confirm
        }
      });

      this.backendProcess.on('exit', (code) => {
        this.log(`Backend process exited with code ${code}`);
        this.backendProcess = null;
      });

      // Start polling health endpoint
      this.startHealthPolling();

      // Wait for health check to pass (with timeout). In parallel, resolve
      // the ready promise if Uvicorn reports it is running.
      const timeout = setTimeout(() => {
        this.log('Backend startup timed out after 15s.');
        if (this.resolveReady) {
          this.resolveReady();
        }
      }, 15000); // 15 second timeout

      // Also listen for stdout/stderr for direct resolution on "Uvicorn running"
      this.backendProcess.stderr?.on('data', (data: Buffer) => {
        const output = stripAnsi(data.toString());
        if (output.includes('Uvicorn running') && this.resolveReady) {
          clearTimeout(timeout);
          this.resolveReady();
          this.resolveReady = null;
        }
      });

      await this.readyPromise;
      clearTimeout(timeout);

      if (await this.checkHealth()) {
        this.log('Backend is ready.');
        return true;
      } else {
        this.log('Backend started but health check failed.');
        vscode.window.showWarningMessage(
          'LLM Training Agent: Backend started but health check failed. ' +
          'Check the "LLM Training Agent: Backend" output channel for details.'
        );
        return false;
      }
    } catch (error) {
      this.log(`Failed to start backend: ${error instanceof Error ? error.message : String(error)}`);
      vscode.window.showWarningMessage(
        `LLM Training Agent: Failed to start backend: ${error instanceof Error ? error.message : String(error)}`
      );
      return false;
    }
  }

  /**
   * Check the backend health endpoint.
   */
  async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.backendUrl}/api/v1/health`, {
        signal: AbortSignal.timeout(5000),
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  /**
   * Periodically poll the health endpoint and resolve the ready promise when healthy.
   */
  private startHealthPolling(): void {
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
    }
    this.healthCheckTimer = setInterval(async () => {
      if (this.backendProcess && this.backendProcess.exitCode === null) {
        const healthy = await this.checkHealth();
        if (healthy && this.resolveReady) {
          this.log('Health check passed.');
          this.resolveReady();
          this.resolveReady = null;
          if (this.healthCheckTimer) {
            clearInterval(this.healthCheckTimer);
            this.healthCheckTimer = null;
          }
        }
      }
    }, 1000);
  }

  /**
   * Get the backend URL.
   */
  getBaseUrl(): string {
    return this.backendUrl;
  }

  /**
   * Find the backend entry point (main.py).
   *
   * Resolution order:
   *   1. backend/main.py packaged inside the extension folder
   *   2. backend/main.py in the repository parent of the extension folder (dev checkout)
   *   3. backend/main.py adjacent to the currently open workspace folder
   */
  private findBackendPath(): string | null {
    const extFsPath = this.context.extensionUri.fsPath;
    const workspaceFolders = vscode.workspace.workspaceFolders ?? [];

    const candidates = [
      // Packaged .vsix: extension folder contains backend/ copied at build time.
      path.join(extFsPath, 'backend', 'main.py'),
      // Dev repo layout: d:\...\PROJECT_TEMPLATE\extension + backend next to it.
      path.join(extFsPath, '..', 'backend', 'main.py'),
      // Workspace-relative layout (workspace/backend).
      ...workspaceFolders.map((folder) =>
        path.join(folder.uri.fsPath, 'backend', 'main.py')
      ),
      // Workspace-parent layout (parent/backend).
      ...workspaceFolders.map((folder) =>
        path.join(folder.uri.fsPath, '..', 'backend', 'main.py')
      ),
    ];

    for (const candidate of candidates) {
      if (fs.existsSync(candidate)) {
        this.log(`Using backend at: ${candidate}`);
        return candidate;
      }
    }

    this.log('Could not find backend/main.py.');
    return null;
  }

  /**
   * Find the Python executable to run the backend.
   *
   * Resolution order:
   *   1. venv310 checked into / next to the extension folder
   *   2. venv310 in the repository parent of the extension folder (dev checkout)
   *   3. venv310 adjacent to the open workspace folder
   *   4. system `python` on PATH
   */
  private findPythonExecutable(): string {
    const extFsPath = this.context.extensionUri.fsPath;
    const workspaceFolders = vscode.workspace.workspaceFolders ?? [];

    const venvCandidates = [
      path.join(extFsPath, 'venv310', 'Scripts', 'python.exe'),
      path.join(extFsPath, '..', 'venv310', 'Scripts', 'python.exe'),
      path.join(extFsPath, '..', '..', 'venv310', 'Scripts', 'python.exe'),
      path.join(extFsPath, '..', '..', '..', 'venv310', 'Scripts', 'python.exe'),
      ...workspaceFolders.map((folder) =>
        path.join(folder.uri.fsPath, '..', 'venv310', 'Scripts', 'python.exe')
      ),
      ...workspaceFolders.map((folder) =>
        path.join(folder.uri.fsPath, 'venv310', 'Scripts', 'python.exe')
      ),
    ];

    for (const candidate of venvCandidates) {
      if (fs.existsSync(candidate)) {
        this.log(`Using Python: ${candidate}`);
        return candidate;
      }
    }

    // Fallback to system python
    this.log('Using system python (no venv310 found).');
    return 'python';
  }

  /**
   * Clean up the backend process.
   */
  private cleanupProcess(): void {
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
      this.healthCheckTimer = null;
    }
    if (this.backendProcess) {
      this.backendProcess.kill();
      this.backendProcess = null;
    }
  }

  /**
   * Shut down the backend gracefully.
   */
  async shutdown(): Promise<void> {
    this.shutdownRequested = true;
    this.cleanupProcess();
    this.outputChannel.dispose();
  }

  /**
   * Get current backend status.
   */
  getStatus(): BackendStatus {
    if (!this.backendProcess) {
      return { status: 'stopped', url: this.backendUrl };
    }
    if (this.backendProcess.exitCode === null) {
      return { status: 'running', url: this.backendUrl };
    }
    return { status: 'failed', url: this.backendUrl, error: 'Process exited' };
  }

  /**
   * Get the backend URL, starting the backend if needed.
   */
  async getBackendUrl(): Promise<string> {
    if (!(await this.ensureRunning())) {
      throw new Error('Backend failed to start');
    }
    return this.backendUrl;
  }
}

/**
 * Utility to strip ANSI escape sequences from terminal output.
 */
function stripAnsi(text: string): string {
  // eslint-disable-next-line no-control-regex
  return text.replace(/\x1b\[[0-9;]*m/g, '');
}