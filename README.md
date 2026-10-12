# Exam Intelligence Assistant

A small Python tool that reads past question papers and tells a student **which topics deserve the most study time, and why**. Built for the GDGoC IET DAVV Technical Task 1.

It uses only the Python standard library (plus `pypdf`, only if you want to read PDF papers).

## What it does

1. **Extract** (`extract.py`): reads `paper_<year>.txt` or `.pdf` files, cleans the messy text (broken words, page headers) and splits it into questions with their marks.
2. **Map to syllabus** (`classify.py`): matches each question to a syllabus topic using IDF-weighted keyword coverage. If nothing matches well it says "Unclassified" instead of guessing.
3. **Analyse** (`analyze.py`): marks share per topic per year, trend over the years, question type (theory / numerical / derivation) and difficulty (easy / medium / hard).
4. **Rank** (`priority.py`): gives every topic a study-priority score (0-100), a confidence level and a plain-English reason, then splits your available hours into a revision plan.

## Run it

```
python main.py                  # uses the sample papers in this folder
python main.py --hours 12       # revision plan for 12 hours
python main.py --papers my_papers --syllabus my_syllabus.json
python test_pipeline.py         # self-check
```

To use your own subject: put `paper_2023.txt` (or `.pdf`) files in a folder, write questions as `Q1. ... [7]` (marks in brackets), and edit `syllabus.json` with your topics and keywords.

## How the score works

```
score = 50% total marks of the topic     (weightage)
      + 20% number of papers it appeared in (frequency)
      + 30% its mark share in the last 2 papers (recency)
      +/- up to 5 points for a rising or falling trend
```

Confidence = 60% topic-matching strength + 30% number of years of data + 10% number of questions. More papers means higher confidence.

## Honest limitations

- The papers in this repo are **synthetic samples I wrote for the demo**, not real DAVV papers. The results show how the tool works, not what will actually come in your exam.
- The classifier matches words, not meaning. Keywords in `syllabus.json` must be written well for a subject, and I tuned them while testing on the sample papers, so the 32/32 test score is optimistic for real papers.
- Difficulty is a simple rule (marks + question type), not a real measure.
- PDFs that are scanned images need OCR first; the tool only reads PDFs that contain real text.
- Question numbering must follow the `Q1.` style. Other layouts need a small change in `extract.py`.

## Ideas for next steps

- Add OCR for scanned papers.
- Replace keyword matching with sentence embeddings for semantic similarity.
- Simple web page (Flask/Streamlit) to upload papers and see charts.
