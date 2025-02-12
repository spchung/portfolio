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

async def product_search_rewrite(userQuery, products: List[Product], stream=False):

    context = ["\n".join([p.to_llm_context() for p in products])]

    '''
    milvus product search context aware response
    '''
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
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an expert skincare assistant."},
                {"role": "user", "content": prompt}],
        stream=True
    )
    return response

async def review_search_rewrite(userQuery, reviews: List[Review], stream=False):
    pass

