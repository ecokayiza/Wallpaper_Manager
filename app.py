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
            'steam_library_path': 'F:\\SteamLibrary',
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
        """Get all wallpapers"""
        try:
            subscribed = wallpaper_api.get_subscribed_wallpapers()
            unsubscribed = wallpaper_api.get_unsubscribed_wallpapers()
            
            return jsonify({
                'success': True,
                'data': {
                    'subscribed': subscribed,
                    'unsubscribed': unsubscribed
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
            stats = wallpaper_api.get_statistics()
            return jsonify({
                'success': True,
                'data': stats
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
