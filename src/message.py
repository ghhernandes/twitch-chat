from dataclasses import dataclass

from .user import User
from .channel import Channel

@dataclass
class Message:
    raw_data: str
    channel: Channel
    user: User
    text: str