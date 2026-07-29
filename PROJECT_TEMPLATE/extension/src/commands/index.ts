import os
BASE = "d:\\Documents\\LLM_Training_Agent\\PROJECT_TEMPLATE\\extension\\src"
def w(r,c):
 path=os.path.join(BASE,r)
 os.makedirs(os.path.dirname(path),exist_ok=True)
 with open(path,"w",encoding="utf-8") as f: f.write(c)
 print("OK:"+r)
print("Builder ready")


private registerAnalyzeProject(): void {
  const disposable = vscode.commands.registerCommand("llmTrainingAgent.analyzeProject", async () => {
    try {
      this.stateManager.setAnalysisStatus("scanning");
      this.stateManager.setError(null);
      const workspaceFolders = vscode.workspace.workspaceFolders;
      if (!workspaceFolders || workspaceFolders.length === 0) {
        throw new Error("No workspace folder open. Please open a project first.");
      }
      const projectPath = workspaceFolders[0].uri.fsPath;
      await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: "LLM Training Agent: Analyzing Project",
        cancellable: true
      }, async (progress, token) => {
        token.onCancellationRequested(() => { this.stateManager.setAnalysisStatus("cancelled"); });
        progress.report({ message: "Connecting to analysis engine..." });
        const result = await this.apiClient.post("/api/v1/project/analyze", { projectPath });
        progress.report({ message: "Processing results..." });
        this.stateManager.setProjectContext(result.project);
        this.stateManager.setCurrentReport(result.report);
        this.stateManager.setAnalysisStatus("complete");
        vscode.window.showInformationMessage("Project analysis complete!");
      });
    } catch (error) {
      const msg = error instanceof Error ? error.message : "Unknown error";
      this.stateManager.setError(msg);
      this.stateManager.setAnalysisStatus("failed");
      vscode.window.showErrorMessage("Analysis failed: " + msg);
    }
  });
  this.disposables.push(disposable);
}
