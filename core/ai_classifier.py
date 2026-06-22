"""core/ai_classifier.py — Inference module for the text classification model."""
import pickle
import os
from core.ai_preprocessor import AIPreprocessor

class AIClassifier:
    """Loads a pre-trained model and provides classification for input text."""

    def __init__(self, model_path="models/text_classifier.pkl"):
        self.model_path = model_path
        self.preprocessor = AIPreprocessor()
        self.pipeline = None
        self._load_model()

    def _load_model(self):
        """Load the pipeline from disk."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    self.pipeline = pickle.load(f)
                print(f"AI Classifier: Model loaded from {self.model_path}")
            except Exception as e:
                print(f"AI Classifier: Error loading model - {e}")
        else:
            print(f"AI Classifier: Warning — Model not found at {self.model_path}")

    def predict(self, text):
        """
        Classifies input text.
        Returns: (label, confidence_score) if possible, else (None, 0.0)
        """
        if self.pipeline is None:
            return None, 0.0

        # Preprocess input
        cleaned = self.preprocessor.clean_text(text)
        if not cleaned:
            return "Safe", 1.0 # Empty text is safe

        # Predict label
        label = self.pipeline.predict([cleaned])[0]

        # Get probability (confidence)
        try:
            probs = self.pipeline.predict_proba([cleaned])
            max_prob = probs.max()
        except:
            max_prob = 1.0

        return label, max_prob
