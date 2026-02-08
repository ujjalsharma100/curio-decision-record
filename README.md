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
| **Context** | Why now? What prompted this decision? |
| **Constraints** | Requirements that must be met |
| **Rationale** | Why this choice was made |
| **Assumptions** | Critical beliefs that must hold true (key for validation) |
| **Consequences** | Positive and negative impacts |
| **Tradeoffs** | What's being given up |
| **Evidence** | Links, resources, benchmarks supporting the decision |
| **Options Considered** | Alternatives and why they were not chosen |

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
└── docs/
    ├── API.md
    └── RUNNING.md
```

## License

MIT
