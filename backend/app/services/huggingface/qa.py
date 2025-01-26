from transformers import pipeline

class QaService:
    def __init__(self):
        print("Initializing QA pipeline")
        self.qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

    def answer_question(self, question, context):
        print("Answering question")
        result = self.qa_pipeline(question=question, context=context)
        return result['answer']        