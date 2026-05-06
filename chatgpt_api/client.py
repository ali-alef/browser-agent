from __future__ import annotations

import json
import urllib.error
import urllib.request

import pydantic

DEFAULT_MODEL = "gpt-4o"
DEFAULT_API_BASE = "http://34.72.104.120/"
API_KEY = "sk-tRFUVokeNnPpOsjoU0zlDw"

class ChatMessage(pydantic.BaseModel):
    role: str
    content: str


class ChatCompletionRequest(pydantic.BaseModel):
    messages: list[ChatMessage]
    temperature: float = 0.0


class ChatCompletionResponse(pydantic.BaseModel):
    content: str
    raw_response: dict


def chat_completion(request_data: ChatCompletionRequest) -> ChatCompletionResponse:
    url = DEFAULT_API_BASE.rstrip("/") + "/chat/completions"
    payload = {
        "model": DEFAULT_MODEL,
        "temperature": request_data.temperature,
        "messages": [message.model_dump() for message in request_data.messages],
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API error ({exc.code}): {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"OpenAI API request failed: {exc}") from exc

    parsed = json.loads(body)
    try:
        content = parsed["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected OpenAI response shape: {body[:500]}") from exc

    return ChatCompletionResponse(content=content, raw_response=parsed)
