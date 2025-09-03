# -*- coding: utf-8 -*-
"""
Wallpaper Engine Web Manager
Flask web application for managing Wallpaper Engine subscriptions
"""

import json
import os
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_file
from api.wallpaper import WallpaperAPI
from api.config import ConfigAPI


def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    config_path = Path('config.json')
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        app.config.update(config)
    else:
        # Default configuration
        app.config.update({
            'steam_library_path': 'F:\\SteamLibrary\\steamapps',
            'server': {
                'host': '127.0.0.1',
                'port': 5000,
                'debug': True
            }
        })
    
    # Initialize APIs
    wallpaper_api = WallpaperAPI(app.config)
    config_api = ConfigAPI(app.config)
    
    @app.route('/')
    def index():
        """Main page"""
        return render_template('index.html')
    
    @app.route('/config-test')
    def config_test():
        """Configuration test page"""
        return render_template('config_test.html')
    
    @app.route('/api/wallpapers')
    def get_wallpapers():
        """Get wallpapers with pagination"""
        try:
            user_filter = request.args.get('user', None)
            search_query = request.args.get('search', None)
            page = int(request.args.get('page', 1))
            page_size = int(request.args.get('page_size', 20))

            if user_filter and user_filter != 'all':
                # 用户过滤也做分页处理
                subscribed = wallpaper_api.get_wallpapers_by_user(user_filter, subscribed_only=True)
                unsubscribed = wallpaper_api.get_wallpapers_by_user(user_filter, subscribed_only=False)
                # 搜索和分页顺序：先搜索再分页
                if search_query and search_query.strip():
                    search_term = search_query.strip().lower()
                    def matches_search(wallpaper):
                        title_match = search_term in wallpaper.get('title', '').lower()
                        return title_match
                    subscribed = [w for w in subscribed if matches_search(w)]
                    unsubscribed = [w for w in unsubscribed if matches_search(w)]
                # 分页切片
                start = (page - 1) * page_size
                end = start + page_size
                subscribed_page = subscribed[start:end]
                unsubscribed_page = unsubscribed[start:end]
                return jsonify({
                    'success': True,
                    'data': {
                        'subscribed': {
                            'total': len(subscribed),
                            'page': page,
                            'page_size': page_size,
                            'wallpapers': subscribed_page
                        },
                        'unsubscribed': {
                            'total': len(unsubscribed),
                            'page': page,
                            'page_size': page_size,
                            'wallpapers': unsubscribed_page
                        }
                    }
                })
            else:
                # 分页获取所有壁纸，搜索和分页顺序：先搜索再分页
                all_subscribed = wallpaper_api.get_subscribed_wallpapers()
                all_unsubscribed = wallpaper_api.get_unsubscribed_wallpapers()
                if search_query and search_query.strip():
                    search_term = search_query.strip().lower()
                    def matches_search(wallpaper):
                        title_match = search_term in wallpaper.get('title', '').lower()
                        return title_match
                    all_subscribed = [w for w in all_subscribed if matches_search(w)]
                    all_unsubscribed = [w for w in all_unsubscribed if matches_search(w)]
                # 分页切片
                start = (page - 1) * page_size
                end = start + page_size
                subscribed_page = all_subscribed[start:end]
                unsubscribed_page = all_unsubscribed[start:end]
                subscribed_result = {
                    'total': len(all_subscribed),
                    'page': page,
                    'page_size': page_size,
                    'wallpapers': subscribed_page
                }
                unsubscribed_result = {
                    'total': len(all_unsubscribed),
                    'page': page,
                    'page_size': page_size,
                    'wallpapers': unsubscribed_page
                }
                return jsonify({
                    'success': True,
                    'data': {
                        'subscribed': subscribed_result,
                        'unsubscribed': unsubscribed_result
                    }
                })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/wallpapers/<wallpaper_id>')
    def get_wallpaper(wallpaper_id):
        """Get specific wallpaper details"""
        try:
            wallpaper = wallpaper_api.get_wallpaper_details(wallpaper_id)
            if wallpaper:
                return jsonify({
                    'success': True,
                    'data': wallpaper
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Wallpaper not found'
                }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/wallpapers/<wallpaper_id>/preview')
    def get_wallpaper_preview(wallpaper_id):
        """Get wallpaper preview image"""
        try:
            preview_path = wallpaper_api.get_preview_image(wallpaper_id)
            if preview_path and os.path.exists(preview_path):
                return send_file(preview_path)
            else:
                # Return placeholder image
                placeholder_path = Path('static/images/no-preview.png')
                if placeholder_path.exists():
                    return send_file(placeholder_path)
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Preview not available'
                    }), 404
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/wallpapers/<wallpaper_id>', methods=['DELETE'])
    def delete_wallpaper(wallpaper_id):
        """Delete a wallpaper"""
        try:
            success = wallpaper_api.delete_wallpaper(wallpaper_id)
            return jsonify({
                'success': success,
                'message': 'Wallpaper deleted successfully' if success else 'Failed to delete wallpaper'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/wallpapers/<wallpaper_id>/open-folder', methods=['POST'])
    def open_wallpaper_folder(wallpaper_id):
        """Open wallpaper folder in file explorer"""
        try:
            success = wallpaper_api.open_wallpaper_folder(wallpaper_id)
            return jsonify({
                'success': success,
                'message': 'Folder opened successfully' if success else 'Failed to open folder'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/config')
    def get_config():
        """Get current configuration"""
        try:
            return jsonify({
                'success': True,
                'data': config_api.get_config()
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/config', methods=['POST'])
    def update_config():
        """Update configuration"""
        try:
            new_config = request.get_json()
            if not new_config:
                return jsonify({
                    'success': False,
                    'error': '请求数据为空'
                }), 400
            
            success = config_api.update_config(new_config)
            if success:
                return jsonify({
                    'success': True,
                    'message': '配置保存成功'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': '配置保存失败'
                }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/stats')
    def get_stats():
        """Get storage and subscription statistics"""
        try:
            user_id = request.args.get('user', None)
            stats = wallpaper_api.get_statistics(user_id)
            return jsonify({
                'success': True,
                'data': stats
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/users')
    def get_users():
        """Get all Steam users with their subscription info"""
        try:
            from utils.steam_parser import SteamParser
            parser = SteamParser(app.config)
            
            # Get all subscription data
            all_data = parser.get_all_subscription_data()
            users = []
            
            for user_id, user_subscriptions in all_data.items():
                active_subscriptions = [item_id for item_id, details in user_subscriptions.items() 
                                      if details['is_active']]
                users.append({
                    'id': user_id,
                    'display_name': f"用户 {user_id}",
                    'subscription_count': len(active_subscriptions)
                })
            
            return jsonify({
                'success': True,
                'data': users
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/steam-paths')
    def get_steam_paths():
        """Get current Steam paths being used by the system"""
        try:
            from utils.steam_parser import SteamParser
            from api.config import ConfigAPI
            
            # Get configuration
            config_api = ConfigAPI(app.config)
            config_data = config_api.get_config()
            configured_userdata = config_data.get('steam_userdata_path', '') if config_data else ''
            
            # Initialize parser with current config
            parser = SteamParser(app.config)
            
            # Get the actual paths being used
            userdata_path = parser.get_steam_user_data_path()
            content_path = parser.get_content_path()
            
            # Check if we're using fallback
            using_fallback = False
            if configured_userdata and configured_userdata.strip():
                # If a path is configured, check if it's different from what's actually used
                actual_path_str = str(userdata_path) if userdata_path else ''
                using_fallback = configured_userdata.strip() != actual_path_str
            
            return jsonify({
                'success': True,
                'data': {
                    'configured_userdata_path': configured_userdata if configured_userdata else None,
                    'actual_userdata_path': str(userdata_path) if userdata_path else None,
                    'content_path': str(content_path),
                    'using_fallback': using_fallback
                }
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    return app


def main():
    """Main function"""
    app = create_app()
    
    # Get server configuration
    server_config = app.config.get('server', {})
    host = server_config.get('host', '127.0.0.1')
    port = server_config.get('port', 5000)
    debug = server_config.get('debug', True)
    
    print("🚀 Starting Wallpaper Engine Web Manager...")
    print(f"📍 Server: http://{host}:{port}")
    print(f"🔧 Debug mode: {'On' if debug else 'Off'}")
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")


if __name__ == '__main__':
    main()
