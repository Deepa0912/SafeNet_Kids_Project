"""tests/test_ai_model.py — Accuracy metrics and evaluation for the AI model."""
import pandas as pd
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import pickle
import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.ai_preprocessor import AIPreprocessor

def evaluate():
    model_path = "models/text_classifier.pkl"
    data_path = "data/training_data.csv"

    if not os.path.exists(model_path):
        print("Error: Model not found. Run core/ai_trainer.py first.")
        return

    # Load model
    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    # Load data
    df = pd.read_csv(data_path)
    preprocessor = AIPreprocessor()
    df['cleaned_text'] = df['text'].apply(preprocessor.clean_text)

    # Prediction
    print("Evaluating AI Model Accuracy...")
    y_true = df['label']
    y_pred = model.predict(df['cleaned_text'])

    # Metrics
    acc = accuracy_score(y_true, y_pred)
    print(f"\nTotal Dataset Accuracy: {acc:.2f}")
    print("\nDetailed Per-Category Report:")
    print(classification_report(y_true, y_pred))

    print("\nSample Predictions:")
    samples = [
        "I love you so much",
        "you should die alone",
        "order free medicine safely",
        "big win at slots today"
    ]
    for s in samples:
        cleaned = preprocessor.clean_text(s)
        label = model.predict([cleaned])[0]
        print(f" - [{s}] -> {label}")

if __name__ == "__main__":
    evaluate()
