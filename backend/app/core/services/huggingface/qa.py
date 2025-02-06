import torch
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import numpy as np


'''
Strict Q&A service
- limited to the context
'''
class StrictQaService:
    def __init__(self):
        model_name = "bert-large-uncased-whole-word-masking-finetuned-squad"  # Example model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForQuestionAnswering.from_pretrained(model_name, output_attentions=True)

    def _tokenize(self, question, context):
        inputs = self.tokenizer(question, context, return_tensors="pt")
        return inputs

    def answer_question(self, question, context):
        inputs = self._tokenize(question, context)
        outputs = self.model(**inputs, output_attentions=True)
        start_logits = outputs.start_logits  # Logits for the start of the answer
        end_logits = outputs.end_logits      # Logits for the end of the answer
        attentions = outputs.attentions      # Attention weights

        start_idx = start_logits.argmax()  # Index of the start token
        end_idx = end_logits.argmax() + 1  # Index of the end token
        tokens = inputs["input_ids"][0][start_idx:end_idx]
        answer = self.tokenizer.decode(tokens, skip_special_tokens=True)

        # inline_attention = self._get_attention(question, attentions, inputs)
        return answer, None
    
    ## WIP: higlight context tokens in the answer
    def _get_attention(self, question, attentions, inputs):
        # Average attention across layers and heads
        avg_attention = torch.mean(torch.stack(attentions), dim=(0, 1))  # Shape: (seq_len, seq_len)

        # Extract the attention from [CLS] to all tokens
        cls_attention = avg_attention[0]  # Shape: (seq_len,)

        # Isolate attention to context tokens (skip [CLS], question, and special tokens)
        context_start_idx = len(self.tokenizer.tokenize(question)) + 2  # Question tokens + [CLS] and [SEP]
        context_attention_scores = cls_attention[context_start_idx:]  # Attention to context tokens

        # Ensure the result is a flat list
        question_len = len(self.tokenizer.tokenize(question)) + 2  # Question tokens + [CLS], [SEP]
        context_attention_scores = context_attention_scores.detach().numpy()
        context_tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][question_len:])

        # Normalize attention scores for readability
        normalized_attention = (context_attention_scores - context_attention_scores.min()) / (
            context_attention_scores.max() - context_attention_scores.min()
        )

        # Validate normalized_attention shape
        assert len(normalized_attention) == len(context_tokens), "Mismatch between tokens and attention scores."
        return self._inline_attention(context_tokens, normalized_attention)
    
    def _inline_attention(self, context_tokens, normalized_attention):
        inline_highlight = []
        normalized_attention = list(normalized_attention.tolist())
        for token, score in zip(context_tokens, normalized_attention):
            inline_highlight.append(f"{token}({int(score * 100)}%)")
        return " ".join(inline_highlight)

from transformers import AutoTokenizer, AutoModelForQuestionAnswering

# Load a model that supports no-answer detection
model_name = "distilbert-base-cased-distilled-squad"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForQuestionAnswering.from_pretrained(model_name)

def answer_question_with_no_answer(question, context):
    inputs = tokenizer(question, context, return_tensors="pt")
    outputs = model(**inputs)

    start_logits = outputs.start_logits
    end_logits = outputs.end_logits

    # Get scores for the predicted answer span
    start_idx = torch.argmax(start_logits)
    end_idx = torch.argmax(end_logits) + 1

    # Get the score for the no-answer token ([CLS])
    no_answer_score = start_logits[0][0].item() + end_logits[0][0].item()

    # Calculate the confidence of the answer
    answer_score = start_logits[0][start_idx].item() + end_logits[0][end_idx - 1].item()

    # Compare scores: if no-answer score is higher, return "I don't know"
    if no_answer_score > answer_score:
        return "I don't know"
    
    # Otherwise, return the predicted answer
    answer = tokenizer.decode(inputs["input_ids"][0][start_idx:end_idx])
    return answer
