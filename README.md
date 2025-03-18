# Discord Daily Check-in Bot

一个支持多账号、多服务器、多频道的 Discord 自动签到机器人，具有智能随机延迟和人性化的日志记录功能。

## 功能特点

- 多账号支持
  - 支持多个 Discord 账号同时管理
  - 账号间随机延迟执行
  - 独立的代理设置
  - Token 有效性验证

- 智能调度系统
  - 每日随机时间执行
  - 频道间智能延迟
  - 账号间随机间隔
  - 防机器人检测策略

- 项目管理
  - 序号化管理签到项目
  - 支持自定义项目名称
  - 清晰的项目状态跟踪
  - 结构化的配置管理

- 日志系统
  - 详细的执行记录
  - 项目化的状态展示
  - 时间戳记录
  - 错误追踪和诊断

## 系统要求

- Python 3.7+
- 操作系统：Windows/Linux/MacOS

## 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/tison-g/discord-daily.git
cd discord-daily
```

2. 创建目录
```bash
mkdir -p logs config
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

## 配置文件

### 1. config/accounts.csv

账号配置文件，包含所有需要进行签到的 Discord 账号信息：

```csv
DISCORD_TOKEN,PROXY,USERNAME,STATUS
your_token_1,http://proxy1:8080,user1,
your_token_2,socks5://proxy2:1080,user2,
your_token_3,,user3,
```

字段说明：
- DISCORD_TOKEN: Discord 账号的令牌
- PROXY: 代理服务器地址（可选）
- USERNAME: 账号用户名（用于日志识别）
- STATUS: 状态字段（留空）

### 2. config/config.csv

签到任务配置文件：

```csv
INDEX,PROJECT,GUILD_ID,CHANNEL_ID,MESSAGE
1,Project A,123456789,987654321,/daily
2,Project B,123456789,987654322,!checkin
3,Discord C,987654321,123456789,Good morning!
```

字段说明：
- INDEX: 项目序号（用于日志标识）
- PROJECT: 项目名称（用于日志标识）
- GUILD_ID: Discord 服务器 ID
- CHANNEL_ID: 频道 ID
- MESSAGE: 签到消息内容

## 运行说明

### 1. 测试运行（立即执行）
```bash
python src/daily_checkin.py
```

### 2. 定时运行
```bash
python src/scheduler.py
```

### 3. 后台运行（Linux）
```bash
# 使用 nohup
nohup python scheduler.py > nohup.out 2>&1 &

# 或使用 screen
screen -S discord-checkin
python scheduler.py
# Ctrl+A+D 分离 screen
```

## 执行逻辑

1. 随机延迟机制
   - 频道间延迟：10-30 秒随机间隔
   - 账号间延迟：15-45 秒随机间隔
   - 每日随机执行时间：配置的时间范围内

2. 执行顺序
   - 随机打乱账号处理顺序
   - 随机打乱每个账号的频道处理顺序
   - 智能分散执行时间

## 日志系统

### 日志位置
- logs/checkin_YYYYMMDD_HHMMSS.log：签到执行日志
- logs/scheduler.log：调度器运行日志

### 日志格式
```log
2025-03-18 10:11:47 | INFO | Loaded 3 configurations from CSV
2025-03-18 10:11:47 | INFO | Loaded projects:
2025-03-18 10:11:47 | INFO | [1] Project A - /daily
2025-03-18 10:11:47 | INFO | [2] Project B - !checkin
2025-03-18 10:11:47 | INFO | Account 1 | Waiting 15.7s before sending message to [2] Project B
```

## 常见问题

1. Token 相关
   - 确保 Token 格式正确
   - 检查 Token 是否过期
   - 验证账号状态是否正常

2. 网络问题
   - 检查代理服务器设置
   - 验证网络连接状态
   - 确认 Discord API 可访问

3. 配置问题
   - 检查 CSV 文件编码（推荐 UTF-8）
   - 验证服务器和频道 ID
   - 确认消息格式正确

## 安全建议

1. 账号安全
   - 定期更换 Token
   - 使用代理服务器
   - 避免频繁操作

2. 配置安全
   - 不要公开分享配置文件
   - 定期备份配置信息
   - 妥善保管账号信息

## 项目结构
```
discord-daily/
├── .gitignore
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── daily_checkin.py
│   └── scheduler.py
├── config/
│   ├── accounts.csv
│   └── config.csv
└── logs/
    └── .gitkeep
```

## 更新日志

### v1.1.0 (2025-03-18)
- 添加项目序号和名称管理
- 改进日志输出格式
- 优化随机延迟机制
- 增强防检测功能

### v1.0.0 (2025-03-17)
- 初始版本发布
- 支持多账号管理
- 支持代理配置
- 实现随机时间签到

## 维护者

[@tison-g](https://github.com/tison-g)

## License

MIT License