import os
import json
import subprocess
import sys
import time

# 配置文件路径
CONFIG_FILE = 'Config/config.json'
ENV_FILE = 'Config/.env'
REQUIREMENTS_FILE = 'Config/requirements.txt'

# 安装依赖项
def create_docs():
    """
    创建示例文档
    """
    # 如果config.json文件不存在，创建它
    if not os.path.exists(CONFIG_FILE):
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "uid": {
                    "1234567890": "1",
                    "0987654321": "0"
                }
            }, f, ensure_ascii=False, indent=2)
    
    if not os.path.exists(ENV_FILE):
        os.makedirs(os.path.dirname(ENV_FILE), exist_ok=True)
        with open(ENV_FILE, 'w', encoding='utf-8') as f:
            f.write("ARK_API_KEY=your_ark_api_key_here\n")
    
    if not os.path.exists("Config/weibo_cookie.json"):
        os.makedirs(os.path.dirname("Config/weibo_cookie.json"), exist_ok=True)
        with open("Config/weibo_cookie.json", 'w', encoding='utf-8') as f:
            f.write("""{
                    "Cookie": "your_weibo_cookie_here",
                    "User-Agent": "your_user_agent_here"
                }""")

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
    print('\n提示：')
    # 启动配置服务器
    import config_server
    config_server.start_config_server()
    

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
    
    # 创建示例文档
    create_docs()
    
    # 检查配置
    if check_config():
        print('配置文件检查通过，正在启动...')
        print('配置服务器默认地址：http://localhost:18002')
        start_config_server()
    else:
        print('配置文件无效，需要进行配置')
        start_config_server()


if __name__ == '__main__':
    main()
