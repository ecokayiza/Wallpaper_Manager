"""
Steam Parser
Handles parsing of Steam workshop data
"""

import vdf
import json
import os
import time
from pathlib import Path


class SteamParser:
    """Steam workshop data parser"""
    
    def __init__(self, config):
        self.config = config
        self._vdf_cache = None
        self._vdf_cache_time = 0
        self._cache_duration = 30  # Cache VDF data for 30 seconds
        
        # Cache for user data to avoid repeated file system access
        self._user_cache = None
        self._user_cache_time = 0
        self._all_subscription_data = None  # Cache all user subscription data
    
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
    
    def get_all_subscription_data(self):
        """
        Get all subscription data from all users with caching
        Returns: dict with {user_id: {workshop_id: subscription_details}}
        """
        current_time = time.time()
        
        # Check cache
        if (self._all_subscription_data is not None and 
            current_time - self._user_cache_time < self._cache_duration):
            return self._all_subscription_data
        
        try:
            steam_userdata_path = self.get_steam_user_data_path()
            if not steam_userdata_path:
                return {}
            
            all_user_ids = self.get_all_steam_user_ids()
            all_data = {}
            
            for user_id in all_user_ids:
                subscription_file = steam_userdata_path / user_id / "ugc" / "431960_subscriptions.vdf"
                
                if not subscription_file.exists():
                    continue
                
                try:
                    with open(subscription_file, 'r', encoding='utf-8') as f:
                        data = vdf.load(f)
                    
                    user_subscriptions = {}
                    
                    if 'subscribedfiles' in data:
                        files_data = data['subscribedfiles']
                        
                        # Iterate through all subscription entries
                        for key, value in files_data.items():
                            if isinstance(value, dict) and 'publishedfileid' in value:
                                file_id = value['publishedfileid']
                                disabled = value.get('disabled_locally', '0') == '1'
                                time_subscribed = value.get('time_subscribed', 'Unknown')
                                
                                user_subscriptions[file_id] = {
                                    'user_id': user_id,
                                    'time_subscribed': time_subscribed,
                                    'disabled_locally': disabled,
                                    'is_active': not disabled
                                }
                    
                    all_data[user_id] = user_subscriptions
                    
                except Exception as e:
                    print(f"Error reading subscriptions for user {user_id}: {e}")
                    continue
            
            # Cache the result
            self._all_subscription_data = all_data
            return all_data
            
        except Exception as e:
            print(f"Error getting all subscription data: {e}")
            return {}
    def get_realtime_subscribed_items(self):
        """
        Get real-time subscribed items from all Steam users' subscription caches
        This combines subscriptions from all users on this system
        """
        try:
            all_data = self.get_all_subscription_data()
            if not all_data:
                return None
            
            all_subscribed_items = set()
            users_with_subscriptions = 0
            
            print("Processing subscription data from cached results...")
            
            for user_id, user_subscriptions in all_data.items():
                active_subscriptions = [item_id for item_id, details in user_subscriptions.items() 
                                      if details['is_active']]
                
                if active_subscriptions:
                    print(f"User {user_id} has {len(active_subscriptions)} active subscriptions")
                    all_subscribed_items.update(active_subscriptions)
                    users_with_subscriptions += 1
                else:
                    print(f"No Wallpaper Engine subscriptions found for user {user_id}")
            
            print(f"Total: {len(all_subscribed_items)} unique subscribed items from {users_with_subscriptions} users")
            return all_subscribed_items
            
        except Exception as e:
            print(f"Error reading real-time subscription data: {e}")
            return None
    
    def load_workshop_data(self):
        """Load workshop data - now prioritizes real-time data"""
        # First try to get real-time subscription data
        realtime_data = self.get_realtime_subscribed_items()
        if realtime_data is not None:
            return realtime_data
        
        print("Falling back to VDF file...")
        
        # Fallback to original VDF method
        current_time = time.time()
        
        # Check if we have cached data that's still valid
        if (self._vdf_cache is not None and 
            current_time - self._vdf_cache_time < self._cache_duration):
            return self._vdf_cache
        
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
                result = set(workshop_items.keys())
            else:
                result = set()
            
            # Cache the result
            self._vdf_cache = result
            self._vdf_cache_time = current_time
            
            return result
                
        except Exception as e:
            print(f"Error loading workshop data: {e}")
            return None
    
    def get_steam_user_data_path(self):
        """Get Steam user data path"""
        try:
            # First check if user has configured a specific path
            if hasattr(self.config, 'steam_userdata_path') and self.config.steam_userdata_path:
                configured_path = Path(self.config.steam_userdata_path.strip())  # Strip whitespace
                if configured_path.exists():
                    print(f"✓ Using configured Steam userdata path: {configured_path}")
                    return configured_path
                else:
                    print(f"⚠️  Configured Steam userdata path does not exist: '{configured_path}'")
                    print(f"   Falling back to automatic detection...")
            
            # Try to get Steam path from registry (Windows)
            if os.name == 'nt':
                try:
                    import winreg
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                      r"SOFTWARE\WOW6432Node\Valve\Steam") as key:
                        steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
                        registry_path = Path(steam_path) / "userdata"
                        if registry_path.exists():
                            print(f"✓ Using Steam userdata path from registry: {registry_path}")
                            return registry_path
                except Exception as e:
                    print(f"   Could not read Steam path from registry: {e}")
            
            # Fallback to common paths
            common_paths = [
                Path.home() / ".steam" / "steam" / "userdata",
                Path("C:") / "Program Files (x86)" / "Steam" / "userdata",
                Path("C:") / "Steam" / "userdata"
            ]
            
            print("   Checking common Steam installation paths...")
            for path in common_paths:
                if path.exists():
                    print(f"✓ Using Steam userdata path from common locations: {path}")
                    return path
                else:
                    print(f"   Path not found: {path}")
                    
        except Exception as e:
            print(f"❌ Error getting Steam user data path: {e}")
        
        print("❌ No valid Steam userdata path found")
        return None
    
    def get_steam_user_id(self):
        """Try to get the current Steam user ID"""
        try:
            steam_userdata_path = self.get_steam_user_data_path()
            if not steam_userdata_path:
                return None
            
            # Look for the most recently modified user directory
            user_dirs = [d for d in steam_userdata_path.iterdir() if d.is_dir() and d.name.isdigit()]
            if not user_dirs:
                return None
            
            # Sort by modification time and get the most recent
            most_recent = max(user_dirs, key=lambda d: d.stat().st_mtime)
            return most_recent.name
            
        except Exception as e:
            print(f"Error getting Steam user ID: {e}")
            return None
    
    def get_all_steam_user_ids(self):
        """Get all Steam user IDs on this system with caching"""
        current_time = time.time()
        
        # Check cache
        if (self._user_cache is not None and 
            current_time - self._user_cache_time < self._cache_duration):
            return self._user_cache
        
        try:
            steam_userdata_path = self.get_steam_user_data_path()
            if not steam_userdata_path:
                return []
            
            # Get all user directories with numeric names
            user_dirs = [d for d in steam_userdata_path.iterdir() if d.is_dir() and d.name.isdigit()]
            user_ids = [d.name for d in user_dirs]
            
            # Cache the result
            self._user_cache = user_ids
            self._user_cache_time = current_time
            
            print(f"Found {len(user_ids)} Steam users: {user_ids}")
            return user_ids
            
        except Exception as e:
            print(f"Error getting all Steam user IDs: {e}")
            return []
    
    def get_subscription_details_by_user(self, workshop_id):
        """
        Get detailed subscription information for a specific workshop item
        Returns which users have it subscribed and when
        """
        try:
            all_data = self.get_all_subscription_data()
            if not all_data:
                return []
            
            subscription_details = []
            
            for user_id, user_subscriptions in all_data.items():
                if workshop_id in user_subscriptions:
                    subscription_details.append(user_subscriptions[workshop_id])
            
            return subscription_details
            
        except Exception as e:
            print(f"Error getting subscription details: {e}")
            return []

    def get_realtime_subscription_status(self, workshop_id):
        """
        Get real-time subscription status using Steam's subscription cache from all users
        Returns True if ANY user has it subscribed
        """
        try:
            # Get the real-time subscribed items from all users
            subscribed_items = self.get_realtime_subscribed_items()
            
            if subscribed_items is not None:
                return workshop_id in subscribed_items
            else:
                # Fallback to VDF method
                print(f"Using fallback VDF method for {workshop_id}")
                return self._check_vdf_subscription(workshop_id)
                
        except Exception as e:
            print(f"Error getting realtime subscription status: {e}")
            return None
    
    def _check_vdf_subscription(self, workshop_id):
        """Check subscription status from VDF file"""
        workshop_items = self.load_workshop_data()
        return workshop_items and workshop_id in workshop_items
    
    def _check_file_modification_time(self, workshop_id):
        """
        Check if files were modified recently (within last hour)
        This can indicate active subscription
        """
        try:
            content_path = self.get_content_path()
            folder_path = content_path / workshop_id
            
            if not folder_path.exists():
                return False
            
            # Check if any file was modified in the last hour
            current_time = time.time()
            one_hour_ago = current_time - 3600
            
            for file_path in folder_path.rglob('*'):
                if file_path.is_file():
                    if file_path.stat().st_mtime > one_hour_ago:
                        return True
            
            return False
            
        except Exception as e:
            print(f"Error checking file modification time: {e}")
            return False
    
    def _check_steam_user_data(self, workshop_id):
        """
        Check Steam user data for subscription info
        This is more experimental and may not always work
        """
        try:
            user_id = self.get_steam_user_id()
            if not user_id:
                return None
            
            steam_userdata_path = self.get_steam_user_data_path()
            if not steam_userdata_path:
                return None
            
            # Look for workshop subscription files
            workshop_config_paths = [
                steam_userdata_path / user_id / "431960" / "remotecache.vdf",
                steam_userdata_path / user_id / "config" / "localconfig.vdf"
            ]
            
            for config_path in workshop_config_paths:
                if config_path.exists():
                    try:
                        with open(config_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if workshop_id in content:
                                return True
                    except:
                        continue
            
            return None
            
        except Exception as e:
            print(f"Error checking Steam user data: {e}")
            return None
    
    def is_valid_workshop_id(self, workshop_id):
        """Check if a workshop ID is valid (numeric)"""
        try:
            int(workshop_id)
            return True
        except ValueError:
            return False
