"""core/ai_trainer.py — Training pipeline for the text classification model."""
import pandas as pd
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
from core.ai_preprocessor import AIPreprocessor

def train_model():
    # 1. Load Data
    data_path = "data/training_data.csv"
    if not os.path.exists(data_path):
        print(f"Error: Dataset not found at {data_path}")
        return

    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} samples across {df['label'].nunique()} categories.")

    # 2. Preprocess Data
    preprocessor = AIPreprocessor()
    print("Preprocessing text data...")
    df['cleaned_text'] = df['text'].apply(preprocessor.clean_text)

    # 3. Split Data
    X_train, X_test, y_train, y_test = train_test_split(
        df['cleaned_text'], df['label'], test_size=0.2, random_state=42, stratify=df['label']
    )

    # 4. Build Pipeline (TF-IDF + Naive Bayes)
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2))),
        ('clf', MultinomialNB(alpha=0.1))
    ])

    # 5. Train
    print("Training model...")
    pipeline.fit(X_train, y_train)

    # 6. Evaluate
    print("\nModel Evaluation Metrics:")
    y_pred = pipeline.predict(X_test)
    print(f"Overall Accuracy: {accuracy_score(y_test, y_pred):.2f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # 7. Save Model
    os.makedirs("models", exist_ok=True)
    model_path = "models/text_classifier.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(pipeline, f)
    print(f"\nSuccess: Model saved to {model_path}")

if __name__ == "__main__":
    train_model()
