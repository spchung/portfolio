from app.db.postgres import Session, engine
from sqlalchemy import select
from app.models.pg.metedata import Metadata
from pydantic import BaseModel
import spacy
from spacy.tokens import Span
from spacy.language import Language
from typing import List, Dict, Tuple
from app.core.ner_topic_extract.rule_based.fuzzy_match import fuzzy_search
from app.models.api.ner import EntityResults

'''
Use list of entitiy stores in metadata.group = 'ner_entity' 
'''

def get_ner_entities():
    with Session(engine) as session:
        keys = ['SKIN_CONDITION', 'SKIN_DESCRIPTION', 'BODY_PART']  # Replace with your list of keys
        entities = session.exec(select(Metadata).where(Metadata.group == 'ner_entity', Metadata.key.in_(keys)))
        entities = entities.scalars().all()

        top_30_ingredients = session.exec(select(Metadata).where(Metadata.group == 'graph', Metadata.key == 'TOP_30_INGREDIENTS'))
        top_30_ingredients = top_30_ingredients.scalars().all()
        
        all_ents = entities + top_30_ingredients
        entity_dict = {}
        for entity in all_ents:
            entity_dict[entity.key] = entity.values

        # rename 
        entity_dict['PRODUCT_INGREDIENT'] = entity_dict.pop('TOP_30_INGREDIENTS')
    return entity_dict

entities = get_ner_entities()

def setup_skin_condition_tagger():
    stop_words = None
    try:
        nlp = spacy.load("en_core_web_md")
        stop_words = nlp.Defaults.stop_words
    except OSError:
        # Fallback to smaller model if medium model not available
        try:
            nlp = spacy.load("en_core_web_sm")
            stop_words = nlp.Defaults.stop_words
            print("Using smaller spaCy model. For better results, install en_core_web_md.")
        except OSError:
            # Provide instructions if no models are installed
            raise OSError(
                "No spaCy models found. Please install one with:\n"
                "python -m spacy download en_core_web_sm\n"
                "or\n"
                "python -m spacy download en_core_web_md"
            )
    return nlp, stop_words

def skincare_gpt_tagger(doc, stop_words):
    matches = [] # list of {label: "SKIN_CONDITION", value: "acne"}

    # filter stop words
    token_indices = [i for i, token in enumerate(doc) if not token.text in stop_words]
    # filter punctuation
    token_indices = [i for i in token_indices if not doc[i].is_punct]

    # Process each token in the document
    for token_idx in token_indices:
        token = doc[token_idx]

        # Check if token or token span matches any of our custom terms
        for category, terms in entities.items():
            results = fuzzy_search(token.text.lower(), terms, threshold=85)

            # only allow one match per token
            if results:
                results.sort(key=lambda x: x[1], reverse=True)
                matched_value, score = results[0]
                span = { "label": category, "value": matched_value}
                matches.append(span)

    # Filter overlapping spans, preferring longer and more specific categories
    filtered_matches = filter_overlapping_spans(matches)
    
    # Set entities
    return filtered_matches

def filter_overlapping_spans(entities: List[dict]) -> List[dict]:
    """
    Filter out duplicate entities, keeping the ones with higher priority.
    Priority: SKIN_CONDITION > SKIN_DESCRIPTION > BODY_PART > PRODUCT_INGREDIENT
    
    Args:
        entities: List of dictionaries with 'label' and 'value' keys
    
    Returns:
        Filtered list of entities with no duplicates, prioritized by entity type
    """
    if not entities:
        return []
    
    # Define category priorities (lower number = higher priority)
    priority = {
        "SKIN_CONDITION": 1, 
        "SKIN_DESCRIPTION": 2, 
        "PRODUCT_INGREDIENT": 3,
        "BODY_PART": 4, 
    }
    
    # Create a unique set of values to handle duplicates
    unique_values = set()
    filtered = []
    
    # Sort entities by priority
    sorted_entities = sorted(
        entities, 
        key=lambda entity: priority.get(entity['label'], 999)
    )
    
    # Keep highest priority entity for each unique value
    for entity in sorted_entities:
        value = entity['value'].lower()  # Case-insensitive comparison
        if value not in unique_values:
            filtered.append(entity)
            unique_values.add(value)
    
    return filtered

### MAIN FUNCTION ###
def rule_based_tag(text: str) -> EntityResults:
    """
    Tag skin conditions, descriptions, and related terms in text.
    
    Args:
        text: Input text to analyze
        custom_terms: Optional dictionary of custom terms to identify
    
    Returns:
        tuple: (processed spaCy Doc, dictionary of extracted entities by category)
    """
    nlp, stopword = setup_skin_condition_tagger()
    doc = nlp(text) # List[{label: "SKIN_CONDITION", value: "acne"}]
    matches = skincare_gpt_tagger(doc, stopword)
    
    # Organize entities by category
    results = {
        "SKIN_CONDITION": [],
        "SKIN_DESCRIPTION": [],
        "BODY_PART": [],
        "PRODUCT_INGREDIENT": []
    }
    
    for match in matches:
        results[match["label"]].append(match["value"])

    return EntityResults(**results)
