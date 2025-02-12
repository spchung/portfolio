'''
prompts for context aware response
'''
from openai import OpenAI
import dotenv
dotenv.load_dotenv()
from app.models.product import Product
from app.models.review import Review
from typing import List
import asyncio

client = OpenAI()

def product_search_rewrite(userQuery, products: List[Product], stream=False, metaData={}):
    '''
    milvus product search llm rewrite
    '''

    context = ["\n".join([p.to_llm_context() for p in products])]
    prompt = f"""
    You are an AI assistant specializing in skincare products. Below is a user's question and relevant product information.
    Choose one to two products to recommend the user and briefly explain why.
    
    Context:
    {context}

    User Query:
    {userQuery}

    Based on the context, generate a helpful response that answers the user's question while recommending suitable products.
    """
    if not stream:
        response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "You are an expert skincare assistant."},
                        {"role": "user", "content": prompt}]
            )

        return response.choices[0].message.content.strip()
    
    # stream response
    return client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an expert skincare assistant."},
                {"role": "user", "content": prompt}],
        stream=True
    )

def review_search_rewrite(userQuery, reviews: List[Review], products: List[Product], stream=False):
    
    # zip reviews and products
    reviews = sorted(reviews, key=lambda x: x.parent_asin)
    products = sorted(products, key=lambda x: x.parent_asin)

    reviewContext = ["\n".join([r.to_llm_context() for r in reviews])]
    productContext = ["\n".join([p.to_llm_context() for p in products])]

    prompt = f"""
    You are an AI assistant specializing in skincare products. Below is a user's question and relevant review information.

    List of Reviews:
    {reviewContext}

    List of Products:
    {productContext}

    User Query:
    {userQuery}

    Based on the Revviews and products, rate the reviews and recommend suitable products.
    """ 

    if not stream:
        response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "You are an expert skincare assistant."},
                        {"role": "user", "content": prompt}]
            )

        return response.choices[0].message.content.strip()
    
    # stream response
    return client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an expert skincare assistant."},
                {"role": "user", "content": prompt}],
        stream=True
    )
