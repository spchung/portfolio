import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from app.core.preprocessing.embedding.open_ai import create_embedding_1536
from app.db.postgres import engine
from sqlmodel import Session
from sqlalchemy.sql import text
from app.models.review import Review
from app.db.milvus import client

collection_name = "review"

res = client.get_collection_stats(collection_name)
print(f"{collection_name} has {res['row_count']} rows.")
