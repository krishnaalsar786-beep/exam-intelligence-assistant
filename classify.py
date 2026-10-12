"""Step 2: map each question to a syllabus topic.

Method: keyword coverage weighted by IDF, written by hand so every step is visible.
  1. Each syllabus topic is a small "document" made of its keywords.
  2. Every word gets a weight (IDF): a word that appears in only one topic, like
     "transformer", is a strong clue; a word shared by many topics is a weak clue.
  3. For each topic we ask: "what fraction of the question's useful words
     (weighted) are found in this topic's keywords?"  That fraction is the score.
  4. The topic with the highest score wins. Confidence is higher when the best
     score is high and clearly ahead of the runner-up. If nothing matches
     well, the question is "Unclassified" instead of a bad guess.

(We first tried cosine similarity, but it unfairly favours topics with fewer
keywords, so we switched to coverage.)
"""
import json
import math
import re
from collections import Counter

STOP = set(
    "a an the of and or to in on for with by is are be from that this as at it its "
    "what which state explain define describe find calculate determine derive show "
    "draw write give using used if then also any all two one three per each between "
    "following given circuit network".split()
)
MIN_SCORE = 0.3  # below this we refuse to guess


def stem(word):
    """Very small stemmer: transformers -> transformer, working -> work."""
    for suffix in ("ing", "es", "ed", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[: -len(suffix)]
    return word


def tokens(text):
    words = re.findall(r"[a-z]+", text.lower())
    return [stem(w) for w in words if w not in STOP and len(w) > 2]


class TopicClassifier:
    def __init__(self, syllabus_path):
        with open(syllabus_path, encoding="utf-8") as f:
            self.syllabus = json.load(f)
        self.names = [t["topic"] for t in self.syllabus["topics"]]
        self.topic_words = [
            set(tokens(t["topic"] + " " + " ".join(t["keywords"])))
            for t in self.syllabus["topics"]
        ]
        n = len(self.topic_words)
        vocab = set().union(*self.topic_words)
        # rarer words (found in fewer topics) get a bigger weight
        self.idf = {
            w: math.log((n + 1) / (1 + sum(1 for d in self.topic_words if w in d))) + 1
            for w in vocab
        }

    def classify(self, text):
        """Return (topic_name, confidence 0-1)."""
        counts = Counter(w for w in tokens(text) if w in self.idf)
        total = sum(self.idf[w] * c for w, c in counts.items())
        if not total:
            return "Unclassified", 0.0
        scores = sorted(
            (
                (sum(self.idf[w] * c for w, c in counts.items() if w in words) / total, name)
                for words, name in zip(self.topic_words, self.names)
            ),
            reverse=True,
        )
        best, second = scores[0][0], scores[1][0]
        if best < MIN_SCORE:
            return "Unclassified", 0.0
        confidence = min(1.0, best + (best - second))
        return scores[0][1], round(confidence, 2)
