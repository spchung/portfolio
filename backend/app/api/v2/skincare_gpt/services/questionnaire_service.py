# app/api/v2/skincare_gpt/services/questionnaire_service.py

from typing import Literal
from app.api.v2.skincare_gpt.context.context_manager import SkincareGPTContext
from app.api.v2.skincare_gpt.services.llm_service import LLMService

class QuestionnaireService:
    """Service to handle user questionnaires"""
    
    def __init__(self, llm_service: LLMService, context: SkincareGPTContext):
        self.llm_service = llm_service
        self.context = context
    
    def get_next_question(self) -> Literal['concerns', 'skin_type'] | None:
        """
        Determine the next question to ask the user.
        
        Returns:
            The type of question to ask, or None if all questions have been asked
        """
        if self.context.user_preference_manager.user_preferences.all_attempted:
            return None
        return self.context.user_preference_manager.choose_question()
    
    def format_question(self, question_type: Literal['concerns', 'skin_type']):
        """
        Format the question for the user.
        
        Args:
            question_type: The type of question to format
            
        Returns:
            The formatted question
        """
        if question_type == 'concerns':
            return self.llm_service.paraphrase("What would you say are your main skin care concerns?")
        elif question_type == 'skin_type':
            return self.llm_service.paraphrase("What is your skin type? (dry, oily, combination, sensitive, normal)")
        else:
            return None