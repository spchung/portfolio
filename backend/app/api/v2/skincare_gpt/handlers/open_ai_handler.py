from fastapi import HTTPException
from openai import OpenAI
from app.db.redis import r
import asyncio, json
from .interface import I_EcommerceRag
from app.api.v2.skincare_gpt.vector_store.qdrant import QdrantStoreService
from app.core.preprocessing.embedding.open_ai import create_embedding_768
from app.api.v2.skincare_gpt.context.context_manager import SkincareGPTContextManager, ChatHistory
from app.api.v2.skincare_gpt.classifier.intent_classifier import IntentClassifier


import dotenv
dotenv.load_dotenv()

class OpenAIHandler():
    def __init__(self, model="chatgpt-4o-latest"):
        self.client = OpenAI()
        self.model = model
        self.qdrant = QdrantStoreService(collection_name="SkincareGPT_768")
        self.llmCtxMgr = SkincareGPTContextManager('test-session')
        self.intentClassifier = IntentClassifier(self.llmCtxMgr)

    def query_vector(self, query):
        emb = create_embedding_768(query)
        res = self.qdrant.search(emb)
        return res
    
    async def chat(self, query):
        # 0. begin 
        self.llmCtxMgr.start_response()
        
        # 1. classify intent
        intent, clsPrompt = self.intentClassifier.classify(query)
        self.llmCtxMgr.last_prompt = clsPrompt

        # start chat history
        chatHistory = ChatHistory()
        chatHistory.user_query = query
        chatHistory.user_intent = intent.value
        
        # TODO: handle by response
        products = None
        reviews = None
        response = self.create_completions(query, True)

        totalResponseTokens = 0
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                totalResponseTokens += len(content)
                full_response += content
                yield content
            await asyncio.sleep(0)

        # post response ctx log
        chatHistory.response = full_response
        
        # log total token
        chatHistory.complete()

        self.llmCtxMgr.end_response(token_count=totalResponseTokens)
        self.llmCtxMgr.add_chat_history(chatHistory)
        self.llmCtxMgr.metadata.last_query_intent = intent.value
        self.llmCtxMgr.metadata.products = products
        self.llmCtxMgr.metadata.reviews = reviews

        r.set(self.llmCtxMgr.session_id, self.llmCtxMgr.serialize())
    
    def create_completions(self, user_query: str, stream=False):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful skincare assistant."},
                    {"role": "user", "content": user_query}],
            stream=stream  # Enable streaming
        )
        return response

    def get_context_snapshot(self):
        try:
            jsonString = r.get(self.llmCtxMgr.session_id)
            return json.loads(jsonString)
        except Exception as e:
            raise HTTPException(status_code=404, detail="Session not found")
