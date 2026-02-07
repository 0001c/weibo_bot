// 添加用户ID输入框
document.getElementById('add-uid').addEventListener('click', function() {
    const uidList = document.getElementById('uid-list');
    const uidItem = document.createElement('div');
    uidItem.className = 'uid-item';
    uidItem.innerHTML = `
        <input type="checkbox" class="uid-enabled" checked>
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

// 显示弹窗
function showToast(message, type = 'success') {
    // 滚动到顶部，增加过度效果
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
    
    const toast = document.getElementById('toast');
    const toastIcon = document.getElementById('toast-icon');
    const toastMessage = document.getElementById('toast-message');
    
    // 设置图标和消息
    const icons = {
        success: '✓',
        error: '✗',
        info: 'ℹ'
    };
    
    toastIcon.textContent = icons[type] || icons.success;
    toastMessage.textContent = message;
    
    // 显示弹窗
    toast.classList.add('show');
    
    // 3秒后自动隐藏
    setTimeout(() => {
        hideToast();
    }, 3000);
}

// 隐藏弹窗
function hideToast() {
    const toast = document.getElementById('toast');
    toast.classList.remove('show');
}

// 保存配置
function saveConfig() {
    // 收集用户ID
    const uidItems = document.querySelectorAll('.uid-item');
    // 收集API Key
    const arkApiKey = document.getElementById('ark-api-key').value.trim();
    // 收集Prompt和Sleep Time
    const prompt = document.getElementById('prompt').value.trim();
    const sleepTime = document.getElementById('sleep-time').value.trim();

    const uidDict = {};
    uidItems.forEach(item => {
        const uidInput = item.querySelector('input[type="text"]');
        const uidCheckbox = item.querySelector('input[type="checkbox"]');
        const uid = uidInput.value.trim();
        
        if (uid) {
            const enabled = uidCheckbox.checked ? '1' : '0';
            uidDict[uid] = enabled;
        }
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
        showToast(data.success ? '配置保存成功！✨' : '配置保存失败，请重试！⚠️', data.success ? 'success' : 'error');
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
                showToast(data.message, 'success');
                // const status = document.getElementById('status');
                // status.className = data.success ? 'status success' : 'status error';
                // status.textContent = data.message;
            })
            .catch(error => {
                showToast('启动爬虫失败，请检查配置！⚠️'+error.message, 'error');
            });
            
        } else {
            const status = document.getElementById('status');
            status.className = 'status error';
            status.textContent = '保存配置失败，无法启动爬虫';
        }
    })
    .catch(error => {
        showToast('保存配置失败！⚠️'+error.message, 'error');
    });
});

// 日志按钮点击事件
document.getElementById('logs-btn').addEventListener('click', function() {
    window.location.href = '/logs';
});