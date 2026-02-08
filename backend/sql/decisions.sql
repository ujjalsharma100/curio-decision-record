-- Decisions Table
-- Table for storing decisions within projects

CREATE TABLE IF NOT EXISTS decisions (
    id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (project_id, title)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_decisions_project_id ON decisions(project_id);
CREATE INDEX IF NOT EXISTS idx_decisions_created_at ON decisions(created_at);
CREATE INDEX IF NOT EXISTS idx_decisions_project_title ON decisions(project_id, title);

-- Add comments for documentation
COMMENT ON TABLE decisions IS 'Table for storing decisions within projects';
COMMENT ON COLUMN decisions.id IS 'Decision unique identifier (UUID)';
COMMENT ON COLUMN decisions.project_id IS 'Foreign key to projects table';
COMMENT ON COLUMN decisions.title IS 'Decision title';
COMMENT ON COLUMN decisions.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN decisions.updated_at IS 'Record last update timestamp';
