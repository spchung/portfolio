from backend.app.api.v1.ecommerce_rag.query_classifier import RetailIntentClassifier
from app.db.postgres import engine
from sqlmodel import Session
from sqlalchemy.sql import text
from app.models.pg.product import Product
from backend.app.api.v1.ecommerce_rag.llm_rewrite import product_query_response

classifier = RetailIntentClassifier()
sess = Session(engine)
while True:
    try:
        q = input("ask me (type 'exit' to quit): ")
        if q.lower() == 'exit':
            print("Exiting the loop.")
            break

        label = classifier.classify(q)

        if str(label).strip() == "product_search":
            print("start product search")
            print("querying...")
            productIds = [1,2,3]
            q = f"SELECT * FROM product WHERE id IN ({','.join(map(str, productIds))}) order by id"
            rows = sess.exec(text(q)).all()
            pgProducts = [Product(**dict(row._mapping)) for row in rows]
            
        
            res = product_query_response(q, pgProducts)
            print("Response: ", res)
            
        elif label.strip() == "review_search":
            print("start review search")

        else:
            print("Start General Chat")
            ## general chat
    except Exception as e:
        print(f"An error occurred: {e}")
        raise e




    