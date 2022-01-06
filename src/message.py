from dataclasses import dataclass
from .user import User

@dataclass
class Message:
    channel: str
    user: User
    text: str


