"""
Data models for Curio Decision Record application.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum


class DecisionRecordStatus(str, Enum):
    PROPOSED = 'proposed'
    ACCEPTED = 'accepted'
    IMPLEMENTED = 'implemented'
    IMPLEMENTED_INFERRED = 'implemented_inferred'
    REJECTED = 'rejected'
    DEPRECATED = 'deprecated'


class Project:
    """Project model."""
    
    def __init__(self, id=None, name=None, description=None, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            description=data.get('description'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )


class Decision:
    """Decision model."""
    
    def __init__(self, id=None, project_id=None, title=None, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.project_id = project_id
        self.title = title
        self.created_at = created_at
        self.updated_at = updated_at
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'title': self.title,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary."""
        return cls(
            id=data.get('id'),
            project_id=data.get('project_id'),
            title=data.get('title'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )


class DecisionRecord:
    """Decision record model."""
    
    def __init__(self, id=None, decision_id=None, context=None, constraints=None,
                 decision_description=None, status=None, rationale=None,
                 assumptions=None, consequences=None, tradeoffs=None,
                 evidence=None, options_considered=None, version=1,
                 created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.decision_id = decision_id
        self.context = context
        self.constraints = constraints
        self.decision_description = decision_description
        self.status = status or DecisionRecordStatus.PROPOSED.value
        self.rationale = rationale
        self.assumptions = assumptions
        self.consequences = consequences
        self.tradeoffs = tradeoffs
        self.evidence = evidence
        self.options_considered = options_considered
        self.version = version
        self.created_at = created_at
        self.updated_at = updated_at
    
    def to_dict(self, include_relationships=False):
        """Convert to dictionary."""
        result = {
            'id': self.id,
            'decision_id': self.decision_id,
            'context': self.context,
            'constraints': self.constraints,
            'decision_description': self.decision_description,
            'status': self.status,
            'rationale': self.rationale,
            'assumptions': self.assumptions,
            'consequences': self.consequences,
            'tradeoffs': self.tradeoffs,
            'evidence': self.evidence,
            'options_considered': self.options_considered,
            'version': self.version,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
        if include_relationships:
            result['outgoing_relationships'] = getattr(self, 'outgoing_relationships', [])
            result['incoming_relationships'] = getattr(self, 'incoming_relationships', [])
        return result
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary."""
        return cls(
            id=data.get('id'),
            decision_id=data.get('decision_id'),
            context=data.get('context'),
            constraints=data.get('constraints'),
            decision_description=data.get('decision_description'),
            status=data.get('status'),
            rationale=data.get('rationale'),
            assumptions=data.get('assumptions'),
            consequences=data.get('consequences'),
            tradeoffs=data.get('tradeoffs'),
            evidence=data.get('evidence'),
            options_considered=data.get('options_considered'),
            version=data.get('version', 1),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )


class StatusHistory:
    """Status history model."""
    
    def __init__(self, id=None, decision_record_id=None, from_status=None,
                 to_status=None, reason=None, metadata=None, changed_at=None):
        self.id = id or str(uuid.uuid4())
        self.decision_record_id = decision_record_id
        self.from_status = from_status
        self.to_status = to_status
        self.reason = reason
        self.metadata = metadata
        self.changed_at = changed_at
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'decision_record_id': self.decision_record_id,
            'from_status': self.from_status,
            'to_status': self.to_status,
            'reason': self.reason,
            'metadata': self.metadata,
            'changed_at': self.changed_at.isoformat() if isinstance(self.changed_at, datetime) else self.changed_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary."""
        return cls(
            id=data.get('id'),
            decision_record_id=data.get('decision_record_id'),
            from_status=data.get('from_status'),
            to_status=data.get('to_status'),
            reason=data.get('reason'),
            metadata=data.get('metadata'),
            changed_at=data.get('changed_at')
        )


class DecisionRecordRelationship:
    """Decision record relationship model."""
    
    def __init__(self, id=None, source_record_id=None, target_record_id=None,
                 relationship_type=None, description=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.source_record_id = source_record_id
        self.target_record_id = target_record_id
        self.relationship_type = relationship_type
        self.description = description
        self.created_at = created_at
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'source_record_id': self.source_record_id,
            'target_record_id': self.target_record_id,
            'relationship_type': self.relationship_type,
            'description': self.description,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary."""
        return cls(
            id=data.get('id'),
            source_record_id=data.get('source_record_id'),
            target_record_id=data.get('target_record_id'),
            relationship_type=data.get('relationship_type'),
            description=data.get('description'),
            created_at=data.get('created_at')
        )


class DecisionRelationship:
    """Decision-level relationship model."""
    
    def __init__(self, id=None, source_decision_id=None, target_decision_id=None,
                 relationship_type=None, description=None, created_at=None):
        self.id = id or str(uuid.uuid4())
        self.source_decision_id = source_decision_id
        self.target_decision_id = target_decision_id
        self.relationship_type = relationship_type
        self.description = description
        self.created_at = created_at
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'source_decision_id': self.source_decision_id,
            'target_decision_id': self.target_decision_id,
            'relationship_type': self.relationship_type,
            'description': self.description,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary."""
        return cls(
            id=data.get('id'),
            source_decision_id=data.get('source_decision_id'),
            target_decision_id=data.get('target_decision_id'),
            relationship_type=data.get('relationship_type'),
            description=data.get('description'),
            created_at=data.get('created_at')
        )
