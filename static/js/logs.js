// 日志内容容器
const logsContent = document.getElementById('logs-content');
// 日志搜索输入框
const logSearch = document.getElementById('log-search');
// 日志级别选择器
const logLevel = document.getElementById('log-level');
// 清空日志按钮
const clearLogsBtn = document.getElementById('clear-logs');
// 返回配置按钮
const configBtn = document.getElementById('config-btn');

// 轮询间隔（毫秒）
const POLLING_INTERVAL = 5000;

// 加载日志
function loadLogs() {
    fetch('/api/logs')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayLogs(data.logs);
        } else {
            console.error('获取日志失败:', data.message);
        }
    })
    .catch(error => {
        console.error('获取日志时发生错误:', error);
        displayError('获取日志时发生错误');
    });
}

// 展示日志
function displayLogs(logs) {
    if (logs.length === 0) {
        logsContent.innerHTML = `
            <div class="log-item">
                <div class="log-time">${new Date().toLocaleString()}</div>
                <div class="log-message">暂无日志数据</div>
            </div>
        `;
        return;
    }
    
    // 清空日志容器
    logsContent.innerHTML = '';
    
    // 展示每条日志
    logs.forEach(log => {
        addLogItem(log);
    });
    
    // 滚动到底部
    scrollToBottom();
}

// 添加日志项
function addLogItem(log) {
    const logItem = document.createElement('div');
    logItem.className = `log-item ${log.level.toLowerCase()}`;
    logItem.innerHTML = `
        <div class="log-time">${log.time}</div>
        <div class="log-content">
            <span class="log-level ${log.level.toLowerCase()}">${log.level}</span>
            <span class="log-message">${log.message}</span>
        </div>
    `;
    logsContent.appendChild(logItem);
}

// 展示错误信息
function displayError(message) {
    logsContent.innerHTML = `
        <div class="log-item error">
            <div class="log-time">${new Date().toLocaleString()}</div>
            <div class="log-message">${message}</div>
        </div>
    `;
}

// 滚动到底部
function scrollToBottom() {
    logsContent.scrollTop = logsContent.scrollHeight;
}

// 清空日志
function clearLogs() {
    if (confirm('确定要清空所有日志吗？')) {
        fetch('/api/logs/clear', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayLogs([]);
                alert('日志清空成功！');
            } else {
                console.error('清空日志失败:', data.message);
                alert('清空日志失败：' + data.message);
            }
        })
        .catch(error => {
            console.error('清空日志时发生错误:', error);
            alert('清空日志时发生错误');
        });
    }
}

// 过滤日志
function filterLogs() {
    const searchTerm = logSearch.value.toLowerCase();
    const selectedLevel = logLevel.value;
    
    const logItems = logsContent.querySelectorAll('.log-item');
    
    logItems.forEach(item => {
        const logMessage = item.querySelector('.log-message').textContent.toLowerCase();
        const logLevel = item.querySelector('.log-level').textContent;
        
        const matchesSearch = logMessage.includes(searchTerm);
        const matchesLevel = selectedLevel === 'all' || logLevel.toLowerCase() === selectedLevel;
        
        if (matchesSearch && matchesLevel) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// 轮询定时器ID
let pollingIntervalId = null;

// 初始化
function init() {
    // 加载日志
    loadLogs();
    
    // 设置轮询
    startPolling();
    
    // 绑定事件
    clearLogsBtn.addEventListener('click', clearLogs);
    configBtn.addEventListener('click', function() {
        // 停止轮询
        stopPolling();
        window.location.href = '/';
    });
    
    // 绑定过滤事件
    logSearch.addEventListener('input', filterLogs);
    logLevel.addEventListener('change', filterLogs);
    
    // 绑定页面可见性变化事件
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            // 页面变为不可见时停止轮询
            stopPolling();
        } else {
            // 页面变为可见时启动轮询
            startPolling();
        }
    });
    
    // 绑定页面卸载事件
    window.addEventListener('beforeunload', function() {
        // 页面即将关闭时停止轮询
        stopPolling();
    });
}

// 启动轮询
function startPolling() {
    // 确保不会重复启动轮询
    if (pollingIntervalId === null) {
        pollingIntervalId = setInterval(loadLogs, POLLING_INTERVAL);
    }
}

// 停止轮询
function stopPolling() {
    // 确保轮询已经启动
    if (pollingIntervalId !== null) {
        clearInterval(pollingIntervalId);
        pollingIntervalId = null;
    }
}

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', init);