"""
Workspace configuration manager for Curio Decision Record MCP Server.

Manages workspace-specific project configuration stored in .curio-decision/config.json
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

CONFIG_DIR_NAME = ".curio-decision"
CONFIG_FILE_NAME = "config.json"


class ConfigManager:
    """Manages workspace-specific configuration for Curio Decision Records."""
    
    def __init__(self, workspace_root: Optional[str] = None):
        """
        Initialize config manager.
        
        Args:
            workspace_root: Root directory of the workspace. If None, tries to detect from environment or uses current working directory.
        """
        if workspace_root is None:
            # Try to get workspace root from environment (set by MCP clients)
            workspace_root = os.getenv('MCP_WORKSPACE_ROOT') or os.getenv('WORKSPACE_ROOT') or os.getcwd()
        
        self.workspace_root = Path(workspace_root).resolve()
        self.config_dir = self.workspace_root / CONFIG_DIR_NAME
        self.config_file = self.config_dir / CONFIG_FILE_NAME
    
    
    def ensure_config_dir(self):
        """Ensure the config directory exists."""
        self.config_dir.mkdir(exist_ok=True)
    
    def get_project_name(self) -> Optional[str]:
        """Get the current project name from workspace config."""
        if not self.config_file.exists():
            return None
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return config.get('project_name')
        except Exception as e:
            logger.error(f"Error reading config file: {e}")
            return None
    
    def set_project_name(self, project_name: str) -> bool:
        """
        Set the current project name in workspace config.
        
        Args:
            project_name: The project name to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.ensure_config_dir()
            
            # Read existing config or create new
            config = {}
            if self.config_file.exists():
                try:
                    with open(self.config_file, 'r') as f:
                        config = json.load(f)
                except:
                    pass
            
            config['project_name'] = project_name
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Set project_name to {project_name} in {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Error writing config file: {e}")
            return False
    
    def get_config(self) -> Dict:
        """Get the full configuration."""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading config file: {e}")
            return {}
    
    def update_config(self, updates: Dict) -> bool:
        """Update configuration with provided values."""
        try:
            self.ensure_config_dir()
            
            config = self.get_config()
            config.update(updates)
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error updating config file: {e}")
            return False
