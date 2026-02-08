-- Decision record changelog table
-- Tracks all changes made to decision records (excluding status changes which are in status_history)

CREATE TABLE IF NOT EXISTS decision_record_changelog (
    id VARCHAR(36) PRIMARY KEY,
    decision_record_id VARCHAR(36) NOT NULL REFERENCES decision_records(id) ON DELETE CASCADE,
    from_version INTEGER NOT NULL,
    to_version INTEGER NOT NULL,

    -- JSON object describing what fields changed: {"field": {"old": "...", "new": "..."}}
    changes JSONB NOT NULL,

    -- Optional summary of the change
    summary VARCHAR(500),

    changed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_changelog_record_id ON decision_record_changelog(decision_record_id);
CREATE INDEX IF NOT EXISTS idx_changelog_changed_at ON decision_record_changelog(decision_record_id, changed_at DESC);
