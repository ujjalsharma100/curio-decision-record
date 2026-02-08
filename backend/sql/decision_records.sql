-- Decision Records Table
-- Table for storing decision records (ADR format)

CREATE TABLE IF NOT EXISTS decision_records (
    id VARCHAR(36) PRIMARY KEY,
    decision_id VARCHAR(36) NOT NULL REFERENCES decisions(id) ON DELETE CASCADE,
    context TEXT,
    constraints TEXT,
    decision_description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'proposed',
    rationale TEXT,
    assumptions TEXT,
    consequences TEXT,
    tradeoffs TEXT,
    evidence TEXT,
    options_considered TEXT,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (decision_id, decision_description)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_decision_records_decision_id ON decision_records(decision_id);
CREATE INDEX IF NOT EXISTS idx_decision_records_status ON decision_records(status);
CREATE INDEX IF NOT EXISTS idx_decision_records_created_at ON decision_records(created_at);
CREATE INDEX IF NOT EXISTS idx_decision_records_decision_description ON decision_records(decision_id, decision_description);

-- Add comments for documentation
COMMENT ON TABLE decision_records IS 'Table for storing decision records (ADR format)';
COMMENT ON COLUMN decision_records.id IS 'Decision record unique identifier (UUID)';
COMMENT ON COLUMN decision_records.decision_id IS 'Foreign key to decisions table';
COMMENT ON COLUMN decision_records.context IS 'Context: Why now?';
COMMENT ON COLUMN decision_records.constraints IS 'Constraints: Requirements to meet';
COMMENT ON COLUMN decision_records.decision_description IS 'The actual decision';
COMMENT ON COLUMN decision_records.status IS 'Record status (proposed, accepted, implemented, etc.)';
COMMENT ON COLUMN decision_records.rationale IS 'Why this decision was chosen';
COMMENT ON COLUMN decision_records.assumptions IS 'Critical assumptions for validation';
COMMENT ON COLUMN decision_records.consequences IS 'Positive/negative impacts';
COMMENT ON COLUMN decision_records.tradeoffs IS 'What is given up';
COMMENT ON COLUMN decision_records.evidence IS 'Links, resources, evidence';
COMMENT ON COLUMN decision_records.options_considered IS 'Alternatives considered';
COMMENT ON COLUMN decision_records.version IS 'Record version number';
COMMENT ON COLUMN decision_records.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN decision_records.updated_at IS 'Record last update timestamp';
