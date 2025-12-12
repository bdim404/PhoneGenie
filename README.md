# PhoneGenie - 手机精灵

基于 [Open-AutoGLM](https://github.com/zai-org/Open-AutoGLM) 的 Telegram Bot 版本，通过聊天机器人操作 Android 手机。

## 快速开始

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 配置 Bot
编辑 `config/bot_config.yaml`：
```yaml
telegram:
  token: "YOUR_BOT_TOKEN"
  allowed_user_id: YOUR_USER_ID

model:
  base_url: "http://localhost:8000/v1"
  model_name: "autoglm-phone-9b"

agent:
  max_steps: 100
  device_id: null
  lang: "cn"
```

3. 连接手机并启动
```bash
python bot_main.py
```

## 使用

在 Telegram 中向你的 Bot 发送任务：
- `/start` - 查看帮助
- `/status` - 查看设备状态
- `/cancel` - 取消当前任务
- 直接发送任务（如"打开微信"）

## 特性

- 实时显示执行步骤和思考过程
- 每步自动发送手机截图
- 支持任务取消和人工接管
- CLI 模式保留（`python main.py`）
