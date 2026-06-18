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