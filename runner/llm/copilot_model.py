from __future__ import annotations

import asyncio
import json
import pathlib
from dataclasses import dataclass
from typing import Any, TypeVar, overload

from pydantic import BaseModel

from browser_use.llm.base import BaseChatModel
from browser_use.llm.exceptions import ModelProviderError
from browser_use.llm.messages import BaseMessage
from browser_use.llm.views import ChatInvokeCompletion

from runner.llm.serializer import CopilotCLIMessageSerializer

T = TypeVar("T", bound=BaseModel)
LOG_FILE = pathlib.Path("storage/runs/llm_trace.jsonl")
MAX_CONTEXT_TOKENS = 100000


@dataclass
class ChatCopilotCLI(BaseChatModel):
    model: str = "gpt-5.3-codex"
    copilot_binary: str = "copilot"
    timeout: float = 180.0

    @property
    def provider(self) -> str:
        return "copilot-cli"

    @property
    def name(self) -> str:
        return self.model

    def _estimate_tokens(self, text: str) -> int:
        return len(text.split())

    def _truncate_messages(self, messages: list[BaseMessage]) -> list[BaseMessage]:
        if len(messages) <= 2:
            return messages

        serialized = CopilotCLIMessageSerializer.serialize_messages(messages)
        if self._estimate_tokens(serialized) <= MAX_CONTEXT_TOKENS:
            return messages

        truncated = [messages[0]]
        for msg in messages[1:]:
            test_serialized = CopilotCLIMessageSerializer.serialize_messages(truncated + [msg])
            if self._estimate_tokens(test_serialized) <= MAX_CONTEXT_TOKENS:
                truncated.append(msg)
            else:
                break

        if len(truncated) == 1 and len(messages) > 1:
            truncated.append(messages[-1])

        return truncated

    @overload
    async def ainvoke(self, messages: list[BaseMessage], output_format: None = None, **kwargs: Any) -> ChatInvokeCompletion[str]: ...

    @overload
    async def ainvoke(self, messages: list[BaseMessage], output_format: type[T], **kwargs: Any) -> ChatInvokeCompletion[T]: ...

    async def ainvoke(
        self, messages: list[BaseMessage], output_format: type[T] | None = None, **kwargs: Any
    ) -> ChatInvokeCompletion[T] | ChatInvokeCompletion[str]:
        try:
            truncated = self._truncate_messages(messages)
            serialized = CopilotCLIMessageSerializer.serialize_messages(truncated)
            if output_format:
                prompt = (
                    f"{serialized}\n\nYou MUST return your response as valid JSON.\n\nRules:\n"
                    f"- Output ONLY JSON\n- No explanations\n- No extra text\n- Must strictly follow this schema\n\n"
                    f"Schema:\n{json.dumps(output_format.model_json_schema(), indent=2)}"
                )
                response_text = await self._run_copilot(prompt)
                self._log_llm_call({"messages": serialized, "response": output_format.model_validate_json(response_text)})
                return ChatInvokeCompletion(completion=output_format.model_validate_json(response_text), usage=None)

            response_text = await self._run_copilot(serialized)
            self._log_llm_call({"messages": serialized, "response": response_text})
            return ChatInvokeCompletion(completion=response_text, usage=None)
        except Exception as e:
            print(f"ridi :D {e}")
            raise

    async def _run_copilot(self, prompt: str) -> str:
        cmd = [self.copilot_binary, "-s", "--output-format", "text", "--no-ask-user"]

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except Exception as exc:
            raise ModelProviderError(message=f"Failed to start Copilot CLI: {exc}", model=self.name) from exc

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(input=prompt.encode()), timeout=self.timeout)
        except TimeoutError as exc:
            process.kill()
            await process.wait()
            raise ModelProviderError(message=f"Copilot CLI timed out after {self.timeout} seconds.", model=self.name) from exc

        stdout_text = stdout.decode("utf-8", errors="replace").strip()
        stderr_text = stderr.decode("utf-8", errors="replace").strip()

        if process.returncode != 0:
            details = stderr_text or stdout_text or f"Copilot CLI exited with code {process.returncode}."
            raise ModelProviderError(message=details, model=self.name)

        if not stdout_text:
            raise ModelProviderError(message="Copilot CLI returned an empty response.", model=self.name)

        return stdout_text

    def _log_llm_call(self, log: dict) -> None:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(log, ensure_ascii=False) + "\n")
