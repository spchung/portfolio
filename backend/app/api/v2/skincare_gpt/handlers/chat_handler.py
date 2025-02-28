import asyncio
from app.db.redis import r
from typing import AsyncGenerator
from app.api.v2.skincare_gpt.classifier.enum import INTENT_ENUM, SKIN_TYPE_ENUM
from app.core.preprocessing.embedding.open_ai import create_embedding_768
from app.api.v2.skincare_gpt.context.context_manager import ChatHistory, SkincareGPTContextManager
from app.api.v2.skincare_gpt.classifier.multi_classifier import MultiClassifier
from app.core.ner_topic_extract.rule_based.rule_based_ner import rule_based_tag
from app.api.v2.skincare_gpt.services.llm_service import LLMService
from app.api.v2.skincare_gpt.services.ner_service import NERService
from app.api.v2.skincare_gpt.services.questionnaire_service import QuestionnaireService
from app.api.v2.skincare_gpt.services.search_service import SearchService
from app.api.v2.skincare_gpt.services.sentiment_service import SentimentService

import dotenv
dotenv.load_dotenv()

context_manager = SkincareGPTContextManager()

class ChatHandler:
    def __init__(self, session_id: str = None):
        if not session_id:
            self.session_id = context_manager.generate_session_id()
        else: 
            self.session_id = session_id

        self.llm_ctx = context_manager.get_context(self.session_id)

        self.context_manager = context_manager
        self.llm_service = LLMService(model='chatgpt-4o-latest', classifier_model='gpt-4o-mini')
        self.ner_service = NERService()
        self.questionnaire_service = QuestionnaireService(llm_service=self.llm_service, context=self.context_manager.get_context(self.session_id))
        self.search_service = SearchService(self.llm_service)
        self.sentiment_service = SentimentService(self.llm_service)
        self.multi_calssifier = MultiClassifier(self.llm_ctx)
    
    async def chat(self, query: str) -> AsyncGenerator[str, None]:
        # response start
        self.llm_ctx.start_response()
        
        # Classify intent
        intent, cls_prompt = self.multi_calssifier.intent(query)
        self.llm_ctx.last_prompt = cls_prompt
        
        # Extract named entities
        entities = self.ner_service.extract_entities(query)
        self.llm_ctx.register_named_entities(entities)
        
        # Create chat history entry
        chat_history = ChatHistory()
        chat_history.user_query = query
        chat_history.user_intent = intent.value

        # Handle based on intent
        if intent == INTENT_ENUM.SEARCH:
            response = await self.search_service.product_search(
                query, 
                self.sentiment_service.analyze(query),
                self.llm_ctx
            )
        elif intent == INTENT_ENUM.KNOWLEDGE:
            response = await self.search_service.knowledge_search(
                query, 
                self.sentiment_service.analyze(query),
                self.llm_ctx
            )
        elif intent == INTENT_ENUM.RECOMMEND:
            response = await self.search_service.recommend_search(
                query, 
                self.sentiment_service.analyze(query),
                self.llm_ctx
            )
        else:
            response = self.llm_service.create_completions(query, stream=True, temperature=0.5)
        
        # collect response metadata
        total_response_tokens = 0
        full_response = ""
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                total_response_tokens += len(content)
                full_response += content
                yield content
            await asyncio.sleep(0)
        
        # Update chat history
        chat_history.response = full_response
        chat_history.complete()
        
        # Update context
        self.llm_ctx.end_response(token_count=total_response_tokens)
        self.llm_ctx.add_chat_history(chat_history)
        self.llm_ctx.metadata.last_query_intent = intent.value
        
        # Save context to Redis
        r.set(self.llm_ctx.session_id, self.llm_ctx.serialize())