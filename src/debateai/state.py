from typing import TypedDict, List, Literal
from langchain_core.messages import BaseMessage


class ChatState(TypedDict):
    messages: List[BaseMessage]
    current_speaker: Literal["left", "right"]
    conversation_count: int
    max_turns: int
