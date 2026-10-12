"""Step 3: question types, difficulty, and per-topic statistics."""
import re

DERIVATION = re.compile(
    r"\b(derive|prove|proof|show that|obtain an expression|deduce)\b", re.I
)
NUMERICAL = re.compile(
    r"\b(calculate|compute|determine|find|numerical)\b|"
    r"\d+(\.\d+)?\s*(v|a|ohm|hz|kva|kw|w|mh|uf|rpm|kv)\b",
    re.I,
)


def question_type(text):
    """derivation > numerical > theory (first rule that matches wins)."""
    if DERIVATION.search(text):
        return "derivation"
    if NUMERICAL.search(text):
        return "numerical"
    return "theory"


def difficulty(qtype, marks):
    """Simple rule: more marks and harder types give a higher level."""
    points = {"derivation": 2, "numerical": 1.5, "theory": 0}[qtype]
    if marks >= 8:
        points += 2
    elif marks >= 6:
        points += 1
    return "hard" if points >= 3.5 else "medium" if points >= 2 else "easy"


def enrich(question):
    question["qtype"] = question_type(question["text"])
    question["difficulty"] = difficulty(question["qtype"], question["marks"])
    return question


def slope(values):
    """Least-squares slope of values against 0, 1, 2, ... (change per year)."""
    n = len(values)
    if n < 2:
        return 0.0
    mean_x, mean_y = (n - 1) / 2, sum(values) / n
    num = sum((i - mean_x) * (v - mean_y) for i, v in enumerate(values))
    den = sum((i - mean_x) ** 2 for i in range(n))
    return num / den


def topic_stats(questions, topics):
    """Marks, frequency, trend and type mix for every topic."""
    years = sorted({q["year"] for q in questions})
    total_marks = sum(q["marks"] for q in questions)
    marks_per_year = {y: sum(q["marks"] for q in questions if q["year"] == y) for y in years}
    stats = {}
    for topic in topics + ["Unclassified"]:
        qs = [q for q in questions if q["topic"] == topic]
        by_year = [
            sum(q["marks"] for q in qs if q["year"] == y) / marks_per_year[y]
            for y in years
        ]
        stats[topic] = {
            "questions": len(qs),
            "marks": sum(q["marks"] for q in qs),
            "share": sum(q["marks"] for q in qs) / total_marks if total_marks else 0,
            "years_present": len({q["year"] for q in qs}),
            "share_by_year": by_year,
            "trend": slope(by_year),  # change in mark-share per year
            "types": {t: sum(1 for q in qs if q["qtype"] == t) for t in ("theory", "numerical", "derivation")},
            "difficulty": {d: sum(1 for q in qs if q["difficulty"] == d) for d in ("easy", "medium", "hard")},
            "avg_confidence": sum(q["confidence"] for q in qs) / len(qs) if qs else 0,
        }
    return stats, years
