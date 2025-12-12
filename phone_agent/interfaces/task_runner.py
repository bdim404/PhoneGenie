import asyncio
import base64
import os
import tempfile
from typing import Optional

from phone_agent import PhoneAgent
from phone_agent.agent import AgentConfig, StepResult
from phone_agent.model import ModelConfig
from phone_agent.interfaces.base import BaseInterface, ProgressUpdate
from phone_agent.adb import get_screenshot


class TaskRunner:
    def __init__(
        self,
        interface: BaseInterface,
        model_config: ModelConfig,
        agent_config: AgentConfig
    ):
        self.interface = interface
        self.model_config = model_config
        self.agent_config = agent_config

    async def run_task(self, task: str) -> str:
        agent = PhoneAgent(
            model_config=self.model_config,
            agent_config=self.agent_config,
            confirmation_callback=self._wrap_confirmation,
            takeover_callback=self._wrap_takeover
        )

        await self.interface.send_message(f"Starting task: {task}")

        is_first = True
        step_num = 0

        while step_num < self.agent_config.max_steps:
            if self.interface.is_cancelled():
                await self.interface.send_message("Task cancelled by user")
                return "Task cancelled"

            step_num += 1

            if is_first:
                result = await asyncio.to_thread(agent.step, task)
                is_first = False
            else:
                result = await asyncio.to_thread(agent.step)

            await self._send_step_progress(result, step_num)

            if result.finished:
                await self.interface.send_message(
                    f"Task completed!\n\n{result.message or 'Done'}"
                )
                return result.message or "Task completed"

        await self.interface.send_message("Max steps reached")
        return "Max steps reached"

    async def _send_step_progress(self, result: StepResult, step_num: int):
        screenshot_path = None

        if self.agent_config.verbose:
            try:
                screenshot = get_screenshot(self.agent_config.device_id)
                image_data = base64.b64decode(screenshot.base64_data)

                temp_file = tempfile.NamedTemporaryFile(
                    suffix='.png', delete=False
                )
                with open(temp_file.name, 'wb') as f:
                    f.write(image_data)
                screenshot_path = temp_file.name
            except Exception as e:
                print(f"Failed to capture screenshot: {e}")

        progress = ProgressUpdate(
            step_num=step_num,
            total_steps=self.agent_config.max_steps,
            thinking=result.thinking,
            action=result.action or {},
            screenshot_path=screenshot_path
        )

        await self.interface.send_progress(progress)

        if screenshot_path:
            try:
                os.unlink(screenshot_path)
            except Exception:
                pass

    def _wrap_confirmation(self, message: str) -> bool:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.interface.ask_confirmation(message)
            )
        finally:
            loop.close()

    def _wrap_takeover(self, message: str) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                self.interface.ask_takeover(message)
            )
        finally:
            loop.close()
