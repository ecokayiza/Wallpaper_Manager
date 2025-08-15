#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wallpaper Engine Web Manager 启动脚本
"""

import sys
import subprocess
from pathlib import Path


def check_dependencies():
    """检查必要的依赖包"""
    required_packages = ['flask', 'vdf', 'PIL']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            else:
                __import__(package)
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} (缺失)")
    
    return missing_packages


def install_dependencies():
    """安装缺失的依赖包"""
    print("\n正在安装依赖包...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Flask', 'vdf', 'Pillow'])
        print("✓ 依赖包安装完成")
        return True
    except subprocess.CalledProcessError:
        print("✗ 依赖包安装失败")
        return False


def main():
    """主函数"""
    print("=" * 50)
    print("🎨 Wallpaper Engine Web Manager")
    print("🌐 Flask Web版本")
    print("=" * 50)
    
    # 检查依赖
    print("\n📦 检查依赖包...")
    missing = check_dependencies()
    
    if missing:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing)}")
        response = input("是否自动安装? (y/n): ").lower().strip()
        
        if response == 'y':
            if not install_dependencies():
                print("\n❌ 无法安装依赖包，程序退出")
                input("按Enter键退出...")
                return 1
        else:
            print("\n❌ 依赖包未安装，程序退出")
            input("按Enter键退出...")
            return 1
    
    # 检查配置文件
    config_file = Path('config.json')
    if not config_file.exists():
        print("\n⚙️  创建默认配置文件...")
        default_config = {
            "steam_library_path": "F:\\SteamLibrary",
            "workshop_file": "",
            "content_path": "",
            "server": {
                "host": "127.0.0.1",
                "port": 5000,
                "debug": True
            },
            "preview": {
                "max_width": 300,
                "max_height": 200,
                "quality": 85
            }
        }
        
        try:
            import json
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            print("✓ 配置文件创建完成")
        except Exception as e:
            print(f"✗ 配置文件创建失败: {e}")
    
    # 启动Flask应用
    print("\n🚀 启动Web服务器...")
    print("📍 地址: http://127.0.0.1:5000")
    print("🔧 调试模式: 开启")
    print("\n按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        # 导入并运行Flask应用
        from app import main as run_app
        return run_app()
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
        return 0
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("\n请检查以下问题:")
        print("1. 是否正确安装了所有依赖包")
        print("2. 是否配置了正确的Steam库路径")
        print("3. 是否有文件权限问题")
        input("\n按Enter键退出...")
        return 1

if __name__ == '__main__':
    sys.exit(main())
