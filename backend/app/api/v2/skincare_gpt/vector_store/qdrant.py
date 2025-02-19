
from qdrant_client import QdrantClient, models

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
    
    def search(self, query_vector, top_k=5, filters: dict | None=None):

        conditions = None
        if not filters is None:
            conditions = []
            for key, value in filters.items():
                conditions.append(
                    models.FieldCondition(
                        key=key,
                        match=models.MatchValue(
                            value=value
                        )
                ))
        
        query_filter = None
        if not conditions is None:
            query_filter = models.Filter(
                conditions=conditions
            )
        
        return self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            query_filter=query_filter,
            # search_params=models.SearchParams(hnsw_ef=128, exact=False),
        )