# PhoneGenie

A Telegram Bot version based on [Open-AutoGLM](https://github.com/zai-org/Open-AutoGLM) for controlling Android phones through chat.

## Quick Start

1. Install dependencies
```bash
pip install -r requirements.txt
```

2. Configure Bot
Edit `config/bot_config.yaml`:
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

3. Connect your phone and start
```bash
python bot_main.py
```

## Usage

Send tasks to your Bot in Telegram:
- `/start` - Show help
- `/status` - Check device status
- `/cancel` - Cancel current task
- Send task directly (e.g., "Open WeChat")

## Features

- Real-time display of execution steps and reasoning
- Automatic screenshot for each step
- Task cancellation and manual takeover support
- CLI mode preserved (`python main.py`)
