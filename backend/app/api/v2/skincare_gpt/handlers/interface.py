from abc import ABC, abstractmethod

class I_EcommerceRag(ABC):
    
    @abstractmethod
    def classify_query(self):
        pass

    @abstractmethod
    async def search_product_title(self):
        pass

    @abstractmethod
    def search_review(self):
        pass

    @abstractmethod
    def product_search_rewrite(self):
        pass

    @abstractmethod
    def review_search_rewrite(self):
        pass

    @abstractmethod
    def create_completions(self):
        pass

    