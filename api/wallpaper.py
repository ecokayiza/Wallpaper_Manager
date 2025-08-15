"""
Wallpaper API
Handles wallpaper data management and operations
"""

import json
import shutil
import subprocess
import os
from utils.steam_parser import SteamParser
from utils.image_processor import ImageProcessor


class WallpaperAPI:
    """Wallpaper management API"""
    
    def __init__(self, config):
        self.config = config
        self.steam_parser = SteamParser(config)
        self.image_processor = ImageProcessor(config)
        
    def get_subscribed_wallpapers(self):
        """Get all subscribed wallpapers"""
        try:
            # Load workshop data
            workshop_items = self.steam_parser.load_workshop_data()
            if not workshop_items:
                return []
            
            wallpapers = []
            content_path = self.steam_parser.get_content_path()
            
            for item_id in workshop_items:
                folder_path = content_path / item_id
                if folder_path.exists():
                    wallpaper_info = self._get_wallpaper_info(item_id, folder_path)
                    wallpaper_info['subscribed'] = True
                    wallpapers.append(wallpaper_info)
            
            # Sort by size (largest first)
            wallpapers.sort(key=lambda x: x['size'], reverse=True)
            return wallpapers
            
        except Exception as e:
            print(f"Error getting subscribed wallpapers: {e}")
            return []
    
    def get_unsubscribed_wallpapers(self):
        """Get wallpapers that are no longer subscribed"""
        try:
            # Load workshop data
            workshop_items = self.steam_parser.load_workshop_data()
            if workshop_items is None:
                return []
            
            wallpapers = []
            content_path = self.steam_parser.get_content_path()
            
            if content_path.exists():
                for folder in content_path.iterdir():
                    if folder.is_dir() and folder.name not in workshop_items:
                        try:
                            int(folder.name)  # Check if it's a numeric ID
                            wallpaper_info = self._get_wallpaper_info(folder.name, folder)
                            wallpaper_info['subscribed'] = False
                            wallpapers.append(wallpaper_info)
                        except ValueError:
                            continue
            
            # Sort by size (largest first)
            wallpapers.sort(key=lambda x: x['size'], reverse=True)
            return wallpapers
            
        except Exception as e:
            print(f"Error getting unsubscribed wallpapers: {e}")
            return []
    
    def get_wallpaper_details(self, wallpaper_id):
        """Get detailed information about a specific wallpaper"""
        try:
            content_path = self.steam_parser.get_content_path()
            folder_path = content_path / wallpaper_id
            
            if not folder_path.exists():
                return None
            
            # Check if subscribed
            workshop_items = self.steam_parser.load_workshop_data()
            is_subscribed = workshop_items and wallpaper_id in workshop_items
            
            wallpaper_info = self._get_wallpaper_info(wallpaper_id, folder_path)
            wallpaper_info['subscribed'] = is_subscribed
            
            return wallpaper_info
            
        except Exception as e:
            print(f"Error getting wallpaper details: {e}")
            return None
    
    def get_preview_image(self, wallpaper_id):
        """Get preview image path for a wallpaper"""
        try:
            content_path = self.steam_parser.get_content_path()
            folder_path = content_path / wallpaper_id
            
            if not folder_path.exists():
                return None
            
            return self.image_processor.get_preview_path(folder_path)
            
        except Exception as e:
            print(f"Error getting preview image: {e}")
            return None
    
    def delete_wallpaper(self, wallpaper_id):
        """Delete a wallpaper folder"""
        try:
            content_path = self.steam_parser.get_content_path()
            folder_path = content_path / wallpaper_id
            
            if folder_path.exists():
                shutil.rmtree(folder_path)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error deleting wallpaper: {e}")
            return False
    
    def open_wallpaper_folder(self, wallpaper_id):
        """Open wallpaper folder in file explorer"""
        try:
            content_path = self.steam_parser.get_content_path()
            folder_path = content_path / wallpaper_id
            
            if not folder_path.exists():
                print(f"Wallpaper folder not found: {folder_path}")
                return False
            
            # Use Windows explorer to open the folder
            if os.name == 'nt':  # Windows
                # Don't use check=True for Windows explorer as it often returns non-zero even on success
                subprocess.Popen(['explorer', str(folder_path)],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
                return True
            elif os.name == 'posix':  # macOS/Linux
                if subprocess.run(['which', 'open'], capture_output=True).returncode == 0:  # macOS
                    subprocess.run(['open', str(folder_path)], check=True)
                else:  # Linux
                    subprocess.run(['xdg-open', str(folder_path)], check=True)
            else:
                print(f"Unsupported OS: {os.name}")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error opening folder: {e}")
            return False
    
    def get_statistics(self):
        """Get storage and subscription statistics"""
        try:
            subscribed = self.get_subscribed_wallpapers()
            unsubscribed = self.get_unsubscribed_wallpapers()
            
            subscribed_count = len(subscribed)
            subscribed_size = sum(wp['size'] for wp in subscribed)
            
            unsubscribed_count = len(unsubscribed)
            unsubscribed_size = sum(wp['size'] for wp in unsubscribed)
            
            total_count = subscribed_count + unsubscribed_count
            total_size = subscribed_size + unsubscribed_size
            
            return {
                'total': {
                    'count': total_count,
                    'size': total_size,
                    'size_formatted': self._format_size(total_size)
                },
                'subscribed': {
                    'count': subscribed_count,
                    'size': subscribed_size,
                    'size_formatted': self._format_size(subscribed_size)
                },
                'unsubscribed': {
                    'count': unsubscribed_count,
                    'size': unsubscribed_size,
                    'size_formatted': self._format_size(unsubscribed_size)
                }
            }
            
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {
                'total': {'count': 0, 'size': 0, 'size_formatted': '0 B'},
                'subscribed': {'count': 0, 'size': 0, 'size_formatted': '0 B'},
                'unsubscribed': {'count': 0, 'size': 0, 'size_formatted': '0 B'}
            }
    
    def _get_wallpaper_info(self, wallpaper_id, folder_path):
        """Get wallpaper information"""
        # Get title from project.json
        title = self._get_wallpaper_title(folder_path)
        
        # Get folder size
        size = self._get_folder_size(folder_path)
        
        # Get preview info
        preview_path, preview_type = self.image_processor.find_preview_file(folder_path)
        
        return {
            'id': wallpaper_id,
            'title': title,
            'size': size,
            'size_formatted': self._format_size(size),
            'path': str(folder_path),
            'preview_available': preview_path is not None,
            'preview_type': preview_type
        }
    
    def _get_wallpaper_title(self, folder_path):
        """Get wallpaper title from project.json"""
        project_file = folder_path / "project.json"
        if project_file.exists():
            try:
                with open(project_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data.get('title', f'ID: {folder_path.name}')
            except:
                pass
        return f'ID: {folder_path.name}'
    
    def _get_folder_size(self, folder_path):
        """Get total size of folder"""
        try:
            return sum(f.stat().st_size for f in folder_path.rglob('*') if f.is_file())
        except:
            return 0
    
    def _format_size(self, size_bytes):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} PB"
