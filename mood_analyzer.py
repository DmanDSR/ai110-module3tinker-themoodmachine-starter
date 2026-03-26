# mood_analyzer.py
"""
Rule based mood analyzer for short text snippets.

This class starts with very simple logic:
  - Preprocess the text
  - Look for positive and negative words
  - Compute a numeric score
  - Convert that score into a mood label
"""

import re
from typing import List, Dict, Tuple, Optional

from dataset import POSITIVE_WORDS, NEGATIVE_WORDS

# Text-face emojis mapped to sentiment tokens
EMOJI_MAP = {
    ":)": "__happy__",
    ":-)": "__happy__",
    ":D": "__happy__",
    ":(": "__sad__",
    ":-(": "__sad__",
    ":/": "__sad__",
    "🥲": "__sad__",
    "😂": "__happy__",
    "😭": "__sad__",
    "😊": "__happy__",
    "😍": "__happy__",
    "😡": "__angry__",
    "💀": "__dead__",
    "🙂": "__happy__",
}


class MoodAnalyzer:
    """
    A very simple, rule based mood classifier.
    """

    def __init__(
        self,
        positive_words: Optional[List[str]] = None,
        negative_words: Optional[List[str]] = None,
    ) -> None:
        # Use the default lists from dataset.py if none are provided.
        positive_words = positive_words if positive_words is not None else POSITIVE_WORDS
        negative_words = negative_words if negative_words is not None else NEGATIVE_WORDS

        # Store as sets for faster lookup.
        self.positive_words = set(w.lower() for w in positive_words)
        self.negative_words = set(w.lower() for w in negative_words)

    # ---------------------------------------------------------------------
    # Preprocessing
    # ---------------------------------------------------------------------

    def preprocess(self, text: str) -> List[str]:
        """
        Convert raw text into a list of tokens the model can work with.

        TODO: Improve this method.

        Right now, it does the minimum:
          - Strips leading and trailing whitespace
          - Converts everything to lowercase
          - Splits on spaces

        Ideas to improve:
          - Remove punctuation
          - Handle simple emojis separately (":)", ":-(", "🥲", "😂")
          - Normalize repeated characters ("soooo" -> "soo")
        """
        cleaned = text.strip()

        # Replace known emojis with sentiment placeholder tokens before lowercasing
        # so that multi-char text-faces like ":)" are matched literally.
        for emoji, token in EMOJI_MAP.items():
            cleaned = cleaned.replace(emoji, f" {token} ")

        cleaned = cleaned.lower()

        # Normalize repeated characters: "soooo" -> "soo", "noooo" -> "noo"
        # Keeps at most 2 of the same letter in a row.
        cleaned = re.sub(r"(.)\1{2,}", r"\1\1", cleaned)

        # Remove punctuation (but keep the placeholder tokens which use underscores)
        cleaned = re.sub(r"[^\w\s]", " ", cleaned)

        tokens = cleaned.split()

        return tokens

    # ---------------------------------------------------------------------
    # Scoring logic
    # ---------------------------------------------------------------------

    def score_text(self, text: str) -> int:
        """
        Compute a numeric "mood score" for the given text.

        Positive words increase the score.
        Negative words decrease the score.

        TODO: You must choose AT LEAST ONE modeling improvement to implement.
        For example:
          - Handle simple negation such as "not happy" or "not bad"
          - Count how many times each word appears instead of just presence
          - Give some words higher weights than others (for example "hate" < "annoyed")
          - Treat emojis or slang (":)", "lol", "💀") as strong signals
        """
        tokens = self.preprocess(text)
        score = 0
        negation_words = {"not", "never", "no", "cant", "cannot", "dont", "wont", "isnt", "wasnt"}

        # Emoji placeholder scores (strong signals)
        emoji_scores = {
            "__happy__": 2,
            "__sad__": -2,
            "__angry__": -2,
            "__dead__": -1,
        }

        negated = False
        for token in tokens:
            if token in negation_words:
                negated = True
                continue

            if token in emoji_scores:
                delta = emoji_scores[token]
            elif token in self.positive_words:
                delta = 1
            elif token in self.negative_words:
                delta = -1
            else:
                negated = False
                continue

            score += -delta if negated else delta
            negated = False

        return score

    # ---------------------------------------------------------------------
    # Label prediction
    # ---------------------------------------------------------------------

    def predict_label(self, text: str) -> str:
        """
        Turn the numeric score for a piece of text into a mood label.

        The default mapping is:
          - score > 0  -> "positive"
          - score < 0  -> "negative"
          - score == 0 -> "neutral"

        TODO: You can adjust this mapping if it makes sense for your model.
        For example:
          - Use different thresholds (for example score >= 2 to be "positive")
          - Add a "mixed" label for scores close to zero
        Just remember that whatever labels you return should match the labels
        you use in TRUE_LABELS in dataset.py if you care about accuracy.
        """
        score = self.score_text(text)
        if score > 0:
            return "positive"
        if score < 0:
            return "negative"
        if score == 0:
            return "mixed"
        return "neutral"

    # ---------------------------------------------------------------------
    # Explanations (optional but recommended)
    # ---------------------------------------------------------------------

    def explain(self, text: str) -> str:
        """
        Return a short string explaining WHY the model chose its label.

        TODO:
          - Look at the tokens and identify which ones counted as positive
            and which ones counted as negative.
          - Show the final score.
          - Return a short human readable explanation.

        Example explanation (your exact wording can be different):
          'Score = 2 (positive words: ["love", "great"]; negative words: [])'

        The current implementation is a placeholder so the code runs even
        before you implement it.
        """
        tokens = self.preprocess(text)

        positive_hits: List[str] = []
        negative_hits: List[str] = []
        score = 0

        for token in tokens:
            if token in self.positive_words:
                positive_hits.append(token)
                score += 1
            if token in self.negative_words:
                negative_hits.append(token)
                score -= 1

        return (
            f"Score = {score} "
            f"(positive: {positive_hits or '[]'}, "
            f"negative: {negative_hits or '[]'})"
        )
