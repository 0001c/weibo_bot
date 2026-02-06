import http.server
import socketserver
import json
import os
import webbrowser
from urllib.parse import parse_qs, urlparse
import time

# 配置文件路径
CONFIG_FILE = 'config.json'
ENV_FILE = '.env'
COOKIE_FILE = 'weibo_cookie.json'

# 读取配置文件
def read_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'uid': {}}

# 读取.env文件
def read_env():
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'r', encoding='utf-8') as f:
            env_vars = {}
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
            return env_vars
    return {}

# 保存配置文件
def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# 保存.env文件
def save_env(env_vars):
    with open(ENV_FILE, 'w', encoding='utf-8') as f:
        for key, value in env_vars.items():
            f.write(f'{key}={value}\n')

# 读取cookie文件
def read_cookie():
    """
    读取cookie文件
    
    Returns:
        dict: cookie信息
    """
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {'Cookie': '', 'User-Agent': ''}
    return {'Cookie': '', 'User-Agent': ''}

# 保存cookie文件
def save_cookie(cookie_data):
    """
    保存cookie文件
    
    Args:
        cookie_data: cookie信息
    """
    with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cookie_data, f, ensure_ascii=False, indent=2)

# 自定义HTTP请求处理器
class ConfigHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            # 提供配置页面
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            config = read_config()
            env_vars = read_env()
            
            # 生成用户ID列表HTML
            uid_list_html = ''
            for uid in config.get('uid', {}).keys():
                uid_list_html += f'''
                <div class="uid-item">
                    <input type="text" value="{uid}" placeholder="请输入用户ID">
                    <button type="button" onclick="removeUid(this)">删除</button>
                </div>
                '''
            if not uid_list_html:
                uid_list_html = f'''
                <div class="uid-item">
                    <input type="text" placeholder="请输入用户ID">
                    <button type="button" onclick="removeUid(this)">删除</button>
                </div>
                '''
            
            # 获取API Key
            try:
                ark_api_key = read_env().get('ARK_API_KEY', '')
            except:
                ark_api_key = ''
            
            # 获取cookie信息
            cookie_data = read_cookie()
            try:
                cookie = cookie_data.get('Cookie', '')
                user_agent = cookie_data.get('User-Agent', '')
            except:
                cookie = ''
                user_agent = ''
            
            # 获取其他配置
            try:
                prompt = config.get('prompt', '')
                sleep_time = config.get('sleep_time', 10)
            except:
                prompt = ''
                sleep_time = 10
            
            # 生成HTML内容
            html = '''
            <!DOCTYPE html>
            <html lang="zh-CN">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>数据配置</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 20px;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }
                    .container {
                        max-width: 800px;
                        margin: 0 auto;
                        background-color: white;
                        padding: 30px;
                        border-radius: 8px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }
                    h1 {
                        color: #333;
                        text-align: center;
                    }
                    h2 {
                        color: #555;
                        margin-top: 30px;
                        margin-bottom: 15px;
                    }
                    .form-group {
                        margin-bottom: 20px;
                    }
                    label {
                        display: block;
                        margin-bottom: 5px;
                        font-weight: bold;
                        color: #666;
                    }
                    input[type="text"] {
                        width: 100%;
                        padding: 10px;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        font-size: 14px;
                    }
                    textarea {
                        width: 100%;
                        padding: 10px;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        font-size: 14px;
                        resize: vertical;
                        min-height: 100px;
                    }
                    .uid-list {
                        margin-bottom: 10px;
                    }
                    .uid-item {
                        display: flex;
                        margin-bottom: 10px;
                        align-items: center;
                    }
                    .uid-item input {
                        flex: 1;
                        margin-right: 10px;
                    }
                    .uid-item button {
                        background-color: #dc3545;
                        color: white;
                        border: none;
                        padding: 6px 12px;
                        border-radius: 4px;
                        cursor: pointer;
                    }
                    .uid-item button:hover {
                        background-color: #c82333;
                    }
                    button {
                        background-color: #007bff;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 14px;
                    }
                    button:hover {
                        background-color: #0069d9;
                    }
                    button#add-uid {
                        background-color: #28a745;
                    }
                    button#add-uid:hover {
                        background-color: #218838;
                    }
                    .status {
                        margin-top: 20px;
                        padding: 10px;
                        border-radius: 4px;
                        text-align: center;
                    }
                    .success {
                        background-color: #d4edda;
                        color: #155724;
                        border: 1px solid #c3e6cb;
                    }
                    .error {
                        background-color: #f8d7da;
                        color: #721c24;
                        border: 1px solid #f5c6cb;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>微博爬虫配置</h1>
                    
                    <div id="status"></div>
                    
                    <h2>1. 微博用户ID配置</h2>
                    <div class="form-group">
                        <label>用户ID列表</label>
                        <div class="uid-list" id="uid-list">
                    ''' + uid_list_html + '''
                        </div>
                        <button id="add-uid">添加用户ID</button>
                    </div>
                    
                    <h2>2. API密钥配置</h2>
                    <div class="form-group">
                        <label for="ark-api-key">豆包 API Key</label>
                        <input type="text" id="ark-api-key" value="''' + ark_api_key + '''" placeholder="请输入豆包 API Key">
                    </div>
                    
                    <h2>3. Cookie配置</h2>
                    <div class="form-group">
                        <label for="cookie">Cookie</label>
                        <textarea id="cookie" placeholder="请输入微博Cookie">''' + cookie + '''</textarea>
                    </div>
                    <div class="form-group">
                        <label for="user-agent">User-Agent</label>
                        <input type="text" id="user-agent" value="''' + user_agent + '''" placeholder="请输入User-Agent">
                    </div>
                    
                    <h2>4. 其他配置</h2>
                    <div class="form-group">
                        <label for="prompt">Prompt</label>
                        <textarea id="prompt" placeholder="请输入微博回复提示文本">''' + prompt + '''</textarea>
                    </div>
                    <div class="form-group">
                        <label for="sleep-time">Sleep Time</label>
                        <input type="number" id="sleep-time" value="''' + str(sleep_time) + '''" placeholder="请输入爬虫休眠时间（秒）">
                    </div>
                    
                    <button id="save-config">保存配置</button>
                    <button id="start-spider" style="margin-left: 10px;">启动爬虫</button>
                </div>
                
                <script>
                    // 添加用户ID输入框
                    document.getElementById('add-uid').addEventListener('click', function() {
                        const uidList = document.getElementById('uid-list');
                        const uidItem = document.createElement('div');
                        uidItem.className = 'uid-item';
                        uidItem.innerHTML = `
                            <input type="text" placeholder="请输入用户ID">
                            <button type="button" onclick="removeUid(this)">删除</button>
                        `;
                        uidList.appendChild(uidItem);
                    });
                    
                    // 删除用户ID输入框
                    function removeUid(button) {
                        const uidItem = button.parentElement;
                        uidItem.remove();
                    }
                    
                    // 保存配置
                    function saveConfig() {
                        // 收集用户ID
                        const uidInputs = document.querySelectorAll('.uid-item input');
                        // 收集API Key
                        const arkApiKey = document.getElementById('ark-api-key').value.trim();
                        // 收集Prompt和Sleep Time
                        const prompt = document.getElementById('prompt').value.trim();
                        const sleepTime = document.getElementById('sleep-time').value.trim();

                        const uidDict = {};
                        uidInputs.forEach(input => {
                            const uid = input.value.trim();
                            
                            if (uid) uidDict[uid] = "1";
                        });
                        
                        const cookie = document.getElementById('cookie').value.trim();
                        const userAgent = document.getElementById('user-agent').value.trim();
                        
                        // 构建配置数据
                        const configData = {
                            uid: uidDict,
                            prompt: prompt,
                            sleep_time: sleepTime ? parseInt(sleepTime) : 10,
                            env: {
                                'ARK_API_KEY': arkApiKey
                            },
                            cookie: {
                                'Cookie': cookie,
                                'User-Agent': userAgent
                            }
                        };
                        
                        return fetch('/save', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(configData)
                        })
                        .then(response => response.json());
                    }

                    // 保存配置按钮点击事件
                    document.getElementById('save-config').addEventListener('click', function() {
                        saveConfig()
                        .then(data => {
                            const status = document.getElementById('status');
                            status.className = data.success ? 'status success' : 'status error';
                            status.textContent = data.message;
                            
                            // 3秒后清空状态
                            setTimeout(() => {
                                status.textContent = '';
                                status.className = '';
                            }, 3000);
                        })
                        .catch(error => {
                            const status = document.getElementById('status');
                            status.className = 'status error';
                            status.textContent = '保存失败：' + error.message;
                        });
                    });

                    // 启动爬虫按钮点击事件
                    document.getElementById('start-spider').addEventListener('click', function() {
                        saveConfig()
                        .then(data => {
                            if (data.success) {
                                // 保存成功后启动爬虫
                                fetch('/start-spider', {
                                    method: 'POST'
                                })
                                .then(response => response.json())
                                .then(data => {
                                    const status = document.getElementById('status');
                                    status.className = data.success ? 'status success' : 'status error';
                                    status.textContent = data.message;
                                    
                                    
                                })
                                .catch(error => {
                                    const status = document.getElementById('status');
                                    status.className = 'status error';
                                    status.textContent = '启动爬虫失败：' + error.message;
                                });
                            } else {
                                const status = document.getElementById('status');
                                status.className = 'status error';
                                status.textContent = '保存配置失败，无法启动爬虫';
                            }
                        })
                        .catch(error => {
                            const status = document.getElementById('status');
                            status.className = 'status error';
                            status.textContent = '保存配置失败：' + error.message;
                        });
                    });
                </script>
            </body>
            </html>
            '''
            
            self.wfile.write(html.encode('utf-8'))
        
        else:
            # 404错误
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/save':
            # 读取请求体
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                # 解析JSON数据
                config_data = json.loads(post_data)
                
                # 保存配置文件
                save_config({
                    'uid': config_data.get('uid', {}),
                    'prompt': config_data.get('prompt', ''),
                    'sleep_time': config_data.get('sleep_time', 10)
                })
                
                # 保存.env文件
                save_env(config_data.get('env', {}))
                
                # 保存cookie文件
                save_cookie(config_data.get('cookie', {}))
                
                # 返回成功响应
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'message': '配置保存成功！点击启动爬虫按钮开始运行。'
                }).encode('utf-8'))
                
            except Exception as e:
                # 返回错误响应
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': f'保存失败：{str(e)}'
                }).encode('utf-8'))
        
        elif path == '/start-spider':
            try:
                # 重启爬虫服务
                import subprocess
                import sys
                import os
                import psutil
                running = False
                # 检查是否有爬虫进程在运行
                spider_processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                            cmdline = proc.info['cmdline']
                            if cmdline and 'spider.py' in ' '.join(cmdline):
                                spider_processes.append(proc)
                    except:
                        pass
                
                # 终止现有的爬虫进程
                for proc in spider_processes:
                    try:
                        proc.terminate()  # 发送SIGTERM信号
                        proc.wait(timeout=5)
                        print(f'已终止爬虫进程 {proc.pid}')
                    except:
                        try:
                            proc.kill()
                        except:
                            pass

                # time.sleep(10)  # 等待3秒，确保进程完全终止
                # 启动爬虫子进程（输出重定向到日志文件，避免管道阻塞）
                spider_process = subprocess.Popen(
                    [sys.executable, 'spider.py'],
                    cwd=os.getcwd(),
                    # 输出写入日志文件，而非PIPE（关键：避免子进程阻塞）
                    # stdout=open('spider_stdout.log', 'a', encoding='utf-8'),
                    # stderr=open('spider_stderr.log', 'a', encoding='utf-8'),
                )
                
                message = '重启' if running else '启动'
                # 返回成功响应
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'message': message + '成功！',
                    'spider_pid': spider_process.pid
                }).encode('utf-8'))

                
            except Exception as e:
                # 返回错误响应
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': f'{message}爬虫失败：{str(e)}'
                }).encode('utf-8'))
        
        else:
            # 404错误
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

def start_config_server():
    """
    启动配置服务器
    """
    global httpd
    PORT = 18002
    
    # 创建服务器
    httpd = socketserver.TCPServer(("", PORT), ConfigHandler)
    print(f"配置服务器已启动：http://localhost:{PORT}")
    print("请在浏览器中打开上述链接进行配置")
    print("添加UID后，点击保存配置按钮即可")
    print("配置完成后直接关闭即可")
    try:
        # 自动打开浏览器
        webbrowser.open(f"http://localhost:{PORT}")
    except:
        pass
    
    try:
        # 启动服务器
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n配置服务器已停止")
    finally:
        httpd.server_close()

if __name__ == "__main__":
    start_config_server()
