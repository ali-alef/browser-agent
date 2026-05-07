from __future__ import annotations

import json

import requests
from urllib import parse

from chatgpt_api import models as chatgpt_models
import settings


def chat_completion(request_data: chatgpt_models.ChatCompletionRequest) -> chatgpt_models.ChatCompletionResponse:
    response = requests.post(
        url=parse.urljoin(settings.MODEL_URL, "/chat/completions"),
        json={
            "model": settings.MODEL_NAME,
            "temperature": request_data.temperature,
            "messages": [message.model_dump() for message in request_data.messages],
        },
        headers={
            "Authorization": f"Bearer {settings.MODEL_API_KEY}",
            "Content-Type": "application/json",
        },
    )
    response.raise_for_status()
    parsed = json.loads(response.text)
    try:
        content = parsed["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected response: {parsed}") from exc

    return chatgpt_models.ChatCompletionResponse(content=content, raw_response=parsed)
