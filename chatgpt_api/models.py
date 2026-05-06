import pydantic


class ChatMessage(pydantic.BaseModel):
    role: str
    content: str


class ChatCompletionRequest(pydantic.BaseModel):
    messages: list[ChatMessage]
    temperature: float = 0.0


class ChatCompletionResponse(pydantic.BaseModel):
    content: str
    raw_response: dict
