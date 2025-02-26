from app.db.postgres import Session, engine
from sqlalchemy import select
from app.models.pg.metedata import Metadata
import spacy
from spacy.tokens import Span
from spacy.language import Language
from typing import List, Dict, Tuple

'''
Use list of entitiy stores in metadata.group = 'ner_entity' 
'''

def get_ner_entities():
    with Session(engine) as session:
        entities = session.exec(select(Metadata).where(Metadata.group == 'ner_entity'))
        entities = entities.scalars().all()
        entity_dict = {}
        for entity in entities:
            entity_dict[entity.key] = entity.values
    return entity_dict


entities = get_ner_entities()

def setup_skin_condition_tagger() -> spacy.language.Language:
    try:
        nlp = spacy.load("en_core_web_md")
    except OSError:
        # Fallback to smaller model if medium model not available
        try:
            nlp = spacy.load("en_core_web_sm")
            print("Using smaller spaCy model. For better results, install en_core_web_md.")
        except OSError:
            # Provide instructions if no models are installed
            raise OSError(
                "No spaCy models found. Please install one with:\n"
                "python -m spacy download en_core_web_sm\n"
                "or\n"
                "python -m spacy download en_core_web_md"
            )
    
    @Language.component("skincare_gpt_tagger")
    def skincare_gpt_tagger(doc):
        matches = []
        
        # Process each token in the document
        for token_idx, token in enumerate(doc):
            # Check if token or token span matches any of our custom terms
            for category, terms in entities.items():
                for term in terms:
                    term_tokens = term.lower().split()
                    
                    # Single token match
                    if len(term_tokens) == 1 and token.text.lower() == term.lower():
                        start = token_idx
                        end = token_idx + 1
                        span = Span(doc, start, end, label=category)
                        matches.append(span)
                    
                    # Multi-token match
                    elif len(term_tokens) > 1 and token_idx + len(term_tokens) <= len(doc):
                        potential_match = doc[token_idx:token_idx + len(term_tokens)]
                        if potential_match.text.lower() == term.lower():
                            span = Span(doc, token_idx, token_idx + len(term_tokens), label=category)
                            matches.append(span)
        
        # Filter overlapping spans, preferring longer and more specific categories
        filtered_matches = filter_overlapping_spans(matches)
        
        # Set entities
        doc.ents = filtered_matches
        return doc

    nlp.add_pipe("skincare_gpt_tagger", last=True)
    return nlp

def filter_overlapping_spans(spans: List[Span]) -> List[Span]:
    """
    Filter out overlapping spans, keeping the ones with higher priority.
    Priority: SKIN_CONDITION > SKIN_DESCRIPTION > BODY_PART > PRODUCT_INGREDIENT
    
    Args:
        spans: List of spaCy Span objects
    
    Returns:
        Filtered list of spans with no overlaps
    """
    if not spans:
        return []
    
    # Define category priorities (lower number = higher priority)
    priority = {
        "SKIN_CONDITION": 1, 
        "SKIN_DESCRIPTION": 2, 
        "PRODUCT_INGREDIENT": 3,
        "BODY_PART": 4, 
    }
    
    # Sort spans by start index, then by length (longer first), then by priority
    sorted_spans = sorted(
        spans, 
        key=lambda span: (
            span.start, 
            -len(span), 
            priority.get(span.label_, 999)
        )
    )
    
    # Filter out overlapping spans
    filtered = []
    last_end = -1
    
    for span in sorted_spans:
        if span.start >= last_end:
            filtered.append(span)
            last_end = span.end
    
    return filtered

### MAIN FUNCTION ###
def rule_based_tag(text: str) -> Tuple[spacy.tokens.Doc, Dict]:
    """
    Tag skin conditions, descriptions, and related terms in text.
    
    Args:
        text: Input text to analyze
        custom_terms: Optional dictionary of custom terms to identify
    
    Returns:
        tuple: (processed spaCy Doc, dictionary of extracted entities by category)
    """
    nlp = setup_skin_condition_tagger()
    doc = nlp(text)
    
    # Organize entities by category
    results = {
        "SKIN_CONDITION": [],
        "SKIN_DESCRIPTION": [],
        "BODY_PART": [],
        "PRODUCT_INGREDIENT": []
    }
    
    for ent in doc.ents:
        if ent.label_ in results:
            results[ent.label_].append({
                "text": ent.text,
                "start": ent.start_char,
                "end": ent.end_char
            })
    
    return doc, results