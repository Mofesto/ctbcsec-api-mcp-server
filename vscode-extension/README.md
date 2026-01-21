# CTBC Securities MCP Server Extension

**CTBC Securities MCP Server** extension for Visual Studio Code provides seamless integration with the CTBC Securities CTS Trading API through the Model Context Protocol (MCP).

## Features

- 🚀 **Quick Setup**: One-command configuration wizard
- 🔄 **Server Management**: Start, stop, and restart MCP server from command palette
- 📊 **Real-time Logs**: Built-in output channel for server logs
- 🔐 **Secure Credentials**: Password prompts (credentials never saved)
- 🌐 **Cross-platform**: Windows, macOS, and Linux support
- 🤖 **AI Integration**: Works with GitHub Copilot, Claude Desktop, and other MCP clients

## Installation

### From VS Code Marketplace

1. Open VS Code
2. Press `Ctrl+Shift+X` (Windows/Linux) or `Cmd+Shift+X` (macOS) to open Extensions
3. Search for "CTBC Securities MCP Server"
4. Click **Install**

### From VSIX File

1. Download the `.vsix` file from [GitHub Releases](https://github.com/YOUR_USERNAME/ctbcsec-api-mcp-server/releases)
2. Open VS Code
3. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
4. Type "Install from VSIX" and select **Extensions: Install from VSIX...**
5. Select the downloaded `.vsix` file

## Prerequisites

- **Python 3.10+** installed and available in PATH
- **CTBC Securities Account** with trading permissions
- **Digital Certificate** for API authentication
- **ctbcsec-mcp-server** Python package:
  ```bash
  pip install ctbcsec-mcp-server
  ```

## Quick Start

### 1. Configure the Extension

Open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) and run:

```
CTBC MCP: Configure CTBC MCP Server
```

Enter the following information when prompted:
- CTBC Securities username
- Path to your digital certificate file

The extension will automatically create/update the MCP configuration file (`mcp.json`) for you.

### 2. Start the Server

From the Command Palette, run:

```
CTBC MCP: Start CTBC MCP Server
```

You'll be prompted to enter:
- CTBC Securities password (not saved)
- Certificate password (if required)

### 3. View Logs

To see server output and debug information:

```
CTBC MCP: Show CTBC MCP Server Logs
```

## Available Commands

| Command | Description |
|---------|-------------|
| `CTBC MCP: Configure` | Run configuration wizard |
| `CTBC MCP: Start` | Start the MCP server |
| `CTBC MCP: Stop` | Stop the MCP server |
| `CTBC MCP: Restart` | Restart the MCP server |
| `CTBC MCP: Show Logs` | Display server logs |

## Configuration

The extension adds the following settings to VS Code:

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `ctbcsec-mcp.username` | string | `""` | CTBC Securities account username |
| `ctbcsec-mcp.certPath` | string | `""` | Path to certificate file |
| `ctbcsec-mcp.autoStart` | boolean | `false` | Auto-start server when VS Code starts |

## Usage with AI Tools

### GitHub Copilot

Once configured, the MCP server will be automatically available to GitHub Copilot. You can ask Copilot to:
- Query market data
- Place trades (if enabled)
- Check account information
- Analyze trading history

### Claude Desktop

The configuration wizard creates a standard `mcp.json` file compatible with Claude Desktop. Restart Claude Desktop after configuration.

## Troubleshooting

### Server won't start

1. Verify Python is installed: `python --version`
2. Verify the package is installed: `pip show ctbcsec-mcp-server`
3. Check the output logs for error messages

### Configuration not saved

- Settings are stored in VS Code user settings (global)
- Passwords are never saved and must be entered each time

### Connection issues

- Verify your CTBC Securities account credentials
- Ensure your digital certificate is valid and accessible
- Check your firewall settings

## Links

- [GitHub Repository](https://github.com/YOUR_USERNAME/ctbcsec-api-mcp-server)
- [PyPI Package](https://pypi.org/project/ctbcsec-mcp-server/)
- [Documentation](https://github.com/YOUR_USERNAME/ctbcsec-api-mcp-server#readme)
- [Report Issues](https://github.com/YOUR_USERNAME/ctbcsec-api-mcp-server/issues)

## License

MIT License - see [LICENSE](https://github.com/YOUR_USERNAME/ctbcsec-api-mcp-server/blob/main/LICENSE)

## Support

For questions, issues, or feature requests:
- Open an issue on [GitHub](https://github.com/YOUR_USERNAME/ctbcsec-api-mcp-server/issues)
- Email: support@ctbcsec.com

---

**Disclaimer**: This is an unofficial extension. Trading involves risk. Use at your own discretion.
