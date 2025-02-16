import asyncio, json
from .llm_handlers.open_ai_handler import OpenAIHandler
from app.api.v1.ecommerce_rag.context.context import ChatHistory, EcommerceRagContextManager
from app.db.redis import r

limit = 1
llmCtxMgr = EcommerceRagContextManager(session_id="test")

async def get_context_snapshot(session_id: str):
    # TODO: context session manager
    jsonString = r.get(session_id)
    return json.loads(jsonString)

async def generate_streaming_response(user_query: str):    
    chaHistory = ChatHistory()
    handler = OpenAIHandler()
    
    llmCtxMgr.start_response()
    chaHistory.user_query = user_query

    queryLabel = handler.classify_query_v2(user_query)
    chaHistory.user_intent = queryLabel

    # metadata return
    products = None
    reviews = None

    if queryLabel == 'product_search':
        query, products = await handler.search_product_title(user_query, limit=1)
        response = handler.product_search_rewrite(query, products, stream=True)
    
    elif queryLabel == 'review_search':
        query, reviews, products = await handler.search_review(user_query, limit=5)
        response = handler.review_search_rewrite(query, reviews, products, stream=True)
    
    elif queryLabel == 'review_of_product':
        '''
        TODO:
        1. get last mentioned products (pg) from the context manager
        2. query reviews of the product (pg)
        3. prompt for rewrite
        '''
        response = handler.create_completions("Tell the user: 'This feature is not ready yet, sorry :('", stream=True)
    
    else:
       response = handler.create_completions(user_query, stream=True)

    totalResponseTokens = 0
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            totalResponseTokens += len(content)
            full_response += content
            yield content
        await asyncio.sleep(0)

    # log response
    chaHistory.response = full_response
    
    # log total token
    chaHistory.complete()

    # metadata register
    llmCtxMgr.end_response(token_count=totalResponseTokens)
    llmCtxMgr.add_chat_history(chaHistory)
    llmCtxMgr.metadata.last_query_intent = queryLabel
    llmCtxMgr.metadata.products = products
    llmCtxMgr.metadata.reviews = reviews

    # store context in redis
    r.set(llmCtxMgr.session_id, llmCtxMgr.serialize())