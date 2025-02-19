import enum

class INTENT_ENUM(enum.Enum):
    PRODUCT_SEARCH = "product_search"
    REVIEW_SEARCH = "review_search"
    REVIEW_OF_PRODUCT = "review_of_product"
    PRODUCT_CATEGORY_SEARCH = "product_category_search"
    GENERAL_CHAT = "general_chat"