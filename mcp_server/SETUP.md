# MCP Server Setup Guide

## Quick Start

1. **Run the setup script** (creates a venv and installs deps — no global install needed):
   ```bash
   cd mcp_server
   python3 setup_env.py
   ```
   This creates `.venv/` and prints the exact Cursor config to use. **Use the printed config** — it points to the venv Python so the server works without global dependencies.

2. **Ensure the Curio Decision Record service is running:**
   - The backend service should be running and accessible
   - Default URL: `http://localhost:5000`
   - See `backend/README.md` for service setup instructions

3. **Configure the service URL:**
   
   The service URL must be configured in your MCP client settings (via environment variable). This is an infrastructure setting and should NOT be stored in workspace config files.
   
   See step 4 below for how to configure it in your MCP client.

4. **Configure MCP client at project level:**

   Use the config printed by `setup_env.py` — it uses the venv Python path so no global deps are needed.

   **Project-level configuration (recommended):** Place `mcp.json` in your project's `.cursor` folder. This makes the project root the workspace root, so `.curio-decision` is created and used in the right place.

   **For Cursor:**
   Add to your project's `.cursor/mcp.json` (not global `~/.cursor/mcp.json`):
   ```
   your-project/
   ├── .cursor/
   │   └── mcp.json          ← Put MCP config here
   ├── .curio-decision/
   │   └── config.json       ← Created by init_project
   └── ...
   ```

   The `command` must be the **full path to the venv Python** (e.g. `/path/to/mcp_server/.venv/bin/python`), not `python`:
   ```json
   {
     "mcpServers": {
       "curio-decision-record": {
         "command": "/absolute/path/to/mcp_server/.venv/bin/python",
         "args": ["/absolute/path/to/mcp_server/main.py"],
         "env": {
           "CURIO_DECISION_SERVICE_URL": "http://localhost:5000"
         }
       }
     }
   }
   ```
   On Windows, use `...\\mcp_server\\.venv\\Scripts\\python.exe` instead.

   **Alternative — project-level rule:** If your IDE supports project-level AI rules, you can add a rule like: *"For this project, use the curio decision project name: `<project_name>`"* — e.g. in Cursor's `.cursor/rules/`. The AI will then use that project name when making tool calls.

   **For Claude Desktop:**
   Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or similar:
   ```json
   {
     "mcpServers": {
       "curio-decision-record": {
         "command": "python",
         "args": ["/absolute/path/to/curio-decision-record/mcp_server/main.py"],
         "env": {
           "CURIO_DECISION_SERVICE_URL": "http://localhost:5000"
         }
       }
     }
   }
   ```

5. **Initialize workspace project:**
   - In your workspace, use the `init_project` tool to create and set a project
   - This creates `.curio-decision/config.json` in your workspace

## Configuration Details

### Service URL Configuration

The MCP server requires the Curio Decision Record service URL to be set via the `CURIO_DECISION_SERVICE_URL` environment variable in your MCP client configuration.

**Important:** The service URL is an infrastructure/deployment setting and should NOT be stored in workspace config files. This allows:
- Different users to point to different service instances
- Easy switching between development/staging/production environments
- Centralized configuration management in MCP client settings

If not set, the server defaults to `http://localhost:5000` (with a warning).

### Workspace Configuration

The workspace config file (`.curio-decision/config.json`) is stored at the project root and contains:
- `project_name`: Current workspace project name (set by `init_project`)

Example:
```json
{
  "project_name": "my-project"
}
```

This file is created automatically when you run `init_project` and should be committed to your repository (it's workspace-specific, not user-specific).

**Project-level MCP config:** Configure the MCP server at project level (e.g. `.cursor/mcp.json` in Cursor) so the workspace root is the project root. That way `.curio-decision` is created and used in the right place.

**Note:** The MCP server uses natural identifiers (project names, decision titles, record descriptions) instead of UUIDs. This makes the tools more intuitive:
- Project names must be unique across the system
- Decision titles must be unique within a project
- Decision record descriptions must be unique within a decision

For decision record status values and valid transitions, see the [Status Enums](README.md#status-enums) section in the main README.

## Testing

You can test the server manually:

```bash
cd mcp_server
python main.py
```

The server uses stdio transport, so it expects JSON-RPC messages on stdin and outputs responses on stdout.

To test the API client directly:
```python
from api_client import CurioDecisionAPIClient

client = CurioDecisionAPIClient("http://localhost:5000")
health = client.health_check()
print(health)
```

## Remote Service Setup

If the Curio Decision Record service is running on a remote server:

1. **Ensure the service is accessible:**
   - Check firewall rules
   - Verify CORS is enabled (if accessing from browser)
   - Use HTTPS for production

2. **Configure the service URL in your MCP client:**
   Update your MCP client configuration to set:
   ```json
   {
     "env": {
       "CURIO_DECISION_SERVICE_URL": "https://your-service.com"
     }
   }
   ```

3. **Test connectivity:**
   ```bash
   curl https://your-service.com/health
   ```

## Troubleshooting

- **Import errors / ModuleNotFoundError**: Run `python3 setup_env.py` and use the printed config. The `command` must point to the venv Python, not system `python`.
- **Service connection errors**: 
  - Verify the service is running: `curl http://localhost:5000/health`
  - Check the service URL is correct
  - Ensure network connectivity
- **Workspace detection**: The server uses the current working directory. MCP clients should set this appropriately
- **Project not found**: Run `init_project` first to set up the workspace project
- **Duplicate name/title errors**: Ensure project names, decision titles (within a project), and record descriptions (within a decision) are unique

## Distribution

The MCP server can be distributed independently:

```bash
# Package for distribution
zip -r curio-decision-mcp-server.zip mcp_server/ -x "*.pyc" "__pycache__/*"
```

Users need:
- Python 3.8+ (to run `setup_env.py`)
- The MCP server package
- The Curio Decision Record service URL
- Run `python3 setup_env.py` once — no global pip install needed

No database or backend code is required on the client side.