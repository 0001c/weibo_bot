import time
import json
import os

# 日志文件路径
LOG_FILE = 'logs/logs.json'

# 日志级别
LOG_LEVELS = {
    'INFO': 'info',
    'WARNING': 'warning',
    'ERROR': 'error'
}

# 初始化日志文件
def init_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

# 添加日志到文件
def add_log(level, message):
    """
    添加日志到文件
    
    Args:
        level: 日志级别 (INFO, WARNING, ERROR)
        message: 日志消息
    """
    # 初始化日志文件
    init_log_file()
    
    # 创建日志条目
    log_entry = {
        'time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'level': level,
        'message': message
    }
    
    # 读取现有日志
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    except:
        logs = []
    
    # 添加新日志
    logs.append(log_entry)
    
    # 限制日志数量，最多保存1000条
    if len(logs) > 1000:
        logs = logs[-1000:]
    
    # 写入日志文件
    try:
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    except:
        pass

# 获取所有日志
def get_all_logs():
    """
    获取文件中的所有日志
    
    Returns:
        list: 日志列表
    """
    # 初始化日志文件
    init_log_file()
    
    # 读取日志文件
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    except:
        logs = []
    
    return logs

# 获取新增日志
def get_new_logs():
    """
    获取文件中的所有日志
    
    Returns:
        list: 日志列表
    """
    return get_all_logs()

# 清空日志
def clear_logs():
    """
    清空日志文件
    """
    try:
        # 将当前日志内容写入另一个文件
        timestamp = time.strftime('%Y%m%d%H%M%S')
        current_logs = get_all_logs()
        with open(f'logs/backup/logs_backup_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(current_logs, f, ensure_ascii=False, indent=2)
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            # 清空当前日志文件
            json.dump([], f, ensure_ascii=False, indent=2)
    except:
        pass
