Data: 2/18/25

SkincareGPT v1 is an initial attempt at creating a LLM powered chat agent that connect users to a selection of products and their reviews through careful conversational design. 

The core concept of connecting user queries to a product database using a vector store as an intermediary is successful. However, the features are not very good and will not be commercially viable.

Challenges:
1\. Generic answers:
While I implemented various intents like product\_search, review\_search, review\_of\_product\_search, and more, it is not enough to provide accurate answers to more in-depth user queries. The chatbot works well only when users ask generic questions like "Recommend me some face wash" or "What are the best reviewed face serum" but is not capable of giving more contextualised answers. 

I believe that significant improvements can be made with better conversational design and context management. However the nature of the dataset is likely to create a ceiling for the usefulness of this product. The data set is very diverse in terms of product variety (loose categories as everything is under the beauty category). This makes it hard to enhance RAG performance beyond basic semantic matching of user query against product title. Any further features like answering specific question about a class of product and recommend similar products difficult, as these features will have to take into consider the diversity of products. (Think about how much work it would take for the chatbot to learn specific and categorical information for EACH class of products in the db). 

Beyond technical challenges, this design is also not very viable from a business standpoint. Why would anyone want to interact with a chatbot if all it really does is to perform a poorly optimised fuzzy search on two tables? I believe the only viable way for this product to be worth implementing in real-life is by narrowing down the scope in terms of product category. Ideally the category is something that is very in-depth and not common knowledge. 

With a specific or "difficult" product category, RAG is more valuable because it can answer more curated questions from user reviews and supplementary knowledge banks. A great example is skincare - there are so many products out there with 
scientific names (think about ingredients in your exfoliator, sunscreen, and facial serum. Furthermore, everyone has different skin types and not everyone uses the same routine. Some people might need to avoid certain products because of their skin type. Additionally, there are soooo many companies making similar products, which makes it even harder to choose. 

In short, there are multiple layers of complexity when it comes to curating a skincare routine. For a person with no prior skincare knowledge, finding a routine that truly suit them is a non-trivial task. They would need to do a lot of research and read forums to come to an optimal solution. 

In SkincareGPT v2, I aim to focus on skin care products ONLY (using a sephora database from kaggle).

