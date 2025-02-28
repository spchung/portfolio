import enum

class INTENT_ENUM(enum.Enum):
    CHAT = "chat"
    SEARCH = "search"
    KNOWLEDGE = "knowledge"
    RECOMMEND = "recommend"
    FOLLOW_UP = "follow_up"

class SKIN_TYPE_ENUM(enum.Enum):
    OILY = "oily"
    DRY = "dry"
    COMBINATION = "combination"
    NORMAL = "normal"
