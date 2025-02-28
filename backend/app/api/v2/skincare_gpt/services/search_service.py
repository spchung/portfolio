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

class SearchService:

    def __init__(self, llm_service: LLMService):
        self.qdrant_client = qdarnt_client
        self.llm_service = llm_service
    
    async def product_search(
        self, 
        query: str, 
        sentiment: str, 
        context: SkincareGPTContext
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
        product_limit = 3

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
        context.set_product_ids([p.product_id for p in products])
        context.set_reviews([r.review_id for r in reviews])

        # rewrite response
        return await self.llm_service.generate_search_response(
            query, sentiment, products, ingredients
        )
    
    async def knowledge_search(self, query: str, sentiment: str, context: SkincareGPTContext):
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
        context.set_product_ids([p.product_id for p in products])
        context.set_reviews([r.review_id for r in reviews])

        # rewrite response
        return await self.llm_service.generate_knowledge_response(
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
            
        return reviews, products, ingredients