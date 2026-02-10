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
from mcp.types import Tool, TextContent, Prompt, PromptArgument, PromptMessage, GetPromptResult

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


def build_metadata() -> Optional[dict]:
    """
    Build metadata dict by auto-detecting VCS information from the workspace.
    
    Returns metadata like {"vcs": {"type": "git", "revision": "abc123..."}}
    or None if no VCS is detected.
    """
    return config_manager.get_vcs_metadata()


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
                        "description": "Why this decision is being made now. The background situation, pressure, or trigger that necessitates it. Helps future readers understand the circumstances, not just the logic."
                    },
                    "constraints": {
                        "type": "string",
                        "description": "Hard requirements or limitations that must be satisfied. These explain why certain 'obvious' options weren't viable (e.g., must use Python ecosystem, latency limits, compatibility with existing backend)."
                    },
                    "decision_details": {
                        "type": "string",
                        "description": "Detailed explanation of the decision. Elaborates on the decision description with implementation specifics, examples, or additional context."
                    },
                    "rationale": {
                        "type": "string",
                        "description": "Why this specific option was chosen over alternatives. The reasoning and justification behind the decision."
                    },
                    "assumptions": {
                        "type": "string",
                        "description": "Things that must remain true for this decision to stay valid. When assumptions break or expire, the decision should be re-evaluated. Critical for assessing ongoing validity."
                    },
                    "consequences": {
                        "type": "string",
                        "description": "Downstream impact of this decision, both positive and negative. What it will cause, enable, or require going forward."
                    },
                    "tradeoffs": {
                        "type": "string",
                        "description": "What is explicitly being given up by choosing this option. Makes costs intentional and visible so future teams know pain points are by design, not accident."
                    },
                    "evidence": {
                        "type": "string",
                        "description": "Links to resources (papers, blogs, benchmarks, experiments, documents) that support and defend the decision. Builds credibility and auditability."
                    },
                    "options_considered": {
                        "type": "string",
                        "description": "Alternatives that were evaluated and why they were rejected. Prevents future teams from re-proposing already-rejected ideas and enables counterfactual analysis."
                    },
                    "code_reference": {
                        "type": "string",
                        "description": "References to implemented code: file paths, line ranges (e.g. src/utils.py:42-58), and code snippets that highlight where the decision is implemented."
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Optional metadata (auto-captured if not provided). Includes VCS info like {\"vcs\": {\"type\": \"git\", \"revision\": \"commit_hash\"}}. Automatically detected from the workspace if the project is version controlled."
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
                        "description": "Why this decision is being made now. The background situation, pressure, or trigger that necessitates it. Helps future readers understand the circumstances, not just the logic."
                    },
                    "constraints": {
                        "type": "string",
                        "description": "Hard requirements or limitations that must be satisfied. These explain why certain 'obvious' options weren't viable (e.g., must use Python ecosystem, latency limits, compatibility with existing backend)."
                    },
                    "decision_details": {
                        "type": "string",
                        "description": "Detailed explanation of the decision. Elaborates on the decision description with implementation specifics, examples, or additional context."
                    },
                    "rationale": {
                        "type": "string",
                        "description": "Why this specific option was chosen over alternatives. The reasoning and justification behind the decision."
                    },
                    "assumptions": {
                        "type": "string",
                        "description": "Things that must remain true for this decision to stay valid. When assumptions break or expire, the decision should be re-evaluated. Critical for assessing ongoing validity."
                    },
                    "consequences": {
                        "type": "string",
                        "description": "Downstream impact of this decision, both positive and negative. What it will cause, enable, or require going forward."
                    },
                    "tradeoffs": {
                        "type": "string",
                        "description": "What is explicitly being given up by choosing this option. Makes costs intentional and visible so future teams know pain points are by design, not accident."
                    },
                    "evidence": {
                        "type": "string",
                        "description": "Links to resources (papers, blogs, benchmarks, experiments, documents) that support and defend the decision. Builds credibility and auditability."
                    },
                    "options_considered": {
                        "type": "string",
                        "description": "Alternatives that were evaluated and why they were rejected. Prevents future teams from re-proposing already-rejected ideas and enables counterfactual analysis."
                    },
                    "code_reference": {
                        "type": "string",
                        "description": "References to implemented code: file paths, line ranges (e.g. src/utils.py:42-58), and code snippets that highlight where the decision is implemented."
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Optional metadata (auto-captured if not provided). Includes VCS info like {\"vcs\": {\"type\": \"git\", \"revision\": \"commit_hash\"}}. Automatically detected from the workspace if the project is version controlled."
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
            
            # Auto-capture metadata (VCS info) if not explicitly provided
            metadata = arguments.get("metadata")
            if metadata is None:
                metadata = build_metadata()
            
            record = api_client.create_record_by_names(
                project_name=project_name,
                decision_title=decision_title,
                decision_description=decision_description,
                context=arguments.get("context"),
                constraints=arguments.get("constraints"),
                decision_details=arguments.get("decision_details"),
                code_reference=arguments.get("code_reference"),
                status=status,
                rationale=arguments.get("rationale"),
                assumptions=arguments.get("assumptions"),
                consequences=arguments.get("consequences"),
                tradeoffs=arguments.get("tradeoffs"),
                evidence=arguments.get("evidence"),
                options_considered=arguments.get("options_considered"),
                metadata=metadata
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
            
            # Auto-capture metadata (VCS info) if not explicitly provided
            metadata = arguments.get("metadata")
            if metadata is None:
                metadata = build_metadata()
            
            record = api_client.update_record_by_description(
                project_name=project_name,
                decision_title=decision_title,
                decision_description=decision_description,
                context=arguments.get("context"),
                constraints=arguments.get("constraints"),
                decision_details=arguments.get("decision_details"),
                rationale=arguments.get("rationale"),
                assumptions=arguments.get("assumptions"),
                consequences=arguments.get("consequences"),
                tradeoffs=arguments.get("tradeoffs"),
                evidence=arguments.get("evidence"),
                options_considered=arguments.get("options_considered"),
                code_reference=arguments.get("code_reference"),
                metadata=metadata
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


# ---------------------------------------------------------------------------
# Prompt definitions — reusable workflow instructions for coding agents
# ---------------------------------------------------------------------------

WORKFLOW_PROMPTS = {
    "initialize_decisions": {
        "prompt": Prompt(
            name="initialize_decisions",
            description="Analyze the codebase and create decision records inferred from existing architectural choices. Use this when a project is first set up in Curio and you want to capture decisions that are already reflected in the code.",
            arguments=[]
        ),
        "build": lambda args: _build_initialize_decisions_prompt()
    },
    "analyze_and_propose": {
        "prompt": Prompt(
            name="analyze_and_propose",
            description="Analyze the codebase and existing decisions, optionally considering additional resources and goals, then propose new decisions or records where gaps exist.",
            arguments=[
                PromptArgument(
                    name="resources",
                    description="Optional comma-separated URLs or references to papers, docs, RFCs, or artifacts to consider during analysis.",
                    required=False
                ),
                PromptArgument(
                    name="intent",
                    description="Optional goals, direction, or specific areas to focus the analysis on (e.g., 'improve observability', 'prepare for multi-tenancy').",
                    required=False
                )
            ]
        ),
        "build": lambda args: _build_analyze_and_propose_prompt(
            resources=args.get("resources") if args else None,
            intent=args.get("intent") if args else None
        )
    },
    "evaluate_decisions": {
        "prompt": Prompt(
            name="evaluate_decisions",
            description="Audit the codebase against existing decision records and update statuses where appropriate — mark implemented decisions, deprecate obsolete ones, and flag invalidated assumptions.",
            arguments=[]
        ),
        "build": lambda args: _build_evaluate_decisions_prompt()
    },
    "implement_decision": {
        "prompt": Prompt(
            name="implement_decision",
            description="Take an accepted decision and implement it in the codebase, then update its status to implemented.",
            arguments=[
                PromptArgument(
                    name="decision_title",
                    description="Title of the decision to implement. If omitted, lists all accepted decisions for you to choose from.",
                    required=False
                )
            ]
        ),
        "build": lambda args: _build_implement_decision_prompt(
            decision_title=args.get("decision_title") if args else None
        )
    },
}


def _build_initialize_decisions_prompt() -> GetPromptResult:
    """Build the initialize-decisions workflow prompt."""
    instructions = """\
You are performing the **Initialize & Infer Decisions** workflow for the Curio Decision Record system.

Your goal: Analyze this codebase thoroughly and create decision records for every significant architectural or design decision that is already reflected in the code. These are recorded as `implemented_inferred` so the team has a living record of decisions that were made — even if they were never formally documented.

## Step-by-step process

### 1. Verify project setup
- Call `get_project` to check if a project is already configured for this workspace.
- If no project exists, call `init_project` with a descriptive name for this codebase.

### 2. Explore the codebase
Systematically analyze the codebase to identify architectural and design decisions. Look at:
- **Languages & frameworks**: What languages, frameworks, and runtimes are used? (e.g., Python + Flask, React + Vite)
- **Database & storage**: What databases, caches, or storage systems are in use? (e.g., PostgreSQL, Redis, S3)
- **Architecture patterns**: Monolith vs microservices, REST vs GraphQL, MVC vs other patterns
- **Infrastructure & deployment**: Docker, Kubernetes, serverless, CI/CD pipelines
- **Authentication & security**: Auth mechanisms, encryption, access control patterns
- **API design**: REST conventions, versioning strategy, error handling patterns
- **Testing strategy**: Unit tests, integration tests, E2E tests, testing frameworks
- **Code organization**: Monorepo vs polyrepo, folder structure conventions, module boundaries
- **Dependencies**: Key libraries chosen (ORM, HTTP client, logging, etc.) and why those over alternatives
- **Configuration**: How config is managed (env vars, config files, secrets management)

Read key files like package.json, requirements.txt, Cargo.toml, Dockerfile, docker-compose.yml, CI configs, and entry points to understand what is in use.

### 3. Create decisions and records
For each significant decision identified:
1. Call `create_decision` with a clear, descriptive title (e.g., "Use PostgreSQL as primary database", "Adopt Flask for backend API").
2. Call `create_record` with `status="implemented_inferred"` and fill in as many fields as you can infer:

   - **decision_description**: A concise statement of what was decided.
   - **context**: Why this decision was likely made — the situation or pressures at the time. Even if you're inferring, reason about what would have motivated this choice.
   - **constraints**: Hard requirements the decision satisfies (e.g., "Must integrate with existing Python services", "Must support ACID transactions").
   - **rationale**: Why this option was chosen over alternatives, based on what you can observe in the code and ecosystem.
   - **assumptions**: What must remain true for this decision to stay valid (e.g., "Team has Python expertise", "Data model remains primarily relational").
   - **consequences**: Observable impacts — both positive (e.g., "Enables rapid prototyping") and negative (e.g., "Requires PostgreSQL expertise for operations").
   - **tradeoffs**: What was given up (e.g., "Traded NoSQL flexibility for relational guarantees").
   - **evidence**: Links to relevant docs, benchmarks, or the specific files/patterns that reveal this decision.
   - **options_considered**: Plausible alternatives that were likely evaluated (e.g., "MySQL — similar but fewer advanced features", "MongoDB — not suitable for relational data").

### 4. Create relationships
After creating all decisions, identify relationships between them:
- Use `manage_decision_relationship` to link related decisions.
- Common relationships: `depends_on` (one decision requires another), `related_to` (decisions are connected), `derived_from` (one builds on another).
- Example: "Use React for frontend" `related_to` "Use Vite as build tool".

### 5. Present summary
After completing all records, present a clear summary:
- Total number of decisions created
- For each: title, brief description, and which fields were populated
- Any relationships created
- Areas where you were uncertain or where the team should review and refine the inferred records

## Important guidelines
- **Be thorough**: Capture every significant decision, not just the obvious ones. Infrastructure, testing strategy, and code organization choices are just as important as technology choices.
- **Be honest about uncertainty**: If you're inferring context or rationale, note that. The team can refine these later.
- **Quality over quantity for fields**: It's better to leave a field empty than to fill it with vague content. Each field should add real value.
- **Use implemented_inferred status**: This distinguishes decisions inferred from code vs. ones that went through a formal proposal process.
"""
    return GetPromptResult(
        description="Analyze the codebase and create decision records inferred from existing architectural choices.",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=instructions)
            )
        ]
    )


def _build_analyze_and_propose_prompt(
    resources: str | None = None,
    intent: str | None = None
) -> GetPromptResult:
    """Build the analyze-and-propose workflow prompt."""
    instructions = """\
You are performing the **Analyze & Propose Decisions** workflow for the Curio Decision Record system.

Your goal: Analyze this codebase alongside all existing decision records, consider any provided resources and goals, then propose new decisions or records where gaps exist or improvements are needed.

## Step-by-step process

### 1. Gather current state
- Call `get_project` to confirm the workspace project.
- Call `list_decisions` to retrieve ALL existing decisions and their records.
- For each decision that looks relevant, call `get_decision` to see full record details.
- Review the existing decisions carefully — understand what has already been decided, what's proposed, what's accepted, and what's implemented.

### 2. Analyze the codebase
- Explore the codebase structure, architecture, and implementation patterns.
- Look for areas where:
  - Significant decisions exist in code but have no corresponding decision record
  - Existing decisions may need new alternative records (e.g., a better approach has emerged)
  - Architectural gaps or risks are not captured in any decision
  - Implemented decisions have drifted from their documented intent
"""

    if resources:
        instructions += f"""
### 3. Incorporate provided resources
The user has provided these resources to consider in your analysis:
**{resources}**

- Read and analyze each resource thoroughly.
- Understand what they propose, recommend, or demonstrate.
- Consider how they relate to the current codebase and existing decisions.
- Use insights from these resources to inform your proposals.
"""
    else:
        instructions += """
### 3. Consider external context
No specific resources were provided. Base your analysis on:
- The codebase itself
- Existing decision records
- General best practices for the technologies and patterns in use
"""

    if intent:
        instructions += f"""
### 4. Focus on stated goals
The user has stated this intent/goal for the analysis:
**{intent}**

Prioritize your analysis and proposals around this goal. Ensure every proposal clearly ties back to how it supports or relates to this intent.
"""
    else:
        instructions += """
### 4. General analysis
No specific intent was provided. Perform a broad analysis looking for:
- Missing decisions that should be documented
- Opportunities to improve architecture or address technical debt
- Risks or assumptions that should be captured
"""

    instructions += """
### 5. Propose new decisions and records
For each gap or improvement identified:
1. If a new decision topic is needed, call `create_decision` with a clear title.
2. Call `create_record` with `status="proposed"` and fill ALL fields thoroughly — this is a proposal, quality matters:

   - **decision_description**: A precise statement of what is being proposed.
   - **context**: Why this decision needs to be made now. What situation, pressure, or trigger necessitates it? Be specific about the current state.
   - **constraints**: What hard requirements must be met? What limitations exist in the current system?
   - **rationale**: Why you are recommending this specific approach over alternatives. Be detailed and persuasive.
   - **assumptions**: What must be true for this proposal to be valid. Be explicit — these are the conditions under which someone should revisit this decision.
   - **consequences**: What will happen downstream if this is adopted, both good and bad. Be honest about costs.
   - **tradeoffs**: What is explicitly being given up. Every decision has costs — name them.
   - **evidence**: Any references that support this proposal — papers, benchmarks, docs, blog posts, or patterns observed in the codebase.
   - **options_considered**: List every alternative you evaluated and why it was not recommended. This prevents future teams from re-proposing rejected ideas.

3. Use `manage_decision_relationship` to link new proposals to existing decisions where relevant (e.g., `related_to`, `supersedes`, `depends_on`).

### 6. Present proposals
For each proposal, present:
- The decision title and proposed record description
- A brief summary of why this proposal matters
- Key assumptions that would need to hold
- Relationship to existing decisions

## Important guidelines
- **Don't duplicate**: Check existing decisions before proposing. If a decision already covers a topic, consider whether a new record for that decision is more appropriate than a new decision entirely.
- **Be opinionated but honest**: Propose what you believe is best, but make tradeoffs visible. Don't hide costs.
- **Assumptions are critical**: The most valuable part of a proposal is often the assumptions — they tell reviewers exactly when this decision should be revisited.
- **Link everything**: Decisions rarely exist in isolation. Create relationships to show how proposals connect to the existing decision landscape.
"""
    return GetPromptResult(
        description="Analyze the codebase and existing decisions, then propose new decisions or records where gaps exist.",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=instructions)
            )
        ]
    )


def _build_evaluate_decisions_prompt() -> GetPromptResult:
    """Build the evaluate-decisions workflow prompt."""
    instructions = """\
You are performing the **Evaluate Decisions** workflow for the Curio Decision Record system.

Your goal: Audit the codebase against all existing decision records and update statuses where appropriate. This includes promoting accepted decisions that have been implemented, deprecating decisions no longer reflected in code, and flagging assumptions that may have been invalidated.

## Step-by-step process

### 1. Gather all decisions
- Call `get_project` to confirm the workspace project.
- Call `list_decisions` to get ALL decisions.
- For each decision, call `get_decision` to retrieve full record details including all fields.

### 2. Evaluate accepted records — should any be marked implemented?
For each record with status `accepted`:
- Read the decision_description, constraints, and rationale carefully.
- Search the codebase for evidence that this decision has been implemented.
- Look for: relevant code files, configuration, dependencies, tests, documentation that match what was decided.
- **If the decision is clearly implemented in code**: Call `change_record_status` with `status="implemented"` and provide a reason explaining what evidence you found (e.g., "Found PostgreSQL configuration in docker-compose.yml and SQLAlchemy models in backend/models.py").
- **If partially implemented**: Do NOT change status. Instead, note what is done and what remains.

### 3. Evaluate proposed records — any already implemented?
For each record with status `proposed`:
- Check if the proposed change has already been implemented (perhaps by someone who didn't update the record).
- **If implemented**: Call `change_record_status` to first move to `accepted` then to `implemented`, or note that the workflow requires acceptance first.
- **If clearly not going to happen**: Consider whether it should be `rejected` and flag it for team review.

### 4. Evaluate implemented records — should any be deprecated?
For each record with status `implemented` or `implemented_inferred`:
- Check if the decision is still reflected in the current codebase.
- Look for: Has the technology been replaced? Has the pattern been abandoned? Has the configuration changed?
- **If the decision is no longer reflected in code**: Call `change_record_status` with `status="deprecated"` and provide a reason explaining what changed (e.g., "Flask backend has been replaced with FastAPI — see backend/main.py").
- **If still valid**: Leave as is.

### 5. Evaluate assumptions — are any invalidated?
This is the most critical evaluation step. For EVERY record (regardless of status):
- Read the `assumptions` field carefully.
- For each assumption stated, evaluate whether it still holds true:
  - Check the codebase for evidence
  - Consider the current technology landscape
  - Look for changes that may have invalidated assumptions
- **If assumptions are invalidated**: Flag the decision prominently. This does not automatically change status, but it means the decision should be reviewed. Use `update_decision_record` to add a note in the context or use the relationship tools to flag it.

### 6. Present evaluation report
Present a clear, structured report:

**Status Changes Made:**
- List each status change with the decision title, record description, old status, new status, and reason.

**Assumptions Flagged:**
- List each decision where assumptions may be invalidated, with the specific assumption and why you believe it may no longer hold.

**No Changes Needed:**
- Briefly note decisions that were evaluated and found to be current and valid.

**Recommendations:**
- Any decisions that need team attention but where you couldn't make a definitive status change.

## Important guidelines
- **Be conservative with status changes**: Only change status when you have clear evidence. When in doubt, flag for human review rather than making the change.
- **Assumptions are the highest-value check**: A decision can have the right status but invalid assumptions — that's a ticking time bomb. Always evaluate assumptions thoroughly.
- **Provide evidence**: Every status change should include specific evidence (file paths, code patterns, configuration) that justifies the change.
- **Don't skip any decisions**: Every decision and record should be evaluated, even if it seems obviously current.
"""
    return GetPromptResult(
        description="Audit the codebase against existing decisions and update statuses where appropriate.",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=instructions)
            )
        ]
    )


def _build_implement_decision_prompt(
    decision_title: str | None = None
) -> GetPromptResult:
    """Build the implement-decision workflow prompt."""
    instructions = """\
You are performing the **Implement Decision** workflow for the Curio Decision Record system.

Your goal: Take an accepted decision and implement it in the codebase, respecting all documented constraints, assumptions, and tradeoffs. After implementation, update the decision record status.

## Step-by-step process

### 1. Identify the decision to implement
"""
    if decision_title:
        instructions += f"""The user has specified: **{decision_title}**
- Call `get_decision(decision_title="{decision_title}")` to retrieve the full decision with all records.
- Find the `accepted` record for this decision. If there is no accepted record, inform the user — only accepted decisions should be implemented.
"""
    else:
        instructions += """\
No specific decision was provided.
- Call `list_decisions(status="accepted")` to show all decisions with accepted records ready for implementation.
- Present the list to the user and ask which one to implement.
- Once selected, call `get_decision(decision_title=...)` to retrieve full details.
"""

    instructions += """
### 2. Study the decision record thoroughly
Before writing any code, read and internalize every field of the accepted record:
- **decision_description**: This is exactly what needs to be implemented.
- **context**: Understand why this decision was made — it affects how you implement it.
- **constraints**: These are non-negotiable. Your implementation MUST satisfy every stated constraint.
- **rationale**: Understand the reasoning so your implementation aligns with the intent.
- **assumptions**: Verify these are still true before proceeding. If any assumption is no longer valid, STOP and inform the user — the decision may need to be re-evaluated before implementation.
- **tradeoffs**: Be aware of what was intentionally given up. Don't accidentally try to "fix" an intentional tradeoff.
- **options_considered**: Understand what was rejected and why, so you don't accidentally implement a rejected approach.
- **evidence**: Review any linked resources for implementation guidance.

Also check for related decisions:
- Call `list_decision_relationships` or `list_decision_record_relationships` to see dependencies.
- If this decision `depends_on` another, verify that dependency is implemented first.

### 3. Plan the implementation
Before coding:
- Identify which files need to be created or modified.
- Plan the changes in a logical order.
- Ensure the plan respects all constraints.
- Identify any tests that need to be written or updated.

### 4. Implement the changes
- Write clean, well-structured code that matches the codebase's existing patterns and conventions.
- Add appropriate comments referencing the decision where it helps future readers understand why something was done a certain way.
- Write or update tests as needed.
- Update any relevant documentation.

### 5. Verify the implementation
- Run existing tests to make sure nothing is broken.
- Verify that every stated constraint is satisfied.
- Confirm that the assumptions listed in the record still hold.
- Check that you haven't accidentally reintroduced something that was an intentional tradeoff.

### 6. Update the decision record
- Call `change_record_status` with `status="implemented"` and provide a descriptive reason summarizing what was done (e.g., "Implemented PostgreSQL migration: added models in backend/models.py, migration in migrations/001_initial.sql, updated docker-compose.yml").
- If the implementation required any deviations from the original proposal, call `update_decision_record` to update relevant fields (e.g., update constraints if new ones were discovered, update consequences if new impacts were found).

### 7. Present summary
Report what was done:
- Files created or modified
- Key implementation decisions made during coding
- Tests added or updated
- Any deviations from the original decision record (and why)
- The status change made

## Important guidelines
- **Constraints are non-negotiable**: If you cannot satisfy a stated constraint, stop and discuss with the user rather than silently violating it.
- **Check assumptions first**: If an assumption is no longer valid, the decision itself may be invalid. Don't implement a decision built on false assumptions.
- **Respect tradeoffs**: The decision record may explicitly say "we give up X for Y." Don't try to have both unless you're proposing a new decision.
- **One decision at a time**: Focus on implementing the single specified decision. If you discover other decisions are needed, note them but don't scope-creep.
- **Update the record**: The implementation is not complete until the status is updated. This closes the loop.
"""
    return GetPromptResult(
        description="Implement an accepted decision in the codebase and update its status.",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=instructions)
            )
        ]
    )


@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List all available workflow prompts."""
    return [entry["prompt"] for entry in WORKFLOW_PROMPTS.values()]


@app.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
    """Get a specific workflow prompt with its detailed instructions."""
    entry = WORKFLOW_PROMPTS.get(name)
    if not entry:
        raise ValueError(f"Unknown prompt: {name}. Available prompts: {', '.join(WORKFLOW_PROMPTS.keys())}")
    return entry["build"](arguments)


