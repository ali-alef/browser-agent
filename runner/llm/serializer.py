from __future__ import annotations

import json

from browser_use.llm import messages as llm_messages


class CopilotCLIMessageSerializer:
    @staticmethod
    def _serialize_content(
            content: str | list[llm_messages.ContentPartTextParam | llm_messages.ContentPartImageParam | llm_messages.ContentPartRefusalParam]
    ) -> str:
        if isinstance(content, str):
            return content
        parts: list[str] = []
        for part in content:
            if part.type == 'text':
                parts.append(part.text)
            elif part.type == 'refusal':
                parts.append(f"[Refusal] {part.refusal}")
            elif part.type == 'image_url':
                parts.append(f"[Image] {part.image_url.url}")
            else:
                raise ValueError(f"Unknown part with type: {part.type}")

        return "\n".join([p for p in parts if p])

    @staticmethod
    def _serialize_tool_call(tool_call: llm_messages.ToolCall) -> str:
        return json.dumps({
            "tool_call_id": tool_call.id,
            "function_name": tool_call.function.name,
            "function_arguments": json.loads(tool_call.function.arguments)
        })

    @staticmethod
    def serialize(message: llm_messages.BaseMessage) -> dict[str, str]:
        if isinstance(message, llm_messages.UserMessage):
            result = {"role": message.role, "content": CopilotCLIMessageSerializer._serialize_content(message.content)}
            if message.name is not None:
                result["name"] = message.name
            return result

        elif isinstance(message, llm_messages.SystemMessage):
            result = {"role": message.role, "content": CopilotCLIMessageSerializer._serialize_content(message.content)}
            if message.name is not None:
                result["name"] = message.name
            return result

        elif isinstance(message, llm_messages.AssistantMessage):
            result: dict[str, str] = {"role": message.role}
            if message.content:
                result["content"] = CopilotCLIMessageSerializer._serialize_content(message.content)
            if message.name is not None:
                result["name"] = message.name
            if message.refusal is not None:
                result["refusal"] = message.refusal
            if message.tool_calls:
                result["tool_calls"] = json.dumps([
                    {
                        "tool_call_id": tc.id,
                        "function_name": tc.function.name,
                        "function_arguments": json.loads(tc.function.arguments)
                    }
                    for tc in message.tool_calls
                ])
            return result

        else:
            raise ValueError(f"Unknown message type: {type(message)}")

    @staticmethod
    def serialize_messages(messages: list[llm_messages.BaseMessage]) -> str:
        lines = []
        for m in messages:
            msg = CopilotCLIMessageSerializer.serialize(m)
            role = msg["role"]
            if role == "system":
                lines.append(f"[SYSTEM]\n{msg['content']}")
            elif role == "user":
                lines.append(f"[USER]\n{msg['content']}")
            elif role == "assistant":
                if "content" in msg:
                    lines.append(f"[ASSISTANT]\n{msg['content']}")
                if "tool_calls" in msg:
                    lines.append(f"[ASSISTANT_TOOL_CALLS]\n{msg['tool_calls']}")
            elif role == "tool":
                lines.append(f"[TOOL]\n{msg['content']}")
        return "\n\n".join(lines)
