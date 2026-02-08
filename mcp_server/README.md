# Curio Decision Record MCP Server

An MCP (Model Context Protocol) server for managing decision records, decisions, and projects. This server allows coding agents to view decisions, create decision records, change their status, and manage projects in a workspace-specific manner.

## Architecture

This MCP server is **decoupled** from the main Curio Decision Record service. It communicates with the backend service via HTTP API, requiring only the service URL for configuration. This makes it easy to distribute and deploy independently.

- **Standalone**: No direct database or backend dependencies
- **API-based**: Communicates with Curio Decision Record service via REST API
- **Workspace-specific**: Each workspace has one project stored in `.curio-decision/config.json`
- **Simple configuration**: Only requires the service URL
- **Natural identifiers**: Uses project names, decision titles, and record descriptions instead of UUIDs for better usability

## Installation

1. Run the setup script (creates a venv — no global deps needed):
```bash
cd mcp_server
python3 setup_env.py
```
Use the printed config in Cursor; it points to the venv Python.

2. Ensure the Curio Decision Record service is running (see backend/README.md)

3. Configure the service URL (see Configuration section below)

## Configuration

The MCP server requires the **Curio Decision Record service URL** to be configured in your MCP client settings (via environment variable). This is an infrastructure setting and should not be stored in workspace config files.

### Service URL Configuration

The service URL must be set via the `CURIO_DECISION_SERVICE_URL` environment variable in your MCP client configuration. See the Setup section below for examples.

### Project-Level Configuration (Recommended)

Configure the MCP server at the **project level** so that the workspace root is your project root. This ensures `.curio-decision` is created and used within the correct project directory.

**For Cursor:** Place `mcp.json` in your project's `.cursor` folder:
```
your-project/
├── .cursor/
│   └── mcp.json          ← MCP config (project-level)
├── .curio-decision/
│   └── config.json       ← Created by init_project
└── ...
```

When configured at project level, the MCP client uses the project root as the workspace root, so `.curio-decision` is created and found in the right place.

**For Claude Desktop:** Use a global config file; the workspace root is typically the current working directory when you open a project.

### Alternative: Project-Level Rule for IDEs

Some IDEs and coding clients support project-level rules that tell the AI which Curio Decision project to use. You can add a rule like:

> **For this project, use the curio decision project name: `my-project-name`**

This can be stored in:
- **Cursor:** `.cursor/rules/` or a project-level rule file
- **Other IDEs:** Their equivalent project-level AI configuration

The AI agent will then use that project name when making tool calls, without requiring `.curio-decision/config.json` to exist first. Use `init_project` first to create the project and config, or reference an existing project name.

## Usage

### Running the Server

The MCP server uses stdio transport and should be configured in your MCP client (e.g., Cursor, Claude Desktop).

**For Cursor (project-level):**
Add to your project's `.cursor/mcp.json`. Use the config printed by `setup_env.py` — the `command` must be the venv Python path (e.g. `/path/to/mcp_server/.venv/bin/python`), not `python`, so it works without global dependencies.

Use project-relative or absolute paths appropriate for your setup:
```json
{
  "mcpServers": {
    "curio-decision-record": {
      "command": "/path/to/curio-decision-record/mcp_server/.venv/bin/python",
      "args": ["/path/to/curio-decision-record/mcp_server/main.py"],
      "env": {
        "CURIO_DECISION_SERVICE_URL": "http://localhost:5000"
      }
    }
  }
}
```

With project-level config, the workspace root is the project root where `.curio-decision` will be created and used.

**For Claude Desktop:**
Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or similar:
```json
{
  "mcpServers": {
    "curio-decision-record": {
      "command": "python",
      "args": ["/path/to/curio-decision-record/mcp_server/main.py"],
      "env": {
        "CURIO_DECISION_SERVICE_URL": "http://localhost:5000"
      }
    }
  }
}
```

**Important:** The service URL is configured in the MCP client settings (via environment variable), not in workspace config files. This allows different users/environments to point to different service instances.

### Workspace Setup

1. **Initialize a project** in your workspace:
   - Use the `init_project` tool to create a project and associate it with your workspace
   - This creates `.curio-decision/config.json` with the project name
   - All subsequent tool calls will use this project unless explicitly overridden
   - Project names must be unique across the system

2. **Create decisions** as needed:
   - Use `create_decision` to create a new decision (titles must be unique within a project)
   - Use `create_record` to create decision records (descriptions must be unique within a decision)
   - Use `create_record` with `status="implemented_inferred"` to record an implemented decision

3. **Manage decision lifecycle**:
   - Use `change_record_status` to move records through statuses
   - Use `list_decisions(status="accepted")` to find decisions ready to implement
   - Use `get_implementation_history` to see implementation history

## Available Tools

### Project Management

- **`init_project`**: Initialize a project for the current workspace
  - Creates a new project and stores its name in `.curio-decision/config.json`
  - Only one project per workspace
  - Project names must be unique across the system
  
- **`get_project`**: Get the current project for this workspace (by name)
- **`list_all_projects`**: List all available projects in the system
- **`set_workspace_project`**: Set a different project as the workspace project (by name)

### Decision Management

- **`list_decisions`**: List all decisions for a project (optionally filtered by status)
  - Uses project name (from workspace config or provided parameter)
  - Status filter: `proposed`, `accepted`, `implemented`, `implemented_inferred`, `rejected`, `deprecated` (see Status Enums)
- **`get_decision`**: Get a decision by project name and title with all its records
- **`create_decision`**: Create a new decision for a project
  - Decision titles must be unique within a project

### Decision Record Management

- **`create_record`**: Create a decision record with specified status (default: "proposed")
  - Uses project name, decision title, and decision description
  - Decision descriptions must be unique within a decision
  - Status: `proposed` (default), `accepted`, `implemented`, `implemented_inferred`, `rejected`, `deprecated` (see Status Enums)
- **`get_decision_record`**: Get a decision record by project name, decision title, and description
- **`update_decision_record`**: Update a decision record's content (context, rationale, etc.; auto-increments version)
  - Uses project name, decision title, and description to identify the record
- **`change_record_status`**: Change the status of a decision record
  - Uses project name, decision title, and description to identify the record
  - Valid transitions: see Status Enums → Status Transitions

### Relationship Tools (cross-decision)

Relationships can link records **across different decisions** within a project.

- **`list_decision_record_relationships`**: List all relationships (outgoing and incoming) for a decision record. Records are identified by project name, decision title, and decision description.
- **`list_decision_relationships`**: List all decision-level relationships (outgoing and incoming) for a decision. Identified by project name and decision title.
- **`manage_decision_record_relationship`**: Single tool for create, update, and delete. Use `mode`: `create`, `update`, or `delete`. Same source/target params for all modes. Source and target can be from different decisions. `relationship_type` required for create and update; optional for delete (identifies which when multiple exist). For update: `description` and/or `new_relationship_type`. Types: `superseded_by`, `supersedes`, `related_to`, `depends_on`, `merged_from`, `derived_from`, `conflicts_with`.

### Query Tools

- **`list_decisions`**: List decisions with optional status filter (e.g., status="accepted" to find decisions ready to implement)
- **`get_implementation_history`**: Get implementation history for a decision (by project name and decision title)

## Status Enums

Decision records use a status enum to track their lifecycle. All tools that accept or filter by status use these values:

| Status | Description |
|--------|-------------|
| **`proposed`** | Initial status when a decision record is created. The decision is under consideration and has not yet been approved. |
| **`accepted`** | The decision has been approved and is ready for implementation. Only one record per decision can be accepted at a time. Use `list_decisions(status="accepted")` to find decisions ready to implement. |
| **`implemented`** | The decision has been fully implemented in code. Use this after completing the implementation work. |
| **`implemented_inferred`** | The decision was inferred from existing code (e.g., when documenting decisions that were already made). Use when creating records that describe current state rather than proposed changes. |
| **`rejected`** | The decision was rejected and will not be pursued. Use when a proposed decision is declined. |
| **`deprecated`** | The decision is no longer valid or has been superseded. Use when an accepted or implemented decision becomes obsolete. |

### Status Transitions

Valid transitions when using `change_record_status`:

| From | To |
|------|-----|
| `proposed` | `accepted`, `rejected` |
| `accepted` | `implemented`, `rejected`, `deprecated` |
| `implemented` | `deprecated` |
| `implemented_inferred` | `deprecated` |

**Note:** When accepting a record, `auto_handle_conflicts=true` (default) will automatically reject any other accepted record for the same decision.

## Workspace Configuration

The workspace configuration is stored in `.curio-decision/config.json` at the project root:

```json
{
  "project_name": "your-project-name"
}
```

The `project_name` allows tools to automatically use the workspace project without requiring the project_name parameter in every call. This is created automatically when you run `init_project`.

**Project-level setup:** When you configure the MCP server at project level (e.g. `.cursor/mcp.json` in Cursor), the workspace root is the project root, so `.curio-decision` is created and looked up in the correct place.

**Note:** The service URL is NOT stored in workspace config - it's configured in your MCP client settings (see Configuration section above).

## Natural Identifiers

The MCP server uses **natural identifiers** instead of UUIDs for better usability:

- **Project names**: Must be unique across the system
- **Decision titles**: Must be unique within a project
- **Decision record descriptions**: Must be unique within a decision

These constraints are enforced at the database level, ensuring data integrity while making the tools more intuitive to use. You can reference projects, decisions, and records by their natural names/titles instead of long UUID strings.

## Example Workflow

1. **Initialize project**:
   ```
   init_project(name="My Project", description="Project description")
   ```
   This creates a project named "My Project" and stores it in workspace config.

2. **Create a decision**:
   ```
   create_decision(title="Use PostgreSQL for data storage")
   ```
   The decision title "Use PostgreSQL for data storage" must be unique within the project.

3. **Create a proposed decision record**:
   ```
   create_record(
     decision_title="Use PostgreSQL for data storage",
     decision_description="We will use PostgreSQL as our primary database...",
     status="proposed",
     context="We need a reliable database...",
     rationale="PostgreSQL offers ACID compliance..."
   )
   ```
   The decision_description must be unique within the decision.
   
   Or create an implemented (inferred) record:
   ```
   create_record(
     decision_title="Use PostgreSQL for data storage",
     decision_description="We implemented PostgreSQL...",
     status="implemented_inferred",
     context="Implementation context...",
     rationale="Implementation rationale..."
   )
   ```

4. **Accept the decision**:
   ```
   change_record_status(
     decision_title="Use PostgreSQL for data storage",
     decision_description="We will use PostgreSQL as our primary database...",
     status="accepted",
     reason="Team approved this approach"
   )
   ```

5. **After implementation, mark as implemented**:
   ```
   change_record_status(
     decision_title="Use PostgreSQL for data storage",
     decision_description="We will use PostgreSQL as our primary database...",
     status="implemented",
     reason="Implementation completed"
   )
   ```

6. **Query accepted decisions** (for coding agents):
   ```
   list_decisions(status="accepted")
   ```

7. **Get a specific decision with all records**:
   ```
   get_decision(decision_title="Use PostgreSQL for data storage")
   ```

8. **Get implementation history**:
   ```
   get_implementation_history(decision_title="Use PostgreSQL for data storage")
   ```

## Distribution

The MCP server is designed to be distributed independently:

1. **No backend dependencies**: Only needs the service URL
2. **Minimal dependencies**: Only requires `mcp` and `requests` packages
3. **Standalone package**: Can be packaged and distributed separately

To distribute:
```bash
# Package the mcp_server directory
zip -r curio-decision-mcp-server.zip mcp_server/
```

Users only need:
- The MCP server package
- The Curio Decision Record service URL
- Python 3.8+ — run `setup_env.py` once (no global pip install)

## Troubleshooting

- **Service connection errors**: Ensure the Curio Decision Record service is running and the URL is correct
- **Project not found**: Run `init_project` first to set up the workspace project
- **Import errors**: Run `python3 setup_env.py` and use the printed config (venv Python path)
- **Service URL not configured**: Set `CURIO_DECISION_SERVICE_URL` environment variable in your MCP client configuration (not in workspace config)

## Development

The MCP server uses:
- `api_client.py`: HTTP client for communicating with the backend service
- `config_manager.py`: Workspace configuration management
- `server.py`: MCP server implementation with all tools
