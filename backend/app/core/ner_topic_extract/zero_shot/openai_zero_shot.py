from openai import OpenAI
import json

client = OpenAI()

def llm_ner(text):
    prompt = f"""Extract skincare entities from the following text. Return ONLY a JSON array with objects containing "text", "label", and "confidence".
    
    Labels to use:
    - INGREDIENT: skincare ingredients like hyaluronic acid, retinol, etc.
    - PRODUCT_TYPE: categories like sunscreen, serum, moisturizer, cleanser
    - SKIN_CONCERN: issues like acne, wrinkles, dry skin, oily skin
    - BRAND: brand names for skincare products
    
    Text: "{text}"
    
    JSON Output:"""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    try:
        result = json.loads(response.choices[0].message.content)
        return result.get("entities", [])
    except:
        return []