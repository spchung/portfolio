### Scripts to Generate custom sub-categories in generic product categories

e.g. generate more fine-grained categories for all products under 'All_Beuty'

### Challenges:
- no named sub-category
- zero-shot classification assumes a named list of category

### Solutions:
1. zero-shot
    - use NER to extract keywords from product title and description
    - then categorise 
    - PRO
        - named categories
    - CON:
        - depends heavily on NER entities


2. kNN based:
    - use title and description in latent space and perform knn
    - PRO:
        - latent space (embedded space) representation 
    - CON:
        - no named entity
