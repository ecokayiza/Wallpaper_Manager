# Wallpaper Engine Web Manager

A web-based interface for managing Wallpaper Engine subscriptions using Flask backend and responsive frontend.

这是一个本地开发版本，使用需要手动配置python环境
请检查 `wallpaper manager.bat`

![demo](static/img/demo.png)

---

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your Steam library path in `config.json` or in the web interface.

3. Run the development server:
```bash
python app.py
```

4. Open your browser to `http://localhost:5000`

## Config
启动网页后请点击`配置`按钮检查相应路径配置，你也可以查看`config.json`文件。
After you successfully run the web, please check the `config button`.
you can also check the local `config.json` file.

订阅数据通过steam客户端下的`userdata`文件夹获取
the subscription data is obtained from the `userdata` folder under the steam client.

## Project Structure

```
manager web/
├── app.py                 # Flask application entry point
├── config.json           # Configuration file
├── requirements.txt      # Python dependencies
├── static/               # Static assets (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   └── components/
├── api/                  # Backend API modules
│   ├── __init__.py
│   ├── wallpaper.py
│   └── config.py
└── utils/                # Utility functions
    ├── __init__.py
    ├── steam_parser.py
    └── image_processor.py
```
