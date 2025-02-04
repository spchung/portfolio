import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.db.milvus import client
from pymilvus import DataType

productSchema = client.create_schema(
    auto_id=True,
    enable_dynamic_field = True,
)

productSchema.add_field(field_name='id', datatype=DataType.INT64, is_primary=True)
productSchema.add_field(field_name='parent_asin', datatype=DataType.VARCHAR, max_length=256)
productSchema.add_field(field_name='title', datatype=DataType.VARCHAR, max_length=1024)
# text-embedding-3-small
productSchema.add_field(field_name='title_vector', datatype=DataType.FLOAT16_VECTOR, dim=1536)

# Prepare index parameters
index_params = client.prepare_index_params()

index_params.add_index(
    field_name="id",
    index_type="STL_SORT"
)

index_params.add_index(
    field_name="title_vector", 
    index_type="AUTOINDEX",
    metric_type="COSINE"
)


client.create_collection(
    collection_name="product_title",
    schema=productSchema,
    index_params=index_params
)

res = client.get_load_state(
    collection_name="product_title"
)