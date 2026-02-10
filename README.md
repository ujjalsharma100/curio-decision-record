# Curio Decision Record System

A comprehensive decision record management system for tracking architectural and design decisions in software projects. Curio helps teams document, version, and evolve their decisions over time, maintaining a clear history of what was decided, why, and how decisions relate to each other.

## Key Features

- **Project Organization**: Group decisions by project
- **Decision Records**: Document decisions with rich context including rationale, assumptions, constraints, and tradeoffs
- **Status Workflow**: Track decisions through their lifecycle (Proposed → Accepted → Implemented → Deprecated)
- **Relationship Mapping**: Link related decisions with custom relationship types
- **Status History**: Full audit trail of status changes
- **Version Control**: Auto-versioned records with full snapshots, changelog, diff, and revert capabilities
- **Assumption Tracking**: Highlight critical assumptions that, when invalidated, signal a need to revisit decisions

## Decision Record Fields

Each decision record captures:

| Field | Description |
|-------|-------------|
| **Decision Description** | The actual decision being made |
| **Decision Details** | Detailed explanation of the decision. Elaborates on the decision description with implementation specifics, examples, or additional context. |
| **Context** | Why this decision is being made now. The background situation, pressure, or trigger that necessitates it. Helps future readers understand the circumstances. |
| **Constraints** | Hard requirements or limitations that must be satisfied. Explains why certain "obvious" options weren't viable (e.g., must use Python ecosystem, latency limits). |
| **Rationale** | Why this specific option was chosen over alternatives. The reasoning and justification behind the decision. |
| **Assumptions** | Things that must remain true for this decision to stay valid. When assumptions break or expire, the decision should be re-evaluated. Critical for assessing ongoing validity. |
| **Consequences** | Downstream impact of this decision, both positive and negative. What it will cause, enable, or require going forward. |
| **Tradeoffs** | What is explicitly being given up by choosing this option. Makes costs intentional so future teams know pain points are by design, not accident. |
| **Evidence** | Links to resources (papers, blogs, benchmarks, experiments) that support and defend the decision. Builds credibility and auditability. |
| **Options Considered** | Alternatives that were evaluated and why they were rejected. Prevents future teams from re-proposing already-rejected ideas. |
| **Code Reference** | References to implemented code: file paths, line ranges (e.g. src/utils.py:42-58), and code snippets that highlight where the decision is implemented. |

## Status Workflow

```
Proposed ──→ Accepted ──→ Implemented ──→ Deprecated
    │            │              │
    └──→ Rejected ←──┘          │
                                └──→ Deprecated
```

- **Proposed**: Initial state for new decision records
- **Accepted**: Decision approved but not yet implemented
- **Implemented**: Decision is in effect
- **Implemented (Inferred)**: Decision inferred from existing codebase (only requires description)
- **Rejected**: Decision was not accepted
- **Deprecated**: Decision is no longer in effect (superseded by another)

### Business Rules

- Only one record per decision can be **Accepted** at a time
- Only one record per decision can be **Implemented** at a time
- When accepting/implementing a new record, conflicting records are automatically deprecated/rejected

## Relationship Types

- `superseded_by` / `supersedes`: One decision replaces another
- `related_to`: Decisions are connected
- `depends_on`: One decision requires another
- `merged_from`: Multiple proposals combined into one
- `derived_from`: Decision builds on another
- `conflicts_with`: Decisions are mutually exclusive

## Version Control

Every decision record is automatically version-controlled:

- **Auto-increment**: Version number increases automatically on every update (cannot be set manually)
- **Snapshots**: Full state of the record is saved before each update
- **Changelog**: Every change is logged with what fields changed (old/new values)
- **Diff**: Compare any two versions to see what changed
- **Revert**: Restore a record to any previous version (creates a new version with the old content)

Note: Status changes are tracked separately in the Status History and don't increment the version number.

## Agent Workflows

Curio provides 4 high-level workflows for coding agents to use via the MCP server. These are available as:
- **MCP Prompts** (Claude Code, VS Code, and any MCP-supporting client)
- **Cursor Commands** (`.cursor/commands/`) invoked as `/curio-*`
- **Claude Code Commands** (`.claude/commands/`) invoked as `/project:curio-*`

| Workflow | Description | How to invoke |
|----------|-------------|---------------|
| **Initialize & Infer** | Analyze the codebase and create `implemented_inferred` decision records for existing architectural choices | MCP prompt: `initialize_decisions` / Cursor: `/curio-initialize-decisions` / Claude Code: `/project:curio-initialize-decisions` |
| **Analyze & Propose** | Analyze codebase + existing decisions, optionally with resources and goals, then propose new decisions | MCP prompt: `analyze_and_propose` / Cursor: `/curio-analyze-and-propose` / Claude Code: `/project:curio-analyze-and-propose` |
| **Evaluate Decisions** | Audit the codebase against decisions — update statuses, flag invalidated assumptions | MCP prompt: `evaluate_decisions` / Cursor: `/curio-evaluate-decisions` / Claude Code: `/project:curio-evaluate-decisions` |
| **Implement Decision** | Take an accepted decision and implement it in code, then update its status | MCP prompt: `implement_decision` / Cursor: `/curio-implement-decision` / Claude Code: `/project:curio-implement-decision` |

## Tech Stack

- **Backend**: Flask (Python) with psycopg2 for PostgreSQL
- **Database**: PostgreSQL
- **Frontend**: React with Vite and Tailwind CSS

## Quick Start

See [docs/RUNNING.md](docs/RUNNING.md) for detailed setup instructions.

```bash
# Backend
cd backend
pip install -r requirements.txt
python init_db.py create  # Create database
python init_db.py init    # Create tables
python app.py             # Run server

# Frontend
cd frontend
npm install
npm run dev
```

## API Documentation

See [docs/API.md](docs/API.md) for the complete API reference.

## Project Structure

```
curio-decision-record/
├── .cursor/commands/          # Cursor slash commands for workflows
├── .claude/commands/          # Claude Code slash commands
├── backend/
│   ├── sql/                  # SQL schema files
│   ├── app.py                # Flask app and routes
│   ├── models.py             # Data models
│   ├── database_service.py   # Database operations
│   ├── decision_service.py   # Business logic
│   ├── init_db.py            # Database initialization
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   └── services/         # API client
│   └── package.json
├── mcp_server/
│   ├── server.py             # MCP server (tools + workflow prompts)
│   ├── api_client.py         # HTTP client for backend
│   ├── config_manager.py     # Workspace config management
│   └── setup_env.py          # Venv setup script
└── docs/
    ├── API.md
    └── RUNNING.md
```

## License

MIT
