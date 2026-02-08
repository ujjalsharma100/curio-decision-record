-- Decision record versions table
-- Stores full snapshots of decision records at each version

CREATE TABLE IF NOT EXISTS decision_record_versions (
    id VARCHAR(36) PRIMARY KEY,
    decision_record_id VARCHAR(36) NOT NULL REFERENCES decision_records(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,

    -- Full snapshot of the record at this version (stored as JSONB)
    snapshot JSONB NOT NULL,

    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    -- Ensure unique versions per record
    CONSTRAINT uq_decision_record_version UNIQUE (decision_record_id, version)
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_record_versions_record_id ON decision_record_versions(decision_record_id);
CREATE INDEX IF NOT EXISTS idx_record_versions_version ON decision_record_versions(decision_record_id, version);
