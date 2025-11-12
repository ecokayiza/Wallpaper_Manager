# -*- coding: utf-8 -*-
"""
Wallpaper Manager Launcher
Auto-starts Flask server and opens browser
"""

import threading
import time
import webbrowser
import sys
import os

# Import the Flask app
from app import create_app

def open_browser(url='http://127.0.0.1:5000', delay=2):
    """Open browser after a delay"""
    time.sleep(delay)
    try:
        print(f"🌐 Opening browser: {url}")
        webbrowser.open(url)
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print(f"📍 Please open manually: {url}")

def main():
    """Main launcher function"""
    print("=" * 60)
    print("🎨 Wallpaper Engine Web Manager")
    print("=" * 60)
    
    # Get configuration
    try:
        import json
        from pathlib import Path
        
        config_path = Path('config.json')
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            host = config.get('server', {}).get('host', '127.0.0.1')
            port = config.get('server', {}).get('port', 5000)
        else:
            host = '127.0.0.1'
            port = 5000
    except Exception as e:
        print(f"⚠️  Could not load config: {e}")
        host = '127.0.0.1'
        port = 5000
    
    url = f"http://{host}:{port}"
    
    print(f"\n🚀 Starting server on {url}")
    print(f"💡 Browser will open automatically in 2 seconds...")
    print(f"⚠️  Press Ctrl+C to stop the server\n")
    
    # Create Flask app
    app = create_app()
    
    # Start browser opener in background thread
    browser_thread = threading.Thread(target=open_browser, args=(url, 2), daemon=True)
    browser_thread.start()
    
    # Start Flask server
    try:
        app.run(host=host, port=port, debug=False, threaded=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == '__main__':
    main()
