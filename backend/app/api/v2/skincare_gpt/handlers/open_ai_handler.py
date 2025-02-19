from .interface import I_EcommerceRag
from openai import OpenAI
from app.api.v2.skincare_gpt.vector_store.qdrant import QdrantStoreService
from app.core.preprocessing.embedding.open_ai import create_embedding_768

import dotenv
dotenv.load_dotenv()

class OpenAIHandler():
    def __init__(self, model="chatgpt-4o-latest"):
        self.client = OpenAI()
        self.model = model
        self.qdrant = QdrantStoreService(collection_name="SkincareGPT_768")

    def query_vector(self, query):
        emb = create_embedding_768(query)
        res = self.qdrant.search(emb)
        return res