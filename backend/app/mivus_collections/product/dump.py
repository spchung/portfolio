import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from app.core.preprocessing.embedding.open_ai import create_embedding_1536
from app.db.postgres import engine
from sqlmodel import Session
from sqlalchemy.sql import text
from app.models.pg.product import Product
from app.db.milvus import client

collection_name = "product_title"

# dumps product data to milvus
def product_to_milvus_collection_item(product: Product):
    embedding = create_embedding_1536(product.title)

    return {
        "id": product.id,
        "parent_asin": product.parent_asin,
        "title": product.title,
        "title_vector": embedding
    }

q = input(f"Are you sure you want to to dump into the collection ({collection_name})? (y/n): ")
if q.lower() == "n":
    res = client.get_collection_stats(collection_name)
    print(f"{collection_name} has {res['row_count']} rows.")
    print("Did nothing.")
    sys.exit()

import time

with Session(engine) as sess:
    resp = sess.exec(text("SELECT * FROM product")).all()
    print(f"Total rows: {len(resp)}")
    batchLimit = 5
    batch = []
    looped = 0
    for item in resp:
        print(f"Processing row {item.id}")
        if len(batch) == batchLimit:
            client.upsert(collection_name=collection_name, data=batch)
            print(f"Inserted {len(batch)} rows into {collection_name}.")
            batch = []
        else:
            batch.append(product_to_milvus_collection_item(Product(**dict(item._mapping))))
        
        if looped % 5 == 0:
            time.sleep(45)
            print("sleeping...")
        
    if len(batch) > 0:
        client.upsert(collection_name=collection_name, data=batch)
        print(f"Inserted {len(batch)} rows into {collection_name}.")
