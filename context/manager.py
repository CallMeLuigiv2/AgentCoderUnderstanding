from prompts.system import get_system_prompt
from dataclasses import dataclass
from utils.text import count_tokens
from typing import Any

@dataclass
class MessageItem:
    role: str
    content: str
    token_count: int | None = None

    def to_dict(self)-> dict[str, Any]:
       result:dict[str, Any] = {
        "role": self.role,
       }
       if self.content:
        result["content"] = self.content
       return result

class ContextManager:


    def __init__(self) -> None:
        self.system_prompt = get_system_prompt()
        self.messages: list[MessageItem] = []
        self.model = "ministral-3:8b-instruct-2512-q4_K_M"

    def add_user_message(self, content:str)-> None:

        item = MessageItem(
            role="user",
            content=content,
            token_count= count_tokens(
                content, 
                self.model,
                )
        )
        self.messages.append(item)

    def add_assistant_message(self, content:str)-> None:
        item = MessageItem(
            role="assistant",
            content=content,
            token_count= count_tokens(
                content, 
                self.model,
                )
        )
        self.messages.append(item)

    def get_messages(self)-> list[dict[str, Any]]:

        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        for item in self.messages:
            messages.append(item.to_dict())
        return messages

