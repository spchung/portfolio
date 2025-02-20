
from qdrant_client import QdrantClient, models
from app.core.preprocessing.embedding.open_ai import create_embedding_768
from typing import List

client = QdrantClient(url="http://localhost:6333")

class QdrantStoreService:
    def __init__(self, collection_name):
        self.client = client
        self.collection_name = collection_name
        
        assert self.client is not None, "Qdrant client is not initialized"
        assert self.collection_name is not None, "Collection name is not set"


    def nearest_neighbor(self, query_vector, top_k=5):
        return self.client.query_points(
            collection_name=self.collection_name,
            query_vector=query_vector,
            top_k=top_k
        )
    
    async def search(self, raw_query, top_k=5, filters: dict = {}, match_all_filters=False) -> List[models.ScoredPoint]:
        queryVec = create_embedding_768(raw_query)
        if match_all_filters:
            query_filter=models.Filter(
                must=[models.FieldCondition(
                    key=k, match=models.MatchValue(value=v)) for k, v in filters.items()])
        else:
            query_filter=models.Filter(
                should=[models.FieldCondition(
                    key=k, match=models.MatchValue(value=v)) for k, v in filters.items()])
        
        result = self.client.query_points(
            collection_name=self.collection_name,
            query=queryVec,
            limit=top_k,
            query_filter=query_filter,
        )

        return [p for p in result.points]