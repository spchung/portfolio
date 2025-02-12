'''
Example Script from Gemini
'''


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import nltk
from nltk.corpus import stopwords
import re
from sklearn.preprocessing import normalize

# Download stopwords if you haven't already
try:
    stopwords.words('english')
except LookupError:
    nltk.download('stopwords')

def prepare_data_for_lda(products):
    """Prepares the data for LDA by combining titles and descriptions, cleaning, and removing stopwords."""
    documents = []
    for product in products:
        text = f"{product['title']} {product['description']}"
        text = re.sub(r'[^\w\s]', '', text.lower())  # Clean the text

        stop_words = set(stopwords.words('english'))
        text = ' '.join([word for word in text.split() if word not in stop_words])  # Remove stopwords

        documents.append(text)
    return documents

def perform_lda(documents, num_topics=5):
    """Performs LDA topic modeling on the given documents."""
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(documents)
    X_normalized = normalize(X, norm='l1', axis=1) #Normalize matrix to improve LDA performance

    lda = LatentDirichletAllocation(n_components=num_topics, random_state=0)
    lda.fit(X_normalized)  # Fit LDA with normalized matrix

    return lda, vectorizer

def display_topics(lda, vectorizer, num_words=10):
    """Displays the top words for each topic."""
    for topic_idx, topic in enumerate(lda.components_):
        print(f"Topic {topic_idx}:")
        top_words_idx = topic.argsort()[:-num_words - 1:-1]
        top_words = [vectorizer.get_feature_names_out()[i] for i in top_words_idx]
        print(" ".join(top_words))

# Example usage (replace with your actual product data)
products = [
    {"product_id": 1, "title": "CeraVe Moisturizing Cream", "description": "..."},
    {"product_id": 2, "title": "Neutrogena Hydro Boost Water Gel", "description": "..."},
    # ... more products
]

documents = prepare_data_for_lda(products)
lda_model, vectorizer = perform_lda(documents, num_topics=5)  # Adjust num_topics as needed

display_topics(lda_model, vectorizer)

# Manually interpret the topics to define subcategories