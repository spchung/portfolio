import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from app.core.preprocessing.embedding.open_ai import create_embedding_1536
from app.db.postgres import engine
from sqlmodel import Session
from sqlalchemy.sql import text
from app.models.review import Review
from app.db.milvus import client

collection_name = "review"

def reveiw_to_milvus_collection_item(review:Review):
    reviewTitleEmbedding = create_embedding_1536(review.title)
    reviewReviewEmbedding = create_embedding_1536(review.text)

    return {
        "id": review.id,
        "parent_asin": review.parent_asin,
        "title": review.title,
        "title_vector": reviewTitleEmbedding,
        "review": review.text[:4095],
        "review_vector": reviewReviewEmbedding
    }

q = input(f"Are you sure you want to to dump into the collection ({collection_name})? (y/n): ")
if q.lower() == "n":
    res = client.get_collection_stats(collection_name)
    print(f"{collection_name} has {res['row_count']} rows.")
    print("Did nothing.")
    sys.exit()

with Session(engine) as sess:
    resp = sess.exec(text("SELECT * FROM review")).all()
    batchLimit = 5
    batch = []
    for item in resp:
        if len(batch) == batchLimit:
            client.upsert(collection_name=collection_name, data=batch)
            print(f"Inserted {len(batch)} rows into {collection_name}.")
            batch = []
        else:    
            batch.append(reveiw_to_milvus_collection_item(Review(**dict(item._mapping))))

    if len(batch) > 0:
        client.upsert(collection_name=collection_name, data=batch)
        print(f"Inserted {len(batch)} rows into {collection_name}.")
    