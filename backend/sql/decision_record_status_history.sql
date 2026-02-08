-- Decision Record Status History Table
-- Table for tracking status changes of decision records

CREATE TABLE IF NOT EXISTS decision_record_status_history (
    id VARCHAR(36) PRIMARY KEY,
    decision_record_id VARCHAR(36) NOT NULL REFERENCES decision_records(id) ON DELETE CASCADE,
    from_status VARCHAR(50),
    to_status VARCHAR(50) NOT NULL,
    reason TEXT,
    metadata JSONB,
    changed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_status_history_record_id ON decision_record_status_history(decision_record_id);
CREATE INDEX IF NOT EXISTS idx_status_history_changed_at ON decision_record_status_history(changed_at);

-- Add comments for documentation
COMMENT ON TABLE decision_record_status_history IS 'Table for tracking status changes of decision records';
COMMENT ON COLUMN decision_record_status_history.id IS 'History entry unique identifier (UUID)';
COMMENT ON COLUMN decision_record_status_history.decision_record_id IS 'Foreign key to decision_records table';
COMMENT ON COLUMN decision_record_status_history.from_status IS 'Previous status (NULL for initial creation)';
COMMENT ON COLUMN decision_record_status_history.to_status IS 'New status';
COMMENT ON COLUMN decision_record_status_history.reason IS 'Reason for status change';
COMMENT ON COLUMN decision_record_status_history.metadata IS 'JSON metadata for status change (e.g., triggering_decision_record_id for automatic changes)';
COMMENT ON COLUMN decision_record_status_history.changed_at IS 'Timestamp when status was changed';
