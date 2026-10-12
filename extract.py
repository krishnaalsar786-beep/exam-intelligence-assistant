"""Step 1: read past papers (.txt or .pdf) and split them into clean questions.

Expected question format (one question per "Q<number>" block, marks in [ ] or ( )):

    Q1. State and explain Kirchhoff's laws with examples. [5]
    Q2(a). Derive the emf equation of a transformer. (8 marks)

Real papers are messy, so we clean the text first: join words split across
lines, drop page headers, and collapse extra spaces.
"""
import glob
import os
import re

# A question starts with Q, a number, and optionally (a)/(b), like "Q3(a)."
Q_START = re.compile(r"(?m)^\s*Q\s*(\d+)\s*(?:\(([a-z])\))?\s*[.):-]?\s*")
# Marks look like [8] or (8 marks)
MARKS = re.compile(r"[\[(]\s*(\d+)\s*(?:marks?)?\s*[\])]", re.I)
HEADER_LINES = re.compile(
    r"(?im)^\s*(page\s*\d+.*|roll no.*|time allowed.*|maximum marks.*)$"
)
DEFAULT_MARKS = 5  # used only when a question has no marks written on it


def read_paper(path):
    """Return the raw text of a paper. PDFs need the `pypdf` package."""
    if path.lower().endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(path)
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    with open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


def clean(text):
    text = text.replace("­", "")  # invisible soft hyphens
    text = re.sub(r"-\n(\w)", r"\1", text)  # "trans-\nformer" -> "transformer"
    text = HEADER_LINES.sub("", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text


def split_questions(text, year):
    """Cut the cleaned text into questions and pull out the marks."""
    starts = list(Q_START.finditer(text))
    questions = []
    for i, m in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(text)
        body = text[m.end():end]
        marks_match = MARKS.search(body)
        marks = int(marks_match.group(1)) if marks_match else DEFAULT_MARKS
        body = MARKS.sub("", body)
        body = re.sub(r"\s+", " ", body).strip()
        if len(body) < 10:  # ignore stray fragments
            continue
        label = m.group(1) + (m.group(2) or "")
        questions.append(
            {
                "year": year,
                "qno": label,
                "text": body,
                "marks": marks,
                "marks_assumed": marks_match is None,
            }
        )
    return questions


def load_questions(papers_dir, pattern="paper_*.*"):
    """Load every paper_<year>.txt / .pdf in the folder."""
    questions = []
    for path in sorted(glob.glob(os.path.join(papers_dir, pattern))):
        year_match = re.search(r"(\d{4})", os.path.basename(path))
        if not year_match or not path.lower().endswith((".txt", ".pdf")):
            continue
        year = int(year_match.group(1))
        questions += split_questions(clean(read_paper(path)), year)
    return questions
