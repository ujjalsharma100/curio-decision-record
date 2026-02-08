"""
Decision service layer for business logic.

This module provides business logic for managing projects, decisions, and decision records.
It acts as an intermediate layer between the API endpoints and the database service.
"""

import uuid
import logging
from typing import Dict, List, Optional
from models import (
    Project, Decision, DecisionRecord, StatusHistory, DecisionRecordRelationship,
    DecisionRelationship, DecisionRecordStatus
)
from database_service import DatabaseService

logger = logging.getLogger(__name__)


# Status transition rules
VALID_TRANSITIONS = {
    DecisionRecordStatus.PROPOSED.value: [
        DecisionRecordStatus.ACCEPTED.value,
        DecisionRecordStatus.REJECTED.value
    ],
    DecisionRecordStatus.ACCEPTED.value: [
        DecisionRecordStatus.IMPLEMENTED.value,
        DecisionRecordStatus.REJECTED.value,
        DecisionRecordStatus.DEPRECATED.value
    ],
    DecisionRecordStatus.IMPLEMENTED.value: [
        DecisionRecordStatus.DEPRECATED.value
    ],
    DecisionRecordStatus.IMPLEMENTED_INFERRED.value: [
        DecisionRecordStatus.DEPRECATED.value
    ],
    DecisionRecordStatus.REJECTED.value: [],
    DecisionRecordStatus.DEPRECATED.value: []
}


class DecisionService:
    """Service for managing decision records with business logic."""
    
    def __init__(self, db_service: DatabaseService = None):
        """Initialize decision service with database service."""
        self.db = db_service or DatabaseService()
    
    # ==================== Projects ====================
    
    def create_project(self, name: str, description: str = None) -> Dict:
        """Create a new project."""
        project = Project(name=name, description=description)
        project_data = project.to_dict()
        result = self.db.create_project(project_data)
        return result
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get a project by ID."""
        project = self.db.get_project(project_id)
        if project:
            # Use get_decisions_by_project which includes status_counts
            decisions = self.db.get_decisions_by_project(project_id)
            for d in decisions:
                dec_rels = self.db.get_decision_relationships_by_decision(d['id'])
                d['outgoing_decision_relationships'] = dec_rels['outgoing']
                d['incoming_decision_relationships'] = dec_rels['incoming']
            project['decisions'] = decisions
            project['decision_count'] = len(decisions)
        return project
    
    def get_all_projects(self) -> List[Dict]:
        """Get all projects."""
        return self.db.get_all_projects()
    
    def update_project(self, project_id: str, name: str = None, description: str = None) -> Dict:
        """Update a project."""
        project_data = {}
        if name is not None:
            project_data['name'] = name
        if description is not None:
            project_data['description'] = description
        
        return self.db.update_project(project_id, project_data)
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        return self.db.delete_project(project_id)
    
    # ==================== Projects (by name) ====================
    
    def get_project_by_name(self, name: str) -> Optional[Dict]:
        """Get a project by name."""
        project = self.db.get_project_by_name(name)
        if project:
            decisions = self.db.get_decisions_by_project(project['id'])
            project['decisions'] = decisions
            project['decision_count'] = len(decisions)
        return project
    
    # ==================== Decisions ====================
    
    def create_decision(self, project_id: str, title: str) -> Dict:
        """Create a new decision."""
        # Verify project exists
        project = self.db.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        decision = Decision(project_id=project_id, title=title)
        decision_data = decision.to_dict()
        result = self.db.create_decision(decision_data)
        return result
    
    def get_decision(self, decision_id: str, include_records: bool = False) -> Optional[Dict]:
        """Get a decision by ID."""
        decision = self.db.get_decision(decision_id)
        if decision:
            if include_records:
                records = self.db.get_decision_records_by_decision(decision_id)
                # Add relationships to each record
                for record in records:
                    relationships = self.db.get_relationships_by_record(record['id'])
                    record['outgoing_relationships'] = relationships['outgoing']
                    record['incoming_relationships'] = relationships['incoming']
                decision['records'] = records
            decision['record_count'] = len(self.db.get_decision_records_by_decision(decision_id))
            # Add decision-level relationships
            dec_rels = self.db.get_decision_relationships_by_decision(decision_id)
            decision['outgoing_decision_relationships'] = dec_rels['outgoing']
            decision['incoming_decision_relationships'] = dec_rels['incoming']
        return decision
    
    def get_decisions_by_project(self, project_id: str) -> List[Dict]:
        """Get all decisions for a project."""
        return self.db.get_decisions_by_project(project_id)
    
    def get_records_by_project(self, project_id: str) -> List[Dict]:
        """Get all decision records across all decisions in a project. Used for cross-decision relationships."""
        decisions = self.db.get_decisions_by_project(project_id)
        all_records = []
        for decision in decisions:
            records = self.get_decision_records_by_decision(decision['id'])
            for record in records:
                record['decision_title'] = decision.get('title', '')
                all_records.append(record)
        return all_records
    
    def update_decision(self, decision_id: str, title: str = None) -> Dict:
        """Update a decision."""
        decision_data = {}
        if title is not None:
            decision_data['title'] = title
        
        return self.db.update_decision(decision_id, decision_data)
    
    def delete_decision(self, decision_id: str) -> bool:
        """Delete a decision."""
        return self.db.delete_decision(decision_id)
    
    # ==================== Decisions (by title) ====================
    
    def get_decision_by_title(self, project_name: str, title: str) -> Optional[Dict]:
        """Get a decision by project name and title."""
        project = self.db.get_project_by_name(project_name)
        if not project:
            return None
        
        decision = self.db.get_decision_by_title(project['id'], title)
        if decision:
            records = self.db.get_decision_records_by_decision(decision['id'])
            for record in records:
                relationships = self.db.get_relationships_by_record(record['id'])
                record['outgoing_relationships'] = relationships['outgoing']
                record['incoming_relationships'] = relationships['incoming']
            decision['records'] = records
            decision['record_count'] = len(records)
            dec_rels = self.db.get_decision_relationships_by_decision(decision['id'])
            decision['outgoing_decision_relationships'] = dec_rels['outgoing']
            decision['incoming_decision_relationships'] = dec_rels['incoming']
        return decision
    
    def get_decisions_by_project_name(self, project_name: str, status: str = None) -> List[Dict]:
        """Get all decisions for a project by project name, optionally filtered by status."""
        project = self.db.get_project_by_name(project_name)
        if not project:
            return []
        
        decisions = self.db.get_decisions_by_project(project['id'])
        
        if status:
            filtered_decisions = []
            for decision in decisions:
                decision_with_records = self.get_decision(decision['id'], include_records=True)
                if decision_with_records and decision_with_records.get('records'):
                    for record in decision_with_records['records']:
                        if record.get('status') == status:
                            filtered_decisions.append(decision)
                            break
            decisions = filtered_decisions
        
        return decisions
    
    def create_decision_by_project_name(self, project_name: str, title: str) -> Dict:
        """Create a new decision by project name."""
        project = self.db.get_project_by_name(project_name)
        if not project:
            raise ValueError(f"Project '{project_name}' not found")
        
        return self.create_decision(project['id'], title)
    
    # ==================== Decision Records ====================
    
    def create_decision_record(self, decision_id: str, decision_description: str,
                              context: str = None, constraints: str = None,
                              status: str = None, rationale: str = None,
                              assumptions: str = None, consequences: str = None,
                              tradeoffs: str = None, evidence: str = None,
                              options_considered: str = None) -> Dict:
        """Create a new decision record."""
        # Verify decision exists
        decision = self.db.get_decision(decision_id)
        if not decision:
            raise ValueError(f"Decision {decision_id} not found")
        
        # Validate status
        if status and status not in [s.value for s in DecisionRecordStatus]:
            raise ValueError(f"Invalid status: {status}")
        
        record = DecisionRecord(
            decision_id=decision_id,
            context=context,
            constraints=constraints,
            decision_description=decision_description,
            status=status or DecisionRecordStatus.PROPOSED.value,
            rationale=rationale,
            assumptions=assumptions,
            consequences=consequences,
            tradeoffs=tradeoffs,
            evidence=evidence,
            options_considered=options_considered,
            version=1  # Always starts at version 1, auto-increments on updates
        )
        record_data = record.to_dict()
        result = self.db.create_decision_record(record_data)
        
        # Create initial status history entry
        history = StatusHistory(
            decision_record_id=result['id'],
            from_status=None,
            to_status=result['status'],
            reason='Initial creation'
        )
        history_data = history.to_dict()
        self.db.create_status_history(history_data)

        # Create initial version snapshot (version 1)
        snapshot_data = {
            'id': result['id'],
            'decision_id': result['decision_id'],
            'context': result.get('context'),
            'constraints': result.get('constraints'),
            'decision_description': result.get('decision_description'),
            'status': result.get('status'),
            'rationale': result.get('rationale'),
            'assumptions': result.get('assumptions'),
            'consequences': result.get('consequences'),
            'tradeoffs': result.get('tradeoffs'),
            'evidence': result.get('evidence'),
            'options_considered': result.get('options_considered'),
            'version': 1,
            'created_at': str(result.get('created_at', '')),
            'updated_at': str(result.get('updated_at', ''))
        }
        self.db.create_record_version({
            'id': str(uuid.uuid4()),
            'decision_record_id': result['id'],
            'version': 1,
            'snapshot': snapshot_data
        })

        # Add relationships
        relationships = self.db.get_relationships_by_record(result['id'])
        result['outgoing_relationships'] = relationships['outgoing']
        result['incoming_relationships'] = relationships['incoming']

        return result
    
    def get_decision_record(self, record_id: str, include_relationships: bool = True) -> Optional[Dict]:
        """Get a decision record by ID."""
        record = self.db.get_decision_record(record_id)
        if record and include_relationships:
            relationships = self.db.get_relationships_by_record(record_id)
            record['outgoing_relationships'] = relationships['outgoing']
            record['incoming_relationships'] = relationships['incoming']
        return record
    
    def get_decision_records_by_decision(self, decision_id: str) -> List[Dict]:
        """Get all decision records for a decision."""
        records = self.db.get_decision_records_by_decision(decision_id)
        # Add relationships to each record
        for record in records:
            relationships = self.db.get_relationships_by_record(record['id'])
            record['outgoing_relationships'] = relationships['outgoing']
            record['incoming_relationships'] = relationships['incoming']
        return records
    
    def update_decision_record(self, record_id: str, context: str = None,
                              constraints: str = None, decision_description: str = None,
                              rationale: str = None, assumptions: str = None,
                              consequences: str = None, tradeoffs: str = None,
                              evidence: str = None, options_considered: str = None) -> Dict:
        """
        Update a decision record with automatic versioning.

        - Version auto-increments on every update (cannot be set manually)
        - A snapshot of the previous state is saved
        - A changelog entry is created documenting the changes
        """
        # Get current record state before update
        current_record = self.db.get_decision_record(record_id)
        if not current_record:
            raise ValueError(f"Record {record_id} not found")

        # Build update data
        record_data = {}
        updatable_fields = [
            'context', 'constraints', 'decision_description', 'rationale',
            'assumptions', 'consequences', 'tradeoffs', 'evidence', 'options_considered'
        ]

        local_vars = {
            'context': context, 'constraints': constraints,
            'decision_description': decision_description, 'rationale': rationale,
            'assumptions': assumptions, 'consequences': consequences,
            'tradeoffs': tradeoffs, 'evidence': evidence,
            'options_considered': options_considered
        }

        for field in updatable_fields:
            if local_vars[field] is not None:
                record_data[field] = local_vars[field]

        # If no actual changes, return current record
        if not record_data:
            relationships = self.db.get_relationships_by_record(record_id)
            current_record['outgoing_relationships'] = relationships['outgoing']
            current_record['incoming_relationships'] = relationships['incoming']
            return current_record

        # Calculate changes (diff)
        changes = {}
        for field, new_value in record_data.items():
            old_value = current_record.get(field)
            if old_value != new_value:
                changes[field] = {'old': old_value, 'new': new_value}

        # If no actual changes, return current record
        if not changes:
            relationships = self.db.get_relationships_by_record(record_id)
            current_record['outgoing_relationships'] = relationships['outgoing']
            current_record['incoming_relationships'] = relationships['incoming']
            return current_record

        # Get current version and calculate new version
        current_version = current_record.get('version', 1)
        new_version = current_version + 1

        # Create snapshot of current state before update (only if it doesn't already exist)
        # This ensures we have a snapshot of the state before it changes
        existing_version = self.db.get_record_version_by_number(record_id, current_version)
        if not existing_version:
            snapshot_data = {
                field: current_record.get(field)
                for field in updatable_fields + ['status', 'version', 'decision_id']
            }
            snapshot_data['id'] = current_record['id']
            snapshot_data['created_at'] = str(current_record.get('created_at', ''))
            snapshot_data['updated_at'] = str(current_record.get('updated_at', ''))

            self.db.create_record_version({
                'id': str(uuid.uuid4()),
                'decision_record_id': record_id,
                'version': current_version,
                'snapshot': snapshot_data
            })

        # Update record with new version
        record_data['version'] = new_version
        result = self.db.update_decision_record(record_id, record_data)

        # Create changelog entry
        change_summary = ', '.join(changes.keys())
        self.db.create_changelog_entry({
            'id': str(uuid.uuid4()),
            'decision_record_id': record_id,
            'from_version': current_version,
            'to_version': new_version,
            'changes': changes,
            'summary': f"Updated: {change_summary}"
        })

        # Add relationships
        relationships = self.db.get_relationships_by_record(record_id)
        result['outgoing_relationships'] = relationships['outgoing']
        result['incoming_relationships'] = relationships['incoming']

        return result
    
    def delete_decision_record(self, record_id: str) -> bool:
        """Delete a decision record."""
        return self.db.delete_decision_record(record_id)
    
    # ==================== Decision Records (by description) ====================
    
    def get_decision_record_by_description(self, project_name: str, decision_title: str, 
                                          decision_description: str) -> Optional[Dict]:
        """Get a decision record by project name, decision title, and description."""
        decision = self.get_decision_by_title(project_name, decision_title)
        if not decision:
            return None
        
        record = self.db.get_decision_record_by_description(decision['id'], decision_description)
        if record:
            relationships = self.db.get_relationships_by_record(record['id'])
            record['outgoing_relationships'] = relationships['outgoing']
            record['incoming_relationships'] = relationships['incoming']
        return record
    
    def create_decision_record_by_names(self, project_name: str, decision_title: str,
                                      decision_description: str,
                                      context: str = None, constraints: str = None,
                                      status: str = None, rationale: str = None,
                                      assumptions: str = None, consequences: str = None,
                                      tradeoffs: str = None, evidence: str = None,
                                      options_considered: str = None) -> Dict:
        """Create a decision record by project name and decision title."""
        decision = self.get_decision_by_title(project_name, decision_title)
        if not decision:
            raise ValueError(f"Decision '{decision_title}' not found in project '{project_name}'")
        
        return self.create_decision_record(
            decision_id=decision['id'],
            decision_description=decision_description,
            context=context,
            constraints=constraints,
            status=status,
            rationale=rationale,
            assumptions=assumptions,
            consequences=consequences,
            tradeoffs=tradeoffs,
            evidence=evidence,
            options_considered=options_considered
        )
    
    def update_decision_record_by_description(self, project_name: str, decision_title: str,
                                            decision_description: str,
                                            context: str = None, constraints: str = None,
                                            rationale: str = None, assumptions: str = None,
                                            consequences: str = None, tradeoffs: str = None,
                                            evidence: str = None, options_considered: str = None) -> Dict:
        """Update a decision record by project name, decision title, and description."""
        record = self.get_decision_record_by_description(project_name, decision_title, decision_description)
        if not record:
            raise ValueError(f"Decision record not found")
        
        return self.update_decision_record(
            record_id=record['id'],
            context=context,
            constraints=constraints,
            rationale=rationale,
            assumptions=assumptions,
            consequences=consequences,
            tradeoffs=tradeoffs,
            evidence=evidence,
            options_considered=options_considered
        )
    
    def change_record_status_by_description(self, project_name: str, decision_title: str,
                                          decision_description: str, new_status: str,
                                          reason: str = None, auto_handle_conflicts: bool = True) -> Dict:
        """Change the status of a decision record by project name, decision title, and description."""
        record = self.get_decision_record_by_description(project_name, decision_title, decision_description)
        if not record:
            raise ValueError(f"Decision record not found")
        
        return self.change_record_status(
            record_id=record['id'],
            new_status=new_status,
            reason=reason,
            auto_handle_conflicts=auto_handle_conflicts
        )
    
    def change_record_status(self, record_id: str, new_status: str, reason: str = None,
                            auto_handle_conflicts: bool = True) -> Dict:
        """Change the status of a decision record."""
        # Get current record
        record = self.db.get_decision_record(record_id)
        if not record:
            raise ValueError(f"Record {record_id} not found")
        
        old_status = record['status']
        
        # Validate status
        if new_status not in [s.value for s in DecisionRecordStatus]:
            raise ValueError(f"Invalid status: {new_status}")
        
        # Validate transition
        if not self._is_valid_transition(old_status, new_status):
            raise ValueError(f"Invalid status transition from '{old_status}' to '{new_status}'")
        
        affected_records = []
        decision_id = record['decision_id']
        
        # Handle conflicts when accepting
        if new_status == DecisionRecordStatus.ACCEPTED.value:
            current_accepted = self.db.get_current_accepted_record(decision_id)
            if current_accepted and current_accepted['id'] != record_id:
                if auto_handle_conflicts:
                    self.db.update_decision_record_status(
                        current_accepted['id'],
                        DecisionRecordStatus.REJECTED.value
                    )
                    self.db.create_status_history({
                        'id': str(uuid.uuid4()),
                        'decision_record_id': current_accepted['id'],
                        'from_status': current_accepted['status'],
                        'to_status': DecisionRecordStatus.REJECTED.value,
                        'reason': 'Automatically rejected: Another record was accepted',
                        'metadata': {
                            'triggering_decision_record_id': record_id,
                            'change_type': 'automatic'
                        }
                    })
                    # Create superseded_by relationship
                    self.db.create_relationship({
                        'id': str(uuid.uuid4()),
                        'source_record_id': current_accepted['id'],
                        'target_record_id': record_id,
                        'relationship_type': 'superseded_by',
                        'description': f'Automatically superseded when record {record_id} was accepted'
                    })
                    affected_records.append(current_accepted['id'])
                else:
                    raise ValueError(
                        'Another record is already accepted. Set auto_handle_conflicts=True to auto-reject it.'
                    )
        
        # Handle conflicts when implementing
        if new_status == DecisionRecordStatus.IMPLEMENTED.value:
            current_implemented = self.db.get_current_implemented_record(decision_id)
            if current_implemented and current_implemented['id'] != record_id:
                if auto_handle_conflicts:
                    self.db.update_decision_record_status(
                        current_implemented['id'],
                        DecisionRecordStatus.DEPRECATED.value
                    )
                    self.db.create_status_history({
                        'id': str(uuid.uuid4()),
                        'decision_record_id': current_implemented['id'],
                        'from_status': current_implemented['status'],
                        'to_status': DecisionRecordStatus.DEPRECATED.value,
                        'reason': 'Automatically deprecated: Another record was implemented',
                        'metadata': {
                            'triggering_decision_record_id': record_id,
                            'change_type': 'automatic'
                        }
                    })
                    # Create superseded_by relationship
                    self.db.create_relationship({
                        'id': str(uuid.uuid4()),
                        'source_record_id': current_implemented['id'],
                        'target_record_id': record_id,
                        'relationship_type': 'superseded_by',
                        'description': f'Automatically superseded when record {record_id} was implemented'
                    })
                    affected_records.append(current_implemented['id'])
                else:
                    raise ValueError(
                        'Another record is already implemented. Set auto_handle_conflicts=True to auto-deprecate it.'
                    )
            
            # Also deprecate the accepted record if different
            current_accepted = self.db.get_current_accepted_record(decision_id)
            if current_accepted and current_accepted['id'] != record_id:
                if auto_handle_conflicts:
                    self.db.update_decision_record_status(
                        current_accepted['id'],
                        DecisionRecordStatus.DEPRECATED.value
                    )
                    self.db.create_status_history({
                        'id': str(uuid.uuid4()),
                        'decision_record_id': current_accepted['id'],
                        'from_status': current_accepted['status'],
                        'to_status': DecisionRecordStatus.DEPRECATED.value,
                        'reason': 'Automatically deprecated: Another record was implemented',
                        'metadata': {
                            'triggering_decision_record_id': record_id,
                            'change_type': 'automatic'
                        }
                    })
                    # Create superseded_by relationship
                    self.db.create_relationship({
                        'id': str(uuid.uuid4()),
                        'source_record_id': current_accepted['id'],
                        'target_record_id': record_id,
                        'relationship_type': 'superseded_by',
                        'description': f'Automatically superseded when record {record_id} was implemented'
                    })
                    affected_records.append(current_accepted['id'])
        
        # Update the record's status
        self.db.update_decision_record_status(record_id, new_status)
        
        # Create history entry
        self.db.create_status_history({
            'id': str(uuid.uuid4()),
            'decision_record_id': record_id,
            'from_status': old_status,
            'to_status': new_status,
            'reason': reason
        })
        
        # Get updated record with relationships
        updated_record = self.get_decision_record(record_id)
        
        return {
            'success': True,
            'message': f"Status changed from '{old_status}' to '{new_status}'",
            'record': updated_record,
            'affected_records': affected_records
        }
    
    def get_status_history(self, record_id: str) -> List[Dict]:
        """Get the status history of a decision record."""
        return self.db.get_status_history_by_record(record_id)
    
    def _is_valid_transition(self, from_status: str, to_status: str) -> bool:
        """Check if a status transition is valid."""
        valid_targets = VALID_TRANSITIONS.get(from_status, [])
        return to_status in valid_targets
    
    # ==================== Relationships ====================
    
    def create_relationship(self, source_record_id: str, target_record_id: str,
                           relationship_type: str, description: str = None) -> Dict:
        """Create a relationship between decision records."""
        # Verify both records exist
        source_record = self.db.get_decision_record(source_record_id)
        if not source_record:
            raise ValueError(f"Source record {source_record_id} not found")
        
        target_record = self.db.get_decision_record(target_record_id)
        if not target_record:
            raise ValueError(f"Target record {target_record_id} not found")
        
        relationship = DecisionRecordRelationship(
            source_record_id=source_record_id,
            target_record_id=target_record_id,
            relationship_type=relationship_type,
            description=description
        )
        relationship_data = relationship.to_dict()
        return self.db.create_relationship(relationship_data)
    
    def get_relationships(self, record_id: str) -> Dict:
        """Get all relationships for a record."""
        return self.db.get_relationships_by_record(record_id)
    
    def update_relationship(self, relationship_id: str, relationship_type: str = None,
                           description: str = None) -> Optional[Dict]:
        """Update a relationship's type or description."""
        rel = self.db.get_relationship(relationship_id)
        if not rel:
            raise ValueError(f"Relationship {relationship_id} not found")
        return self.db.update_relationship(relationship_id, relationship_type, description)
    
    def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a relationship."""
        return self.db.delete_relationship(relationship_id)
    
    # ==================== Decision-Level Relationships ====================
    
    def create_decision_relationship(self, source_decision_id: str, target_decision_id: str,
                                    relationship_type: str, description: str = None) -> Dict:
        """Create a relationship between decisions."""
        source_decision = self.db.get_decision(source_decision_id)
        if not source_decision:
            raise ValueError(f"Source decision {source_decision_id} not found")
        
        target_decision = self.db.get_decision(target_decision_id)
        if not target_decision:
            raise ValueError(f"Target decision {target_decision_id} not found")
        
        if source_decision_id == target_decision_id:
            raise ValueError("Source and target decision cannot be the same")
        
        relationship = DecisionRelationship(
            source_decision_id=source_decision_id,
            target_decision_id=target_decision_id,
            relationship_type=relationship_type,
            description=description
        )
        relationship_data = relationship.to_dict()
        return self.db.create_decision_relationship(relationship_data)
    
    def get_decision_relationships(self, decision_id: str) -> Dict:
        """Get all decision-level relationships for a decision."""
        return self.db.get_decision_relationships_by_decision(decision_id)
    
    def update_decision_relationship(self, relationship_id: str, relationship_type: str = None,
                                     description: str = None) -> Optional[Dict]:
        """Update a decision relationship's type or description."""
        rel = self.db.get_decision_relationship(relationship_id)
        if not rel:
            raise ValueError(f"Decision relationship {relationship_id} not found")
        return self.db.update_decision_relationship(relationship_id, relationship_type, description)
    
    def delete_decision_relationship(self, relationship_id: str) -> bool:
        """Delete a decision relationship."""
        return self.db.delete_decision_relationship(relationship_id)

    # ==================== Version Control ====================

    def get_record_versions(self, record_id: str) -> List[Dict]:
        """Get all versions of a decision record."""
        return self.db.get_all_record_versions(record_id)

    def get_record_at_version(self, record_id: str, version: int) -> Optional[Dict]:
        """Get a decision record as it was at a specific version."""
        version_record = self.db.get_record_version_by_number(record_id, version)
        if version_record:
            return version_record.get('snapshot')
        return None

    def get_record_changelog(self, record_id: str) -> List[Dict]:
        """Get the changelog for a decision record."""
        return self.db.get_record_changelog(record_id)

    def get_version_diff(self, record_id: str, from_version, to_version) -> Dict:
        """
        Get the diff between two versions of a decision record.

        Args:
            record_id: The decision record ID
            from_version: The starting version number (int) or "current" for the current live version
            to_version: The ending version number (int) or "current" for the current live version

        Returns a dict with changed fields and their old/new values.
        """
        # Handle "current" version - get the live record from database
        if from_version == "current":
            from_snapshot = self.db.get_decision_record(record_id)
            if not from_snapshot:
                raise ValueError(f"Record {record_id} not found")
            from_version_label = "current"
            from_version_number = from_snapshot.get('version', 1)
        else:
            from_snapshot = self.get_record_at_version(record_id, from_version)
            if not from_snapshot:
                raise ValueError(f"Version {from_version} not found for record {record_id}")
            from_version_label = from_version
            from_version_number = from_version

        if to_version == "current":
            to_snapshot = self.db.get_decision_record(record_id)
            if not to_snapshot:
                raise ValueError(f"Record {record_id} not found")
            to_version_label = "current"
            to_version_number = to_snapshot.get('version', 1)
        else:
            to_snapshot = self.get_record_at_version(record_id, to_version)
            if not to_snapshot:
                raise ValueError(f"Version {to_version} not found for record {record_id}")
            to_version_label = to_version
            to_version_number = to_version

        # Calculate diff
        diff = {
            'from_version': from_version_label,
            'from_version_number': from_version_number,
            'to_version': to_version_label,
            'to_version_number': to_version_number,
            'changes': {}
        }

        comparable_fields = [
            'context', 'constraints', 'decision_description', 'rationale',
            'assumptions', 'consequences', 'tradeoffs', 'evidence', 'options_considered'
        ]

        for field in comparable_fields:
            old_value = from_snapshot.get(field)
            new_value = to_snapshot.get(field)
            if old_value != new_value:
                diff['changes'][field] = {
                    'old': old_value,
                    'new': new_value
                }

        return diff

    def revert_to_version(self, record_id: str, version: int, reason: str = None) -> Dict:
        """
        Revert a decision record to a previous version.

        This creates a new version with the content from the specified version.
        """
        # Get the snapshot at the target version
        target_snapshot = self.get_record_at_version(record_id, version)
        if not target_snapshot:
            raise ValueError(f"Version {version} not found for record {record_id}")

        # Get current record
        current_record = self.db.get_decision_record(record_id)
        if not current_record:
            raise ValueError(f"Record {record_id} not found")

        current_version = current_record.get('version', 1)
        new_version = current_version + 1

        # Create snapshot of current state before revert (only if it doesn't already exist)
        updatable_fields = [
            'context', 'constraints', 'decision_description', 'rationale',
            'assumptions', 'consequences', 'tradeoffs', 'evidence', 'options_considered'
        ]

        existing_version = self.db.get_record_version_by_number(record_id, current_version)
        if not existing_version:
            snapshot_data = {
                field: current_record.get(field)
                for field in updatable_fields + ['status', 'version', 'decision_id']
            }
            snapshot_data['id'] = current_record['id']
            snapshot_data['created_at'] = str(current_record.get('created_at', ''))
            snapshot_data['updated_at'] = str(current_record.get('updated_at', ''))

            self.db.create_record_version({
                'id': str(uuid.uuid4()),
                'decision_record_id': record_id,
                'version': current_version,
                'snapshot': snapshot_data
            })

        # Build update data from target snapshot
        record_data = {}
        for field in updatable_fields:
            record_data[field] = target_snapshot.get(field)
        record_data['version'] = new_version

        # Calculate changes for changelog
        changes = {}
        for field in updatable_fields:
            old_value = current_record.get(field)
            new_value = target_snapshot.get(field)
            if old_value != new_value:
                changes[field] = {'old': old_value, 'new': new_value}

        # Update record
        result = self.db.update_decision_record(record_id, record_data)

        # Create changelog entry for revert
        summary = reason or f"Reverted to version {version}"
        self.db.create_changelog_entry({
            'id': str(uuid.uuid4()),
            'decision_record_id': record_id,
            'from_version': current_version,
            'to_version': new_version,
            'changes': changes,
            'summary': summary
        })

        # Add relationships
        relationships = self.db.get_relationships_by_record(record_id)
        result['outgoing_relationships'] = relationships['outgoing']
        result['incoming_relationships'] = relationships['incoming']

        return result

    # ==================== Decision Timeline & History ====================

    def get_decision_timeline(self, decision_id: str) -> List[Dict]:
        """
        Get a comprehensive timeline of all events for a decision.
        Events include: record creation, status changes, and content changes.
        Events are sorted by timestamp (most recent first) and grouped by date.
        """
        # Verify decision exists
        decision = self.db.get_decision(decision_id)
        if not decision:
            raise ValueError(f"Decision {decision_id} not found")
        
        events = self.db.get_decision_timeline_events(decision_id)
        
        # Group events by date for UI convenience
        from collections import defaultdict
        from datetime import datetime
        
        grouped_by_date = defaultdict(list)
        for event in events:
            if event['timestamp']:
                if isinstance(event['timestamp'], str):
                    date_key = event['timestamp'][:10]
                else:
                    date_key = event['timestamp'].strftime('%Y-%m-%d')
                grouped_by_date[date_key].append(event)
        
        # Also group events that happen at the exact same timestamp
        for date_key, date_events in grouped_by_date.items():
            timestamp_groups = defaultdict(list)
            for event in date_events:
                ts = event['timestamp']
                if isinstance(ts, datetime):
                    ts_key = ts.isoformat()
                else:
                    ts_key = str(ts)
                timestamp_groups[ts_key].append(event)
            
            # Mark events that share the same timestamp
            for ts_key, ts_events in timestamp_groups.items():
                if len(ts_events) > 1:
                    for ev in ts_events:
                        ev['has_concurrent_events'] = True
                        ev['concurrent_count'] = len(ts_events)
        
        return {
            'decision_id': decision_id,
            'decision_title': decision['title'],
            'total_events': len(events),
            'events': events,
            'grouped_by_date': dict(grouped_by_date)
        }

    def get_implementation_history(self, decision_id: str) -> Dict:
        """
        Get the implementation history for a decision.
        Shows the current implemented decision and all past implemented decisions
        that have been deprecated, in chronological order.
        """
        # Verify decision exists
        decision = self.db.get_decision(decision_id)
        if not decision:
            raise ValueError(f"Decision {decision_id} not found")
        
        history = self.db.get_implementation_history(decision_id)
        
        # Add relationships to current implementation
        if history['current_implementation']:
            record_id = history['current_implementation']['id']
            relationships = self.db.get_relationships_by_record(record_id)
            history['current_implementation']['outgoing_relationships'] = relationships['outgoing']
            history['current_implementation']['incoming_relationships'] = relationships['incoming']
        
        # Add relationships to past implementations
        for impl in history['past_implementations']:
            record_id = impl['id']
            relationships = self.db.get_relationships_by_record(record_id)
            impl['outgoing_relationships'] = relationships['outgoing']
            impl['incoming_relationships'] = relationships['incoming']
        
        return {
            'decision_id': decision_id,
            'decision_title': decision['title'],
            'current_implementation': history['current_implementation'],
            'past_implementations': history['past_implementations'],
            'total_implementations': 1 + len(history['past_implementations']) if history['current_implementation'] else len(history['past_implementations'])
        }
