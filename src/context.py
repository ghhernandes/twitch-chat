from .message import Message

class Context:
    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_message(self) -> Message:
        return self.message

    def get_last_ping(self) -> float:
        return self.last_ping