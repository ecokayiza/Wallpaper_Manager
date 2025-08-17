import subprocess, time, webbrowser, os, sys 
 
# 启动Flask服务器 
flask_process = subprocess.Popen([sys.executable, 'app.py']) 
 
# 等待服务器启动 
time.sleep(3) 
 
# 打开浏览器 
webbrowser.open('http://127.0.0.1:5000') 
 
# 等待Flask进程结束 
try: 
    flask_process.wait() 
except KeyboardInterrupt: 
    flask_process.terminate() 
    flask_process.wait() 
 
# 清理临时文件 
if os.path.exists('temp_launcher.py'): 
    os.remove('temp_launcher.py') 
