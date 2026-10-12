"""Quick self-check: run `python test_pipeline.py`.

We labelled every question in the 4 sample papers by hand and check that the
classifier agrees. This is how we know the topic matching actually works.
"""
from analyze import question_type
from classify import TopicClassifier
from extract import load_questions, split_questions

DC, AC, TP, MAG = "DC Circuits and Network Theorems", "Single Phase AC Circuits", "Three Phase Circuits", "Magnetic Circuits"
TR, DCM, IM, SAF = "Transformers", "DC Machines", "Induction Motors", "Electrical Safety and Wiring"

# (year, question number) -> topic we expect, labelled by hand
EXPECTED = {
    2022: [DC, DC, AC, TP, TR, DCM, SAF, MAG],
    2023: [DC, DC, AC, TP, TR, IM, SAF, MAG],
    2024: [DC, AC, IM, TR, TR, DCM, SAF, TP],
    2025: [DC, AC, TR, TR, IM, DCM, SAF, TP],
}


def test_extraction():
    qs = load_questions(".")
    assert len(qs) == 32, f"expected 32 questions, got {len(qs)}"
    assert all(not q["marks_assumed"] for q in qs), "every sample question has marks"
    # hyphenated line break "signifi-\ncance" must be repaired
    assert any("significance" in q["text"] for q in qs)


def test_messy_text():
    messy = "Page 1\nQ1(a). Derive the trans-\nformer emf equation. (8 marks)\nQ2 Explain earthing"
    qs = split_questions(__import__("extract").clean(messy), 2030)
    assert qs[0]["marks"] == 8 and "transformer" in qs[0]["text"]
    assert qs[1]["marks_assumed"] and qs[1]["marks"] == 5


def test_question_types():
    assert question_type("Derive the emf equation") == "derivation"
    assert question_type("A load of 10 A at 230 V. Calculate power") == "numerical"
    assert question_type("Explain earthing") == "theory"


def test_classifier_accuracy():
    clf = TopicClassifier("syllabus.json")
    qs = load_questions(".")
    wrong = []
    for q in qs:
        want = EXPECTED[q["year"]][int(q["qno"]) - 1]
        got, _ = clf.classify(q["text"])
        if got != want:
            wrong.append((q["year"], q["qno"], want, got))
    print(f"classifier: {len(qs) - len(wrong)}/{len(qs)} correct")
    assert not wrong, wrong


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok:", name)
