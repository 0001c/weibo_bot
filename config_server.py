import http.server
import socketserver
import json
import os
import webbrowser
from urllib.parse import parse_qs, urlparse
import time
import threading

# 模板文件路径
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
# 静态文件路径
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
print(f"STATIC_DIR: {STATIC_DIR}")
print(f"TEMPLATE_DIR: {TEMPLATE_DIR}")

# 从log_manager.py导入日志相关的函数
from log_manager import add_log, get_all_logs, get_new_logs, clear_logs

# 配置文件路径
CONFIG_FILE = 'Config/config.json'
ENV_FILE = 'Config/.env'
COOKIE_FILE = 'Config/weibo_cookie.json'

# 读取模板文件
def read_template(template_name):
    """
    读取HTML模板文件
    
    Args:
        template_name: 模板文件名
        
    Returns:
        str: 模板文件内容
    """
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

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
            for uid, enabled in config.get('uid', {}).items():
                checked = 'checked' if enabled == '1' else ''
                uid_list_html += f'''
                <div class="uid-item">
                    <input type="checkbox" class="uid-enabled" data-uid="{uid}" {checked}>
                    <input type="text" value="{uid}" placeholder="请输入用户ID">
                    <button type="button" onclick="removeUid(this)">删除</button>
                </div>
                '''
            if not uid_list_html:
                uid_list_html = f'''
                <div class="uid-item">
                    <input type="checkbox" class="uid-enabled" checked>
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
            
            # 读取HTML模板文件
            template_content = read_template('config.html')
            
            # 替换模板中的占位符
            html = template_content.replace('{{uid_list_html}}', uid_list_html)
            html = html.replace('{{ark_api_key}}', ark_api_key)
            html = html.replace('{{cookie}}', cookie)
            html = html.replace('{{user_agent}}', user_agent)
            html = html.replace('{{prompt}}', prompt)
            html = html.replace('{{sleep_time}}', str(sleep_time))
            
            self.wfile.write(html.encode('utf-8'))
        
        elif path == '/logs':
            # 提供日志页面
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # 读取HTML模板文件
            template_content = read_template('logs.html')
            
            self.wfile.write(template_content.encode('utf-8'))
        
        elif path == '/api/logs':
            # 提供日志数据
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # 获取日志
            logs = get_all_logs()
            
            # 返回日志数据
            self.wfile.write(json.dumps({
                'success': True,
                'logs': logs
            }).encode('utf-8'))
        
        elif path.startswith('/static/'):
            # 提供静态文件
            try:
                # 获取静态文件相对路径
                relative_path = path[7:]
                # 构建静态文件路径
                static_file_path = os.path.join(STATIC_DIR, *relative_path.split('/'))
                
                # 检查文件是否存在
                if os.path.exists(static_file_path) and os.path.isfile(static_file_path):
                    # 根据文件扩展名设置Content-type
                    if static_file_path.endswith('.css'):
                        content_type = 'text/css'
                    elif static_file_path.endswith('.js'):
                        content_type = 'application/javascript'
                    else:
                        content_type = 'application/octet-stream'
                    
                    # 读取并返回文件内容
                    self.send_response(200)
                    self.send_header('Content-type', content_type)
                    self.end_headers()
                    
                    with open(static_file_path, 'rb') as f:
                        self.wfile.write(f.read())
                else:
                    # 文件不存在
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(f'Not Found: {static_file_path}\nRelative path: {relative_path}'.encode('utf-8'))
            except Exception as e:
                # 发生错误
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f'Internal Server Error: {str(e)}\nSTATIC_DIR: {STATIC_DIR}'.encode('utf-8'))
        
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
                add_log('INFO', '配置文件已更新。')
                
            except Exception as e:
                # 返回错误响应
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': f'保存失败：{str(e)}'
                }).encode('utf-8'))
                add_log('ERROR', f'保存配置文件时出错：{str(e)}')
        
        elif path == '/start-spider':
            try:
                global spider_running
                
                # 启动爬虫子进程（输出重定向到日志文件，避免管道阻塞）
                restart_spider()
                
                message = '重启' if spider_running else '启动'
                # 返回成功响应
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'message': message + '成功！',
                }).encode('utf-8'))
                add_log('INFO', message + '爬虫启动成功！')

                
            except Exception as e:
                # 返回错误响应
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': f'{message}爬虫失败：{str(e)}'
                }).encode('utf-8'))
                add_log('ERROR', f'{message}爬虫失败：{str(e)}')
        
        elif path == '/api/logs/clear':
            # 清空日志
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # 清空日志文件
            clear_logs()
            
            # 返回成功响应
            self.wfile.write(json.dumps({
                'success': True,
                'message': '日志清空成功！'
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
    # 添加日志记录
    add_log('INFO', f"配置服务已启动：http://localhost:{PORT}")
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

def restart_spider():
    """
    重启爬虫服务
    """

    global spider_running,spider_thread
    # 初始化爬虫线程
    spider_thread = None
    if spider_thread is None:
        spider_thread = threading.Thread(target=start_spider,daemon=True)   
        spider_thread.start()
    else:
        if spider_thread is not None and spider_thread.is_alive():
            print('正在等待爬虫线程结束...')
            add_log('INFO','正在等待爬虫线程结束...')
            spider_running = False\
                and spider_thread.join(timeout=10)
                
            if spider_thread.is_alive():
                print('等待超时，强制终止爬虫线程')
                add_log('WARNING','等待超时，强制终止爬虫线程')
                spider_thread.terminate()
        
        print('重启新爬虫线程')
        add_log('INFO','重启新爬虫线程')
        spider_thread = threading.Thread(target=start_spider,daemon=True)   
        spider_thread.start()

def start_spider():
    """
    启动爬虫服务
    """
    global spider_running
    spider_running = True
    while spider_running:
        try:
            import spider
            spider.main()
        except Exception as e:
            add_log('ERROR',f'爬虫运行出错：{e}')
            print(f'爬虫运行出错：{e}')
            time.sleep(5)  # 出错后等待5秒后重试
        
if __name__ == "__main__":
    start_config_server()
