# app/ai/sentiment_engine.py
"""
Sentiment Analysis Engine for EventPro AI.

A lightweight, dependency-free sentiment analyser that scores text
on a –1 … +1 scale using curated word lists, intensity modifiers,
and negation handling.
"""

from __future__ import annotations

import re
import string
from collections import Counter


class SentimentEngine:
    """
    Analyse event-feedback text for sentiment polarity.

    Features:
        - Curated positive / negative word lists (event-domain-aware).
        - Intensity modifiers ("very", "really", "extremely") boost scores.
        - Simple negation handling ("not good" → negative).
        - Batch analysis with summary statistics and common-theme extraction.

    Usage::

        engine = SentimentEngine()
        result = engine.analyze("The food was amazing and the venue was beautiful!")
        # {'sentiment': 'Positive', 'score': 0.82, ...}
    """

    # ── Word lists ──────────────────────────────────────────────────────
    POSITIVE_WORDS: set[str] = {
        # General
        "great", "excellent", "amazing", "wonderful", "fantastic", "loved",
        "beautiful", "awesome", "brilliant", "superb", "outstanding",
        "perfect", "incredible", "delightful", "magnificent",
        "impressive", "phenomenal", "splendid", "marvellous",
        "enjoyable", "pleasant", "lovely", "charming", "elegant",
        "graceful", "exquisite", "remarkable",
        # Event-domain
        "organised", "organized", "professional", "smooth", "seamless",
        "entertaining", "fun", "exciting", "engaging", "memorable",
        "delicious", "tasty", "scrumptious", "yummy",
        "friendly", "helpful", "attentive", "welcoming", "warm",
        "creative", "innovative", "unique", "stunning",
        "clean", "spacious", "comfortable", "cozy",
        # Short positive
        "good", "nice", "fine", "happy", "glad", "pleased",
        "satisfied", "recommend", "recommended", "best", "top",
        "love", "like", "liked", "enjoyed", "appreciate",
        "thankyou", "thanks", "thank",
    }

    NEGATIVE_WORDS: set[str] = {
        # General
        "bad", "terrible", "awful", "poor", "disappointed",
        "boring", "horrible", "dreadful", "worst", "pathetic",
        "mediocre", "unpleasant", "disgusting", "atrocious",
        "frustrating", "annoying", "irritating",
        # Event-domain
        "late", "delayed", "slow", "cold", "stale", "overpriced",
        "crowded", "noisy", "chaotic", "disorganised", "disorganized",
        "messy", "dirty", "rude", "unprofessional", "unhelpful",
        "tasteless", "bland", "overcooked", "undercooked",
        "uncomfortable", "cramped", "dark",
        # Short negative
        "hate", "hated", "dislike", "disliked", "worse",
        "fail", "failed", "lacking", "missing", "broken",
        "waste", "wasted", "avoid", "never", "nowhere",
        "unfortunately", "sadly", "regret",
    }

    # Words that amplify the next sentiment word's score.
    INTENSIFIERS: set[str] = {
        "very", "really", "extremely", "incredibly", "absolutely",
        "totally", "completely", "highly", "deeply", "super",
        "truly", "utterly", "remarkably",
    }

    # Words that flip the sentiment of the following word.
    NEGATORS: set[str] = {
        "not", "no", "never", "neither", "nor",
        "hardly", "barely", "rarely", "seldom",
        "don't", "doesn't", "didn't", "isn't", "wasn't",
        "aren't", "weren't", "won't", "wouldn't",
        "can't", "cannot", "couldn't", "shouldn't",
    }

    # Weights
    _BASE_WEIGHT = 1.0
    _INTENSITY_MULTIPLIER = 1.5
    _NEGATION_FLIP = -1.0

    # ── Single-text analysis ────────────────────────────────────────────
    def analyze(self, text: str) -> dict:
        """
        Analyse a single piece of text.

        Parameters
        ----------
        text : str
            Raw feedback / review text.

        Returns
        -------
        dict
            Keys: sentiment, score, positive_words, negative_words,
                  word_count, confidence.
        """
        tokens = self._tokenize(text)
        if not tokens:
            return {
                "sentiment": "Neutral",
                "score": 0.0,
                "positive_words": [],
                "negative_words": [],
                "word_count": 0,
                "confidence": 0.0,
            }

        positive_found: list[str] = []
        negative_found: list[str] = []
        raw_score = 0.0

        i = 0
        while i < len(tokens):
            word = tokens[i]

            # Look-ahead for intensifier or negator
            is_negated = False
            intensity = self._BASE_WEIGHT

            # Check if previous word was a negator
            if i > 0 and tokens[i - 1] in self.NEGATORS:
                is_negated = True

            # Check if previous word was an intensifier
            if i > 0 and tokens[i - 1] in self.INTENSIFIERS:
                intensity = self._INTENSITY_MULTIPLIER

            # Negator two words back + intensifier one word back
            if i > 1 and tokens[i - 2] in self.NEGATORS:
                is_negated = True

            if word in self.POSITIVE_WORDS:
                if is_negated:
                    raw_score -= intensity
                    negative_found.append(word)
                else:
                    raw_score += intensity
                    positive_found.append(word)
            elif word in self.NEGATIVE_WORDS:
                if is_negated:
                    raw_score += intensity * 0.5  # negated negatives are mildly positive
                    positive_found.append(word)
                else:
                    raw_score -= intensity
                    negative_found.append(word)

            i += 1

        # Normalise to [-1, 1]
        max_possible = max(len(positive_found) + len(negative_found), 1) * self._INTENSITY_MULTIPLIER
        score = max(-1.0, min(1.0, raw_score / max_possible))
        score = round(score, 3)

        # Classify
        if score > 0.1:
            sentiment = "Positive"
        elif score < -0.1:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        # Confidence based on how many sentiment words were found relative to text length
        sentiment_word_ratio = (len(positive_found) + len(negative_found)) / max(len(tokens), 1)
        confidence = round(min(1.0, sentiment_word_ratio * 3), 2)  # scale up, cap at 1

        return {
            "sentiment": sentiment,
            "score": score,
            "positive_words": list(set(positive_found)),
            "negative_words": list(set(negative_found)),
            "word_count": len(tokens),
            "confidence": confidence,
        }

    # ── Batch analysis ──────────────────────────────────────────────────
    def analyze_batch(self, feedbacks: list[str]) -> dict:
        """
        Analyse a list of feedback texts and return aggregate statistics.

        Parameters
        ----------
        feedbacks : list[str]
            List of raw feedback strings.

        Returns
        -------
        dict
            Keys: total, positive_count, neutral_count, negative_count,
                  average_score, score_distribution, common_positive,
                  common_negative, results.
        """
        if not feedbacks:
            return {
                "total": 0,
                "positive_count": 0,
                "neutral_count": 0,
                "negative_count": 0,
                "average_score": 0.0,
                "score_distribution": {"positive": 0, "neutral": 0, "negative": 0},
                "common_positive": [],
                "common_negative": [],
                "results": [],
            }

        results: list[dict] = []
        all_positive: list[str] = []
        all_negative: list[str] = []
        pos_count = neu_count = neg_count = 0
        total_score = 0.0

        for text in feedbacks:
            r = self.analyze(text)
            results.append(r)
            total_score += r["score"]
            all_positive.extend(r["positive_words"])
            all_negative.extend(r["negative_words"])

            if r["sentiment"] == "Positive":
                pos_count += 1
            elif r["sentiment"] == "Negative":
                neg_count += 1
            else:
                neu_count += 1

        total = len(feedbacks)
        avg_score = round(total_score / total, 3)

        # Most common words
        common_positive = [
            {"word": w, "count": c}
            for w, c in Counter(all_positive).most_common(10)
        ]
        common_negative = [
            {"word": w, "count": c}
            for w, c in Counter(all_negative).most_common(10)
        ]

        return {
            "total": total,
            "positive_count": pos_count,
            "neutral_count": neu_count,
            "negative_count": neg_count,
            "average_score": avg_score,
            "score_distribution": {
                "positive": round(pos_count / total * 100, 1),
                "neutral": round(neu_count / total * 100, 1),
                "negative": round(neg_count / total * 100, 1),
            },
            "common_positive": common_positive,
            "common_negative": common_negative,
            "results": results,
        }

    # ── Tokenizer ───────────────────────────────────────────────────────
    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """
        Lowercase, keep contractions (don't → don't), split on whitespace
        and strip remaining punctuation from edges.
        """
        text = text.lower().strip()
        # Keep apostrophes inside words for contraction handling
        tokens = re.findall(r"[a-z']+", text)
        # Remove standalone apostrophes
        tokens = [t.strip("'") for t in tokens if t.strip("'")]
        return tokens
