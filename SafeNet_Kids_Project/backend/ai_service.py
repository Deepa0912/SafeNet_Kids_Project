"""
backend/ai_service.py — AI Threat Detection
Primary:  Google Gemini (gemini-1.5-flash) via google-generativeai
Fallback: NLTK keyword scan + TF-IDF + Logistic Regression + VADER Sentiment
"""
import os
import re
import string
import logging
from dataclasses import dataclass
from typing import Optional

# ── Load env vars ─────────────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import numpy as np

log = logging.getLogger("safenet.ai")

# Download NLTK resources silently
for res in ["stopwords", "punkt", "vader_lexicon"]:
    try:
        nltk.download(res, quiet=True)
    except Exception:
        pass

try:
    from nltk.sentiment import SentimentIntensityAnalyzer
    _sia = SentimentIntensityAnalyzer()
except Exception:
    _sia = None

# ── Gemini Setup (new google-genai SDK) ──────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
_gemini_client = None

if GEMINI_API_KEY:
    try:
        from google import genai as google_genai
        _gemini_client = google_genai.Client(api_key=GEMINI_API_KEY)
        log.info("✅ Gemini AI client ready (gemini-2.0-flash)")
    except Exception as e:
        log.warning(f"Gemini load failed: {e}. Using local ML fallback.")
        _gemini_client = None
else:
    log.warning("No GEMINI_API_KEY found — using local ML fallback.")


# ── Keyword Database ──────────────────────────────────────────────────────────
THREAT_KEYWORDS = {
    "Adult Content":  ["porn", "xxx", "adult video", "explicit", "nsfw", "nude", "erotic"],
    "Gambling":       ["betting", "casino", "poker", "gamble", "wager", "slot machine"],
    "Drug Related":   ["cocaine", "weed", "marijuana", "heroin", "meth", "drugs", "crack", "mdma"],
    "Cyberbullying":  ["hate you", "loser", "idiot", "kill yourself", "worthless", "ugly", "go die"],
    "Self Harm":      ["suicide", "kill myself", "self harm", "cut myself", "end my life", "want to die"],
    "Violence":       ["murder", "kill", "shoot", "bomb", "stab", "terrorist", "weapon"],
}

# ── Local ML Pipeline ─────────────────────────────────────────────────────────
_TRAIN_X, _TRAIN_Y = [], []
for label, kws in THREAT_KEYWORDS.items():
    for kw in kws:
        _TRAIN_X.append(kw); _TRAIN_Y.append(label)
    _TRAIN_X += ["homework", "school project", "weather forecast", "cook recipe", "sports match"] * 2
    _TRAIN_Y += ["Safe"] * 10

_STEMMER = PorterStemmer()
try:
    _STOP = set(stopwords.words("english"))
except Exception:
    _STOP = set()


def _preprocess(text: str) -> str:
    text = text.lower().translate(str.maketrans("", "", string.punctuation))
    return " ".join(_STEMMER.stem(w) for w in text.split() if w not in _STOP)


_pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(preprocessor=_preprocess, ngram_range=(1, 2), max_features=5000)),
    ("clf",   LogisticRegression(max_iter=500, C=2.0, class_weight="balanced")),
])
_pipeline.fit(_TRAIN_X, _TRAIN_Y)
log.info("Local ML classifier trained.")


# ── Result Dataclass ──────────────────────────────────────────────────────────
@dataclass
class ThreatResult:
    is_threat:   bool
    threat_type: str
    confidence:  float
    sentiment:   Optional[float] = None


# ── Gemini Text Analysis ──────────────────────────────────────────────────────
_GEMINI_PROMPT = """You are SafeNet Kids, a child safety AI. Analyze the following text and classify it.

Categories: Adult Content, Gambling, Drug Related, Cyberbullying, Self Harm, Violence, Safe

Respond ONLY in this exact format:
CATEGORY: <category name>
CONFIDENCE: <0.0 to 1.0>
IS_THREAT: <true or false>

Text to analyze:
{text}"""


def _analyze_with_gemini(text: str) -> Optional[ThreatResult]:
    """Use Gemini to classify the text. Returns None on failure."""
    if not _gemini_client:
        return None
    try:
        response = _gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=_GEMINI_PROMPT.format(text=text[:800]),
        )
        raw = response.text.strip()

        category_match   = re.search(r"CATEGORY:\s*(.+)", raw)
        confidence_match = re.search(r"CONFIDENCE:\s*([\d.]+)", raw)
        threat_match     = re.search(r"IS_THREAT:\s*(true|false)", raw, re.IGNORECASE)

        if not (category_match and confidence_match and threat_match):
            return None

        category   = category_match.group(1).strip()
        confidence = float(confidence_match.group(1))
        is_threat  = threat_match.group(1).lower() == "true"

        return ThreatResult(is_threat=is_threat, threat_type=category, confidence=confidence)
    except Exception as e:
        log.warning(f"Gemini analysis failed: {e}")
        return None


# ── Image Moderation via Gemini ───────────────────────────────────────────────
_IMAGE_PROMPT = """You are SafeNet Kids, a child safety AI. Look at this screenshot and determine if it contains any harmful content.

Categories to check: Adult Content, Gambling, Drug Related, Cyberbullying, Self Harm, Violence, Safe

Respond ONLY in this exact format:
CATEGORY: <category name>
CONFIDENCE: <0.0 to 1.0>
IS_THREAT: <true or false>"""


def analyze_image(pil_image) -> Optional[ThreatResult]:
    """Use Gemini Vision to check a screenshot for harmful content."""
    if not _gemini_client:
        return None
    try:
        import io
        buf = io.BytesIO()
        pil_image.save(buf, format="PNG")
        image_bytes = buf.getvalue()

        from google.genai import types as genai_types
        response = _gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                _IMAGE_PROMPT,
                genai_types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            ],
        )
        raw = response.text.strip()

        category_match   = re.search(r"CATEGORY:\s*(.+)", raw)
        confidence_match = re.search(r"CONFIDENCE:\s*([\d.]+)", raw)
        threat_match     = re.search(r"IS_THREAT:\s*(true|false)", raw, re.IGNORECASE)

        if not (category_match and confidence_match and threat_match):
            return None

        return ThreatResult(
            is_threat  = threat_match.group(1).lower() == "true",
            threat_type= category_match.group(1).strip(),
            confidence = float(confidence_match.group(1)),
        )
    except Exception as e:
        log.warning(f"Gemini image analysis failed: {e}")
        return None


# ── Main Text Entry Point ─────────────────────────────────────────────────────
def analyze_text(text: str) -> ThreatResult:
    """
    Threat pipeline:
    1. Fast keyword scan
    2. Gemini AI (if available) — most accurate
    3. Local TF-IDF + Logistic Regression fallback
    4. VADER sentiment refinement for cyberbullying
    """
    if not text or not text.strip():
        return ThreatResult(False, "Safe", 1.0)

    # Step 1 — Keyword fast path
    lower = text.lower()
    for category, kws in THREAT_KEYWORDS.items():
        for kw in kws:
            if kw in lower:
                sentiment = _get_sentiment(text)
                return ThreatResult(True, category, 0.95, sentiment)

    # Step 2 — Gemini (primary AI)
    gemini_result = _analyze_with_gemini(text)
    if gemini_result is not None:
        gemini_result.sentiment = _get_sentiment(text)
        return gemini_result

    # Step 3 — Local ML fallback
    processed = _preprocess(text)
    try:
        proba     = _pipeline.predict_proba([processed])[0]
        classes   = _pipeline.classes_
        top_idx   = int(np.argmax(proba))
        top_label = classes[top_idx]
        top_conf  = float(proba[top_idx])
    except Exception:
        return ThreatResult(False, "Safe", 1.0)

    # Step 4 — VADER sentiment for cyberbullying
    sentiment = _get_sentiment(text)
    if sentiment is not None and sentiment < -0.5 and top_label == "Safe":
        top_label = "Cyberbullying"
        top_conf  = abs(sentiment)

    is_threat = top_label != "Safe" and top_conf > 0.55
    return ThreatResult(is_threat, top_label if is_threat else "Safe", top_conf, sentiment)


def _get_sentiment(text: str) -> Optional[float]:
    if _sia is None:
        return None
    try:
        return _sia.polarity_scores(text)["compound"]
    except Exception:
        return None
