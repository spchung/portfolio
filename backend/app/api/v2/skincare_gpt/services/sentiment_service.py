from app.api.v2.skincare_gpt.services.llm_service import LLMService

class SentimentService:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def analyze(self, query):
        prompt = f"""
        You are a sentiment analysis model that classifies text into one of thre categories: positive, neutral or negative sentiment.  

        Analyze the sentiment of the following text and respond with only positive, neutral or negative, without any explanation.

        Text:
        "{query}"

        Response:
        """
        
        response = self.llm_service.llm.chat.completions.create(
            model=self.llm_service.classifier_model,
            messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    
    def binary_analyze(self, query: str) -> str:
        """
        Analyze sentiment as either positive or negative.
        
        Args:
            query: The text to analyze
            
        Returns:
            str: "positive" or "negative"
        """
        prompt = f"""
        You are a sentiment analysis model that classifies text into one of two categories: **positive** or **negative** sentiment.  

        Analyze the sentiment of the following text and respond with only **"positive"** or **"negative"**, without any explanation.

        Text:
        "{query}"

        Response:
        """
        
        response = self.llm_service.llm.chat.completions.create(
            model=self.llm_service.classifier_model,
            messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0].message.content.strip()