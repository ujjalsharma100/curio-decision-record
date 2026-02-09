"""
API Client for Curio Decision Record Service.

This client handles all HTTP communication with the backend service.
"""

import requests
import logging
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)


class CurioDecisionAPIClient:
    """Client for interacting with Curio Decision Record API."""
    
    def __init__(self, base_url: str):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL of the Curio Decision Record service (e.g., "http://localhost:5000")
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            endpoint: API endpoint (e.g., "/api/projects")
            **kwargs: Additional arguments for requests
            
        Returns:
            Response data as dictionary
            
        Raises:
            requests.RequestException: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            # Handle empty responses (204 No Content)
            if response.status_code == 204:
                return {}
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {method} {url} - {e}")
            if hasattr(e.response, 'json'):
                error_data = e.response.json()
                raise Exception(error_data.get('error', str(e)))
            raise Exception(str(e))
    
    # ==================== Projects ====================
    
    def list_projects(self) -> List[Dict]:
        """List all projects."""
        return self._request('GET', '/api/projects')
    
    def create_project(self, name: str, description: Optional[str] = None) -> Dict:
        """Create a new project."""
        return self._request('POST', '/api/projects', json={
            'name': name,
            'description': description
        })
    
    def get_project(self, project_id: str) -> Dict:
        """Get a project by ID."""
        return self._request('GET', f'/api/projects/{project_id}')
    
    def update_project(self, project_id: str, name: Optional[str] = None, 
                      description: Optional[str] = None) -> Dict:
        """Update a project."""
        data = {}
        if name is not None:
            data['name'] = name
        if description is not None:
            data['description'] = description
        return self._request('PUT', f'/api/projects/{project_id}', json=data)
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        self._request('DELETE', f'/api/projects/{project_id}')
        return True
    
    # ==================== Decisions ====================
    
    def list_decisions(self, project_id: str, status: Optional[str] = None) -> List[Dict]:
        """List all decisions for a project."""
        params = {}
        if status:
            params['status'] = status
        return self._request('GET', f'/api/projects/{project_id}/decisions', params=params)
    
    def get_accepted_decisions(self, project_id: str) -> List[Dict]:
        """Get all accepted decisions for a project."""
        return self._request('GET', f'/api/projects/{project_id}/decisions/accepted')
    
    def create_decision(self, project_id: str, title: str) -> Dict:
        """Create a new decision."""
        return self._request('POST', f'/api/projects/{project_id}/decisions', json={
            'title': title
        })
    
    def get_decision(self, decision_id: str, include_records: bool = True) -> Dict:
        """Get a decision by ID."""
        return self._request('GET', f'/api/decisions/{decision_id}')
    
    def update_decision(self, decision_id: str, title: Optional[str] = None) -> Dict:
        """Update a decision."""
        data = {}
        if title is not None:
            data['title'] = title
        return self._request('PUT', f'/api/decisions/{decision_id}', json=data)
    
    def delete_decision(self, decision_id: str) -> bool:
        """Delete a decision."""
        self._request('DELETE', f'/api/decisions/{decision_id}')
        return True
    
    def get_implementation_history(self, decision_id: str) -> Dict:
        """Get implementation history for a decision."""
        return self._request('GET', f'/api/decisions/{decision_id}/implementation-history')
    
    # ==================== Decision Records ====================
    
    def list_records(self, decision_id: str) -> List[Dict]:
        """List all records for a decision."""
        return self._request('GET', f'/api/decisions/{decision_id}/records')
    
    def create_record(self, decision_id: str, decision_description: str,
                     context: Optional[str] = None,
                     constraints: Optional[str] = None,
                     decision_details: Optional[str] = None,
                     status: Optional[str] = None,
                     rationale: Optional[str] = None,
                     assumptions: Optional[str] = None,
                     consequences: Optional[str] = None,
                     tradeoffs: Optional[str] = None,
                     evidence: Optional[str] = None,
                     options_considered: Optional[str] = None,
                     code_reference: Optional[str] = None) -> Dict:
        """Create a new decision record."""
        data = {
            'decision_description': decision_description,
            'context': context,
            'constraints': constraints,
            'decision_details': decision_details,
            'status': status,
            'rationale': rationale,
            'assumptions': assumptions,
            'consequences': consequences,
            'tradeoffs': tradeoffs,
            'evidence': evidence,
            'options_considered': options_considered,
            'code_reference': code_reference
        }
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        return self._request('POST', f'/api/decisions/{decision_id}/records', json=data)
    
    def get_record(self, record_id: str) -> Dict:
        """Get a decision record by ID."""
        return self._request('GET', f'/api/records/{record_id}')
    
    def update_record(self, record_id: str,
                     context: Optional[str] = None,
                     constraints: Optional[str] = None,
                     decision_description: Optional[str] = None,
                     decision_details: Optional[str] = None,
                     rationale: Optional[str] = None,
                     assumptions: Optional[str] = None,
                     consequences: Optional[str] = None,
                     tradeoffs: Optional[str] = None,
                     evidence: Optional[str] = None,
                     options_considered: Optional[str] = None,
                     code_reference: Optional[str] = None) -> Dict:
        """Update a decision record."""
        data = {
            'context': context,
            'constraints': constraints,
            'decision_description': decision_description,
            'decision_details': decision_details,
            'rationale': rationale,
            'assumptions': assumptions,
            'consequences': consequences,
            'tradeoffs': tradeoffs,
            'evidence': evidence,
            'options_considered': options_considered,
            'code_reference': code_reference
        }
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        return self._request('PUT', f'/api/records/{record_id}', json=data)
    
    def delete_record(self, record_id: str) -> bool:
        """Delete a decision record."""
        self._request('DELETE', f'/api/records/{record_id}')
        return True
    
    def change_record_status(self, record_id: str, status: str, 
                           reason: Optional[str] = None,
                           auto_handle_conflicts: bool = True) -> Dict:
        """Change the status of a decision record."""
        return self._request('PATCH', f'/api/records/{record_id}/status', json={
            'status': status,
            'reason': reason,
            'auto_handle_conflicts': auto_handle_conflicts
        })
    
    def get_status_history(self, record_id: str) -> List[Dict]:
        """Get status history for a decision record."""
        return self._request('GET', f'/api/records/{record_id}/history')
    
    # ==================== Relationships ====================
    
    def list_relationships(self, record_id: str) -> Dict:
        """List all relationships (outgoing and incoming) for a record."""
        return self._request('GET', f'/api/records/{record_id}/relationships')
    
    def create_relationship(self, source_record_id: str, target_record_id: str,
                            relationship_type: str, description: Optional[str] = None) -> Dict:
        """Create a relationship between two decision records. Records can be from different decisions within the same project."""
        return self._request('POST', f'/api/records/{source_record_id}/relationships', json={
            'target_record_id': target_record_id,
            'relationship_type': relationship_type,
            'description': description
        })
    
    def update_relationship(self, relationship_id: str, relationship_type: Optional[str] = None,
                           description: Optional[str] = None) -> Dict:
        """Update a relationship's type or description."""
        data = {}
        if relationship_type is not None:
            data['relationship_type'] = relationship_type
        if description is not None:
            data['description'] = description
        return self._request('PATCH', f'/api/relationships/{relationship_id}', json=data)
    
    def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a relationship by ID."""
        self._request('DELETE', f'/api/relationships/{relationship_id}')
        return True
    
    # ==================== Decision-Level Relationships ====================
    
    def list_decision_relationships(self, decision_id: str) -> Dict:
        """List all decision-level relationships for a decision."""
        return self._request('GET', f'/api/decisions/{decision_id}/decision-relationships')
    
    def create_decision_relationship(self, source_decision_id: str, target_decision_id: str,
                                    relationship_type: str, description: Optional[str] = None) -> Dict:
        """Create a relationship between two decisions."""
        return self._request('POST', f'/api/decisions/{source_decision_id}/decision-relationships', json={
            'target_decision_id': target_decision_id,
            'relationship_type': relationship_type,
            'description': description
        })
    
    def update_decision_relationship(self, relationship_id: str, relationship_type: Optional[str] = None,
                                    description: Optional[str] = None) -> Dict:
        """Update a decision relationship's type or description."""
        data = {}
        if relationship_type is not None:
            data['relationship_type'] = relationship_type
        if description is not None:
            data['description'] = description
        return self._request('PATCH', f'/api/decision-relationships/{relationship_id}', json=data)
    
    def delete_decision_relationship(self, relationship_id: str) -> bool:
        """Delete a decision relationship by ID."""
        self._request('DELETE', f'/api/decision-relationships/{relationship_id}')
        return True
    
    # ==================== Health Check ====================
    
    def health_check(self) -> Dict:
        """Check service health."""
        return self._request('GET', '/health')
    
    # ==================== MCP Endpoints (by name/title) ====================
    # These methods use natural identifiers instead of UUIDs
    
    def get_project_by_name(self, project_name: str) -> Dict:
        """Get a project by name (MCP endpoint)."""
        return self._request('GET', f'/api/mcp/projects/{project_name}')
    
    def list_decisions_by_project_name(self, project_name: str, status: Optional[str] = None) -> List[Dict]:
        """List all decisions for a project by name (MCP endpoint)."""
        params = {}
        if status:
            params['status'] = status
        return self._request('GET', f'/api/mcp/projects/{project_name}/decisions', params=params)
    
    def create_decision_by_project_name(self, project_name: str, title: str) -> Dict:
        """Create a new decision by project name (MCP endpoint)."""
        return self._request('POST', f'/api/mcp/projects/{project_name}/decisions', json={
            'title': title
        })
    
    def get_decision_by_title(self, project_name: str, decision_title: str) -> Dict:
        """Get a decision by project name and title (MCP endpoint)."""
        return self._request('GET', f'/api/mcp/projects/{project_name}/decisions/{decision_title}')
    
    def create_record_by_names(self, project_name: str, decision_title: str,
                              decision_description: str,
                              context: Optional[str] = None,
                              constraints: Optional[str] = None,
                              decision_details: Optional[str] = None,
                              code_reference: Optional[str] = None,
                              status: Optional[str] = None,
                              rationale: Optional[str] = None,
                              assumptions: Optional[str] = None,
                              consequences: Optional[str] = None,
                              tradeoffs: Optional[str] = None,
                              evidence: Optional[str] = None,
                              options_considered: Optional[str] = None,
                              metadata: Optional[Dict] = None) -> Dict:
        """Create a decision record by project name and decision title (MCP endpoint)."""
        data = {
            'decision_description': decision_description,
            'context': context,
            'constraints': constraints,
            'decision_details': decision_details,
            'code_reference': code_reference,
            'status': status,
            'rationale': rationale,
            'assumptions': assumptions,
            'consequences': consequences,
            'tradeoffs': tradeoffs,
            'evidence': evidence,
            'options_considered': options_considered,
            'metadata': metadata
        }
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        return self._request('POST', f'/api/mcp/projects/{project_name}/decisions/{decision_title}/records', json=data)
    
    def get_record_by_description(self, project_name: str, decision_title: str, 
                                  decision_description: str) -> Dict:
        """Get a decision record by project name, decision title, and description (MCP endpoint)."""
        # URL encode the description for path parameter
        from urllib.parse import quote
        encoded_description = quote(decision_description, safe='')
        return self._request('GET', f'/api/mcp/projects/{project_name}/decisions/{decision_title}/records/{encoded_description}')
    
    def update_record_by_description(self, project_name: str, decision_title: str,
                                     decision_description: str,
                                     context: Optional[str] = None,
                                     constraints: Optional[str] = None,
                                     decision_details: Optional[str] = None,
                                     code_reference: Optional[str] = None,
                                     rationale: Optional[str] = None,
                                     assumptions: Optional[str] = None,
                                     consequences: Optional[str] = None,
                                     tradeoffs: Optional[str] = None,
                                     evidence: Optional[str] = None,
                                     options_considered: Optional[str] = None,
                                     metadata: Optional[Dict] = None) -> Dict:
        """Update a decision record by project name, decision title, and description (MCP endpoint)."""
        from urllib.parse import quote
        encoded_description = quote(decision_description, safe='')
        data = {
            'context': context,
            'constraints': constraints,
            'decision_details': decision_details,
            'code_reference': code_reference,
            'rationale': rationale,
            'assumptions': assumptions,
            'consequences': consequences,
            'tradeoffs': tradeoffs,
            'evidence': evidence,
            'options_considered': options_considered,
            'metadata': metadata
        }
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        return self._request('PUT', f'/api/mcp/projects/{project_name}/decisions/{decision_title}/records/{encoded_description}', json=data)
    
    def change_record_status_by_description(self, project_name: str, decision_title: str,
                                           decision_description: str, status: str,
                                           reason: Optional[str] = None,
                                           auto_handle_conflicts: bool = True) -> Dict:
        """Change the status of a decision record by project name, decision title, and description (MCP endpoint)."""
        from urllib.parse import quote
        encoded_description = quote(decision_description, safe='')
        return self._request('PATCH', f'/api/mcp/projects/{project_name}/decisions/{decision_title}/records/{encoded_description}/status', json={
            'status': status,
            'reason': reason,
            'auto_handle_conflicts': auto_handle_conflicts
        })
    
    def get_implementation_history_by_title(self, project_name: str, decision_title: str) -> Dict:
        """Get implementation history for a decision by project name and title (MCP endpoint)."""
        return self._request('GET', f'/api/mcp/projects/{project_name}/decisions/{decision_title}/implementation-history')
