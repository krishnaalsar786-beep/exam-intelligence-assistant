"""Exam Intelligence Assistant: tells you which topics deserve the most study time.

Run:  python main.py                       (uses the sample papers in this folder)
      python main.py --hours 12            (revision plan for 12 hours)
      python main.py --papers my_papers    (your own paper_2023.txt / .pdf files)
"""
import argparse
import json

from analyze import enrich, topic_stats
from classify import TopicClassifier
from extract import load_questions
from priority import make_plan, rank


def run(papers_dir, syllabus_path, hours):
    classifier = TopicClassifier(syllabus_path)
    questions = load_questions(papers_dir)
    if not questions:
        raise SystemExit("No questions found. Name files like paper_2023.txt and use Q1., Q2. ...")
    for q in questions:
        q["topic"], q["confidence"] = classifier.classify(q["text"])
        enrich(q)
    stats, years = topic_stats(questions, classifier.names)
    rows = rank(stats, years)
    return questions, stats, years, rows, make_plan(rows, hours)


def print_report(questions, stats, years, rows, plan, hours):
    assumed = sum(q["marks_assumed"] for q in questions)
    print(f"\nPapers: {years[0]}-{years[-1]} ({len(years)} papers), {len(questions)} questions")
    if assumed:
        print(f"Note: {assumed} questions had no marks written; assumed 5 marks each.")

    print("\n=== STUDY PRIORITY (highest first) ===")
    for i, r in enumerate(rows, 1):
        print(f"{i}. {r['topic']}  | score {r['score']}  | confidence {r['confidence_label']} ({r['confidence']})")
        print(f"   why: {r['reason']}")

    print("\n=== TOPIC-WISE MARK SHARE BY YEAR (%) ===")
    print("Topic".ljust(40) + "".join(str(y).rjust(7) for y in years))
    for r in rows:
        shares = stats[r["topic"]]["share_by_year"]
        print(r["topic"].ljust(40) + "".join(f"{s * 100:7.0f}" for s in shares))

    print("\n=== QUESTION TYPES AND DIFFICULTY ===")
    for t in ("theory", "numerical", "derivation"):
        print(f"{t}: {sum(1 for q in questions if q['qtype'] == t)} questions")
    for d in ("easy", "medium", "hard"):
        print(f"{d}: {sum(1 for q in questions if q['difficulty'] == d)} questions")

    print(f"\n=== REVISION PLAN FOR {hours} HOURS ===")
    for topic, h in plan:
        print(f"{h:5.2f} h  {topic}")

    unclassified = [q for q in questions if q["topic"] == "Unclassified"]
    if unclassified:
        print(f"\n{len(unclassified)} questions could not be matched to a topic:")
        for q in unclassified:
            print(f"  {q['year']} Q{q['qno']}: {q['text'][:70]}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--papers", default=".", help="folder with paper_<year>.txt/.pdf files")
    parser.add_argument("--syllabus", default="syllabus.json")
    parser.add_argument("--hours", type=float, default=10, help="hours you have to revise")
    parser.add_argument("--json", help="also save the ranking to this JSON file")
    args = parser.parse_args()

    questions, stats, years, rows, plan = run(args.papers, args.syllabus, args.hours)
    print_report(questions, stats, years, rows, plan, args.hours)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"ranking": rows, "plan": plan}, f, indent=2)


if __name__ == "__main__":
    main()
