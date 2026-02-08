"""
MCP Server for Curio Decision Record System.

This server provides tools for managing decision records, decisions, and projects
through the Model Context Protocol (MCP).

This server communicates with the Curio Decision Record service via HTTP API.
"""

import asyncio
import json
import logging
import os
from typing import Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import local modules
try:
    from .config_manager import ConfigManager
    from .api_client import CurioDecisionAPIClient
except ImportError:
    from config_manager import ConfigManager
    from api_client import CurioDecisionAPIClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize config manager (will use current working directory)
config_manager = ConfigManager()

# Get service URL from environment variable (set by MCP client configuration)
# This should NOT be in workspace config - it's an infrastructure setting
service_url = os.getenv('CURIO_DECISION_SERVICE_URL')
if not service_url:
    # Default to localhost if not configured
    service_url = 'http://localhost:5000'
    logger.warning(f"CURIO_DECISION_SERVICE_URL not set, using default: {service_url}")
    logger.warning("Set CURIO_DECISION_SERVICE_URL in your MCP client configuration")
else:
    logger.info(f"Using Curio Decision Record service: {service_url}")

# Initialize API client
api_client = CurioDecisionAPIClient(service_url)

# Create MCP server
app = Server("curio-decision-record")


def get_project_name_from_args(args: dict) -> Optional[str]:
    """Get project_name from args or workspace config."""
    project_name = args.get('project_name')
    if not project_name:
        project_name = config_manager.get_project_name()
    return project_name


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="init_project",
            description="Initialize a project for the current workspace. Creates a new project and stores its name in .curio-decision/config.json. Only one project per workspace.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the project (must be unique)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description of the project"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="get_project",
            description="Get the current project for this workspace, or a specific project by name.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "Optional project name. If not provided, uses the workspace project."
                    }
                }
            }
        ),
        Tool(
            name="list_all_projects",
            description="List all available projects in the system. Useful for finding projects to switch to.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="set_workspace_project",
            description="Set a different project as the workspace project. Updates .curio-decision/config.json.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "The project name to set as the workspace project"
                    }
                },
                "required": ["project_name"]
            }
        ),
        Tool(
            name="list_decisions",
            description="List all decisions for a project. If project_name is not provided, uses the workspace project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "Optional project name. If not provided, uses the workspace project."
                    },
                    "status": {
                        "type": "string",
                        "enum": ["proposed", "accepted", "implemented", "implemented_inferred", "rejected", "deprecated"],
                        "description": "Optional filter by decision record status. Values: proposed (under consideration), accepted (approved, ready to implement), implemented (done), implemented_inferred (inferred from existing code), rejected (declined), deprecated (no longer valid)"
                    }
                }
            }
        ),
        Tool(
            name="get_decision",
            description="Get a decision by project name and title with all its records.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "Project name. If not provided, uses the workspace project."
                    },
                    "decision_title": {
                        "type": "string",
                        "description": "The decision title"
                    }
                },
                "required": ["decision_title"]
            }
        ),
        Tool(
            name="create_decision",
            description="Create a new decision for a project. Decision titles must be unique within a project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the decision (must be unique within the project)"
                    },
                    "project_name": {
                        "type": "string",
                        "description": "Optional project name. If not provided, uses the workspace project."
                    }
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="create_record",
            description="Create a decision record for a decision. Can create proposed, implemented, or other status records based on the status parameter. Decision descriptions must be unique within a decision.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "Project name. If not provided, uses the workspace project."
                    },
                    "decision_title": {
                        "type": "string",
                        "description": "The decision title"
                    },
                    "decision_description": {
                        "type": "string",
                        "description": "Description of the decision record (must be unique within the decision)"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["proposed", "accepted", "implemented", "implemented_inferred", "rejected", "deprecated"],
                        "description": "Status of the decision record. proposed=under consideration (default), accepted=approved, implemented=done, implemented_inferred=inferred from existing code, rejected=declined, deprecated=no longer valid. Use implemented_inferred when documenting decisions already in code.",
                        "default": "proposed"
                    },
                    "context": {
                        "type": "string",
                        "description": "Context in which the decision was made"
                    },
                    "constraints": {
                        "type": "string",
                        "description": "Constraints that influenced the decision"
                    },
                    "rationale": {
                        "type": "string",
                        "description": "Rationale for the decision"
                    },
                    "assumptions": {
                        "type": "string",
                        "description": "Assumptions made"
                    },
                    "consequences": {
                        "type": "string",
                        "description": "Expected consequences"
                    },
                    "tradeoffs": {
                        "type": "string",
                        "description": "Tradeoffs considered"
                    },
                    "evidence": {
                        "type": "string",
                        "description": "Evidence supporting the decision"
                    },
                    "options_considered": {
                        "type": "string",
                        "description": "Other options that were considered"
                    }
                },
                "required": ["decision_title", "decision_description"]
            }
        ),
        Tool(
            name="change_record_status",
            description="Change the status of a decision record. Valid transitions: proposed→accepted/rejected, accepted→implemented/rejected/deprecated, implemented→deprecated. With auto_handle_conflicts=true (default), accepting a record will reject any other accepted record for the same decision.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "Project name. If not provided, uses the workspace project."
                    },
                    "decision_title": {
                        "type": "string",
                        "description": "The decision title"
                    },
                    "decision_description": {
                        "type": "string",
                        "description": "The decision record description"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["proposed", "accepted", "implemented", "implemented_inferred", "rejected", "deprecated"],
                        "description": "The new status. proposed=under consideration, accepted=approved, implemented=done, implemented_inferred=inferred from code, rejected=declined, deprecated=obsolete. Must follow valid transitions from current status."
                    },
                    "reason": {
                        "type": "string",
                        "description": "Optional reason for the status change"
                    },
                    "auto_handle_conflicts": {
                        "type": "boolean",
                        "description": "Automatically handle conflicts (e.g., reject other accepted records when accepting a new one). Default: true",
                        "default": True
                    }
                },
                "required": ["decision_title", "decision_description", "status"]
            }
        ),
        Tool(
            name="get_decision_record",
            description="Get a decision record by project name, decision title, and description with its relationships.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "Project name. If not provided, uses the workspace project."
                    },
                    "decision_title": {
                        "type": "string",
                        "description": "The decision title"
                    },
                    "decision_description": {
                        "type": "string",
                        "description": "The decision record description"
                    }
                },
                "required": ["decision_title", "decision_description"]
            }
        ),
        Tool(
            name="get_implementation_history",
            description="Get the implementation history for a decision, showing current and past implementations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "Project name. If not provided, uses the workspace project."
                    },
                    "decision_title": {
                        "type": "string",
                        "description": "The decision title"
                    }
                },
                "required": ["decision_title"]
            }
        ),
        Tool(
            name="list_decision_record_relationships",
            description="List all relationships (outgoing and incoming) for a decision record. Relationships can link records across different decisions within the project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "Project name. If not provided, uses the workspace project."
                    },
                    "decision_title": {
                        "type": "string",
                        "description": "The decision title containing the record"
                    },
                    "decision_description": {
                        "type": "string",
                        "description": "The decision record description"
                    }
                },
                "required": ["decision_title", "decision_description"]
            }
        ),
        Tool(
            name="list_decision_relationships",
            description="List all decision-level relationships (outgoing and incoming) for a decision. Identified by project name and decision title.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "Project name. If not provided, uses the workspace project."
                    },
                    "decision_title": {
                        "type": "string",
                        "description": "The decision title"
                    }
                },
                "required": ["decision_title"]
            }
        ),
        Tool(
            name="manage_decision_record_relationship",
            description="Create, update, or delete a relationship between two decision records. Records can be from different decisions within the project. Mode: create, update, delete.",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["create", "update", "delete"],
                        "description": "create: add new relationship; update: modify description/type; delete: remove relationship"
                    },
                    "project_name": {
                        "type": "string",
                        "description": "Project name. If not provided, uses the workspace project."
                    },
                    "source_decision_title": {
                        "type": "string",
                        "description": "Decision title of the source record (where relationship originates)"
                    },
                    "source_decision_description": {
                        "type": "string",
                        "description": "Description of the source decision record"
                    },
                    "target_decision_title": {
                        "type": "string",
                        "description": "Decision title of the target record (can be different from source for cross-decision links)"
                    },
                    "target_decision_description": {
                        "type": "string",
                        "description": "Description of the target decision record"
                    },
                    "relationship_type": {
                        "type": "string",
                        "enum": ["superseded_by", "supersedes", "related_to", "depends_on", "merged_from", "derived_from", "conflicts_with"],
                        "description": "Required for create and update. Optional for delete (identifies which relationship when multiple exist between same pair)."
                    },
                    "description": {
                        "type": "string",
                        "description": "For create: optional description. For update: new description (optional). Ignored for delete."
                    },
                    "new_relationship_type": {
                        "type": "string",
                        "enum": ["superseded_by", "supersedes", "related_to", "depends_on", "merged_from", "derived_from", "conflicts_with"],
                        "description": "For update only: optional new type to change the relationship type."
                    }
                },
                "required": ["mode", "source_decision_title", "source_decision_description", "target_decision_title", "target_decision_description"]
            }
        ),
        Tool(
            name="manage_decision_relationship",
            description="Create, update, or delete a relationship between two decisions (whole-decision level). Captures conceptual links: supersedes, depends_on, etc. Mode: create, update, delete.",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["create", "update", "delete"],
                        "description": "create: add new relationship; update: modify description/type; delete: remove relationship"
                    },
                    "project_name": {
                        "type": "string",
                        "description": "Project name. If not provided, uses the workspace project."
                    },
                    "source_decision_title": {
                        "type": "string",
                        "description": "Title of the source decision (where relationship originates)"
                    },
                    "target_decision_title": {
                        "type": "string",
                        "description": "Title of the target decision"
                    },
                    "relationship_type": {
                        "type": "string",
                        "enum": ["superseded_by", "supersedes", "related_to", "depends_on", "merged_from", "derived_from", "conflicts_with"],
                        "description": "Required for create and update. Optional for delete (identifies which when multiple exist between same pair)."
                    },
                    "description": {
                        "type": "string",
                        "description": "For create: optional description. For update: new description (optional). Ignored for delete."
                    },
                    "new_relationship_type": {
                        "type": "string",
                        "enum": ["superseded_by", "supersedes", "related_to", "depends_on", "merged_from", "derived_from", "conflicts_with"],
                        "description": "For update only: optional new type."
                    }
                },
                "required": ["mode", "source_decision_title", "target_decision_title"]
            }
        ),
        Tool(
            name="update_decision_record",
            description="Update a decision record's content (context, constraints, rationale, assumptions, consequences, tradeoffs, evidence, options_considered). Version is automatically incremented. Use decision_title and decision_description to identify the record.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "Project name. If not provided, uses the workspace project."
                    },
                    "decision_title": {
                        "type": "string",
                        "description": "The decision title"
                    },
                    "decision_description": {
                        "type": "string",
                        "description": "The decision record description (identifies the record to update)"
                    },
                    "context": {
                        "type": "string",
                        "description": "Updated context"
                    },
                    "constraints": {
                        "type": "string",
                        "description": "Updated constraints"
                    },
                    "rationale": {
                        "type": "string",
                        "description": "Updated rationale"
                    },
                    "assumptions": {
                        "type": "string",
                        "description": "Updated assumptions"
                    },
                    "consequences": {
                        "type": "string",
                        "description": "Updated consequences"
                    },
                    "tradeoffs": {
                        "type": "string",
                        "description": "Updated tradeoffs"
                    },
                    "evidence": {
                        "type": "string",
                        "description": "Updated evidence"
                    },
                    "options_considered": {
                        "type": "string",
                        "description": "Updated options considered"
                    }
                },
                "required": ["decision_title", "decision_description"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "init_project":
            name_arg = arguments.get("name")
            description = arguments.get("description")
            
            if not name_arg:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "name is required"}, indent=2)
                )]
            
            # Create project via API
            project = api_client.create_project(
                name=name_arg,
                description=description
            )
            
            # Store project name in workspace config
            project_name = project.get("name")
            if project_name:
                config_manager.set_project_name(project_name)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "project": project,
                    "message": f"Project '{project_name}' initialized and set as workspace project"
                }, indent=2, default=str)
            )]
        
        elif name == "get_project":
            project_name = get_project_name_from_args(arguments)
            
            if not project_name:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "No project configured for this workspace. Use init_project first."
                    }, indent=2)
                )]
            
            project = api_client.get_project_by_name(project_name)
            
            return [TextContent(
                type="text",
                text=json.dumps(project, indent=2, default=str)
            )]
        
        elif name == "list_all_projects":
            projects = api_client.list_projects()
            
            return [TextContent(
                type="text",
                text=json.dumps(projects, indent=2, default=str)
            )]
        
        elif name == "set_workspace_project":
            project_name = arguments.get("project_name")
            
            if not project_name:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "project_name is required"}, indent=2)
                )]
            
            # Verify project exists
            project = api_client.get_project_by_name(project_name)
            
            # Set in workspace config
            success = config_manager.set_project_name(project_name)
            if not success:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "Failed to update workspace config"}, indent=2)
                )]
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": True,
                    "project": project,
                    "message": f"Workspace project set to '{project_name}'"
                }, indent=2, default=str)
            )]
        
        elif name == "list_decisions":
            project_name = get_project_name_from_args(arguments)
            
            if not project_name:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "No project configured for this workspace. Use init_project first."
                    }, indent=2)
                )]
            
            status_filter = arguments.get("status")
            decisions = api_client.list_decisions_by_project_name(project_name, status=status_filter)
            
            return [TextContent(
                type="text",
                text=json.dumps(decisions, indent=2, default=str)
            )]
        
        elif name == "get_decision":
            decision_title = arguments.get("decision_title")
            project_name = get_project_name_from_args(arguments)
            
            if not decision_title:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "decision_title is required"}, indent=2)
                )]
            
            if not project_name:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "No project configured for this workspace. Use init_project first or provide project_name."
                    }, indent=2)
                )]
            
            decision = api_client.get_decision_by_title(project_name, decision_title)
            
            return [TextContent(
                type="text",
                text=json.dumps(decision, indent=2, default=str)
            )]
        
        elif name == "create_decision":
            title = arguments.get("title")
            project_name = get_project_name_from_args(arguments)
            
            if not title:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "title is required"}, indent=2)
                )]
            
            if not project_name:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "No project configured for this workspace. Use init_project first."
                    }, indent=2)
                )]
            
            decision = api_client.create_decision_by_project_name(project_name=project_name, title=title)
            
            return [TextContent(
                type="text",
                text=json.dumps(decision, indent=2, default=str)
            )]
        
        elif name == "create_record":
            decision_title = arguments.get("decision_title")
            decision_description = arguments.get("decision_description")
            project_name = get_project_name_from_args(arguments)
            status = arguments.get("status", "proposed")
            
            if not decision_title or not decision_description:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "decision_title and decision_description are required"}, indent=2)
                )]
            
            if not project_name:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "No project configured for this workspace. Use init_project first or provide project_name."
                    }, indent=2)
                )]
            
            record = api_client.create_record_by_names(
                project_name=project_name,
                decision_title=decision_title,
                decision_description=decision_description,
                context=arguments.get("context"),
                constraints=arguments.get("constraints"),
                status=status,
                rationale=arguments.get("rationale"),
                assumptions=arguments.get("assumptions"),
                consequences=arguments.get("consequences"),
                tradeoffs=arguments.get("tradeoffs"),
                evidence=arguments.get("evidence"),
                options_considered=arguments.get("options_considered")
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(record, indent=2, default=str)
            )]
        
        elif name == "change_record_status":
            decision_title = arguments.get("decision_title")
            decision_description = arguments.get("decision_description")
            status = arguments.get("status")
            project_name = get_project_name_from_args(arguments)
            reason = arguments.get("reason")
            auto_handle_conflicts = arguments.get("auto_handle_conflicts", True)
            
            if not decision_title or not decision_description or not status:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "decision_title, decision_description, and status are required"}, indent=2)
                )]
            
            if not project_name:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "No project configured for this workspace. Use init_project first or provide project_name."
                    }, indent=2)
                )]
            
            result = api_client.change_record_status_by_description(
                project_name=project_name,
                decision_title=decision_title,
                decision_description=decision_description,
                status=status,
                reason=reason,
                auto_handle_conflicts=auto_handle_conflicts
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
        
        elif name == "get_decision_record":
            decision_title = arguments.get("decision_title")
            decision_description = arguments.get("decision_description")
            project_name = get_project_name_from_args(arguments)
            
            if not decision_title or not decision_description:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "decision_title and decision_description are required"}, indent=2)
                )]
            
            if not project_name:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "No project configured for this workspace. Use init_project first or provide project_name."
                    }, indent=2)
                )]
            
            record = api_client.get_record_by_description(
                project_name=project_name,
                decision_title=decision_title,
                decision_description=decision_description
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(record, indent=2, default=str)
            )]
        
        elif name == "get_implementation_history":
            decision_title = arguments.get("decision_title")
            project_name = get_project_name_from_args(arguments)
            
            if not decision_title:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "decision_title is required"}, indent=2)
                )]
            
            if not project_name:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "No project configured for this workspace. Use init_project first or provide project_name."
                    }, indent=2)
                )]
            
            history = api_client.get_implementation_history_by_title(
                project_name=project_name,
                decision_title=decision_title
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(history, indent=2, default=str)
            )]
        
        elif name == "list_decision_record_relationships":
            decision_title = arguments.get("decision_title")
            decision_description = arguments.get("decision_description")
            project_name = get_project_name_from_args(arguments)
            
            if not decision_title or not decision_description:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "decision_title and decision_description are required"}, indent=2)
                )]
            
            if not project_name:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "No project configured for this workspace. Use init_project first or provide project_name."
                    }, indent=2)
                )]
            
            record = api_client.get_record_by_description(
                project_name=project_name,
                decision_title=decision_title,
                decision_description=decision_description
            )
            relationships = api_client.list_relationships(record['id'])
            
            return [TextContent(
                type="text",
                text=json.dumps(relationships, indent=2, default=str)
            )]
        
        elif name == "manage_decision_record_relationship":
            mode = arguments.get("mode")
            source_decision_title = arguments.get("source_decision_title")
            source_decision_description = arguments.get("source_decision_description")
            target_decision_title = arguments.get("target_decision_title")
            target_decision_description = arguments.get("target_decision_description")
            relationship_type = arguments.get("relationship_type")
            description = arguments.get("description")
            new_relationship_type = arguments.get("new_relationship_type")
            project_name = get_project_name_from_args(arguments)
            
            if not all([mode, source_decision_title, source_decision_description, target_decision_title, target_decision_description]):
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "mode, source_decision_title, source_decision_description, target_decision_title, target_decision_description are required"}, indent=2)
                )]
            
            if mode not in ("create", "update", "delete"):
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "mode must be create, update, or delete"}, indent=2)
                )]
            
            if mode in ("create", "update") and not relationship_type:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "relationship_type is required for create and update modes"}, indent=2)
                )]
            
            if not project_name:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "No project configured for this workspace. Use init_project first or provide project_name."
                    }, indent=2)
                )]
            
            source_record = api_client.get_record_by_description(
                project_name=project_name,
                decision_title=source_decision_title,
                decision_description=source_decision_description
            )
            target_record = api_client.get_record_by_description(
                project_name=project_name,
                decision_title=target_decision_title,
                decision_description=target_decision_description
            )
            
            if mode == "create":
                relationship = api_client.create_relationship(
                    source_record_id=source_record['id'],
                    target_record_id=target_record['id'],
                    relationship_type=relationship_type,
                    description=description
                )
                return [TextContent(
                    type="text",
                    text=json.dumps(relationship, indent=2, default=str)
                )]
            
            # For update and delete: find relationship by source->target and optionally relationship_type
            rels = api_client.list_relationships(source_record['id'])
            outgoing = rels.get('outgoing', [])
            matching = [r for r in outgoing if r['target_record_id'] == target_record['id']]
            if relationship_type:
                matching = [r for r in matching if r['relationship_type'] == relationship_type]
            
            if not matching:
                err = "No matching relationship found between source and target"
                if relationship_type:
                    err += f" with type {relationship_type}"
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": err}, indent=2)
                )]
            if len(matching) > 1:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "Multiple relationships exist between source and target; specify relationship_type to identify which one"}, indent=2)
                )]
            
            relationship_id = matching[0]['id']
            
            if mode == "delete":
                api_client.delete_relationship(relationship_id)
                return [TextContent(
                    type="text",
                    text=json.dumps({"success": True, "message": f"Relationship {relationship_id} deleted"}, indent=2)
                )]
            
            # mode == "update"
            if not description and not new_relationship_type:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "For update mode, provide description and/or new_relationship_type"}, indent=2)
                )]
            
            relationship = api_client.update_relationship(
                relationship_id=relationship_id,
                relationship_type=new_relationship_type,
                description=description
            )
            return [TextContent(
                type="text",
                text=json.dumps(relationship, indent=2, default=str)
            )]
        
        elif name == "list_decision_relationships":
            decision_title = arguments.get("decision_title")
            project_name = get_project_name_from_args(arguments)
            
            if not decision_title:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "decision_title is required"}, indent=2)
                )]
            
            if not project_name:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "No project configured for this workspace. Use init_project first or provide project_name."
                    }, indent=2)
                )]
            
            decision = api_client.get_decision_by_title(project_name, decision_title)
            relationships = api_client.list_decision_relationships(decision['id'])
            
            return [TextContent(
                type="text",
                text=json.dumps(relationships, indent=2, default=str)
            )]
        
        elif name == "manage_decision_relationship":
            mode = arguments.get("mode")
            source_decision_title = arguments.get("source_decision_title")
            target_decision_title = arguments.get("target_decision_title")
            relationship_type = arguments.get("relationship_type")
            description = arguments.get("description")
            new_relationship_type = arguments.get("new_relationship_type")
            project_name = get_project_name_from_args(arguments)
            
            if not all([mode, source_decision_title, target_decision_title]):
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "mode, source_decision_title, target_decision_title are required"}, indent=2)
                )]
            
            if mode not in ("create", "update", "delete"):
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "mode must be create, update, or delete"}, indent=2)
                )]
            
            if mode in ("create", "update") and not relationship_type:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "relationship_type is required for create and update modes"}, indent=2)
                )]
            
            if not project_name:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "No project configured for this workspace. Use init_project first or provide project_name."
                    }, indent=2)
                )]
            
            source_decision = api_client.get_decision_by_title(project_name, source_decision_title)
            target_decision = api_client.get_decision_by_title(project_name, target_decision_title)
            
            if mode == "create":
                relationship = api_client.create_decision_relationship(
                    source_decision_id=source_decision['id'],
                    target_decision_id=target_decision['id'],
                    relationship_type=relationship_type,
                    description=description
                )
                return [TextContent(
                    type="text",
                    text=json.dumps(relationship, indent=2, default=str)
                )]
            
            # For update and delete: find relationship by source->target and optionally relationship_type
            rels = api_client.list_decision_relationships(source_decision['id'])
            outgoing = rels.get('outgoing', [])
            matching = [r for r in outgoing if r['target_decision_id'] == target_decision['id']]
            if relationship_type:
                matching = [r for r in matching if r['relationship_type'] == relationship_type]
            
            if not matching:
                err = "No matching decision relationship found between source and target"
                if relationship_type:
                    err += f" with type {relationship_type}"
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": err}, indent=2)
                )]
            if len(matching) > 1:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "Multiple relationships exist; specify relationship_type to identify which one"}, indent=2)
                )]
            
            relationship_id = matching[0]['id']
            
            if mode == "delete":
                api_client.delete_decision_relationship(relationship_id)
                return [TextContent(
                    type="text",
                    text=json.dumps({"success": True, "message": f"Decision relationship {relationship_id} deleted"}, indent=2)
                )]
            
            # mode == "update"
            if not description and not new_relationship_type:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "For update mode, provide description and/or new_relationship_type"}, indent=2)
                )]
            
            relationship = api_client.update_decision_relationship(
                relationship_id=relationship_id,
                relationship_type=new_relationship_type,
                description=description
            )
            return [TextContent(
                type="text",
                text=json.dumps(relationship, indent=2, default=str)
            )]
        
        elif name == "update_decision_record":
            decision_title = arguments.get("decision_title")
            decision_description = arguments.get("decision_description")
            project_name = get_project_name_from_args(arguments)
            
            if not decision_title or not decision_description:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "decision_title and decision_description are required"}, indent=2)
                )]
            
            if not project_name:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "No project configured for this workspace. Use init_project first or provide project_name."
                    }, indent=2)
                )]
            
            record = api_client.update_record_by_description(
                project_name=project_name,
                decision_title=decision_title,
                decision_description=decision_description,
                context=arguments.get("context"),
                constraints=arguments.get("constraints"),
                rationale=arguments.get("rationale"),
                assumptions=arguments.get("assumptions"),
                consequences=arguments.get("consequences"),
                tradeoffs=arguments.get("tradeoffs"),
                evidence=arguments.get("evidence"),
                options_considered=arguments.get("options_considered")
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(record, indent=2, default=str)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2)
            )]
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]


