from app.core.ner_topic_extract.rule_based.rule_based_ner import rule_based_tag

class NERService:
    """Service to handle named entity recognition (NER)"""
    
    def extract_entities(self, text: str):
        res = rule_based_tag(text)
        return res