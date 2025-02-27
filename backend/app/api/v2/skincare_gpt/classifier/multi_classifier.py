'''
Running summary + Vector bases representation intent matching

Running Summary:
- keep i < n-k turns (older turns) into a summary
- keep k turns (newer turns) as is
- generate a summary using summary and k turnss 

Vector base representation:
- store 5-20 representative queries for each intent in a new vecotor collection

Work flow:
- get the last n turns in the conversation
- generate a summary of the conversation

branch(2):
    1. use the summary to query the vector collection
    2. zero shot classification of the summary

merge(2):
- output
'''
from app.api.v2.skincare_gpt.classifier.enum import INTENT_ENUM, SKIN_TYPE_ENUM
from app.api.v2.skincare_gpt.context.context_manager import SkincareGPTContextManager

# use running summary from context and next k rounds of conversation to produce a classification
import dotenv
dotenv.load_dotenv()
from openai import OpenAI

class MultiClassifier:
    model = "gpt-4o-mini"

    def __init__(self, llmCtxMgr: SkincareGPTContextManager):
        self.llmCtxMgr = llmCtxMgr
        self.llmClient = OpenAI()

    def intent(self, userQuery: str):
        runningSummary = self.llmCtxMgr.running_summary
        chatHistory = self.llmCtxMgr.history[-self.llmCtxMgr.k_chat_size:]
        kTurnUserQueries = "\n".join([f"User: {chat.user_query}" for chat in chatHistory])
        
        prompt = f"""You are an AI assistant that classifies user queries into the following intents:
        1. **chat** - casual conversation unrelated to products, reviews, or skincare knowledge.
        2. **search** - searching for a product, product category, or reviews of a product.
        3. **knowledge** - asking about skincare ingredients, routines, best practices, or product usage advice.

        Use the running summary of previous messages and recent user queries to classify the **new** user query:

        Running Summary:
        {runningSummary if runningSummary else "No running summary available"}

        Previous User Queries:
        {kTurnUserQueries}

        New User Query:
        {userQuery}

        **Instructions:** Respond with ONLY the category name: "chat", "search", or "knowledge"."""

        response = self.llmClient.chat.completions.create(
            temperature=0,
            model=self.model,
            messages=[{"role": "system", "content": "You are an expert query classifier for an skincare ecommerce platform."},
                    {"role": "user", "content": prompt}]
        )

        res = response.choices[0].message.content.strip()
        return INTENT_ENUM(res), prompt

    def skin_type(self, query):
        prompt = f"""
        You are an AI assistant that extracts information about the user's skin type from their messages.:
        1. **oily** - skin that is shiny, greasy, and prone to acne.
        2. **dry** - skin that is rough, scaly, and itchy.
        3. **combination** - skin that is oily in some areas and dry in others.
        4. **normal** - skin that is neither too dry nor too oily.

        **Instruction**
        - respond only with the skin type: "oily", "dry", "combination", or "normal".

        Query:
        {query}
        """
        response = self.llmClient.chat.completions.create(
            temperature=0,
            model=self.model,
            messages=[{"role": "system", "content": "You are an expert query classifier for an skincare ecommerce platform."},
                    {"role": "user", "content": prompt}]
        )
        res = response.choices[0].message.content.strip()
        return SKIN_TYPE_ENUM(res), prompt