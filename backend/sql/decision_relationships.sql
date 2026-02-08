-- Decision Relationships Table
-- Table for storing relationships between decisions (whole-decision level)
-- Captures conceptual/topic-level links: supersedes, depends_on, etc.

CREATE TABLE IF NOT EXISTS decision_relationships (
    id VARCHAR(36) PRIMARY KEY,
    source_decision_id VARCHAR(36) NOT NULL REFERENCES decisions(id) ON DELETE CASCADE,
    target_decision_id VARCHAR(36) NOT NULL REFERENCES decisions(id) ON DELETE CASCADE,
    relationship_type VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT decision_relationships_no_self CHECK (source_decision_id != target_decision_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_decision_relationships_source ON decision_relationships(source_decision_id);
CREATE INDEX IF NOT EXISTS idx_decision_relationships_target ON decision_relationships(target_decision_id);
CREATE INDEX IF NOT EXISTS idx_decision_relationships_type ON decision_relationships(relationship_type);

-- Add comments for documentation
COMMENT ON TABLE decision_relationships IS 'Table for storing relationships between decisions (whole-decision level)';
COMMENT ON COLUMN decision_relationships.id IS 'Relationship unique identifier (UUID)';
COMMENT ON COLUMN decision_relationships.source_decision_id IS 'Foreign key to source decision';
COMMENT ON COLUMN decision_relationships.target_decision_id IS 'Foreign key to target decision';
COMMENT ON COLUMN decision_relationships.relationship_type IS 'Type of relationship (superseded_by, supersedes, related_to, depends_on, merged_from, derived_from, conflicts_with)';
COMMENT ON COLUMN decision_relationships.description IS 'Description of the relationship';
COMMENT ON COLUMN decision_relationships.created_at IS 'Record creation timestamp';
