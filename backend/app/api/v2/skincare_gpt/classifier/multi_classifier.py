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

import textwrap
from app.api.v2.skincare_gpt.classifier.enum import INTENT_ENUM, SKIN_TYPE_ENUM
from app.api.v2.skincare_gpt.context.context_manager import SkincareGPTContext

# use running summary from context and next k rounds of conversation to produce a classification
import dotenv
dotenv.load_dotenv()
from openai import OpenAI

class MultiClassifier:
    model = "gpt-4o-mini"

    def __init__(self, llm_context: SkincareGPTContext):
        self.llm_context = llm_context
        self.llmClient = OpenAI()

    def intent(self, userQuery: str):
        runningSummary = self.llm_context.running_summary
        chatHistory = self.llm_context.history[-self.llm_context.k_chat_size:]
        kTurnUserQueries = "\n".join([f"User: {chat.user_query}" for chat in chatHistory])
        
        prompt = f"""You are an AI assistant that classifies user queries into the following intents:
        1. **chat** - casual conversation unrelated to products, reviews, or skincare knowledge.
        2. **search** - searching for a product, product category, or reviews of a product.
        3. **knowledge** - asking about reviews, ingredients, or general skincare knowledge.
        4. **recommend** - asking about product recommendations for specific skin types, concerns, or ingredients.

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

    def intentv2(self, userQuery: str):
        runningSummary = self.llm_context.running_summary
        chatHistory = self.llm_context.history[-self.llm_context.k_chat_size:]
        kTurnUserQueries = "\n".join([f"User: {chat.user_query}\nBot: {chat.assistant_response}" for chat in chatHistory if hasattr(chat, 'assistant_response')])
        previous_intent = getattr(self.llm_context, 'current_intent', None)
        previous_topic = getattr(self.llm_context, 'current_topic', None)
        
        prompt = f"""You are an AI assistant that classifies user queries into the following intents:
        1. **chat** - casual conversation unrelated to products, reviews, or skincare knowledge.
        2. **search** - searching for a product, product category, or reviews of a product.
        3. **knowledge** - asking about reviews, ingredients, or general skincare knowledge.
        
        **Instructions:**
        - Respond with ONLY the category name: "chat", "search", or "knowledge"
        - Take into account the previous conversation if it is relevant to the current query.

        Previous conversation:
        {kTurnUserQueries}
        
        New User Query:
        {userQuery}

        """
        
        response = self.llmClient.chat.completions.create(
            temperature=0,
            model=self.model,
            messages=[{"role": "system", "content": "You are an expert query classifier for a skincare ecommerce platform with strong context awareness."},
                    {"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.strip()
        
        # Parse the structured response
        # intent_line = [line for line in result.split("\n") if line.startswith("Intent:")][0]
        # topic_line = [line for line in result.split("\n") if line.startswith("Topic:")][0]
        
        # intent_value = intent_line.replace("Intent:", "").strip()
        # topic_value = topic_line.replace("Topic:", "").strip()
        
        # Store for future reference
        # self.llm_context.current_intent = intent_value
        # self.llm_context.current_topic = topic_value
        
        # Convert to your enum format
        intent_enum = INTENT_ENUM(result)
        
        return intent_enum, prompt

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
    
    def context_check(self, query:str):
        chatHistory = self.llm_context.history[-self.llm_context.k_chat_size:]
        conversation_history = "\n".join([f"User: {chat.user_query}\nAssistant: {chat.response}" for chat in chatHistory])


        def find_review(product_id):
            for review in self.llm_context.reviews:
                if review.product_id == product_id:
                    return review
            return None

        previous_rag_results = ""
        for prod in self.llm_context.products:
            review = find_review(prod.product_id)
            if review:
                previous_rag_results += f"Product: {prod.product_name}\nReview: {review.review_text}\n\n"
            else:
                previous_rag_results += f"Product: {prod.product_name}\n\n"
            
        prompt = textwrap.dedent("""
        You are evaluating whether a user's query in a skincare e-commerce chat requires retrieving new product information or can be answered with existing conversation context.

        Previous conversation:
        {conversation_history}

        Previously retrieved product information:
        {previous_rag_results}

        New user query:
        "{query}"

        Analyze the query to determine if it can be answered using ONLY the information already available in the conversation history and previously retrieved data.

        Consider the following:
        1. Is the query referencing specific products/topics already mentioned in the conversation?
        2. Does the query use pronouns (it, this, these, they) that clearly refer to previously discussed items?
        3. Is the query asking for clarification or additional details about information already provided?
        4. Is the query comparing between options already presented?
        5. Is the query a simple follow-up that builds directly on the previous exchange?

        Requirements for using EXISTING context:
        - The query must be about entities/topics already explicitly present in the conversation
        - All information needed to provide a helpful response must be available in the context
        - The connection to previous context must be clear and unambiguous
        - The query is a clear follow-up that builds directly on the previous exchange

        Requirements for NEW information retrieval:
        - The query asks for recommendations or information not previously discussed
        - The query demonstrats a clear shift in topic or introduces new products
        - The query introduces entirely new products, ingredients, or skincare concerns
        - The query substantially shifts focus within a category (e.g., from dry skin moisturizers to acne treatments)
        - Essential information to answer the query is missing from current context

        Then provide your final decision: respond with either "CONTEXT_SUFFICIENT" or "NEED_NEW_INFORMATION".
        """
        ).format(
            conversation_history=conversation_history,
            previous_rag_results=previous_rag_results,
            query=query
        )
        
        response = self.llmClient.chat.completions.create(
            temperature=0,
            model=self.model,
            messages=[{"role": "system", "content": "You are an expert query classifier for an skincare ecommerce platform."},
                    {"role": "user", "content": prompt}]
        )
        res = response.choices[0].message.content.strip()
        if "CONTEXT_SUFFICIENT" in res:
            return "CONTEXT_SUFFICIENT", prompt
        else:
            return "NEED_NEW_INFORMATION", prompt