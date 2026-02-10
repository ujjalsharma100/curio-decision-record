"""
Curio Decision Record Flask Application

A simple Flask application for managing decision records.
"""

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from decision_service import DecisionService
from database_service import DatabaseService

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize services
db_service = DatabaseService()
decision_service = DecisionService(db_service)


# ==================== Projects Routes ====================

@app.route('/api/projects', methods=['GET'])
def list_projects():
    """List all projects."""
    try:
        projects = decision_service.get_all_projects()
        return jsonify(projects)
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects', methods=['POST'])
def create_project():
    """Create a new project."""
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    
    try:
        project = decision_service.create_project(
            name=data['name'],
            description=data.get('description')
        )
        return jsonify(project), 201
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>', methods=['GET'])
def get_project(project_id):
    """Get a project by ID."""
    try:
        project = decision_service.get_project(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        return jsonify(project)
    except Exception as e:
        logger.error(f"Error getting project: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>', methods=['PUT'])
def update_project(project_id):
    """Update a project."""
    data = request.get_json()
    
    try:
        project = decision_service.update_project(
            project_id=project_id,
            name=data.get('name'),
            description=data.get('description')
        )
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        return jsonify(project)
    except Exception as e:
        logger.error(f"Error updating project: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>/records', methods=['GET'])
def list_project_records(project_id):
    """List all decision records across all decisions in a project. Supports cross-decision relationships."""
    try:
        records = decision_service.get_records_by_project(project_id)
        return jsonify(records)
    except Exception as e:
        logger.error(f"Error listing project records: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>/action-items', methods=['GET'])
def get_project_action_items(project_id):
    """
    Get action items for a project.
    Returns decisions needing review (proposed records) and
    decisions pending implementation (accepted records).
    """
    try:
        action_items = decision_service.get_project_action_items(project_id)
        return jsonify(action_items)
    except Exception as e:
        logger.error(f"Error getting project action items: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project."""
    try:
        success = decision_service.delete_project(project_id)
        if not success:
            return jsonify({'error': 'Project not found'}), 404
        return '', 204
    except Exception as e:
        logger.error(f"Error deleting project: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== Decisions Routes ====================

@app.route('/api/projects/<project_id>/decisions', methods=['GET'])
def list_decisions(project_id):
    """List all decisions for a project."""
    try:
        decisions = decision_service.get_decisions_by_project(project_id)
        
        # Filter by status if provided
        status_filter = request.args.get('status')
        if status_filter:
            filtered_decisions = []
            for decision in decisions:
                decision_with_records = decision_service.get_decision(
                    decision['id'],
                    include_records=True
                )
                if decision_with_records and decision_with_records.get('records'):
                    for record in decision_with_records['records']:
                        if record.get('status') == status_filter:
                            filtered_decisions.append(decision)
                            break
            decisions = filtered_decisions
        
        return jsonify(decisions)
    except Exception as e:
        logger.error(f"Error listing decisions: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>/decisions', methods=['POST'])
def create_decision(project_id):
    """Create a new decision for a project."""
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    try:
        decision = decision_service.create_decision(
            project_id=project_id,
            title=data['title']
        )
        return jsonify(decision), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error creating decision: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/decisions/<decision_id>', methods=['GET'])
def get_decision(decision_id):
    """Get a decision by ID with all its records."""
    try:
        decision = decision_service.get_decision(decision_id, include_records=True)
        if not decision:
            return jsonify({'error': 'Decision not found'}), 404
        return jsonify(decision)
    except Exception as e:
        logger.error(f"Error getting decision: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/decisions/<decision_id>', methods=['PUT'])
def update_decision(decision_id):
    """Update a decision."""
    data = request.get_json()
    
    try:
        decision = decision_service.update_decision(
            decision_id=decision_id,
            title=data.get('title')
        )
        if not decision:
            return jsonify({'error': 'Decision not found'}), 404
        return jsonify(decision)
    except Exception as e:
        logger.error(f"Error updating decision: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/decisions/<decision_id>', methods=['DELETE'])
def delete_decision(decision_id):
    """Delete a decision."""
    try:
        success = decision_service.delete_decision(decision_id)
        if not success:
            return jsonify({'error': 'Decision not found'}), 404
        return '', 204
    except Exception as e:
        logger.error(f"Error deleting decision: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/decisions/<decision_id>/timeline', methods=['GET'])
def get_decision_timeline(decision_id):
    """
    Get a comprehensive timeline of all events for a decision.
    Events include: record creation, status changes, and content changes.
    """
    try:
        timeline = decision_service.get_decision_timeline(decision_id)
        return jsonify(timeline)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting decision timeline: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/decisions/<decision_id>/implementation-history', methods=['GET'])
def get_implementation_history(decision_id):
    """
    Get the implementation history for a decision.
    Shows the current implemented decision and all past implementations
    that have been deprecated, in chronological order.
    """
    try:
        history = decision_service.get_implementation_history(decision_id)
        return jsonify(history)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting implementation history: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/projects/<project_id>/decisions/accepted', methods=['GET'])
def get_accepted_decisions(project_id):
    """
    Get all accepted decisions for a project.
    Useful for finding decisions ready to implement.
    """
    try:
        decisions = decision_service.get_decisions_by_project(project_id)
        accepted_decisions = []
        
        for decision in decisions:
            decision_with_records = decision_service.get_decision(
                decision['id'],
                include_records=True
            )
            if decision_with_records and decision_with_records.get('records'):
                for record in decision_with_records['records']:
                    if record.get('status') == 'accepted':
                        accepted_decisions.append({
                            'decision': decision,
                            'accepted_record': record
                        })
                        break
        
        return jsonify(accepted_decisions)
    except Exception as e:
        logger.error(f"Error getting accepted decisions: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== Decision Records Routes ====================

@app.route('/api/decisions/<decision_id>/records', methods=['GET'])
def list_records(decision_id):
    """List all records for a decision."""
    try:
        records = decision_service.get_decision_records_by_decision(decision_id)
        return jsonify(records)
    except Exception as e:
        logger.error(f"Error listing records: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/decisions/<decision_id>/records', methods=['POST'])
def create_record(decision_id):
    """Create a new decision record."""
    data = request.get_json()
    
    if not data or not data.get('decision_description'):
        return jsonify({'error': 'decision_description is required'}), 400
    
    try:
        record = decision_service.create_decision_record(
            decision_id=decision_id,
            decision_description=data['decision_description'],
            context=data.get('context'),
            constraints=data.get('constraints'),
            decision_details=data.get('decision_details'),
            status=data.get('status'),
            rationale=data.get('rationale'),
            assumptions=data.get('assumptions'),
            consequences=data.get('consequences'),
            tradeoffs=data.get('tradeoffs'),
            evidence=data.get('evidence'),
            options_considered=data.get('options_considered'),
            code_reference=data.get('code_reference'),
            metadata=data.get('metadata')
        )
        return jsonify(record), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating record: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/records/<record_id>', methods=['GET'])
def get_record(record_id):
    """Get a decision record by ID."""
    try:
        record = decision_service.get_decision_record(record_id)
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        return jsonify(record)
    except Exception as e:
        logger.error(f"Error getting record: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/records/<record_id>', methods=['PUT'])
def update_record(record_id):
    """
    Update a decision record.

    Version is auto-incremented on each update.
    A snapshot of the previous state is saved.
    A changelog entry is created documenting the changes.
    """
    data = request.get_json()

    try:
        record = decision_service.update_decision_record(
            record_id=record_id,
            context=data.get('context'),
            constraints=data.get('constraints'),
            decision_description=data.get('decision_description'),
            decision_details=data.get('decision_details'),
            rationale=data.get('rationale'),
            assumptions=data.get('assumptions'),
            consequences=data.get('consequences'),
            tradeoffs=data.get('tradeoffs'),
            evidence=data.get('evidence'),
            options_considered=data.get('options_considered'),
            code_reference=data.get('code_reference'),
            metadata=data.get('metadata')
        )
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        return jsonify(record)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error updating record: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/records/<record_id>', methods=['DELETE'])
def delete_record(record_id):
    """Delete a decision record."""
    try:
        success = decision_service.delete_decision_record(record_id)
        if not success:
            return jsonify({'error': 'Record not found'}), 404
        return '', 204
    except Exception as e:
        logger.error(f"Error deleting record: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/records/<record_id>/status', methods=['PATCH'])
def change_status(record_id):
    """Change the status of a decision record."""
    data = request.get_json()
    
    if not data or not data.get('status'):
        return jsonify({'error': 'status is required'}), 400
    
    try:
        result = decision_service.change_record_status(
            record_id=record_id,
            new_status=data['status'],
            reason=data.get('reason'),
            auto_handle_conflicts=data.get('auto_handle_conflicts', True)
        )
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error changing status: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/records/<record_id>/history', methods=['GET'])
def get_status_history(record_id):
    """Get the status history of a decision record."""
    try:
        history = decision_service.get_status_history(record_id)
        return jsonify(history)
    except Exception as e:
        logger.error(f"Error getting status history: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== Relationship Routes ====================

@app.route('/api/records/<record_id>/relationships', methods=['GET'])
def list_relationships(record_id):
    """List all relationships for a record."""
    try:
        relationships = decision_service.get_relationships(record_id)
        return jsonify(relationships)
    except Exception as e:
        logger.error(f"Error listing relationships: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/records/<record_id>/relationships', methods=['POST'])
def create_relationship(record_id):
    """Create a relationship from this record to another."""
    data = request.get_json()
    
    if not data or not data.get('target_record_id') or not data.get('relationship_type'):
        return jsonify({'error': 'target_record_id and relationship_type are required'}), 400
    
    try:
        relationship = decision_service.create_relationship(
            source_record_id=record_id,
            target_record_id=data['target_record_id'],
            relationship_type=data['relationship_type'],
            description=data.get('description')
        )
        return jsonify(relationship), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error creating relationship: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/relationships/<relationship_id>', methods=['PATCH'])
def update_relationship(relationship_id):
    """Update a relationship's type or description."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body required'}), 400
    try:
        relationship = decision_service.update_relationship(
            relationship_id,
            relationship_type=data.get('relationship_type'),
            description=data.get('description')
        )
        if not relationship:
            return jsonify({'error': 'Relationship not found'}), 404
        return jsonify(relationship)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error updating relationship: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/relationships/<relationship_id>', methods=['DELETE'])
def delete_relationship(relationship_id):
    """Delete a relationship."""
    try:
        success = decision_service.delete_relationship(relationship_id)
        if not success:
            return jsonify({'error': 'Relationship not found'}), 404
        return '', 204
    except Exception as e:
        logger.error(f"Error deleting relationship: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== Decision-Level Relationship Routes ====================

@app.route('/api/decisions/<decision_id>/decision-relationships', methods=['GET'])
def list_decision_relationships(decision_id):
    """List all decision-level relationships for a decision."""
    try:
        relationships = decision_service.get_decision_relationships(decision_id)
        return jsonify(relationships)
    except Exception as e:
        logger.error(f"Error listing decision relationships: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/decisions/<decision_id>/decision-relationships', methods=['POST'])
def create_decision_relationship(decision_id):
    """Create a decision-level relationship from this decision to another."""
    data = request.get_json()
    
    if not data or not data.get('target_decision_id') or not data.get('relationship_type'):
        return jsonify({'error': 'target_decision_id and relationship_type are required'}), 400
    
    try:
        relationship = decision_service.create_decision_relationship(
            source_decision_id=decision_id,
            target_decision_id=data['target_decision_id'],
            relationship_type=data['relationship_type'],
            description=data.get('description')
        )
        return jsonify(relationship), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error creating decision relationship: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/decision-relationships/<relationship_id>', methods=['PATCH'])
def update_decision_relationship(relationship_id):
    """Update a decision relationship's type or description."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body required'}), 400
    try:
        relationship = decision_service.update_decision_relationship(
            relationship_id,
            relationship_type=data.get('relationship_type'),
            description=data.get('description')
        )
        if not relationship:
            return jsonify({'error': 'Decision relationship not found'}), 404
        return jsonify(relationship)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error updating decision relationship: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/decision-relationships/<relationship_id>', methods=['DELETE'])
def delete_decision_relationship(relationship_id):
    """Delete a decision relationship."""
    try:
        success = decision_service.delete_decision_relationship(relationship_id)
        if not success:
            return jsonify({'error': 'Decision relationship not found'}), 404
        return '', 204
    except Exception as e:
        logger.error(f"Error deleting decision relationship: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== Version Control Routes ====================

@app.route('/api/records/<record_id>/versions', methods=['GET'])
def get_record_versions(record_id):
    """Get all versions of a decision record."""
    try:
        versions = decision_service.get_record_versions(record_id)
        return jsonify(versions)
    except Exception as e:
        logger.error(f"Error getting record versions: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/records/<record_id>/versions/<int:version>', methods=['GET'])
def get_record_at_version(record_id, version):
    """Get a decision record as it was at a specific version."""
    try:
        snapshot = decision_service.get_record_at_version(record_id, version)
        if not snapshot:
            return jsonify({'error': f'Version {version} not found'}), 404
        return jsonify(snapshot)
    except Exception as e:
        logger.error(f"Error getting record at version: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/records/<record_id>/changelog', methods=['GET'])
def get_record_changelog(record_id):
    """Get the changelog for a decision record."""
    try:
        changelog = decision_service.get_record_changelog(record_id)
        return jsonify(changelog)
    except Exception as e:
        logger.error(f"Error getting record changelog: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/records/<record_id>/diff', methods=['GET'])
def get_version_diff(record_id):
    """
    Get the diff between two versions of a decision record.

    Query params:
    - from_version: The starting version number (int) or "current" for the current live version
    - to_version: The ending version number (int) or "current" for the current live version
    """
    from_version_param = request.args.get('from_version')
    to_version_param = request.args.get('to_version')

    if from_version_param is None or to_version_param is None:
        return jsonify({'error': 'from_version and to_version query params are required'}), 400

    # Parse version parameters - allow "current" string or integer
    try:
        if from_version_param.lower() == "current":
            from_version = "current"
        else:
            from_version = int(from_version_param)
    except (ValueError, AttributeError):
        return jsonify({'error': 'from_version must be an integer or "current"'}), 400

    try:
        if to_version_param.lower() == "current":
            to_version = "current"
        else:
            to_version = int(to_version_param)
    except (ValueError, AttributeError):
        return jsonify({'error': 'to_version must be an integer or "current"'}), 400

    try:
        diff = decision_service.get_version_diff(record_id, from_version, to_version)
        return jsonify(diff)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting version diff: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/records/<record_id>/revert', methods=['POST'])
def revert_to_version(record_id):
    """
    Revert a decision record to a previous version.

    This creates a new version with the content from the specified version.

    Request body:
    - version: The version number to revert to
    - reason: Optional reason for the revert
    """
    data = request.get_json()

    if not data or data.get('version') is None:
        return jsonify({'error': 'version is required'}), 400

    try:
        record = decision_service.revert_to_version(
            record_id=record_id,
            version=data['version'],
            reason=data.get('reason')
        )
        return jsonify(record)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error reverting to version: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== MCP Server API (by name/title) ====================
# These endpoints use natural identifiers (names/titles) instead of UUIDs
# for better usability in MCP tools

@app.route('/api/mcp/projects/<project_name>', methods=['GET'])
def get_project_by_name_mcp(project_name):
    """Get a project by name (MCP endpoint)."""
    try:
        project = decision_service.get_project_by_name(project_name)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        return jsonify(project)
    except Exception as e:
        logger.error(f"Error getting project by name: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/mcp/projects/<project_name>/decisions', methods=['GET'])
def list_decisions_by_project_name_mcp(project_name):
    """List all decisions for a project by name (MCP endpoint)."""
    try:
        status_filter = request.args.get('status')
        decisions = decision_service.get_decisions_by_project_name(project_name, status=status_filter)
        return jsonify(decisions)
    except Exception as e:
        logger.error(f"Error listing decisions by project name: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/mcp/projects/<project_name>/decisions', methods=['POST'])
def create_decision_by_project_name_mcp(project_name):
    """Create a new decision by project name (MCP endpoint)."""
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'error': 'title is required'}), 400
    
    try:
        decision = decision_service.create_decision_by_project_name(
            project_name=project_name,
            title=data['title']
        )
        return jsonify(decision), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error creating decision by project name: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/mcp/projects/<project_name>/decisions/<decision_title>', methods=['GET'])
def get_decision_by_title_mcp(project_name, decision_title):
    """Get a decision by project name and title (MCP endpoint)."""
    try:
        decision = decision_service.get_decision_by_title(project_name, decision_title)
        if not decision:
            return jsonify({'error': 'Decision not found'}), 404
        return jsonify(decision)
    except Exception as e:
        logger.error(f"Error getting decision by title: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/mcp/projects/<project_name>/decisions/<decision_title>/records', methods=['POST'])
def create_record_by_names_mcp(project_name, decision_title):
    """Create a decision record by project name and decision title (MCP endpoint)."""
    data = request.get_json()
    
    if not data or not data.get('decision_description'):
        return jsonify({'error': 'decision_description is required'}), 400
    
    try:
        record = decision_service.create_decision_record_by_names(
            project_name=project_name,
            decision_title=decision_title,
            decision_description=data['decision_description'],
            context=data.get('context'),
            constraints=data.get('constraints'),
            decision_details=data.get('decision_details'),
            status=data.get('status'),
            rationale=data.get('rationale'),
            assumptions=data.get('assumptions'),
            consequences=data.get('consequences'),
            tradeoffs=data.get('tradeoffs'),
            evidence=data.get('evidence'),
            options_considered=data.get('options_considered'),
            code_reference=data.get('code_reference'),
            metadata=data.get('metadata')
        )
        return jsonify(record), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error creating record by names: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/mcp/projects/<project_name>/decisions/<decision_title>/records/<path:decision_description>', methods=['GET'])
def get_record_by_description_mcp(project_name, decision_title, decision_description):
    """Get a decision record by project name, decision title, and description (MCP endpoint)."""
    try:
        record = decision_service.get_decision_record_by_description(
            project_name, decision_title, decision_description
        )
        if not record:
            return jsonify({'error': 'Decision record not found'}), 404
        return jsonify(record)
    except Exception as e:
        logger.error(f"Error getting record by description: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/mcp/projects/<project_name>/decisions/<decision_title>/records/<path:decision_description>', methods=['PUT'])
def update_record_by_description_mcp(project_name, decision_title, decision_description):
    """Update a decision record by project name, decision title, and description (MCP endpoint)."""
    data = request.get_json()
    
    try:
        record = decision_service.update_decision_record_by_description(
            project_name=project_name,
            decision_title=decision_title,
            decision_description=decision_description,
            context=data.get('context'),
            constraints=data.get('constraints'),
            decision_details=data.get('decision_details'),
            rationale=data.get('rationale'),
            assumptions=data.get('assumptions'),
            consequences=data.get('consequences'),
            tradeoffs=data.get('tradeoffs'),
            evidence=data.get('evidence'),
            options_considered=data.get('options_considered'),
            code_reference=data.get('code_reference'),
            metadata=data.get('metadata')
        )
        return jsonify(record)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error updating record by description: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/mcp/projects/<project_name>/decisions/<decision_title>/records/<path:decision_description>/status', methods=['PATCH'])
def change_record_status_by_description_mcp(project_name, decision_title, decision_description):
    """Change the status of a decision record by project name, decision title, and description (MCP endpoint)."""
    data = request.get_json()
    
    if not data or not data.get('status'):
        return jsonify({'error': 'status is required'}), 400
    
    try:
        result = decision_service.change_record_status_by_description(
            project_name=project_name,
            decision_title=decision_title,
            decision_description=decision_description,
            new_status=data['status'],
            reason=data.get('reason'),
            auto_handle_conflicts=data.get('auto_handle_conflicts', True)
        )
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error changing record status by description: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/mcp/projects/<project_name>/decisions/<decision_title>/implementation-history', methods=['GET'])
def get_implementation_history_by_title_mcp(project_name, decision_title):
    """Get implementation history for a decision by project name and title (MCP endpoint)."""
    try:
        decision = decision_service.get_decision_by_title(project_name, decision_title)
        if not decision:
            return jsonify({'error': 'Decision not found'}), 404
        
        history = decision_service.get_implementation_history(decision['id'])
        return jsonify(history)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting implementation history by title: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== Health Check ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        if db_service.test_connection():
            return jsonify({'status': 'healthy', 'database': 'connected'}), 200
        else:
            return jsonify({'status': 'unhealthy', 'database': 'disconnected'}), 503
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 503


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
