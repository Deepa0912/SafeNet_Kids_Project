"""core/ai_preprocessor.py — Text cleaning and NLTK-based preprocessing."""
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize

# Ensure NLTK resources are available
try:
    nltk.data.find('corpora/stopwords')
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('stopwords')
    nltk.download('punkt')
    # punkt_tab is sometimes needed in newer NLTK versions
    try:
        nltk.download('punkt_tab')
    except:
        pass

class AIPreprocessor:
    """Handles text cleaning, tokenization, stopword removal, and stemming."""

    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.stemmer = SnowballStemmer('english')

    def clean_text(self, text):
        """Standard NLP cleaning pipeline."""
        if not text:
            return ""

        # 1. Lowercase
        text = text.lower()

        # 2. Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))

        # 3. Remove numbers and special characters
        text = re.sub(r'\d+', '', text)

        # 4. Tokenization
        tokens = word_tokenize(text)

        # 5. Stopword removal & Stemming
        cleaned_tokens = [
            self.stemmer.stem(w) for w in tokens 
            if w not in self.stop_words and len(w) > 2
        ]

        return " ".join(cleaned_tokens)

    def preprocess_list(self, text_list):
        """Clean a list of strings."""
        return [self.clean_text(t) for t in text_list]
