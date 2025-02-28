from openai import OpenAI
from app.db.redis import r
from typing import List
from app.models.pg.sephora import SephoraProduct, SephoraReview
from app.api.v2.skincare_gpt.classifier.enum import INTENT_ENUM

class LLMService:
    def __init__(self, model='chatgpt-4o-latest', classifier_model='gpt-4o-mini'):
        self.llm = OpenAI()
        self.model = model
        self.classifier_model = classifier_model

    def create_completions(self, user_query: str, stream=False, temperature = 0.5):
        response = self.llm.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=temperature,
            messages=[{"role": "system", "content": "You are a helpful skincare assistant."},
                    {"role": "user", "content": user_query}],
            stream=stream  # Enable streaming
        )
        return response
    
    def paraphrase(self, query):
        prompt = f"""
        You are a paraphrasing model that rewrites text to convey the same meaning in different words. 
        Rewrite the following text in a different way while preserving the original meaning:

        **Instructions:**
        - Be friendly, concise, and informative.
        - The response has to be conversational and from a skincare helper's perspective.

        Text:
        "{query}"

        Response:
        """
        
        response = self.llm.chat.completions.create(
            temperature=2,
            model=self.model,
            messages=[
                {"role": "system", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    
    async def generate_search_response(
        self, 
        query: str, 
        sentiment: str,
        products: List[SephoraProduct], 
        ingredients: List[str] = None,
        stream=True
    ):
        llm_generated_response = "I recommed trying XXX product because contains the key ingredients YYY and ZZZ."
            
        context = ""
        for product in products:
            context += f"Name: {product.product_name}\n"
            context += f"Brand: {product.brand_name}\n"
            context += f"Ingredients: {','.join(product.ingredients)}\n"
            context += f"Highlights: {','.join(product.highlights)}\n"

        prompt = f"""
        You are an expert AI assistant specializing in skincare. Given a user query, your task is to generate a knowledgeable, well-structured response using the retrieved **reviews, product details, and ingredient information**.

        ### Context:
        - **User Query:** "{query}"
        - **Sentiment:** {sentiment}
        - **Relevant Products:**  
        {context}  

        ### Instructions:
        - **Use the retrieved product reviews to provide real-world insights** (mention common experiences, benefits, and concerns).
        '- **Explain the role of key ingredients**, especially how they relate to the user’s query.'
        - **Keep it concise, well-structured, and free of unnecessary repetition.**
        - **Maintain a helpful, informative, and friendly tone.**

        ### Example Response Format:
        "{llm_generated_response}"

        ### Output:
        Generate a final response based on this information, ensuring it is **direct, informative, and engaging**. Do not include any formatting or extra explanations—just provide the response.
        """

        r.set('last_prompt', prompt)

        response = self.llm.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": "Use provided information to answer the query."},
                    {"role": "user", "content": prompt}],
            stream=stream
        )
        return response
    
    async def generate_knowledge_response(
        self,
        query: str,
        sentiment: str,
        products: List[SephoraProduct],
        reviews: List[SephoraReview],
        ingredients: List[str] = None,
        stream=True
    ):
        llm_generated_response = "This product is great for dry skin. It contains hyaluronic acid and glycerin, which are known for their hydrating properties. The reviews mention that it absorbs quickly and..."
        
        context = ""
        for product, review in zip(products, reviews):
            context += f"Product: {product.product_name}\n"
            context += f"Review: {review.review_text}\n\n"
        
        if ingredients :
            formatted_ingredients = ", ".join(ingredients)

        prompt = f"""
        You are an expert AI assistant specializing in skincare. Given a user query, your task is to generate a knowledgeable, well-structured response using the retrieved **reviews, product details, and ingredient information**.

        ### Context:
        - **User Query:** "{query}"
        - **Sentiment:** {sentiment}
        - **Relevant Product Reveiws:**  
        {context}  

        {f"- **Key Ingredients:** {formatted_ingredients}" if ingredients else ""}

        ### Instructions:
        - **Use the retrieved product reviews to provide real-world insights** (mention common experiences, benefits, and concerns).
        {'- **Explain the role of key ingredients**, especially how they relate to the user’s query.' if ingredients else ''}
        - **Keep it concise, well-structured, and free of unnecessary repetition.**
        - **Maintain a helpful, informative, and friendly tone.**

        ### Example Response Format:
        "{llm_generated_response}"

        ### Output:
        Generate a final response based on this information, ensuring it is **direct, informative, and engaging**. Do not include any formatting or extra explanations—just provide the response.
        """

        r.set('last_prompt', prompt)

        response = self.llm.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": "Use provided information to answer the query."},
                    {"role": "user", "content": prompt}],
            stream=stream  # Enable streaming
        )
        return response
    
    async def generate_recommend_response(
        self,
        query: str,
        sentiment: str,
        products: List[SephoraProduct],
        reviews: List[SephoraReview],
        ingredients: List[str] = None,
        stream=True
    ):
        llm_generated_response = "I recommend trying this product because it contains key ingredients that are beneficial for your skin. The reviews mention that it is suitable for sensitive skin and helps with hydration."

        context = ""
        if products:
            for product in products:
                context += f"Product: {product.product_name}\n"

        if reviews:
            for review in reviews:
                context += f"Review: {review.review_text}\n"
        
        if ingredients :
            formatted_ingredients = ", ".join(ingredients)
        
        prompt = f"""
        You are an expert AI assistant specializing in skincare. Given a user query, your task is to generate a knowledgeable, well-structured response using the retrieved **reviews, product details, and ingredient information**.

        ### Context:
        - **User Query:** "{query}"
        - **Sentiment:** {sentiment}
        - **Relevant Product Reveiws:**  
        {context}  

        {f"- **Key Ingredients:** {formatted_ingredients}" if ingredients else ""}

        ### Instructions:
        - **Use the retrieved product reviews to provide real-world insights** (mention common experiences, benefits, and concerns).
        {'- **Explain the role of key ingredients**, especially how they relate to the user’s query.' if ingredients else ''}
        - **Keep it concise, well-structured, and free of unnecessary repetition.**
        - **Maintain a helpful, informative, and friendly tone.**

        ### Example Response Format:
        "{llm_generated_response}"

        ### Output:
        Generate a final response based on this information, ensuring it is **direct, informative, and engaging**. Do not include any formatting or extra explanations—just provide the response.
        """

        r.set('last_prompt', prompt)

        response = self.llm.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": "Use provided information to answer the query."},
                    {"role": "user", "content": prompt}],
            stream=stream  # Enable streaming
        )
        return response