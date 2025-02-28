from app.core.ner_topic_extract.rule_based.rule_based_ner import rule_based_tag
from app.models.api.ner import EntityResults
class NERService:
    """Service to handle named entity recognition (NER)"""
    
    def extract_entities(self, text: str) -> EntityResults:
        return rule_based_tag(text)