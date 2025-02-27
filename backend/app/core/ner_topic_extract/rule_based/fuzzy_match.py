from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re

def fuzzy_search(query, dictionary, threshold=80):
    """
    Performs fuzzy search on a dictionary of terms, handling both single and multi-token queries.
    """
    # Clean and tokenize the query
    query = query.lower().strip()
    query_tokens = re.findall(r'\b\w+\b', query)
    
    results = []
    
    # Case 1: Single token query
    if len(query_tokens) == 1:
        # Simple ratio for exact matches and misspellings
        matches = process.extractBests(
            query, 
            dictionary, 
            scorer=fuzz.ratio, 
            score_cutoff=threshold,
            limit=1
        )
        for match, score in matches:
            if int(score) >= threshold:
                results.append((match, score, 'single_token'))
    
    # Case 2: Multi-token query
    else:
        # Token set ratio for when word order doesn't matter and there might be extra words
        token_set_matches = process.extractBests(
            query, 
            dictionary, 
            scorer=fuzz.token_set_ratio, 
            score_cutoff=threshold,
            limit=1
        )
        for match, score in token_set_matches:
            results.append((match, score, 'token_set'))
        
        # Token sort ratio for when word order might be different
        token_sort_matches = process.extractBests(
            query, 
            dictionary, 
            scorer=fuzz.token_sort_ratio, 
            score_cutoff=threshold,
            limit=1
        )
        for match, score in token_sort_matches:
            # Only add if not already in results with a higher score
            if not any(match == m and score <= s for m, s, _ in results):
                results.append((match, score, 'token_sort'))
        
        # Also check for partial token matches within multi-token terms
        # This helps when only part of a condition name is mentioned
        for token in query_tokens:
            if len(token) >= 3:  # Only check tokens of reasonable length
                partial_matches = process.extractBests(
                    token, 
                    dictionary, 
                    scorer=fuzz.partial_ratio, 
                    score_cutoff=max(threshold, 80),  # Higher threshold for partial matches
                    limit=3
                )
                for match, score in partial_matches:
                    # Only add if not already in results
                    if not any(match == m for m, _, _ in results):
                        results.append((match, score * 0.9, 'partial_token'))  # Slightly lower weight
    
    # Remove duplicates and sort by score
    unique_results = {}
    for match, score, match_type in results:
        if match not in unique_results or score > unique_results[match][0]:
            unique_results[match] = (score, match_type)
    
    # print(unique_results)

    # Return sorted results
    sorted_results = [(term, score) 
                      for term, (score, _) in unique_results.items()]
    sorted_results.sort(key=lambda x: x[1], reverse=True)
    return sorted_results