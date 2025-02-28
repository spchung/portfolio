from typing import List, Tuple
from app.db.qdrant import qdarnt_client
from app.core.preprocessing.embedding.open_ai import create_embedding_768
from qdrant_client import models
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db.postgres import async_engine
from app.models.pg.sephora import SephoraProduct, SephoraReview
from app.api.v2.skincare_gpt.context.context_manager import SkincareGPTContext
from app.api.v2.skincare_gpt.services.llm_service import LLMService
from typing import Literal
from app.models.api.ner import EntityResults

class SearchService:

    def __init__(self, llm_service: LLMService, llm_ctx: SkincareGPTContext):
        self.qdrant_client = qdarnt_client
        self.llm_service = llm_service
        self.llm_ctx = llm_ctx
    
    async def product_search(
        self, 
        query: str, 
        sentiment: str, 
    ) -> Tuple[str, List[str]]:
        """
        Search for products based on query and sentiment.

        Args:
            query: The user query
            sentiment: The sentiment of the user query
            context: an insance of SkincareGPTContext

        Returns:
            stream chuncked response from llm service
        """
        product_limit = 2

        # qdrant search filters
        filters = []
        filters.append(("vector_column", "product_highlights"))
        filters.append(("vector_column", "product_ingredients"))
        filters.append(("vector_column", "product_name"))

        # query the vector database
        qdrant_res = self.qdrant_client.query_points(
            collection_name="SkincareGPT_768",
            query=create_embedding_768(query),
            limit=15,
            query_filter=models.Filter(
                should=[models.FieldCondition(
                    key=k, match=models.MatchValue(value=v)) for k, v in filters]
            )
        )

        # process search results
        products, reviews, ingredients = await self._process_search_results(
            qdrant_res.points, product_limit, sentiment
        )

        # update context
        self.llm_ctx.set_product_ids([p.product_id for p in products])
        self.llm_ctx.set_review_ids([r.review_id for r in reviews])

        # rewrite response
        return await self.llm_service.generate_search_response(
            query, sentiment, products, ingredients
        )
    
    async def knowledge_search(self, query: str, sentiment: str):
        """
        Search for knowledge based on query and sentiment.

        Args:
            query: The user query
            sentiment: The sentiment of the user query
            context: an insance of SkincareGPTContext

        Returns:
            stream chuncked response from llm service
        """
        review_limit = 5

        # qdrant search filters
        filters = {"vector_column": "review_text"}
        if sentiment == "positive" or sentiment == "negative":
            filters['is_recommended'] = sentiment == "positive"

        # query the vector database
        qdrant_res = self.qdrant_client.query_points(
            collection_name="SkincareGPT_768",
            query=create_embedding_768(query),
            limit=15,
            query_filter=models.Filter(
                must=[models.FieldCondition(
                    key=k, match=models.MatchValue(value=v)) for k, v in filters.items()]
            )
        )

        # get reviews, products and ingredients
        reviews, products, ingredients = await self._process_knowledge_results(
            qdrant_res.points, review_limit
        )

        # update context
        self.llm_ctx.set_product_ids([p.product_id for p in products])
        self.llm_ctx.set_review_ids([r.review_id for r in reviews])

        # rewrite response
        return await self.llm_service.generate_knowledge_response(
            query, sentiment, products, reviews, ingredients
        )
    
    async def recommend_search(self, query: str, sentiment: str, ner_entities: EntityResults):
        """
        Search for knowledge based on query and sentiment.

        Args:
            query: The user query
            sentiment: The sentiment of the user query
            context: an insance of SkincareGPTContext

        Returns:
            stream chuncked response from llm service
        """
        ## 1. if ner entitiy product_ingredient is present then search those ingredient first
        # match ingredients from NER
        should_filters = []
        should_filters.append(("vector_column", "product_ingredients"))
        should_filters.append(("vector_column", "review_text"))
        
        # sentiment filter
        must_filters = []
        if sentiment == "positive" or sentiment == "negative":
            must_filters.append(("is_recommended", sentiment == "positive"))

        # query the vector database
        ingredient_points = []
        if ner_entities.product_ingredient:
            ner_ingredient_query = " ".join(ner_entities.product_ingredient)
            
            # query the vector database
            ingredient_query_res = self.qdrant_client.query_points(
                collection_name="SkincareGPT_768",
                query=create_embedding_768(ner_ingredient_query),
                limit=5,
                query_filter=models.Filter(
                    must=[models.FieldCondition(
                        key=k, match=models.MatchValue(value=v)) for k, v in must_filters],
                    should=[models.FieldCondition(
                        key=k, match=models.MatchValue(value=v)) for k, v in should_filters]
                )
            )
            ingredient_points = ingredient_query_res.points
            ingredient_points.sort(key=lambda x: x.score, reverse=True)
        
        ## search again with user query
        qdrant_res = self.qdrant_client.query_points(
            collection_name="SkincareGPT_768",
            query=create_embedding_768(query),
            limit=5,
            query_filter=models.Filter(
                should=[models.FieldCondition(
                    key=k, match=models.MatchValue(value=v)) for k, v in should_filters],
                must=[models.FieldCondition(
                    key=k, match=models.MatchValue(value=v)) for k, v in must_filters]
            )
        )

        # join query results
        points = qdrant_res.points
        points.sort(key=lambda x: x.score, reverse=True)
        result_points = points + ingredient_points

        # get reviews, products and ingredients
        reviews, products, ingredients = await self._process_recommend_results(result_points, 1)

        # update context
        self.llm_ctx.set_product_ids([p.product_id for p in products])
        self.llm_ctx.set_review_ids([r.review_id for r in reviews])

        # rewrite response
        return await self.llm_service.generate_recommend_response(
            query, sentiment, products, reviews, ingredients
        )

    async def _process_search_results(self, points: List[models.ScoredPoint], limit:int, sentiment: Literal['neutral', 'positive', 'negative']):
        """Process search results to get products, reviews, and ingredients."""
        # Sort by score
        points.sort(key=lambda x: x.score, reverse=True)
        
        # Extract product IDs
        product_ids = []
        for p in points[:limit]:
            product_ids.append(p.payload.get("product_id"))
        
        # Get product details
        async with AsyncSession(async_engine) as session:
            products = await session.execute(
                select(SephoraProduct).filter(
                    SephoraProduct.product_id.in_(product_ids)).order_by(SephoraProduct.product_id))
            products = products.scalars().all()
        
        # Get reviews
        reviews = []
        async with AsyncSession(async_engine) as session:
            if sentiment == "neutral":
                for product_id in product_ids:
                    review = await session.execute(
                        select(SephoraReview).filter(
                            SephoraReview.product_id == product_id).order_by(SephoraReview.helpfulness.desc()).limit(1))
                    reviews += review.scalars().all()
            else:
                for product_id in product_ids:
                    review = await session.execute(
                        select(SephoraReview).filter(
                            SephoraReview.product_id == product_id).where(
                                SephoraReview.is_recommended == (sentiment == 'positive')).order_by(SephoraReview.helpfulness.desc()).limit(1))
                    reviews += review.scalars().all()
        
        # Extract ingredients
        ingredients = set()
        for p in products:
            ingredients.update(p.ingredients)
        

        self.llm_ctx.set_products(products)
        self.llm_ctx.set_reviews(reviews)
            
        return products, reviews, ingredients

    async def _process_knowledge_results(self, points: List[models.ScoredPoint], limit:int):
        """Process knowledge search results to get reviews, products, and ingredients."""
        # Sort by score
        points.sort(key=lambda x: x.score, reverse=True)
        
        # Extract review and product IDs
        review_ids = []
        product_ids = []
        for p in points[:limit]:
            review_ids.append(p.payload.get("review_id"))
            product_ids.append(p.payload.get("product_id"))
        
        # Get review and product details
        async with AsyncSession(async_engine) as session:
            reviews = await session.execute(
                select(SephoraReview).filter(
                    SephoraReview.review_id.in_(review_ids)).order_by(SephoraReview.product_id))
            reviews = reviews.scalars().all()
            
            products = await session.execute(
                select(SephoraProduct).filter(
                    SephoraProduct.product_id.in_(product_ids)).order_by(SephoraProduct.product_id))
            products = products.scalars().all()
        
        # Extract ingredients
        ingredients = set()
        for p in products:
            ingredients.update(p.ingredients)
        
        self.llm_ctx.set_products(products)
        self.llm_ctx.set_reviews(reviews)
            
        return reviews, products, ingredients
    
    async def _process_recommend_results(self, points: List[models.ScoredPoint], limit:int):
        # Extract reviews and products
        review_ids = []
        product_ids = []

        for p in points[:limit]:
            review_id = p.payload.get("review_id")
            product_id = p.payload.get("product_id")
            
            if review_id:
                review_ids.append(review_id)
            if product_id:
                product_ids.append(product_id)
        
        async with AsyncSession(async_engine) as session:
            reviews = None
            if review_ids:
                reviews = await session.execute(
                    select(SephoraReview).filter(
                        SephoraReview.review_id.in_(review_ids)).order_by(SephoraReview.product_id))
                reviews = reviews.scalars().all()
            
            products = None
            if product_ids:
                products = await session.execute(
                    select(SephoraProduct).filter(
                        SephoraProduct.product_id.in_(product_ids)).order_by(SephoraProduct.product_id))
                products = products.scalars().all()
        
        ingredients = set()
        for p in products:
            ingredients.update(p.ingredients)
        
        self.llm_ctx.set_products(products)
        self.llm_ctx.set_reviews(reviews)
            
        return reviews, products, ingredients
