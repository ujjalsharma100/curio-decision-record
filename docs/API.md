# Curio Decision Record System - API Documentation

Base URL: `http://localhost:5000/api`

## Projects

### List Projects
```
GET /projects
```

Response:
```json
[
  {
    "id": "uuid",
    "name": "My Project",
    "description": "Project description",
    "decision_count": 5,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

### Create Project
```
POST /projects
Content-Type: application/json

{
  "name": "My Project",
  "description": "Optional description"
}
```

### Get Project
```
GET /projects/{id}
```

Response includes nested decisions list.

### Update Project
```
PUT /projects/{id}
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "Updated description"
}
```

### Delete Project
```
DELETE /projects/{id}
```

---

## Decisions

### List Decisions for Project
```
GET /projects/{project_id}/decisions
```

### Create Decision
```
POST /projects/{project_id}/decisions
Content-Type: application/json

{
  "title": "Database Technology Choice"
}
```

### Get Decision
```
GET /decisions/{id}
```

Response includes all decision records.

### Update Decision
```
PUT /decisions/{id}
Content-Type: application/json

{
  "title": "Updated Title"
}
```

### Delete Decision
```
DELETE /decisions/{id}
```

---

## Decision Records

### List Records for Decision
```
GET /decisions/{decision_id}/records
```

### Create Record
```
POST /decisions/{decision_id}/records
Content-Type: application/json

{
  "decision_description": "Use PostgreSQL for primary data storage",
  "decision_details": "We will use PostgreSQL 15+ with connection pooling via PgBouncer. Read replicas for analytics workload.",
  "status": "proposed",
  "context": "We need a reliable database for our growing application",
  "constraints": "Must support ACID transactions, horizontal scaling",
  "rationale": "PostgreSQL offers the best balance of features and reliability",
  "assumptions": "Our data model will remain primarily relational",
  "consequences": "Team needs PostgreSQL expertise, hosting costs increase",
  "tradeoffs": "Giving up NoSQL flexibility for relational guarantees",
  "evidence": "https://benchmark.com/postgresql-performance",
  "options_considered": "MySQL - less feature-rich, MongoDB - not suitable for relational data",
  "code_reference": "backend/database_service.py:56-72\n\nwith self.get_connection() as conn:\n    cursor = conn.cursor()"
}
```

Required fields:
- `decision_description` (always required)

For `implemented_inferred` status, all other fields are optional.

**Field descriptions:**

| Field | Description |
|-------|-------------|
| `decision_details` | Detailed explanation of the decision. Elaborates on the decision description with implementation specifics, examples, or additional context. |
| `context` | Why this decision is being made now. The background situation, pressure, or trigger that necessitates it. |
| `constraints` | Hard requirements or limitations that must be satisfied. Explains why certain "obvious" options weren't viable. |
| `rationale` | Why this specific option was chosen over alternatives. The reasoning and justification. |
| `assumptions` | Things that must remain true for this decision to stay valid. When assumptions break, the decision should be re-evaluated. |
| `consequences` | Downstream impact, both positive and negative. What it will cause, enable, or require going forward. |
| `tradeoffs` | What is explicitly being given up. Makes costs intentional so future teams know pain points are by design. |
| `evidence` | Links to resources (papers, blogs, benchmarks, experiments) that support and defend the decision. |
| `options_considered` | Alternatives that were evaluated and why they were rejected. Prevents re-proposing already-rejected ideas. |
| `code_reference` | References to implemented code: file paths, line ranges (e.g. src/utils.py:42-58), and code snippets that highlight where the decision is implemented. |

Note: Version starts at 1 and auto-increments on updates. Cannot be set manually.

### Get Record
```
GET /records/{id}
```

### Update Record
```
PUT /records/{id}
Content-Type: application/json

{
  "context": "Updated context",
  "rationale": "Updated rationale"
}
```

Same field descriptions as Create Record apply. Provide only the fields you wish to update.

**Version Control Behavior:**
- Version auto-increments on every update
- A snapshot of the previous state is saved before the update
- A changelog entry is created documenting what fields changed

Note: Status cannot be changed via PUT. Use PATCH for status changes.

### Delete Record
```
DELETE /records/{id}
```

### Change Record Status
```
PATCH /records/{id}/status
Content-Type: application/json

{
  "status": "accepted",
  "reason": "Approved by architecture review board",
  "auto_handle_conflicts": true
}
```

Valid status values:
- `proposed`
- `accepted`
- `implemented`
- `implemented_inferred`
- `rejected`
- `deprecated`

Valid transitions:
- `proposed` → `accepted`, `rejected`
- `accepted` → `implemented`, `rejected`, `deprecated`
- `implemented` → `deprecated`
- `implemented_inferred` → `deprecated`

When `auto_handle_conflicts` is true (default):
- Accepting a record rejects other accepted records
- Implementing a record deprecates other implemented records

### Get Status History
```
GET /records/{id}/history
```

Response:
```json
[
  {
    "id": "uuid",
    "decision_record_id": "uuid",
    "from_status": "proposed",
    "to_status": "accepted",
    "reason": "Approved by team",
    "changed_at": "2024-01-15T10:30:00Z"
  }
]
```

---

## Relationships

### List Relationships for Record
```
GET /records/{id}/relationships
```

Response:
```json
{
  "outgoing": [
    {
      "id": "uuid",
      "source_record_id": "uuid",
      "target_record_id": "uuid",
      "relationship_type": "superseded_by",
      "description": "Replaced with newer approach",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "incoming": [...]
}
```

### Create Relationship
```
POST /records/{id}/relationships
Content-Type: application/json

{
  "target_record_id": "uuid",
  "relationship_type": "depends_on",
  "description": "Optional description"
}
```

Relationship types:
- `superseded_by` - This record is replaced by another
- `supersedes` - This record replaces another
- `related_to` - General relationship
- `depends_on` - This record requires another
- `merged_from` - This record combines others
- `derived_from` - This record builds on another
- `conflicts_with` - Records are mutually exclusive

### Update Relationship
```
PATCH /relationships/{id}
Content-Type: application/json

{
  "relationship_type": "related_to",
  "description": "Optional updated description"
}
```
At least one of `relationship_type` or `description` must be provided.

### Delete Relationship
```
DELETE /relationships/{id}
```

---

## Decision-Level Relationships

Whole-decision relationships capture conceptual links between decisions (e.g., one decision supersedes another).

### List Decision Relationships
```
GET /decisions/{id}/decision-relationships
```

Response:
```json
{
  "outgoing": [
    {
      "id": "uuid",
      "source_decision_id": "uuid",
      "target_decision_id": "uuid",
      "relationship_type": "supersedes",
      "description": "Replaced with newer approach",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "incoming": [...]
}
```

### Create Decision Relationship
```
POST /decisions/{id}/decision-relationships
Content-Type: application/json

{
  "target_decision_id": "uuid",
  "relationship_type": "depends_on",
  "description": "Optional description"
}
```

### Update Decision Relationship
```
PATCH /decision-relationships/{id}
Content-Type: application/json

{
  "relationship_type": "related_to",
  "description": "Updated description"
}
```

### Delete Decision Relationship
```
DELETE /decision-relationships/{id}
```

---

## Version Control

Decision records support full version control with snapshots, changelog, and diff capabilities.

### Get All Versions
```
GET /records/{id}/versions
```

Response:
```json
[
  {
    "id": "uuid",
    "decision_record_id": "uuid",
    "version": 2,
    "snapshot": {
      "id": "uuid",
      "decision_id": "uuid",
      "context": "...",
      "decision_description": "...",
      "version": 2,
      ...
    },
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### Get Record at Specific Version
```
GET /records/{id}/versions/{version}
```

Returns the record snapshot as it was at the specified version.

### Get Changelog
```
GET /records/{id}/changelog
```

Response:
```json
[
  {
    "id": "uuid",
    "decision_record_id": "uuid",
    "from_version": 1,
    "to_version": 2,
    "changes": {
      "context": {
        "old": "Original context",
        "new": "Updated context"
      },
      "rationale": {
        "old": null,
        "new": "Added rationale"
      }
    },
    "summary": "Updated: context, rationale",
    "changed_at": "2024-01-15T11:00:00Z"
  }
]
```

### Get Diff Between Versions
```
GET /records/{id}/diff?from_version=1&to_version=3
```

Response:
```json
{
  "from_version": 1,
  "to_version": 3,
  "changes": {
    "context": {
      "old": "Original context",
      "new": "Latest context"
    },
    "assumptions": {
      "old": "Old assumption",
      "new": "New assumption"
    }
  }
}
```

### Revert to Previous Version
```
POST /records/{id}/revert
Content-Type: application/json

{
  "version": 2,
  "reason": "Rolling back due to incorrect assumptions"
}
```

This creates a new version (e.g., v4) with the content from version 2. The changelog records this as a revert operation.

---

## Error Responses

All endpoints return errors in this format:
```json
{
  "error": "Error message description"
}
```

Common HTTP status codes:
- `400` - Bad request (validation error)
- `404` - Resource not found
- `500` - Internal server error
