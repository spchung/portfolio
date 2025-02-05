from openai import OpenAI
import dotenv
import numpy as np

dotenv.load_dotenv()
client = OpenAI()

model_1536 = "text-embedding-3-small"

def create_embedding_1536(text: str) -> np.array:
    try: 
        response = client.embeddings.create(
            input=text,
            model=model_1536
        )
        emb = response.data[0].embedding
        return np.array(emb).astype(np.float16)
    except Exception as e: 
        raise e