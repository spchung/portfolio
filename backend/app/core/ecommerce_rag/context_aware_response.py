'''
prompts for context aware response
'''
from openai import OpenAI
import dotenv
dotenv.load_dotenv()
from app.models.product import Product
from typing import List

client = OpenAI()

def product_query_response(userQuery, products: List[Product]):

    context = ["\n".join([p.to_llm_context() for p in products])]

    '''
    milvus product search context aware response
    '''
    prompt = f"""
    You are an AI assistant specializing in skincare products. Below is a user's question and relevant product information.
    
    Context:
    {context}

    User Query:
    {userQuery}

    Based on the context, generate a helpful response that answers the user's question while recommending suitable products.
    """

    response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an expert skincare assistant."},
                    {"role": "user", "content": prompt}]
        )

    return response.choices[0].message.content.strip()
