"""
Database service layer for PostgreSQL integration.

This module provides database operations for storing and retrieving
data from the Curio Decision Record application.
"""

import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseService:
    """Database service for PostgreSQL operations."""
    
    def __init__(self, 
                 host: str = None,
                 port: int = None,
                 database: str = None,
                 user: str = None,
                 password: str = None,
                 schema: str = None,
                 min_conn: int = 1,
                 max_conn: int = 10):
        """
        Initialize database service with connection pool.
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
            schema: Database schema name
            min_conn: Minimum connections in pool
            max_conn: Maximum connections in pool
        """
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.port = port or int(os.getenv('DB_PORT', '5432'))
        self.database = database or os.getenv('DB_NAME', 'curio_decision_record')
        self.user = user or os.getenv('DB_USER', 'postgres')
        self.password = password or os.getenv('DB_PASSWORD', 'postgres')
        self.schema = schema or os.getenv('DB_SCHEMA', 'public')
        
        # Connection pool
        self.pool = None
        self._initialize_pool(min_conn, max_conn)
    
    def _initialize_pool(self, min_conn: int, max_conn: int):
        """Initialize connection pool."""
        try:
            self.pool = SimpleConnectionPool(
                min_conn, max_conn,
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                cursor_factory=RealDictCursor
            )
            logger.info(f"Database connection pool initialized for {self.database}")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool."""
        conn = None
        try:
            conn = self.pool.getconn()
            # Set the schema for this connection
            with conn.cursor() as cursor:
                cursor.execute(f"SET search_path TO {self.schema}, public")
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                self.pool.putconn(conn)
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    logger.info("Database connection test successful")
                    return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def _execute_sql_file(self, sql_file_path: str):
        """Execute SQL commands from a file."""
        try:
            sql_path = os.path.join(os.path.dirname(__file__), 'sql', sql_file_path)
            
            if not os.path.exists(sql_path):
                logger.error(f"SQL file not found: {sql_path}")
                raise FileNotFoundError(f"SQL file not found: {sql_path}")
            
            with open(sql_path, 'r') as file:
                sql_content = file.read()
            
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql_content)
                    conn.commit()
                    logger.info(f"Successfully executed SQL file: {sql_file_path}")
                    
        except Exception as e:
            logger.error(f"Failed to execute SQL file {sql_file_path}: {e}")
            raise
    
    def drop_tables(self):
        """Drop all tables in reverse order to respect foreign key constraints."""
        try:
            # Drop tables in reverse order of creation to respect foreign key constraints
            tables_to_drop = [
                'decision_record_changelog',
                'decision_record_versions',
                'decision_record_relationships',
                'decision_record_status_history',
                'decision_records',
                'decision_relationships',
                'decisions',
                'projects'
            ]
            
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Drop tables in reverse order (CASCADE handles dependencies automatically)
                    for table in tables_to_drop:
                        try:
                            cursor.execute(f'DROP TABLE IF EXISTS {self.schema}.{table} CASCADE')
                            logger.info(f"Dropped table: {table}")
                        except Exception as e:
                            logger.warning(f"Failed to drop table {table}: {e}")
                    conn.commit()
            
            logger.info("All tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise
    
    def create_tables(self):
        """Create all required tables using SQL files."""
        try:
            # Execute SQL files to create tables in order
            sql_files = [
                'projects.sql',
                'decisions.sql',
                'decision_relationships.sql',
                'decision_records.sql',
                'decision_record_status_history.sql',
                'decision_record_relationships.sql',
                'decision_record_versions.sql',
                'decision_record_changelog.sql'
            ]
            
            for sql_file in sql_files:
                self._execute_sql_file(sql_file)
            
            logger.info("All tables created successfully from SQL files")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    # ==================== Projects CRUD ====================
    
    def create_project(self, project_data: Dict) -> Dict:
        """Create a new project."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO projects (id, name, description)
                    VALUES (%s, %s, %s)
                """, (project_data['id'], project_data['name'], project_data.get('description')))
                conn.commit()
                return self.get_project(project_data['id'])
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get a project by ID."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
    
    def get_project_by_name(self, name: str) -> Optional[Dict]:
        """Get a project by name."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM projects WHERE name = %s", (name,))
                result = cursor.fetchone()
                return dict(result) if result else None
    
    def get_all_projects(self) -> List[Dict]:
        """Get all projects."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT p.*, COUNT(d.id) as decision_count
                    FROM projects p
                    LEFT JOIN decisions d ON p.id = d.project_id
                    GROUP BY p.id
                    ORDER BY p.created_at DESC
                """)
                return [dict(row) for row in cursor.fetchall()]
    
    def update_project(self, project_id: str, project_data: Dict) -> Dict:
        """Update a project."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                updates = []
                params = []
                
                if 'name' in project_data:
                    updates.append("name = %s")
                    params.append(project_data['name'])
                if 'description' in project_data:
                    updates.append("description = %s")
                    params.append(project_data['description'])
                
                if updates:
                    updates.append("updated_at = CURRENT_TIMESTAMP")
                    params.append(project_id)
                    cursor.execute(f"""
                        UPDATE projects SET {', '.join(updates)}
                        WHERE id = %s
                    """, params)
                    conn.commit()
                
                return self.get_project(project_id)
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM projects WHERE id = %s", (project_id,))
                conn.commit()
                return cursor.rowcount > 0
    
    def get_project_decisions(self, project_id: str) -> List[Dict]:
        """Get all decisions for a project."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM decisions WHERE project_id = %s ORDER BY created_at
                """, (project_id,))
                return [dict(row) for row in cursor.fetchall()]
    
    # ==================== Decisions CRUD ====================
    
    def create_decision(self, decision_data: Dict) -> Dict:
        """Create a new decision."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO decisions (id, project_id, title)
                    VALUES (%s, %s, %s)
                """, (decision_data['id'], decision_data['project_id'], decision_data['title']))
                conn.commit()
                return self.get_decision(decision_data['id'])
    
    def get_decision(self, decision_id: str) -> Optional[Dict]:
        """Get a decision by ID."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM decisions WHERE id = %s", (decision_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
    
    def get_decision_by_title(self, project_id: str, title: str) -> Optional[Dict]:
        """Get a decision by project ID and title."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM decisions WHERE project_id = %s AND title = %s LIMIT 1",
                    (project_id, title),
                )
                result = cursor.fetchone()
                return dict(result) if result else None
    
    def get_decisions_by_project(self, project_id: str) -> List[Dict]:
        """Get all decisions for a project."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT d.*, COUNT(dr.id) as record_count
                    FROM decisions d
                    LEFT JOIN decision_records dr ON d.id = dr.decision_id
                    WHERE d.project_id = %s
                    GROUP BY d.id
                    ORDER BY d.created_at DESC
                """, (project_id,))
                decisions = [dict(row) for row in cursor.fetchall()]
                
                # Add status counts for each decision
                for decision in decisions:
                    cursor.execute("""
                        SELECT status, COUNT(*)::int as count
                        FROM decision_records
                        WHERE decision_id = %s
                        GROUP BY status
                    """, (decision['id'],))
                    status_counts = {}
                    for row in cursor.fetchall():
                        # RealDictCursor already returns dict, but ensure count is int
                        row_dict = dict(row) if not isinstance(row, dict) else row
                        status_counts[row_dict['status']] = int(row_dict['count'])
                    decision['status_counts'] = status_counts
                
                return decisions
    
    def update_decision(self, decision_id: str, decision_data: Dict) -> Dict:
        """Update a decision."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                if 'title' in decision_data:
                    cursor.execute("""
                        UPDATE decisions SET title = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (decision_data['title'], decision_id))
                    conn.commit()
                return self.get_decision(decision_id)
    
    def delete_decision(self, decision_id: str) -> bool:
        """Delete a decision."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM decisions WHERE id = %s", (decision_id,))
                conn.commit()
                return cursor.rowcount > 0
    
    # ==================== Decision Records CRUD ====================
    
    def create_decision_record(self, record_data: Dict) -> Dict:
        """Create a new decision record."""
        import json as _json
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                metadata_value = record_data.get('metadata')
                if metadata_value is not None and isinstance(metadata_value, dict):
                    metadata_value = _json.dumps(metadata_value)
                cursor.execute("""
                    INSERT INTO decision_records (
                        id, decision_id, context, constraints, decision_description,
                        decision_details, status, rationale, assumptions, consequences, tradeoffs,
                        evidence, options_considered, code_reference, metadata, version
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    record_data['id'], record_data['decision_id'],
                    record_data.get('context'), record_data.get('constraints'),
                    record_data['decision_description'], record_data.get('decision_details'),
                    record_data.get('status', 'proposed'),
                    record_data.get('rationale'), record_data.get('assumptions'),
                    record_data.get('consequences'), record_data.get('tradeoffs'),
                    record_data.get('evidence'), record_data.get('options_considered'),
                    record_data.get('code_reference'), metadata_value,
                    record_data.get('version', 1)
                ))
                conn.commit()
                return self.get_decision_record(record_data['id'])
    
    def get_decision_record(self, record_id: str) -> Optional[Dict]:
        """Get a decision record by ID."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM decision_records WHERE id = %s", (record_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
    
    def get_decision_record_by_description(self, decision_id: str, decision_description: str) -> Optional[Dict]:
        """Get a decision record by decision_id and decision_description."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM decision_records WHERE decision_id = %s AND decision_description = %s", 
                             (decision_id, decision_description))
                result = cursor.fetchone()
                return dict(result) if result else None
    
    def get_decision_records_by_decision(self, decision_id: str) -> List[Dict]:
        """Get all decision records for a decision."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM decision_records 
                    WHERE decision_id = %s 
                    ORDER BY created_at DESC
                """, (decision_id,))
                return [dict(row) for row in cursor.fetchall()]
    
    def update_decision_record(self, record_id: str, record_data: Dict) -> Dict:
        """Update a decision record."""
        import json as _json
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                updates = []
                params = []
                
                updatable_fields = [
                    'context', 'constraints', 'decision_description', 'decision_details', 'rationale',
                    'assumptions', 'consequences', 'tradeoffs', 'evidence', 'options_considered', 'code_reference'
                ]
                
                for field in updatable_fields:
                    if field in record_data:
                        updates.append(f"{field} = %s")
                        params.append(record_data[field])
                
                if 'metadata' in record_data:
                    updates.append("metadata = %s")
                    metadata_value = record_data['metadata']
                    if metadata_value is not None and isinstance(metadata_value, dict):
                        metadata_value = _json.dumps(metadata_value)
                    params.append(metadata_value)
                
                if 'version' in record_data:
                    updates.append("version = %s")
                    params.append(record_data['version'])
                
                if updates:
                    updates.append("updated_at = CURRENT_TIMESTAMP")
                    params.append(record_id)
                    cursor.execute(f"""
                        UPDATE decision_records SET {', '.join(updates)}
                        WHERE id = %s
                    """, params)
                    conn.commit()
                
                return self.get_decision_record(record_id)
    
    def update_decision_record_status(self, record_id: str, new_status: str) -> Dict:
        """Update decision record status."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE decision_records SET status = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (new_status, record_id))
                conn.commit()
                return self.get_decision_record(record_id)
    
    def delete_decision_record(self, record_id: str) -> bool:
        """Delete a decision record."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM decision_records WHERE id = %s", (record_id,))
                conn.commit()
                return cursor.rowcount > 0
    
    def get_current_accepted_record(self, decision_id: str) -> Optional[Dict]:
        """Get the currently accepted record for a decision."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM decision_records 
                    WHERE decision_id = %s AND status = 'accepted'
                    LIMIT 1
                """, (decision_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
    
    def get_current_implemented_record(self, decision_id: str) -> Optional[Dict]:
        """Get the currently implemented record for a decision."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM decision_records 
                    WHERE decision_id = %s AND status IN ('implemented', 'implemented_inferred')
                    LIMIT 1
                """, (decision_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
    
    # ==================== Status History CRUD ====================
    
    def create_status_history(self, history_data: Dict) -> Dict:
        """Create a status history entry."""
        import json
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                metadata_json = None
                if history_data.get('metadata'):
                    metadata_json = json.dumps(history_data['metadata'])
                
                cursor.execute("""
                    INSERT INTO decision_record_status_history 
                    (id, decision_record_id, from_status, to_status, reason, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    history_data['id'], history_data['decision_record_id'],
                    history_data.get('from_status'), history_data['to_status'],
                    history_data.get('reason'), metadata_json
                ))
                conn.commit()
                return self.get_status_history(history_data['id'])
    
    def get_status_history(self, history_id: str) -> Optional[Dict]:
        """Get a status history entry by ID."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM decision_record_status_history WHERE id = %s
                """, (history_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
    
    def get_status_history_by_record(self, record_id: str) -> List[Dict]:
        """Get all status history entries for a decision record."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM decision_record_status_history 
                    WHERE decision_record_id = %s 
                    ORDER BY changed_at DESC
                """, (record_id,))
                return [dict(row) for row in cursor.fetchall()]
    
    # ==================== Relationships CRUD ====================
    
    def create_relationship(self, relationship_data: Dict) -> Dict:
        """Create a decision record relationship."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO decision_record_relationships 
                    (id, source_record_id, target_record_id, relationship_type, description)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    relationship_data['id'], relationship_data['source_record_id'],
                    relationship_data['target_record_id'], relationship_data['relationship_type'],
                    relationship_data.get('description')
                ))
                conn.commit()
                return self.get_relationship(relationship_data['id'])
    
    def get_relationship(self, relationship_id: str) -> Optional[Dict]:
        """Get a relationship by ID."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM decision_record_relationships WHERE id = %s
                """, (relationship_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
    
    def get_relationships_by_record(self, record_id: str) -> Dict:
        """Get all relationships for a record."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM decision_record_relationships 
                    WHERE source_record_id = %s
                """, (record_id,))
                outgoing = [dict(row) for row in cursor.fetchall()]
                
                cursor.execute("""
                    SELECT * FROM decision_record_relationships 
                    WHERE target_record_id = %s
                """, (record_id,))
                incoming = [dict(row) for row in cursor.fetchall()]
                
                return {'outgoing': outgoing, 'incoming': incoming}
    
    def update_relationship(self, relationship_id: str, relationship_type: str = None,
                            description: str = None) -> Optional[Dict]:
        """Update a relationship's type or description."""
        updates = []
        params = []
        if relationship_type is not None:
            updates.append("relationship_type = %s")
            params.append(relationship_type)
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        if not updates:
            return self.get_relationship(relationship_id)
        params.append(relationship_id)
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE decision_record_relationships 
                    SET {', '.join(updates)}
                    WHERE id = %s
                """, tuple(params))
                conn.commit()
                return self.get_relationship(relationship_id)
    
    def delete_relationship(self, relationship_id: str) -> bool:
        """Delete a relationship."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM decision_record_relationships WHERE id = %s
                """, (relationship_id,))
                conn.commit()
                return cursor.rowcount > 0
    
    # ==================== Decision Relationships CRUD ====================
    
    def create_decision_relationship(self, relationship_data: Dict) -> Dict:
        """Create a decision-level relationship."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO decision_relationships 
                    (id, source_decision_id, target_decision_id, relationship_type, description)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    relationship_data['id'], relationship_data['source_decision_id'],
                    relationship_data['target_decision_id'], relationship_data['relationship_type'],
                    relationship_data.get('description')
                ))
                conn.commit()
                return self.get_decision_relationship(relationship_data['id'])
    
    def get_decision_relationship(self, relationship_id: str) -> Optional[Dict]:
        """Get a decision relationship by ID."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM decision_relationships WHERE id = %s
                """, (relationship_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
    
    def get_decision_relationships_by_decision(self, decision_id: str) -> Dict:
        """Get all decision-level relationships for a decision."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM decision_relationships 
                    WHERE source_decision_id = %s
                """, (decision_id,))
                outgoing = [dict(row) for row in cursor.fetchall()]
                
                cursor.execute("""
                    SELECT * FROM decision_relationships 
                    WHERE target_decision_id = %s
                """, (decision_id,))
                incoming = [dict(row) for row in cursor.fetchall()]
                
                return {'outgoing': outgoing, 'incoming': incoming}
    
    def update_decision_relationship(self, relationship_id: str, relationship_type: str = None,
                                    description: str = None) -> Optional[Dict]:
        """Update a decision relationship's type or description."""
        updates = []
        params = []
        if relationship_type is not None:
            updates.append("relationship_type = %s")
            params.append(relationship_type)
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        if not updates:
            return self.get_decision_relationship(relationship_id)
        params.append(relationship_id)
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE decision_relationships 
                    SET {', '.join(updates)}
                    WHERE id = %s
                """, tuple(params))
                conn.commit()
                return self.get_decision_relationship(relationship_id)
    
    def delete_decision_relationship(self, relationship_id: str) -> bool:
        """Delete a decision relationship."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM decision_relationships WHERE id = %s
                """, (relationship_id,))
                conn.commit()
                return cursor.rowcount > 0
    
    # ==================== Version Control ====================

    def create_record_version(self, version_data: Dict) -> Dict:
        """Create a version snapshot of a decision record."""
        import json
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                # Use ON CONFLICT DO NOTHING to avoid duplicate key errors
                # This allows the method to be idempotent - if the version already exists, skip it
                cursor.execute("""
                    INSERT INTO decision_record_versions
                    (id, decision_record_id, version, snapshot)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (decision_record_id, version) DO NOTHING
                """, (
                    version_data['id'], version_data['decision_record_id'],
                    version_data['version'], json.dumps(version_data['snapshot'])
                ))
                conn.commit()
                # If the insert was skipped due to conflict, get the existing version
                if cursor.rowcount == 0:
                    existing_version = self.get_record_version_by_number(
                        version_data['decision_record_id'],
                        version_data['version']
                    )
                    if existing_version:
                        return existing_version
                return self.get_record_version(version_data['id'])

    def get_record_version(self, version_id: str) -> Optional[Dict]:
        """Get a version by ID."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM decision_record_versions WHERE id = %s
                """, (version_id,))
                result = cursor.fetchone()
                return dict(result) if result else None

    def get_record_version_by_number(self, record_id: str, version: int) -> Optional[Dict]:
        """Get a specific version of a record."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM decision_record_versions
                    WHERE decision_record_id = %s AND version = %s
                """, (record_id, version))
                result = cursor.fetchone()
                return dict(result) if result else None

    def get_all_record_versions(self, record_id: str) -> List[Dict]:
        """Get all versions of a decision record."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM decision_record_versions
                    WHERE decision_record_id = %s
                    ORDER BY version DESC
                """, (record_id,))
                return [dict(row) for row in cursor.fetchall()]

    def get_latest_version_number(self, record_id: str) -> int:
        """Get the latest version number for a record."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COALESCE(MAX(version), 0) as max_version
                    FROM decision_record_versions
                    WHERE decision_record_id = %s
                """, (record_id,))
                result = cursor.fetchone()
                return result['max_version'] if result else 0

    def create_changelog_entry(self, changelog_data: Dict) -> Dict:
        """Create a changelog entry for a decision record update."""
        import json
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO decision_record_changelog
                    (id, decision_record_id, from_version, to_version, changes, summary)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    changelog_data['id'], changelog_data['decision_record_id'],
                    changelog_data['from_version'], changelog_data['to_version'],
                    json.dumps(changelog_data['changes']), changelog_data.get('summary')
                ))
                conn.commit()
                return self.get_changelog_entry(changelog_data['id'])

    def get_changelog_entry(self, changelog_id: str) -> Optional[Dict]:
        """Get a changelog entry by ID."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM decision_record_changelog WHERE id = %s
                """, (changelog_id,))
                result = cursor.fetchone()
                return dict(result) if result else None

    def get_record_changelog(self, record_id: str) -> List[Dict]:
        """Get all changelog entries for a decision record."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM decision_record_changelog
                    WHERE decision_record_id = %s
                    ORDER BY changed_at DESC
                """, (record_id,))
                return [dict(row) for row in cursor.fetchall()]

    # ==================== Decision Timeline & History ====================

    def get_decision_timeline_events(self, decision_id: str) -> List[Dict]:
        """
        Get all timeline events for a decision from multiple sources.
        Returns events from:
        - Record creation (new record proposed)
        - Status changes
        - Version/content changes (changelog)
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                # Get all records for this decision first
                cursor.execute("""
                    SELECT id, version, status, decision_description, created_at
                    FROM decision_records
                    WHERE decision_id = %s
                """, (decision_id,))
                records = {row['id']: dict(row) for row in cursor.fetchall()}
                record_ids = list(records.keys())
                
                if not record_ids:
                    return []
                
                events = []
                
                # 1. Record creation events
                for record_id, record in records.items():
                    events.append({
                        'event_type': 'record_created',
                        'timestamp': record['created_at'],
                        'record_id': record_id,
                        'record_version': record['version'],
                        'decision_description': record['decision_description'][:100] + '...' if len(record.get('decision_description', '') or '') > 100 else record.get('decision_description'),
                        'details': {
                            'initial_status': record['status']
                        }
                    })
                
                # 2. Status change events (excluding initial creation which is already captured)
                cursor.execute("""
                    SELECT sh.*, dr.decision_description, dr.version as record_version
                    FROM decision_record_status_history sh
                    JOIN decision_records dr ON sh.decision_record_id = dr.id
                    WHERE dr.decision_id = %s AND sh.from_status IS NOT NULL
                    ORDER BY sh.changed_at
                """, (decision_id,))
                
                for row in cursor.fetchall():
                    row_dict = dict(row)
                    events.append({
                        'event_type': 'status_change',
                        'timestamp': row_dict['changed_at'],
                        'record_id': row_dict['decision_record_id'],
                        'record_version': row_dict['record_version'],
                        'decision_description': row_dict['decision_description'][:100] + '...' if len(row_dict.get('decision_description', '') or '') > 100 else row_dict.get('decision_description'),
                        'details': {
                            'from_status': row_dict['from_status'],
                            'to_status': row_dict['to_status'],
                            'reason': row_dict['reason'],
                            'metadata': row_dict['metadata'],
                            'is_automatic': row_dict.get('metadata', {}).get('change_type') == 'automatic' if row_dict.get('metadata') else False
                        }
                    })
                
                # 3. Content/version change events
                cursor.execute("""
                    SELECT cl.*, dr.decision_description, dr.version as current_version
                    FROM decision_record_changelog cl
                    JOIN decision_records dr ON cl.decision_record_id = dr.id
                    WHERE dr.decision_id = %s
                    ORDER BY cl.changed_at
                """, (decision_id,))
                
                for row in cursor.fetchall():
                    row_dict = dict(row)
                    events.append({
                        'event_type': 'content_change',
                        'timestamp': row_dict['changed_at'],
                        'record_id': row_dict['decision_record_id'],
                        'record_version': row_dict['to_version'],
                        'decision_description': row_dict['decision_description'][:100] + '...' if len(row_dict.get('decision_description', '') or '') > 100 else row_dict.get('decision_description'),
                        'details': {
                            'from_version': row_dict['from_version'],
                            'to_version': row_dict['to_version'],
                            'summary': row_dict['summary'],
                            'changes': row_dict['changes']
                        }
                    })
                
                # Sort all events by timestamp
                events.sort(key=lambda x: x['timestamp'] if x['timestamp'] else '', reverse=True)
                
                return events

    def get_implementation_history(self, decision_id: str) -> Dict:
        """
        Get the implementation history for a decision.
        Returns:
        - current_implementation: The currently implemented record (if any)
        - past_implementations: List of previously implemented records (now deprecated)
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                # Get current implemented record
                cursor.execute("""
                    SELECT dr.*, sh.changed_at as implemented_at
                    FROM decision_records dr
                    LEFT JOIN decision_record_status_history sh ON dr.id = sh.decision_record_id 
                        AND sh.to_status IN ('implemented', 'implemented_inferred')
                    WHERE dr.decision_id = %s 
                    AND dr.status IN ('implemented', 'implemented_inferred')
                    ORDER BY sh.changed_at DESC
                    LIMIT 1
                """, (decision_id,))
                current_impl = cursor.fetchone()
                current_implementation = dict(current_impl) if current_impl else None
                
                # Get deprecated records that were previously implemented
                # We look at status history to find records that transitioned FROM implemented/implemented_inferred TO deprecated
                cursor.execute("""
                    SELECT DISTINCT dr.*, 
                        impl_sh.changed_at as implemented_at,
                        dep_sh.changed_at as deprecated_at,
                        dep_sh.reason as deprecation_reason
                    FROM decision_records dr
                    JOIN decision_record_status_history impl_sh ON dr.id = impl_sh.decision_record_id 
                        AND impl_sh.to_status IN ('implemented', 'implemented_inferred')
                    JOIN decision_record_status_history dep_sh ON dr.id = dep_sh.decision_record_id 
                        AND dep_sh.to_status = 'deprecated'
                        AND dep_sh.from_status IN ('implemented', 'implemented_inferred')
                    WHERE dr.decision_id = %s 
                    AND dr.status = 'deprecated'
                    ORDER BY dep_sh.changed_at DESC
                """, (decision_id,))
                past_implementations = [dict(row) for row in cursor.fetchall()]
                
                return {
                    'current_implementation': current_implementation,
                    'past_implementations': past_implementations
                }

    def close(self):
        """Close the connection pool."""
        if self.pool:
            self.pool.closeall()
            logger.info("Database connection pool closed")
