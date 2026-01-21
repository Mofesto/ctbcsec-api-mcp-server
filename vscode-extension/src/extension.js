const vscode = require('vscode');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

let mcpServerProcess = null;
let outputChannel = null;

/**
 * Extension activation
 */
function activate(context) {
    console.log('CTBC Securities MCP Server extension is now active');

    // Create output channel
    outputChannel = vscode.window.createOutputChannel('CTBC MCP Server');
    context.subscriptions.push(outputChannel);

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('ctbcsec-mcp.start', startMCPServer)
    );
    context.subscriptions.push(
        vscode.commands.registerCommand('ctbcsec-mcp.stop', stopMCPServer)
    );
    context.subscriptions.push(
        vscode.commands.registerCommand('ctbcsec-mcp.restart', restartMCPServer)
    );
    context.subscriptions.push(
        vscode.commands.registerCommand('ctbcsec-mcp.showLogs', showLogs)
    );
    context.subscriptions.push(
        vscode.commands.registerCommand('ctbcsec-mcp.configure', configureMCPServer)
    );

    // Register MCP Server Provider
    registerMCPServerProvider(context);

    // Auto-start if configured
    const config = vscode.workspace.getConfiguration('ctbcsec-mcp');
    if (config.get('autoStart')) {
        setTimeout(() => {
            startMCPServer();
        }, 1000);
    }
}

/**
 * Register MCP Server Provider (for GitHub Copilot / Claude Desktop integration)
 */
function registerMCPServerProvider(context) {
    const mcpConfigPath = getMCPConfigPath();

    if (!fs.existsSync(mcpConfigPath)) {
        outputChannel.appendLine('MCP config file not found. Please run "Configure CTBC MCP Server" command');
    } else {
        outputChannel.appendLine(`MCP config file: ${mcpConfigPath}`);
    }
}

/**
 * Get MCP configuration file path
 */
function getMCPConfigPath() {
    const homeDir = os.homedir();

    // Detect VS Code variant
    let vscodeDir = 'Code'; // Default to Stable
    if (vscode.env.appName.includes('Insiders')) {
        vscodeDir = 'Code - Insiders';
    } else if (vscode.env.appName.includes('VSCodium')) {
        vscodeDir = 'VSCodium';
    } else if (vscode.env.appName.includes('Cursor')) {
        vscodeDir = 'Cursor';
    }

    if (process.platform === 'win32') {
        return path.join(homeDir, 'AppData', 'Roaming', vscodeDir, 'User', 'mcp.json');
    } else if (process.platform === 'darwin') {
        return path.join(homeDir, 'Library', 'Application Support', vscodeDir, 'User', 'mcp.json');
    } else {
        return path.join(homeDir, '.config', vscodeDir, 'User', 'mcp.json');
    }
}

/**
 * Configure MCP Server
 */
async function configureMCPServer() {
    const config = vscode.workspace.getConfiguration('ctbcsec-mcp');

    // Get configuration
    const username = await vscode.window.showInputBox({
        prompt: 'Enter CTBC Securities Account Username',
        value: config.get('username') || '',
        placeHolder: 'Your CTBC Securities username'
    });

    if (!username) {
        vscode.window.showWarningMessage('No username entered, configuration cancelled');
        return;
    }

    const certPath = await vscode.window.showInputBox({
        prompt: 'Enter Certificate File Path',
        value: config.get('certPath') || '',
        placeHolder: 'C:\\path\\to\\your\\certificate.cer'
    });

    if (!certPath) {
        vscode.window.showWarningMessage('No certificate path entered, configuration cancelled');
        return;
    }

    // Save configuration
    await config.update('username', username, vscode.ConfigurationTarget.Global);
    await config.update('certPath', certPath, vscode.ConfigurationTarget.Global);

    // Update MCP configuration file
    try {
        await updateMCPConfig(username, certPath);
        vscode.window.showInformationMessage('CTBC MCP Server configuration updated! Please reload VS Code for changes to take effect.');
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to update MCP configuration: ${error.message}`);
    }
}

/**
 * Update MCP configuration file (standard mcp.json format)
 */
async function updateMCPConfig(username, certPath) {
    const mcpConfigPath = getMCPConfigPath();
    const configDir = path.dirname(mcpConfigPath);

    outputChannel.appendLine(`Preparing to write MCP config: ${mcpConfigPath}`);

    // Ensure directory exists
    if (!fs.existsSync(configDir)) {
        fs.mkdirSync(configDir, { recursive: true });
        outputChannel.appendLine(`Created directory: ${configDir}`);
    }

    // Read or create configuration
    let mcpConfig = { servers: {}, inputs: [] };

    if (fs.existsSync(mcpConfigPath)) {
        try {
            const content = fs.readFileSync(mcpConfigPath, 'utf8');
            mcpConfig = JSON.parse(content);
            if (!mcpConfig.servers) {
                mcpConfig.servers = {};
            }
            if (!mcpConfig.inputs) {
                mcpConfig.inputs = [];
            }
        } catch (error) {
            outputChannel.appendLine(`Failed to read MCP config: ${error.message}`);
        }
    }

    // Add CTBC MCP Server configuration
    mcpConfig.servers['ctbcsec-mcp-server'] = {
        type: 'stdio',
        command: 'python',
        args: ['-m', 'ctbcsec_mcp.server'],
        env: {
            CTBC_USERNAME: '${input:ctbc_username}',
            CTBC_PASSWORD: '${input:ctbc_password}',
            CTBC_CERT_PATH: '${input:ctbc_cert_path}',
            CTBC_CERT_PASSWORD: '${input:ctbc_cert_password}'
        }
    };

    // Update inputs (ensure no duplicates)
    const inputIds = new Set(mcpConfig.inputs.map(i => i.id));
    const newInputs = [
        { id: 'ctbc_username', type: 'promptString', description: 'CTBC_USERNAME (CTBC Securities Account)' },
        { id: 'ctbc_password', type: 'promptString', description: 'CTBC_PASSWORD (CTBC Securities Password)' },
        { id: 'ctbc_cert_path', type: 'promptString', description: 'CTBC_CERT_PATH (Certificate Path)' },
        { id: 'ctbc_cert_password', type: 'promptString', description: 'CTBC_CERT_PASSWORD (Certificate Password)' }
    ];

    for (const input of newInputs) {
        if (!inputIds.has(input.id)) {
            mcpConfig.inputs.push(input);
        }
    }

    // Write configuration
    fs.writeFileSync(mcpConfigPath, JSON.stringify(mcpConfig, null, 2), 'utf8');
    outputChannel.appendLine(`MCP config written: ${mcpConfigPath}`);
}

/**
 * Start MCP Server
 */
async function startMCPServer() {
    if (mcpServerProcess) {
        vscode.window.showWarningMessage('CTBC MCP Server is already running');
        return;
    }

    try {
        const config = vscode.workspace.getConfiguration('ctbcsec-mcp');
        const username = config.get('username');
        const certPath = config.get('certPath');

        if (!username || !certPath) {
            vscode.window.showErrorMessage(
                'Please configure CTBC Securities account and certificate path in settings (ctbcsec-mcp.username, ctbcsec-mcp.certPath)'
            );
            return;
        }

        // Prompt for passwords
        const password = await vscode.window.showInputBox({
            prompt: 'Enter CTBC Securities Password',
            password: true,
            placeHolder: 'Password will not be saved'
        });

        if (!password) {
            vscode.window.showWarningMessage('No password entered, startup cancelled');
            return;
        }

        const certPassword = await vscode.window.showInputBox({
            prompt: 'Enter Certificate Password (if required)',
            password: true,
            placeHolder: 'Leave blank if no password'
        });

        outputChannel.appendLine('Starting CTBC MCP Server...');
        outputChannel.show(true);

        // Set environment variables
        const env = {
            ...process.env,
            CTBC_USERNAME: username,
            CTBC_PASSWORD: password,
            CTBC_CERT_PATH: certPath
        };

        if (certPassword) {
            env.CTBC_CERT_PASSWORD = certPassword;
        }

        // Set Python environment variables for UTF-8 output
        env.PYTHONIOENCODING = 'utf-8';
        env.PYTHONUTF8 = '1';

        // Start Python MCP Server
        mcpServerProcess = spawn('python', ['-m', 'ctbcsec_mcp.server'], {
            env: env,
            cwd: vscode.workspace.rootPath || process.cwd(),
            shell: false
        });

        mcpServerProcess.stdout.on('data', (data) => {
            try {
                const text = data.toString('utf8');
                outputChannel.appendLine(`[OUT] ${text}`);
            } catch (e) {
                outputChannel.appendLine(`[OUT] ${data.toString()}`);
            }
        });

        mcpServerProcess.stderr.on('data', (data) => {
            try {
                const text = data.toString('utf8');
                outputChannel.appendLine(`[ERR] ${text}`);
            } catch (e) {
                outputChannel.appendLine(`[ERR] ${data.toString()}`);
            }
        });

        mcpServerProcess.on('close', (code) => {
            outputChannel.appendLine(`CTBC MCP Server stopped (exit code: ${code})`);
            mcpServerProcess = null;

            if (code !== 0) {
                vscode.window.showErrorMessage(`CTBC MCP Server exited abnormally (code: ${code})`);
            }
        });

        mcpServerProcess.on('error', (error) => {
            outputChannel.appendLine(`Error: ${error.message}`);
            vscode.window.showErrorMessage(`Failed to start MCP Server: ${error.message}`);
            mcpServerProcess = null;
        });

        vscode.window.showInformationMessage('CTBC MCP Server started');

    } catch (error) {
        outputChannel.appendLine(`Startup failed: ${error.message}`);
        vscode.window.showErrorMessage(`Failed to start MCP Server: ${error.message}`);
    }
}

/**
 * Stop MCP Server
 */
function stopMCPServer() {
    if (!mcpServerProcess) {
        vscode.window.showWarningMessage('CTBC MCP Server is not running');
        return;
    }

    outputChannel.appendLine('Stopping CTBC MCP Server...');
    mcpServerProcess.kill();
    mcpServerProcess = null;
    vscode.window.showInformationMessage('CTBC MCP Server stopped');
}

/**
 * Restart MCP Server
 */
async function restartMCPServer() {
    stopMCPServer();
    // Wait to ensure process has terminated
    await new Promise(resolve => setTimeout(resolve, 1000));
    await startMCPServer();
}

/**
 * Show logs
 */
function showLogs() {
    outputChannel.show(true);
}

/**
 * Extension deactivation
 */
function deactivate() {
    if (mcpServerProcess) {
        mcpServerProcess.kill();
    }
}

module.exports = {
    activate,
    deactivate
};
