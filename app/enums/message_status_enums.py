import enum

class MessageStatusEnum(enum.Enum):
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    READ = "READ"


class MessageTypeEnum(enum.Enum):
    TEXT = "TEXT"
    FILE = "FILE"