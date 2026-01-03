import enum

class TokenTypeEnum(str, enum.Enum):
    INVITATION = "INVITATION"
    RESET_PASSWORD = 'RESET_PASSWORD'
    FORGOT_PASSWORD = 'FORGOT_PASSWORD'

class EventEnum(str, enum.Enum):

    CHAT_MESSAGE = "CHAT_MESSAGE"