"""Step 4: rank topics by study priority and build a revision plan.

Priority score (0-100) =
    50%  how many marks the topic carried overall   (weightage)
  + 20%  in how many of the papers it appeared      (frequency)
  + 30%  its mark share in the latest 2 papers      (recency)
  +/- up to 5 points for a rising / falling trend
Each of the three parts is first scaled so the best topic gets 1.0.

Confidence (0-1) = 60% how sure the topic matching was
                 + 30% how many years of papers we have (5+ is best)
                 + 10% how many questions the topic has (6+ is best)
"""


def rank(stats, years):
    topics = [t for t in stats if t != "Unclassified" and stats[t]["questions"] > 0]
    recent = {t: sum(stats[t]["share_by_year"][-2:]) / min(2, len(years)) for t in topics}
    max_w = max(stats[t]["share"] for t in topics) or 1
    max_f = max(stats[t]["years_present"] for t in topics) or 1
    max_r = max(recent.values()) or 1

    rows = []
    for t in topics:
        s = stats[t]
        base = 50 * s["share"] / max_w + 20 * s["years_present"] / max_f + 30 * recent[t] / max_r
        bonus = max(-5, min(5, s["trend"] * 100))  # trend in percentage points per year
        score = max(0, min(100, base + bonus))
        conf = 0.6 * s["avg_confidence"] + 0.3 * min(len(years) / 5, 1) + 0.1 * min(s["questions"] / 6, 1)
        trend_label = "rising" if s["trend"] > 0.015 else "falling" if s["trend"] < -0.015 else "steady"
        by_count = sorted(s["types"].items(), key=lambda kv: kv[1], reverse=True)
        if by_count[0][1] == by_count[1][1]:  # tie: don't pretend one type dominates
            type_note = f"a mix of {by_count[0][0]} and {by_count[1][0]} questions"
        else:
            type_note = f"mostly {by_count[0][0]} questions"
        reason = (
            f"{s['marks']} marks ({s['share']:.0%} of all marks) over {s['questions']} questions; "
            f"appeared in {s['years_present']}/{len(years)} papers; trend {trend_label}; "
            f"{type_note}."
        )
        rows.append(
            {
                "topic": t,
                "score": round(score, 1),
                "confidence": round(conf, 2),
                "confidence_label": "High" if conf >= 0.7 else "Medium" if conf >= 0.5 else "Low",
                "trend": trend_label,
                "reason": reason,
                "types": s["types"],
            }
        )
    return sorted(rows, key=lambda r: r["score"], reverse=True)


def make_plan(rows, hours):
    """Split `hours` across topics in proportion to score (minimum 30 minutes each)."""
    total = sum(r["score"] for r in rows) or 1
    plan = []
    for r in rows:
        h = max(0.5, hours * r["score"] / total)
        plan.append((r["topic"], round(h * 4) / 4))  # round to 15 minutes
    return plan
