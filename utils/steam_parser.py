"""
Steam Parser
Handles parsing of Steam workshop data
"""

import vdf
from pathlib import Path


class SteamParser:
    """Steam workshop data parser"""
    
    def __init__(self, config):
        self.config = config
    
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
    
    def load_workshop_data(self):
        """Load workshop data from Steam files"""
        try:
            workshop_file = self.get_workshop_file_path()
            
            if not Path(workshop_file).exists():
                print(f"Workshop file not found: {workshop_file}")
                return None
            
            with open(workshop_file, 'r', encoding='utf-8') as f:
                data = vdf.load(f)
            
            # Extract workshop items
            workshop_items = data.get('AppWorkshop', {}).get('WorkshopItemsInstalled', {})
            
            if isinstance(workshop_items, dict):
                return set(workshop_items.keys())
            else:
                return set()
                
        except Exception as e:
            print(f"Error loading workshop data: {e}")
            return None
    
    def is_valid_workshop_id(self, workshop_id):
        """Check if a workshop ID is valid (numeric)"""
        try:
            int(workshop_id)
            return True
        except ValueError:
            return False
