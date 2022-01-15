

class EventNotExistError(Exception):
    pass

class CommandExistsError(Exception):
    pass

class SendMessageError(Exception):
    pass

class JoinChannelError(Exception):
    pass

class SocketConnectError(Exception):
    pass

class ParseDataError(Exception):
    pass

class ChannelLimitExceededError(Exception):
    pass