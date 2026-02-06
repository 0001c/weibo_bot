import os
import json
import subprocess
import sys
import time

# 配置文件路径
CONFIG_FILE = 'config.json'
ENV_FILE = '.env'
REQUIREMENTS_FILE = 'requirements.txt'

# 安装依赖项
def install_dependencies():
    """
    安装依赖项
    """
    print('正在检查依赖项...')
    
    # 检查requirements.txt文件是否存在
    if not os.path.exists(REQUIREMENTS_FILE):
        print(f'警告：{REQUIREMENTS_FILE} 文件不存在，跳过依赖项安装')
        return
    
    try:
        # 安装依赖项
        print('正在安装依赖项...')
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', REQUIREMENTS_FILE],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print('依赖项安装成功')
    except subprocess.CalledProcessError as e:
        print(f'错误：安装依赖项时发生错误：{e.stderr}')
        print('请手动安装依赖项后重试')
    except Exception as e:
        print(f'错误：检查依赖项时发生错误：{e}')

# 检查配置文件是否存在且有效
def check_config():
    """
    检查配置文件是否存在且有效
    
    Returns:
        bool: 配置是否有效
    """
    # 检查config.json文件
    if not os.path.exists(CONFIG_FILE):
        print(f'错误：{CONFIG_FILE} 文件不存在')
        return False
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查uid字典是否存在且非空
        if 'uid' not in config or not isinstance(config['uid'], dict) or len(config['uid']) == 0:
            print('错误：config.json 文件中缺少有效的 uid 字典')
            return False
        
        # 检查每个uid是否为非空字符串，值是否为"1"
        for uid, value in config['uid'].items():
            if not isinstance(uid, str) or not uid.strip():
                print('错误：config.json 文件中的 uid 必须是非空字符串')
                return False
            if value != "1" and value != "0":
                print('错误：config.json 文件中的 uid 值必须为"1"或"0"')
                return False
                
    except json.JSONDecodeError as e:
        print(f'错误：{CONFIG_FILE} 文件格式错误：{e}')
        return False
    except Exception as e:
        print(f'错误：检查 {CONFIG_FILE} 文件时发生错误：{e}')
        return False
    
    # 检查.env文件
    if not os.path.exists(ENV_FILE):
        print(f'错误：{ENV_FILE} 文件不存在')
        return False
    
    try:
        with open(ENV_FILE, 'r', encoding='utf-8') as f:
            env_vars = {}
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        
        # 检查ARK_API_KEY是否存在且非空
        if 'ARK_API_KEY' not in env_vars or not env_vars['ARK_API_KEY'].strip():
            print('错误：.env 文件中缺少有效的 ARK_API_KEY')
            return False
            
    except Exception as e:
        print(f'错误：检查 {ENV_FILE} 文件时发生错误：{e}')
        return False
    
    return True

# 启动配置服务器
def start_config_server():
    """
    启动配置服务器让用户配置
    """
    print('正在启动配置服务器...')
    print('请在浏览器中完成配置')
    print('配置服务器将保持运行，您可以随时修改配置并重启爬虫')
    
    # 启动配置服务器
    config_server_process = subprocess.Popen([sys.executable, 'config_server.py'])
    
    # 不等待用户输入，让配置服务器一直运行
    print('配置服务器已启动，您可以通过配置页面上的按钮启动或重启爬虫')
    
    # 注意：这里不再停止配置服务器，它会一直运行直到用户手动关闭

# 运行爬虫脚本
# def run_spider():
#     """
#     运行爬虫脚本
#     """
#     print('正在启动爬虫脚本...')
#     subprocess.run([sys.executable, 'spider.py'])

# 主函数
def main():
    """
    主函数
    """
    print('=== 启动脚本 ===')
    
    # 安装依赖项
    # install_dependencies()
    
    # 检查配置
    if check_config():
        print('配置文件检查通过，正在启动...')
        print('配置服务器默认地址：http://localhost:18002')
        start_config_server()
    else:
        print('配置文件无效，需要进行配置')
        start_config_server()
        print('\n提示：')
        print('1. 配置服务器已启动，您可以在浏览器中进行配置')
        print('2. 配置完成后，点击"启动爬虫"按钮启动爬虫服务')
        print('3. 后续如需修改配置，可直接访问配置页面进行修改并重启爬虫')
        print('4. 配置服务器默认地址：http://localhost:18002')

if __name__ == '__main__':
    main()
