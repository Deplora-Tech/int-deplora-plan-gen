from transformers import pipeline

class ClassifierService:
    def __init__(self):
        self.intent_classifier = None

    def load_model(self):
        if self.intent_classifier is None:
            print("Loading the Hugging Face model...")
            self.intent_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
            print("Model loaded successfully.")

    def classify_intent(self, message: str, chat_history: dict) -> str:
        self.load_model()
        input_text = f"Chat History: {chat_history}\nCurrent Message: {message}"
        result = self.intent_classifier(
            input_text,
            candidate_labels=["greeting", "deployment_plan", "feedback", "unknown"]
        )
        return result["labels"][0]
