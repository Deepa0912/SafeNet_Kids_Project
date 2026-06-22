import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer


class NLPAnalyzer:
    def __init__(self):
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            nltk.download('vader_lexicon', quiet=True)
        self.sia = SentimentIntensityAnalyzer()

    def analyze_text(self, text):
        return self.sia.polarity_scores(text)

    def is_highly_negative(self, text, threshold=-0.6):
        if not text:
            return False
        scores = self.analyze_text(text)
        return scores['compound'] <= threshold

    def is_extreme_intent(self, text):
        """Detects phrases specifying immediate harm or illegal acts."""
        extreme_phrases = ["how to kill", "how to commit", "suicide", "end my life", "build a bomb", "hurt myself"]
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in extreme_phrases)

    def calculate_toxicity_risk(self, text, keyword_match_found):
        if not text:
            return 0.0
        scores = self.analyze_text(text)
        risk_score = 0.0

        if scores['compound'] < -0.3:
            risk_score += 0.4
        if scores['compound'] < -0.6:
            risk_score += 0.3

        if keyword_match_found:
            risk_score += 0.3

        return min(risk_score, 1.0)