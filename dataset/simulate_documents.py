"""Convert synthetic records into simulated PDF clinical documents with optional noise."""
import json
import os
import random
import re
import argparse
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def add_typos(text: str, typo_rate: float = 0.02) -> str:
    if typo_rate <= 0:
        return text
    chars = list(text)
    for i in range(len(chars)):
        if random.random() < typo_rate and chars[i].isalpha():
            mutation = random.choice(["swap", "duplicate", "drop", "nearby"])
            if mutation == "swap" and i < len(chars) - 1:
                chars[i], chars[i + 1] = chars[i + 1], chars[i]
            elif mutation == "duplicate":
                chars[i] = chars[i] + chars[i]
            elif mutation == "drop":
                chars[i] = ""
            elif mutation == "nearby":
                nearby = {"a": "s", "s": "a", "e": "r", "r": "e", "o": "i", "i": "o", "n": "m", "m": "n"}
                chars[i] = nearby.get(chars[i].lower(), chars[i])
    return "".join(chars)


def generate_clinical_note(encounter: dict, note_type: str = "progress_note") -> str:
    date = encounter["encounter_date"]
    provider = encounter["provider"]
    cc = encounter["chief_complaint"]
    vitals = encounter["vitals"]
    hpi = encounter["hpi"]
    aap = encounter["assessment_and_plan"]
    dx = ", ".join(encounter["diagnoses"])
    meds = "; ".join(encounter["medications"]) if encounter["medications"] else "None"
    procs = "; ".join(encounter["procedures"]) if encounter["procedures"] else "None"

    if note_type == "discharge_summary":
        return f"""DISCHARGE SUMMARY
Date: {date}
Provider: {provider}
Chief Complaint: {cc}

HISTORY OF PRESENT ILLNESS:
{hpi}

VITALS ON ADMISSION:
BP {vitals['bp']}, HR {vitals['hr']}, Temp {vitals['temp']}F, RR {vitals['rr']}, SpO2 {vitals['spo2']}%

DIAGNOSES:
{dx}

MEDICATIONS ON DISCHARGE:
{meds}

PROCEDURES PERFORMED:
{procs}

ASSESSMENT AND PLAN:
{aap}

Follow up in 2 weeks or sooner if symptoms worsen.
"""
    elif note_type == "radiology_report":
        return f"""RADIOLOGY REPORT
Date: {date}
Radiologist: {provider}
Exam: {random.choice(encounter['procedures']) if encounter['procedures'] else 'Chest X-ray PA and lateral'}

CLINICAL INDICATION: {cc}

TECHNIQUE: Standard protocol performed without complications.

FINDINGS:
{fake_radiology_findings()}

IMPRESSION:
{aap[:200]} No acute findings.
"""
    else:
        return f"""PROGRESS NOTE
Date: {date}
Provider: {provider}
Chief Complaint: {cc}

VITALS:
BP {vitals['bp']}, HR {vitals['hr']}, Temp {vitals['temp']}F, RR {vitals['rr']}, SpO2 {vitals['spo2']}%

HPI:
{hpi}

DIAGNOSES:
{dx}

MEDICATIONS:
{meds}

PROCEDURES:
{procs}

ASSESSMENT AND PLAN:
{aap}
"""


def fake_radiology_findings():
    sentences = [
        "Lungs are clear without focal consolidation, pleural effusion, or pneumothorax.",
        "Heart size is within normal limits.",
        "Mediastinal contours are unremarkable.",
        "No acute osseous abnormalities identified.",
        "Visualized upper abdomen is unremarkable.",
        "There is mild degenerative change in the thoracic spine.",
    ]
    return " ".join(random.sample(sentences, k=random.randint(3, 5)))


def create_pdf(filename: str, content: str):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    for line in content.split("\n"):
        if line.strip():
            style = styles["Heading2"] if line.isupper() and len(line) < 40 else styles["BodyText"]
            story.append(Paragraph(line, style))
        else:
            story.append(Spacer(1, 6))
    doc.build(story)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="synthetic_patients.json")
    parser.add_argument("--output-dir", default="simulated_pdfs")
    parser.add_argument("--typos", type=float, default=0.02)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    with open(args.input) as f:
        data = json.load(f)

    count = 0
    for record in data[:args.limit]:
        patient = record["patient"]
        for enc in record["encounters"]:
            note_type = random.choice(["progress_note", "discharge_summary", "radiology_report"])
            text = generate_clinical_note(enc, note_type)
            text = add_typos(text, typo_rate=args.typos)

            filename = os.path.join(
                args.output_dir,
                f"{patient['patient_id']}_{enc['encounter_id']}_{note_type}.pdf"
            )
            create_pdf(filename, text)
            count += 1

    print(f"Generated {count} simulated PDF documents in {args.output_dir}")


if __name__ == "__main__":
    main()
