import * as vscode from 'vscode';
import * as cp from 'child_process';
import * as path from 'path';
import * as util from 'util';

const exec = util.promisify(cp.exec);

// State view data provider
class StateViewProvider implements vscode.TreeDataProvider<StateItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<StateItem | undefined | void> = new vscode.EventEmitter<StateItem | undefined | void>();
    readonly onDidChangeTreeData: vscode.Event<StateItem | undefined | void> = this._onDidChangeTreeData.event;

    private stateData: any = null;

    refresh(data?: any): void {
        this.stateData = data;
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: StateItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: StateItem): Thenable<StateItem[]> {
        if (!this.stateData) {
            return Promise.resolve([new StateItem('No scan data', 'Run "Repo Doctor: Scan Repository" to begin', vscode.TreeItemCollapsibleState.None)]);
        }

        if (!element) {
            // Root items
            const items: StateItem[] = [
                new StateItem(`Score: ${this.stateData.score}/100`, `Energy: ${this.stateData.energy?.toFixed(2) || 'N/A'}`, vscode.TreeItemCollapsibleState.None),
                new StateItem(`Healthy: ${this.stateData.healthy ? '✓' : '✗'}`, '', vscode.TreeItemCollapsibleState.None),
                new StateItem(`Releaseable: ${this.stateData.releaseable ? '✓' : '✗'}`, '', vscode.TreeItemCollapsibleState.None),
            ];

            if (this.stateData.hard_failures?.length > 0) {
                items.push(new StateItem('Hard Failures', `${this.stateData.hard_failures.length} invariants failed`, vscode.TreeItemCollapsibleState.Expanded));
            }

            return Promise.resolve(items);
        }

        if (element.label?.toString().startsWith('Hard Failures')) {
            return Promise.resolve(
                this.stateData.hard_failures.map((f: string) =>
                    new StateItem(f, 'Click to see repair plan', vscode.TreeItemCollapsibleState.None)
                )
            );
        }

        return Promise.resolve([]);
    }
}

class StateItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly description: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState
    ) {
        super(label, collapsibleState);
        this.tooltip = description;
    }
}

// Main extension activation
export function activate(context: vscode.ExtensionContext) {
    console.log('Repo Doctor extension is now active');

    const stateProvider = new StateViewProvider();

    // Register tree view
    vscode.window.registerTreeDataProvider('repoDoctor.stateView', stateProvider);

    // Scan command
    let scanCommand = vscode.commands.registerCommand('repoDoctor.scan', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }

        const rootPath = workspaceFolders[0].uri.fsPath;
        const pythonPath = vscode.workspace.getConfiguration('repoDoctor').get('pythonPath', 'python3');

        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Repo Doctor: Scanning repository...',
            cancellable: false
        }, async (progress) => {
            try {
                const { stdout, stderr } = await exec(
                    `${pythonPath} -m repo_doctor scan . --json`,
                    { cwd: rootPath, timeout: 60000 }
                );

                const data = JSON.parse(stdout);
                stateProvider.refresh(data);

                // Show summary
                const message = `Score: ${data.score}/100 | Energy: ${data.energy?.toFixed(2)} | Releaseable: ${data.releaseable ? '✓' : '✗'}`;
                vscode.window.showInformationMessage(message);

            } catch (error) {
                vscode.window.showErrorMessage(`Scan failed: ${error}`);
            }
        });
    });

    // Scan with sensors command
    let scanSensorsCommand = vscode.commands.registerCommand('repoDoctor.scanWithSensors', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }

        const rootPath = workspaceFolders[0].uri.fsPath;
        const pythonPath = vscode.workspace.getConfiguration('repoDoctor').get('pythonPath', 'python3');

        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Repo Doctor: Full scan with external sensors...',
            cancellable: false
        }, async (progress) => {
            try {
                const { stdout } = await exec(
                    `${pythonPath} -m repo_doctor scan . --sensors --json`,
                    { cwd: rootPath, timeout: 120000 }
                );

                const data = JSON.parse(stdout);
                stateProvider.refresh(data);

                vscode.window.showInformationMessage(`Full scan complete. Score: ${data.score}/100`);

            } catch (error) {
                vscode.window.showErrorMessage(`Full scan failed: ${error}`);
            }
        });
    });

    // Fix command
    let fixCommand = vscode.commands.registerCommand('repoDoctor.fix', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }

        const rootPath = workspaceFolders[0].uri.fsPath;
        const pythonPath = vscode.workspace.getConfiguration('repoDoctor').get('pythonPath', 'python3');

        const answer = await vscode.window.showWarningMessage(
            'Apply auto-fixes? This will modify files.',
            'Yes', 'Dry Run', 'Cancel'
        );

        if (answer === 'Cancel' || !answer) {
            return;
        }

        const dryRunFlag = answer === 'Dry Run' ? '--dry-run' : '';

        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Repo Doctor: Applying fixes...',
            cancellable: false
        }, async (progress) => {
            try {
                const { stdout } = await exec(
                    `${pythonPath} -m repo_doctor scan . --fix ${dryRunFlag}`,
                    { cwd: rootPath, timeout: 120000 }
                );

                vscode.window.showInformationMessage(`Fixes applied. Check output for details.`);
                console.log(stdout);

            } catch (error) {
                vscode.window.showErrorMessage(`Fix failed: ${error}`);
            }
        });
    });

    // Show state command
    let showStateCommand = vscode.commands.registerCommand('repoDoctor.showState', () => {
        vscode.commands.executeCommand('repoDoctor.stateView.focus');
    });

    // Repair plan command
    let repairPlanCommand = vscode.commands.registerCommand('repoDoctor.repairPlan', async () => {
        vscode.window.showInformationMessage('Repair plan generation - Feature coming soon!');
    });

    context.subscriptions.push(
        scanCommand,
        scanSensorsCommand,
        fixCommand,
        showStateCommand,
        repairPlanCommand
    );

    // Auto-scan on save if enabled
    const config = vscode.workspace.getConfiguration('repoDoctor');
    if (config.get('autoScanOnSave', false)) {
        vscode.workspace.onDidSaveTextDocument((document) => {
            if (document.languageId === 'python') {
                vscode.commands.executeCommand('repoDoctor.scan');
            }
        });
    }
}

export function deactivate() {
    console.log('Repo Doctor extension is now deactivated');
}
