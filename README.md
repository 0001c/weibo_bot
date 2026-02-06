# 微博爬虫与AI回复系统

这是一个自动化微博爬虫系统，能够监控指定用户的微博动态，并使用AI生成回复内容。

## 功能特性

- **微博监控**：自动监控指定用户的新微博
- **AI回复**：使用OpenAI API生成智能回复内容
- **Web配置**：提供网页界面进行配置管理
- **Docker部署**：支持Docker容器化部署
- **自动化运行**：可在后台持续运行，定期检查新内容

## 技术栈

- **Python 3.12**：主要开发语言
- **Requests**：HTTP请求处理
- **OpenAI API**：AI回复生成
- **http.server**：Web配置界面
- **Docker**：容器化部署

## 安装与部署

### 方法1：本地直接运行

1. **克隆项目**：
   ```bash
   git clone <项目仓库地址>
   cd weibo-spider
   ```

2. **创建虚拟环境**：
   ```bash
   python -m venv .venv
   ```

3. **激活虚拟环境**：
   - Windows：
     ```bash
     .venv\Scripts\activate
     ```
   - Linux/Mac：
     ```bash
     source .venv/bin/activate
     ```

4. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

5. **运行系统**：
   ```bash
   python start.py
   ```

### 方法2：Docker容器部署

1. **构建镜像**：
   ```bash
   docker-compose -p weibo-spider build
   ```

2. **启动容器**：
   ```bash
   docker-compose -p weibo-spider up -d
   ```

3. **查看运行状态**：
   ```bash
   docker-compose -p weibo-spider ps
   ```

## 配置说明

### 首次配置

系统启动后会自动打开配置页面（默认地址：http://localhost:18002），您需要填写以下配置：

1. **微博用户ID**：需要监控的微博用户ID列表
2. **ARK API Key**：OpenAI API密钥
3. **微博Cookie**：用于访问微博API的Cookie
4. **User-Agent**：浏览器标识
5. **Prompt**：AI回复的提示文本
6. **Sleep Time**：爬虫休眠时间（秒）

### 配置文件

配置信息会保存到以下文件：
- `config.json`：包含用户ID、prompt和sleep_time等配置
- `.env`：包含API密钥等环境变量
- `weibo_cookie.json`：包含Cookie和User-Agent配置

## 使用方法

1. **启动系统**：
   ```bash
   python start.py
   # 或使用Docker
   docker-compose -p weibo-spider up -d
   ```

2. **配置系统**：
   - 打开配置页面（http://localhost:18002）
   - 填写所有必要的配置信息
   - 点击"保存配置"按钮

3. **启动爬虫**：
   - 在配置页面点击"启动爬虫"按钮
   - 系统会自动启动服务

4. **查看日志**：
   - 本地运行：直接在终端查看
   - Docker运行：
     ```bash
     docker-compose -p weibo-spider logs -f
     ```

## 项目结构

```
weibo-spider/
├── spider.py          # 微博爬虫主脚本
├── ai_utils.py        # AI回复生成模块
├── config_server.py   # Web配置服务器
├── start.py           # 启动脚本
├── requirements.txt   # 依赖文件
├── config.json        # 配置文件
├── weibo_cookie.json  # Cookie配置文件
├── Dockerfile         # Docker构建文件
├── docker-compose.yml # Docker Compose配置
└── README.md          # 项目说明
```

## 常见问题

### 1. 无法访问微博API

**解决方法**：
- 确保Cookie和User-Agent配置正确
- 检查网络连接是否正常
- 尝试更新Cookie（微博Cookie有过期时间）

### 2. AI回复生成失败

**解决方法**：
- 确保ARK_API_KEY配置正确
- 检查网络连接是否正常
- 查看日志中的错误信息

### 3. Docker容器反复重启

**解决方法**：
- 检查配置文件是否正确
- 查看容器日志获取详细错误信息
- 确保所有依赖项都已正确安装

## 注意事项

1. **合规性**：使用本系统时，请遵守微博平台的使用规则和相关法律法规
2. **频率限制**：避免过于频繁的API请求，以免被微博平台封禁
3. **API费用**：使用OpenAI API会产生费用，请合理设置使用频率
4. **隐私保护**：不要在配置文件中存储敏感信息，特别是API密钥

## 许可证

本项目采用MIT许可证。

## 更新日志

- **v1.0.0**：初始版本，实现基本功能
- **v1.1.0**：添加Web配置界面
- **v1.2.0**：支持Docker部署
- **v1.3.0**：优化AI回复生成

## 贡献

欢迎提交Issue和Pull Request来改进本项目。

## 联系方式

如有问题，请联系：<gkgrby@163.com>
