'''
RAG - Product search

Query behaviour - Hybrid:
Step 1: keyword parse
    - parse keywords used in direct query againt the database. e.g. 'laptop', 'price' ... etc
Step 2:
    - fuzzy vector search using description of needs. e.g. "good for student", "suitable for childdren" ... etc
'''

from app.db.milvus import client