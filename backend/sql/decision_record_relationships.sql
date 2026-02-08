-- Decision Record Relationships Table
-- Table for storing relationships between decision records

CREATE TABLE IF NOT EXISTS decision_record_relationships (
    id VARCHAR(36) PRIMARY KEY,
    source_record_id VARCHAR(36) NOT NULL REFERENCES decision_records(id) ON DELETE CASCADE,
    target_record_id VARCHAR(36) NOT NULL REFERENCES decision_records(id) ON DELETE CASCADE,
    relationship_type VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_relationships_source ON decision_record_relationships(source_record_id);
CREATE INDEX IF NOT EXISTS idx_relationships_target ON decision_record_relationships(target_record_id);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON decision_record_relationships(relationship_type);

-- Add comments for documentation
COMMENT ON TABLE decision_record_relationships IS 'Table for storing relationships between decision records';
COMMENT ON COLUMN decision_record_relationships.id IS 'Relationship unique identifier (UUID)';
COMMENT ON COLUMN decision_record_relationships.source_record_id IS 'Foreign key to source decision record';
COMMENT ON COLUMN decision_record_relationships.target_record_id IS 'Foreign key to target decision record';
COMMENT ON COLUMN decision_record_relationships.relationship_type IS 'Type of relationship (superseded_by, related_to, depends_on, merged_from)';
COMMENT ON COLUMN decision_record_relationships.description IS 'Description of the relationship';
COMMENT ON COLUMN decision_record_relationships.created_at IS 'Record creation timestamp';
