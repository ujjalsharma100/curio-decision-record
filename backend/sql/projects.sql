-- Projects Table
-- Main table for storing projects

CREATE TABLE IF NOT EXISTS projects (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at);
CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name);

-- Add comments for documentation
COMMENT ON TABLE projects IS 'Main table for storing projects';
COMMENT ON COLUMN projects.id IS 'Project unique identifier (UUID)';
COMMENT ON COLUMN projects.name IS 'Project name';
COMMENT ON COLUMN projects.description IS 'Project description';
COMMENT ON COLUMN projects.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN projects.updated_at IS 'Record last update timestamp';
