# import spacy
# from spacy.training.example import Example
# from spacy.util import minibatch, compounding

# # Example training data
# TRAIN_DATA = [
#     ("I need a good sunscreen for oily skin", 
#      {"entities": [(12, 21, "PRODUCT_TYPE"), (26, 35, "SKIN_CONCERN")]}),
#     ("Does niacinamide help with acne?", 
#      {"entities": [(5, 16, "INGREDIENT"), (27, 31, "SKIN_CONCERN")]}),
#     # Add more examples
# ]

# def train_ner_model():
#     nlp = spacy.blank("en")
#     ner = nlp.add_pipe("ner")
    
#     # Add entity labels
#     for _, annotations in TRAIN_DATA:
#         for ent in annotations.get("entities"):
#             ner.add_label(ent[2])
    
#     # Training
#     optimizer = nlp.begin_training()
#     for i in range(20):
#         losses = {}
#         batches = minibatch(TRAIN_DATA, size=compounding(4., 32., 1.001))
#         for batch in batches:
#             examples = []
#             for text, annotations in batch:
#                 doc = nlp.make_doc(text)
#                 example = Example.from_dict(doc, annotations)
#                 examples.append(example)
#             nlp.update(examples, drop=0.5, losses=losses)
    
#     nlp.to_disk("skincare_ner_model")
#     return nlp