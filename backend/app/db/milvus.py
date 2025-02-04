from pymilvus import MilvusClient
import dotenv, os
dotenv.load_dotenv()
client = MilvusClient(uri=os.environ.get('MILVUS_URI', ''), token="root:Milvus")