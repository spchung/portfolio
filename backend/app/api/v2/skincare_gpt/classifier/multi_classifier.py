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
        kTurnUserQueries = "\n".join([f"User: {chat.user_query}\nAssistant: {chat.assistant_response}" for chat in chatHistory if hasattr(chat, 'assistant_response')])
        previous_intent = getattr(self.llm_context, 'current_intent', None)
        previous_topic = getattr(self.llm_context, 'current_topic', None)
        
        prompt = f"""You are an AI assistant that classifies user queries into the following intents:
        1. **chat** - casual conversation unrelated to products, reviews, or skincare knowledge.
        2. **search** - searching for a product, product category, or reviews of a product.
        3. **knowledge** - asking about reviews, ingredients, or general skincare knowledge.
        4. **recommend** - asking about product recommendations for specific skin types, concerns, or ingredients.
        
        IMPORTANT: When determining intent, consider CONTEXT CONTINUITY. If the user is clearly continuing on the same topic as before, maintain the previous intent rather than assigning a new one.
        
        Previous intent: {previous_intent if previous_intent else "None"}
        Previous topic: {previous_topic if previous_topic else "None"}
        
        Use the running summary of previous messages and recent user-assistant exchanges to classify the NEW user query.
        
        Context continuity indicators:
        - Pronouns without clear new references (it, this, that, these, they)
        - Short queries building on previous information
        - Questions asking for elaboration without specifying a new topic
        - Comparative questions (better, worse, vs, compared to) without introducing entirely new products
        
        Running Summary:
        {runningSummary if runningSummary else "No running summary available"}
        
        Recent Conversation:
        {kTurnUserQueries}
        
        New User Query:
        {userQuery}
        
        **Instructions:** 
        1. First, determine if this query is continuing the previous conversation topic or introducing a new one.
        2. If continuing the same topic, retain the previous intent.
        3. If introducing a new topic, assign the appropriate new intent.
        4. Identify the topic being discussed (e.g., "retinol products", "moisturizer recommendations", "acne treatment").
        
        Return your answer in this format:
        Intent: [intent]
        Topic: [topic]"""
        
        response = self.llmClient.chat.completions.create(
            temperature=0,
            model=self.model,
            messages=[{"role": "system", "content": "You are an expert query classifier for a skincare ecommerce platform with strong context awareness."},
                    {"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.strip()
        
        # Parse the structured response
        intent_line = [line for line in result.split("\n") if line.startswith("Intent:")][0]
        topic_line = [line for line in result.split("\n") if line.startswith("Topic:")][0]
        
        intent_value = intent_line.replace("Intent:", "").strip()
        topic_value = topic_line.replace("Topic:", "").strip()
        
        # Store for future reference
        self.llm_context.current_intent = intent_value
        self.llm_context.current_topic = topic_value
        
        # Convert to your enum format
        intent_enum = INTENT_ENUM(intent_value)
        
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
            
        prompt = f"""
        You are evaluating whether a user's query in a skincare e-commerce chat requires retrieving new product information or can be answered with existing conversation context.

        Previous conversation:
        {conversation_history}

        Previously retrieved product information:
        {previous_rag_results}

        New user query:
        "{query}"

        Determine if this query requires looking up NEW product information from the database.

        IMPORTANT: Users often phrase requests in ways that SEEM like follow-ups but actually require new information retrieval. Be generous in recommending new information retrieval.

        When to retrieve NEW information (default to this option):
        - User mentions ANY new product type, category, or concern
        - User's intent seems to be discovering products they haven't seen yet
        - User asks about recommendations or options
        - The query could benefit from fresh product details even if somewhat related to previous topics
        - When in doubt, prefer retrieving new information

        When to use EXISTING context (only in clear cases):
        - User is clearly asking about a specific product just mentioned by name
        - User is asking for clarification on information that was just provided
        - User is making a direct comparison between specific products already discussed

        First, identify if this appears to be a request that would benefit from product information.
        Then provide your decision: respond with either "CONTEXT_SUFFICIENT" or "NEED_NEW_INFORMATION".

        DEFAULT TO "NEED_NEW_INFORMATION" WHEN UNCERTAIN.
        """
        response = self.llmClient.chat.completions.create(
            temperature=0,
            model=self.model,
            messages=[{"role": "system", "content": "You are an expert query classifier for an skincare ecommerce platform."},
                    {"role": "user", "content": prompt}]
        )
        res = response.choices[0].message.content.strip()
        return res, prompt