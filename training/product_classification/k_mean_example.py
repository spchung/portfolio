'''
Example Script from Gemini
'''

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sentence_transformers import SentenceTransformer  # Or any embedding model
import numpy as np

def cluster_products_by_embedding(products, num_clusters=5):
    """Clusters products based on embeddings of their titles and descriptions."""
    model = SentenceTransformer('all-MiniLM-L6-v2')  # Or your preferred model
    embeddings = model.encode([f"{p['title']} {p['description']}" for p in products])

    kmeans = KMeans(n_clusters=num_clusters, random_state=0, n_init = 10) # explicitly declaring n_init to suppress warning
    clusters = kmeans.fit_predict(embeddings)

    # Evaluate clustering (optional)
    silhouette_avg = silhouette_score(embeddings, clusters)
    print(f"Silhouette Score: {silhouette_avg}")

    return clusters

def assign_clusters_to_products(products, clusters):
    """Assigns cluster labels to products."""
    for i, product in enumerate(products):
        product['cluster'] = clusters[i]
    return products

# Example usage (replace with your actual product data)
products = [
    {"product_id": 1, "title": "CeraVe Moisturizing Cream", "description": "..."},
    {"product_id": 2, "title": "Neutrogena Hydro Boost Water Gel", "description": "..."},
    # ... more products
]

clusters = cluster_products_by_embedding(products, num_clusters=5)
products_with_clusters = assign_clusters_to_products(products, clusters)

# Analyze the clusters to define subcategories
for i in range(np.unique(clusters).shape[0]):
    print(f"Cluster {i}:")
    for product in [product for product in products_with_clusters if product['cluster'] == i]:
        print(f"  - {product['title']}")