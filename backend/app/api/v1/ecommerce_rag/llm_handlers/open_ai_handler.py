from .interface import I_EcommerceRag
from openai import OpenAI
from app.core.preprocessing.embedding.open_ai import create_embedding_1536
from typing import Tuple, List
from sqlmodel import Session, select
from app.models.pg.product import Product
from app.models.pg.review import Review
from app.core.services.vector_search.query import MilvusCollectionService
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.postgres import engine, asyncEngine

import dotenv
dotenv.load_dotenv()

class OpenAIHandler(I_EcommerceRag):
    
    def __init__(self, model="gpt-3.5-turbo"):
        self.client = OpenAI()
        self.model = model
        self.milvusService = MilvusCollectionService()
    
    def classify_query(self, query:str):
        prompt = f"""
        Classify the following query into one of the categories:
        - general_chat: if it's a casual conversation.
        - product_search: if it's about skincare product recommendations.
        - review_search: if it's about customer reviews or opinions.
        - review_of_product: if it's about a review of a specific product.
        
        Query: "{query}"
        Classification:
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": "You are an expert query classifier for a beauty chatbot."},
                    {"role": "user", "content": prompt}]
        )

        choices = ['general_chat', 'product_search', 'review_search', 'review_of_product']

        res = response.choices[0].message.content.strip()
        return res if res in choices else "general_chat"
    
    def classify_query_v2(self, query: str, context: str = None):
        prompt = f"""
            You are an AI assistant that classifies user queries into one of four categories: 

            1. **general_chat** - The user is engaging in casual conversation, and the query is unrelated to products or reviews.
            2. **product_search** - The user is searching for a product or product category.
            3. **review_search** - The user is asking for general opinions or reviews about a product category.
            4. **review_of_product** - The user is asking about reviews or opinions of a **specific** product or an ongoing product discussion.

            ### **Classify the following user query:**  
            {"### Context: The user is currently discussing the following product or category: " + context + ". Always consider this context when classifying the query." if context else ""}
            **User Query:** "{query}"

            **Instructions:**  
            - Respond with ONLY the category name:  
            - general_chat  
            - product_search  
            - review_search  
            - review_of_product  
        """

        response = self.client.chat.completions.create(
            model="chatgpt-4o-latest",
            messages=[{"role": "system", "content": "You are an expert query classifier for a beauty chatbot."},
                    {"role": "user", "content": prompt}]
        )

        choices = ['general_chat', 'product_search', 'review_search', 'review_of_product']

        res = response.choices[0].message.content.strip()
        return res if res in choices else "general_chat"
    
    async def search_product_title(self, query: str, limit:int) -> Tuple[str, List[Product]]:
        collection = 'product_title'
        queryVec = create_embedding_1536(query)
        self.milvusService.set_collection(collection)
        
        milvusEnts = self.milvusService.query([queryVec], anns_field="title_vector" ,limit=limit)
        milvusEnts.sort(key=lambda x: x.distance)
        productIds = [item.id for item in milvusEnts]

        # query pg
        pgProducts = []
        # Query PostgreSQL using SQLAlchemy ORM
        async with AsyncSession(asyncEngine) as session:
            result = await session.execute(select(Product).filter(Product.id.in_(productIds)).order_by(Product.id))
            pgProducts = result.scalars().all()

        return query, pgProducts
    
    async def search_review(self, query:str, limit:int) -> Tuple[str, List[Review], List[Product]]:
        collection = 'review'
        queryVec = create_embedding_1536(query)
        self.milvusService.set_collection(collection)
        milvusEnts = self.milvusService.query([queryVec], anns_field="review_vector", limit=limit)
        milvusEnts.sort(key=lambda x: x.distance)
        reviewIds = [item.id for item in milvusEnts]
        # query pg - get reviews and Products
        async with AsyncSession(asyncEngine) as session:
            # get top reveiw parent_asins
            reviews = await session.execute(
                select(Review).filter(Review.id.in_(reviewIds)).order_by(Review.id))
            reviews = reviews.scalars().all()
            
            parentAsins = [r.parent_asin for r in reviews]
            products = await session.execute(
                select(Product).filter(Product.parent_asin.in_(parentAsins)).order_by(Product.id))
            products = products.scalars().all()

        return query, reviews, products
        
    def product_search_rewrite(self, userQuery, products: List[Product], stream=False, metaData={}):
        '''
        milvus product search llm rewrite
        '''
        context = ["\n".join([p.to_llm_context() for p in products])]
        prompt = f"""
        You are an AI assistant specializing in skincare products. Below is a user's question and relevant product information.
        Choose one to two products to recommend the user and briefly explain why.
        
        Context:
        {context}

        User Query:
        {userQuery}

        Based on the context, generate a helpful response that answers the user's question while recommending suitable products.

        ** Instructions: **
        DO NOT include products or reviews not provided in the context.
        """
        if not stream:
            response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": "You are an expert skincare assistant."},
                            {"role": "user", "content": prompt}]
                )

            return response.choices[0].message.content.strip()
        
        # stream response
        return self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are an expert skincare assistant."},
                    {"role": "user", "content": prompt}],
            stream=True
        )
    
    def review_search_rewrite(self, userQuery, reviews: List[Review], products: List[Product], stream=False):
        # zip reviews and products
        reviews = sorted(reviews, key=lambda x: x.parent_asin)
        products = sorted(products, key=lambda x: x.parent_asin)

        reviewContext = ["\n".join([r.to_llm_context() for r in reviews])]
        productContext = ["\n".join([p.to_llm_context() for p in products])]

        prompt = f"""
        You are an AI assistant specializing in skincare products. Below is a user's question and relevant review information.

        List of Reviews:
        {reviewContext}

        List of Products:
        {productContext}

        User Query:
        {userQuery}

        Based on the context, list the top 2-3 products and their reviews that are most relevant to the user's query.

        ** Instructions: **
        DO NOT include products or reviews not provided in the context.
        """ 

        if not stream:
            response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": "You are an expert skincare assistant."},
                            {"role": "user", "content": prompt}]
                )

            return response.choices[0].message.content.strip()
        
        # stream response
        return self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are an expert skincare assistant."},
                    {"role": "user", "content": prompt}],
            stream=True
        )
    
    def review_of_product_rewrite(self, userQuery, product: Product, reviews: List[Review], stream=False):
        
        reviews = sorted(reviews, key=lambda x: x.parent_asin)
        reviewContext = ["\n".join([r.to_llm_context() for r in reviews])]

        prompt = f"""
        You are an AI assistant specializing in skincare products. Below is a user's question about a specific product.

        List of Reviews:
        {reviewContext}

        Product: 
        {product.to_llm_context()}

        User Query:
        {userQuery}

        Based on the context, provide a detailed review of the product and answer any questions the user may have.
        """

        if not stream:
            response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": "You are a helpful skincare assistant."},
                            {"role": "user", "content": prompt}]
                )

            return response.choices[0].message.content.strip()
        
        # stream response
        return self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful skincare assistant."},
                    {"role": "user", "content": prompt}],
            stream=True
        )

    def create_completions(self, user_query: str, stream=False):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful skincare assistant."},
                    {"role": "user", "content": user_query}],
            stream=stream  # Enable streaming
        )
        return response