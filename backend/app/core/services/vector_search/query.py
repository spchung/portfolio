from typing import List
from app.db.milvus import client
from app.models.milvus import MilvusSearchResultItem

class MilvusCollectionService:
    def __init__(self, collection_name):
        self.client = client
        self.collection_name = collection_name

    def query(self, vectors, anns_field=None, top_k=5, limit=3) -> List[MilvusSearchResultItem]:
        res = self.client.search(
            self.collection_name, 
            anns_field=anns_field,
            data=vectors, 
            top_k=top_k,
            limit=limit
        )
        res = res[0]
        return [
            MilvusSearchResultItem(
                id=item['id'], 
                distance=item['distance']
            ) for item in res
        ]