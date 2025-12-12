import json
from phone_agent.interfaces.base import BaseInterface, ProgressUpdate


class CLIInterface(BaseInterface):
    def __init__(self):
        self._cancelled = False

    async def send_message(self, text: str) -> None:
        print(text)

    async def send_image(self, image_path: str, caption: str = "") -> None:
        print(f"[Screenshot saved: {image_path}]")
        if caption:
            print(caption)

    async def send_progress(self, update: ProgressUpdate) -> None:
        print(f"\n{'=' * 50}")
        print(f"Step {update.step_num}/{update.total_steps}")
        print(f"Thinking: {update.thinking}")
        print(f"Action: {json.dumps(update.action, ensure_ascii=False, indent=2)}")
        print('=' * 50)

    async def ask_confirmation(self, message: str) -> bool:
        response = input(f"Confirm: {message} (Y/N): ")
        return response.upper() == 'Y'

    async def ask_takeover(self, message: str) -> None:
        input(f"{message}\nPress Enter after completing...")

    def is_cancelled(self) -> bool:
        return self._cancelled
