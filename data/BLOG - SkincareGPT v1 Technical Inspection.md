SkincareGPT v1 is an initial attempt at creating a LLM powered chat agent that connect users to a selection of products and their reviews through careful conversational design.

The overall infrastructure:

Frontend
\- chat interface with product and metadata display

Backend:
\- api:
\- fastapi
\- vector database:
\- milvus
\- relational
\- postgres
\- context store
\- redis

Database schema:
pg:
\- product \-\> **title**
\- review \-\> title\, review
vector db:
\- product\_title \-\> stores the vector representation of pg\.product\.title
\- reviews \-\> store vector representation of pg\.review\.title and pg\.review\.review
redis:
\- stores serialised context against session\_id

Conversational Design Components:
1\. Intent Matcher \-\> zero\-shot text classification with openai\.o4\-mini model
\- uses current session context manager to get required info for classification
1\. running summary
2\. last k turns of user query
2\. pg \+ milvus workflow
\- mixed query workflow
1\. user query is embedded and queried against the vector db
2\. top n results from milvus then used to fetch structured data from pg
3\. provide pg result entities as context to LLM rewrite
4\. return rewrite result to frontend
3\. Context Manager
\*\* i = current turn; k = preservation limit; n = total turns
\*\* k refers to the number of turns that should be kept in tact in the context (conversation context window length)
\- keeps track of
1\. chat history \(length k\) \- each item in this list is a full conversation turn \(query \+ response\)
2\. running summary \- a short summary of old \(i \> n\-k\) messages \-\> think of this as a condensation of older messages
3\. metadata \- collection of useful metrics \(last response token count\, elapsed seconds \.\.\. etc\)
4\. Handlers
\- interface and implementations of LLM class functions that satisfies the requirements of the RAG features
\- can have multiple implementations for different LLM vendors
\- includes prompts

<br>
Data: Sourced from UCSD Amazon database
[https://jmcauley.ucsd.edu/data/amazon/](https://jmcauley.ucsd.edu/data/amazon/)