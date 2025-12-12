from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProgressUpdate:
    step_num: int
    total_steps: int
    thinking: str
    action: dict
    screenshot_path: Optional[str] = None


class BaseInterface(ABC):
    @abstractmethod
    async def send_message(self, text: str) -> None:
        pass

    @abstractmethod
    async def send_image(self, image_path: str, caption: str = "") -> None:
        pass

    @abstractmethod
    async def send_progress(self, update: ProgressUpdate) -> None:
        pass

    @abstractmethod
    async def ask_confirmation(self, message: str) -> bool:
        pass

    @abstractmethod
    async def ask_takeover(self, message: str) -> None:
        pass

    @abstractmethod
    def is_cancelled(self) -> bool:
        pass
