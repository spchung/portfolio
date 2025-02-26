from typing import List
from fastapi import HTTPException
from openai import OpenAI
from app.db.redis import r
import asyncio, json
from .interface import I_EcommerceRag
from app.api.v2.skincare_gpt.classifier.intent_enum import INTENT_ENUM
from app.core.preprocessing.embedding.open_ai import create_embedding_768
from app.api.v2.skincare_gpt.context.context_manager import SkincareGPTContext, ChatHistory, SkincareGPTContextManager
from app.api.v2.skincare_gpt.classifier.intent_classifier import IntentClassifier
from app.db.postgres import async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from qdrant_client import QdrantClient, models
from app.models.pg.sephora import SephoraProduct, SephoraReview
from app.core.ner_topic_extract.rule_based.rule_based_ner import rule_based_tag

import dotenv
dotenv.load_dotenv()

context_manager = SkincareGPTContextManager()

class OpenAIHandler():
    def __init__(self, session_id, model="chatgpt-4o-latest"):
        # generate new session_id if not provided
        if not session_id:
            self.session_id = context_manager.generate_session_id()
        else: 
            self.session_id = session_id

        self.client = OpenAI()
        self.model = model
        self.qdrant_client = QdrantClient(url="http://localhost:6333")
        self.llm_ctx = context_manager.get_context(self.session_id)
        self.intent_classifier = IntentClassifier(self.llm_ctx)

    def query_vector(self, query):
        res = self.qdrant.search(query)
        return res
    
    # main chat function
    async def chat(self, query, session_id=None):
        # 0. begin 
        self.llm_ctx.start_response()
        
        # 1. classify intent
        intent, cls_prompt = self.intent_classifier.classify(query)
        self.llm_ctx.last_prompt = cls_prompt

        # 2. NER
        _, entities = rule_based_tag(query)
        self.llm_ctx.register_named_entities(entities)

        # start chat history
        chat_history = ChatHistory()
        chat_history.user_query = query
        chat_history.user_intent = intent.value

        if intent == INTENT_ENUM.SEARCH:
            response = await self.search(query)
        elif intent == INTENT_ENUM.KNOWLEDGE:
            response = await self.knowledge_search(query)
        else: 
            response = self.create_completions(query, stream=True, temperature=0.5)

        total_response_tokens = 0
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                total_response_tokens += len(content)
                full_response += content
                yield content
            await asyncio.sleep(0)

        # post response ctx log
        chat_history.response = full_response
        
        # log total token
        chat_history.complete()

        self.llm_ctx.end_response(token_count=total_response_tokens)
        self.llm_ctx.add_chat_history(chat_history)
        self.llm_ctx.metadata.last_query_intent = intent.value

        r.set(self.llm_ctx.session_id, self.llm_ctx.serialize())
    
    def create_completions(self, user_query: str, stream=False, temperature = 0.5):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=temperature,
            messages=[{"role": "system", "content": "You are a helpful skincare assistant."},
                    {"role": "user", "content": user_query}],
            stream=stream  # Enable streaming
        )
        return response

    def get_context_snapshot(self):
        try:
            json_string = r.get(self.llm_ctx.session_id)
            return json.loads(json_string)
        except Exception as e:
            raise HTTPException(status_code=404, detail="Session not found")

    def get_last_prompt(self):
        return r.get('last_prompt')

    # INTENT - SEARCH
    async def search(self, query):
        context_limit = 3

        # 0. get positive or negative
        sentiment = self.binary_sentiment_analysis(query)

        filters = []
        filters.append(("vector_column", "product_highlights"))
        filters.append(("vector_column", "product_ingredients"))
        filters.append(("vector_column", "product_name"))

        qdrant_res = self.qdrant_client.query_points(
            collection_name="SkincareGPT_768",
            query=create_embedding_768(query),
            limit=15,
            query_filter=models.Filter(
                should=[models.FieldCondition(
                    key=k, match=models.MatchValue(value=v)) for k, v in filters]
            )
        )

        # assume always return points
        points = qdrant_res.points

        # 2. get products
        # sort by score
        points.sort(key=lambda x: x.score, reverse=True)

        product_ids = []
        for p in points[:context_limit]:
            product_ids.append(p.payload.get("product_id"))

        async with AsyncSession(async_engine) as session:
            products = await session.execute(
                select(SephoraProduct).filter(
                    SephoraProduct.product_id.in_(product_ids)).order_by(SephoraProduct.product_id))
            products = products.scalars().all()
        
        # get ingredients
        ingredients = set()
        for p in products:
            ingredients.update(p.ingredients)
        
        # context operations
        self.llm_ctx.set_product_ids([p.product_id for p in  products])

        # 3. PROMPT FOR REWRITE
        response = await self.llm_rewrite(
            INTENT_ENUM.SEARCH,
            query,
            sentiment,
            products=products,
            ingredients=ingredients
        )
        return response

    # INTENT - KNOWLEDGE
    async def knowledge_search(self, query):
        context_limit = 5

        # 0. get positive or negative
        sentiment = self.binary_sentiment_analysis(query)

        # 1. search reviews 
        filters = {"vector_column": "review_text"}
        if sentiment == "positive" or "negative":
            filters['is_recommended'] = sentiment == "positive"

        qdrant_res = self.qdrant_client.query_points(
            collection_name="SkincareGPT_768",
            query=create_embedding_768(query),
            limit=15,
            query_filter=models.Filter(
                must=[models.FieldCondition(
                    key=k, match=models.MatchValue(value=v)) for k, v in filters.items()]
            )
        )

        # assume always return points
        points = qdrant_res.points

        # 2. get products & review text
        # sort by score
        points.sort(key=lambda x: x.score, reverse=True)
        
        review_ids = []
        product_ids = []
        for p in points[:context_limit]:
            review_ids.append(p.payload.get("review_id"))
            product_ids.append(p.payload.get("product_id"))
        
        async with AsyncSession(async_engine) as session:
            reviews = await session.execute(
                select(SephoraReview).filter(
                    SephoraReview.review_id.in_(review_ids)).order_by(SephoraReview.product_id))
            reviews = reviews.scalars().all()
            
            products = await session.execute(
                select(SephoraProduct).filter(
                    SephoraProduct.product_id.in_(product_ids)).order_by(SephoraProduct.product_id))
            products = products.scalars().all()

            
        # 3. get ingredients
        ingredients = set()
        for p in products:
            ingredients.update(p.ingredients)

        # context operations
        self.llm_ctx.set_product_ids([p.product_id for p in  products])
        self.llm_ctx.set_reviews([r.review_id for r in reviews])

        # 4. PROMPT FOR REWRITE
        response = await self.llm_rewrite(
            INTENT_ENUM.KNOWLEDGE,
            query,
            sentiment,
            products=products,
            reviews=reviews
        )
        return response
    
    def binary_sentiment_analysis(self, query):
        prompt = f"""
        You are a sentiment analysis model that classifies text into one of two categories: **positive** or **negative** sentiment.  

        Analyze the sentiment of the following text and respond with only **"positive"** or **"negative"**, without any explanation.

        Text:
        "{query}"

        Response:
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": prompt}]
        )
        
        return response.choices[0].message.content.strip()
    
    def sentiment_analysis(self, query):
        prompt = f"""
        You are a sentiment analysis model that classifies text into one of two categories: **positive** or **negative** sentiment.  

        Analyze the sentiment of the following text and respond with only **"positive"**, **"neutral"** or **"negative"**, without any explanation.

        Text:
        "{query}"

        Response:
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    async def llm_rewrite(
        self, 
        intnet: INTENT_ENUM, 
        query: str, 
        sentiment: str,
        products: List[SephoraProduct] = None,
        reviews: List[SephoraReview] = None,
        ingredients: List[str] = None
    ):
        if intnet == INTENT_ENUM.SEARCH:
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
        elif intnet == INTENT_ENUM.KNOWLEDGE:
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
        else:
            prompt = query

        r.set('last_prompt', prompt)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": "Use provided information to answer the query."},
                    {"role": "user", "content": prompt}],
            stream=True  # Enable streaming
        )
        return response