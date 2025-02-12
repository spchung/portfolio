'''
A service thay uses LLM api to classify user query using zero-shot classification
'''

from openai import OpenAI
import dotenv
dotenv.load_dotenv()

client = OpenAI()

class RetailIntentClassifier:
    def __init__(self):
        pass

    def classify(self, query:str):
        prompt = f"""
        Classify the following query into one of the categories:
        - general_chat: if it's a casual conversation.
        - product_search: if it's about skincare product recommendations.
        - review_search: if it's about customer reviews or opinions.
        
        Query: "{query}"
        Classification:
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are an expert query classifier for a beauty chatbot."},
                    {"role": "user", "content": prompt}]
        )

        choices = ['general_chat', 'product_search', 'review_search']

        res = response.choices[0].message.content.strip()
        return res if res in choices else "general_chat"