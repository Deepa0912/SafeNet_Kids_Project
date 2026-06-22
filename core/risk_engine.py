import os
import re
from datetime import datetime, timedelta

class RiskEngine:
    """
    AI Risk Scoring System for SafeNet Kids.
    Analyzes behavior patterns, frequency, and severity to assign a risk score.
    """

    def __init__(self, audit_log="data/safenet_audit.log"):
        self.audit_log = audit_log
        self.weights = {
            "Self-Harm": 25,
            "Adult Content": 20,
            "Violence": 15,
            "Gore": 15,
            "Cyberbullying": 10,
            "Drugs": 8,
            "Gambling": 8,
            "Info": 1
        }

    def calculate_score(self):
        """Calculates a risk score between 0 and 100."""
        if not os.path.exists(self.audit_log):
            return 0

        threats = self._parse_logs()
        if not threats:
            return 0

        now = datetime.now()
        base_score = 0
        categories_count = {}

        for timestamp, category in threats:
            # 1. Severity Weight
            weight = self.weights.get(category, 5)
            
            # 2. Time Decay (Recent threats weigh more)
            age_days = (now - timestamp).total_seconds() / 86400
            decay = max(0, 1 - (age_days / 7)) # Linear decay over 7 days
            
            base_score += weight * decay
            categories_count[category] = categories_count.get(category, 0) + 1

        # 3. Frequency Multiplier
        # Count threats in the last hour
        recent_count = sum(1 for ts, _ in threats if (now - ts) < timedelta(hours=1))
        freq_multiplier = 1.0 + (min(recent_count, 10) * 0.1) # Up to 2x for 10+ recent threats

        # 4. Repeat Behavior Penalty
        repeat_penalty = 1.0
        for cat, count in categories_count.items():
            if count > 3:
                repeat_penalty += 0.1 # 10% extra for repeated violations in same category

        total_score = (base_score * freq_multiplier * repeat_penalty)
        return min(round(total_score), 100)

    def get_category(self, score):
        """Returns the risk level category based on the score."""
        if score <= 30:
            return "Safe"
        elif score <= 70:
            return "Moderate Risk"
        else:
            return "High Risk"

    def _parse_logs(self):
        """Extracts timestamps and categories from the audit log."""
        threats = []
        # Pattern: 2026-06-18 19:35:45,123 - INFO - Threat: Adult Content | ...
        # Or: 2026-06-18 19:35:45,123 - INFO - AI Detected Image: Violence | ...
        pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?(?:Threat|AI Detected Image): ([\w\s-]+)")
        
        try:
            with open(self.audit_log, "r", encoding='utf-8') as f:
                for line in f:
                    match = pattern.search(line)
                    if match:
                        timestamp_str, category = match.groups()
                        category = category.strip()
                        # Simple mapping to known weight keys
                        matched_cat = "Others"
                        for key in self.weights:
                            if key.lower() in category.lower():
                                matched_cat = key
                                break
                        
                        ts = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                        threats.append((ts, matched_cat))
        except Exception:
            pass
        
        return threats
