"""
Configuration API
Handles application configuration management
"""

import json
from pathlib import Path


class ConfigAPI:
    """Configuration management API"""
    
    def __init__(self, config):
        self.config = config
        self.config_file = Path('config.json')
    
    def get_config(self):
        """Get current configuration"""
        return {
            'steam_library_path': self.config.get('steam_library_path', ''),
            'workshop_file': self.config.get('workshop_file', ''),
            'content_path': self.config.get('content_path', ''),
            'server': self.config.get('server', {}),
            'preview': self.config.get('preview', {})
        }
    
    def update_config(self, new_config):
        """Update configuration"""
        try:
            if not new_config:
                print("Error: Empty config data received")
                return False
            
            print(f"Updating config with: {new_config}")
            
            # Validate config structure
            if not isinstance(new_config, dict):
                print("Error: Config must be a dictionary")
                return False
            
            # Only update our custom config items, not Flask's built-in config
            custom_config_keys = [
                'steam_library_path',
                'workshop_file', 
                'content_path',
                'server',
                'preview'
            ]
            
            # Load existing custom config from file
            file_config = {}
            if self.config_file.exists():
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        file_config = json.load(f)
                except Exception as e:
                    print(f"Warning: Could not load existing config: {e}")
                    file_config = {}
            
            # Update only the provided keys
            for key, value in new_config.items():
                if key in custom_config_keys:
                    file_config[key] = value
                    # Also update in-memory config for Flask
                    self.config[key] = value
            
            # Ensure config file directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file with backup
            try:
                # Create backup if file exists
                if self.config_file.exists():
                    backup_file = self.config_file.with_suffix('.json.bak')
                    import shutil
                    shutil.copy2(self.config_file, backup_file)
                
                # Write new config (only custom keys)
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(file_config, f, ensure_ascii=False, indent=2)
                
                print(f"Config saved successfully to {self.config_file}")
                return True
                
            except PermissionError:
                print(f"Error: Permission denied writing to {self.config_file}")
                return False
            except OSError as e:
                print(f"Error: OS error writing config file: {e}")
                return False
            
        except Exception as e:
            print(f"Error updating config: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_steam_library_path(self):
        """Get Steam library path"""
        return self.config.get('steam_library_path', '')
    
    def get_workshop_file_path(self):
        """Get workshop file path"""
        if self.config.get('workshop_file'):
            return self.config['workshop_file']
        else:
            steam_path = self.get_steam_library_path()
            return str(Path(steam_path) / "steamapps" / "workshop" / "appworkshop_431960.acf")
    
    def get_content_path(self):
        """Get content path"""
        if self.config.get('content_path'):
            return Path(self.config['content_path'])
        else:
            steam_path = self.get_steam_library_path()
            return Path(steam_path) / "steamapps" / "workshop" / "content" / "431960"
