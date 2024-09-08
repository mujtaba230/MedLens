"""Generate synthetic clinical documents using LLM for diverse content."""
import json
import os
import random
import argparse
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


# Templates for LLM-style generation (simulated with templates)
RADIOLOGY_TEMPLATES = [
    """CHEST X-RAY REPORT
Date: {date}
Ordering Provider: {provider}
Indication: {cc}

COMPARISON: None available.

FINDINGS:
The lungs are clear. No focal consolidation, pleural effusion, or pneumothorax. 
Cardiomediastinal silhouette is normal. Osseous structures are intact.

IMPRESSION:
No acute cardiopulmonary process.
""",
    """HEAD CT REPORT
Date: {date}
Ordering Provider: {provider}
Indication: {cc}

TECHNIQUE: Non-contrast CT of the head performed.

FINDINGS:
No intracranial hemorrhage, mass effect, or midline shift. 
Ventricular system is normal in size and configuration. 
No acute skull fracture identified.

IMPRESSION:
Normal non-contrast head CT.
""",
]

LAB_SUMMARY_TEMPLATES = [
    """LABORATORY SUMMARY
Date: {date}
Provider: {provider}

COMPREHENSIVE METABOLIC PANEL:
Sodium: {na} mEq/L (135-145)
Potassium: {k} mEq/L (3.5-5.0)
Chloride: {cl} mEq/L (98-107)
CO2: {co2} mEq/L (22-29)
BUN: {bun} mg/dL (7-20)
Creatinine: {cr} mg/dL (0.7-1.3)
Glucose: {glu} mg/dL (70-100)
Calcium: {ca} mg/dL (8.5-10.5)

HEMOGRAM:
WBC: {wbc} K/uL (4.5-11.0)
Hgb: {hgb} g/dL (12.0-16.0)
Hct: {hct} % (36-46)
Platelets: {plt} K/uL (150-400)

IMPRESSION:
{impression}
""",
]


def generate_radiology_report(provider: str, cc: str):
    template = random.choice(RADIOLOGY_TEMPLATES)
    return template.format(
        date=datetime.now().strftime("%Y-%m-%d"),
        provider=provider,
        cc=cc,
    )


def generate_lab_summary(provider: str, cc: str):
    template = random.choice(LAB_SUMMARY_TEMPLATES)
    values = {
        "na": round(random.gauss(140, 3), 1),
        "k": round(random.gauss(4.2, 0.4), 1),
        "cl": round(random.gauss(102, 2), 1),
        "co2": round(random.gauss(25, 1.5), 1),
        "bun": round(random.gauss(14, 3), 1),
        "cr": round(random.gauss(1.0, 0.2), 2),
        "glu": round(random.gauss(95, 15), 1),
        "ca": round(random.gauss(9.5, 0.4), 1),
        "wbc": round(random.gauss(7.5, 1.5), 1),
        "hgb": round(random.gauss(13.5, 1.0), 1),
        "hct": round(random.gauss(41, 2), 1),
        "plt": round(random.gauss(250, 40), 0),
    }
    abnormal = []
    if values["glu"] > 100:
        abnormal.append("Elevated glucose, consider diabetes workup.")
    if values["cr"] > 1.3:
        abnormal.append("Elevated creatinine, monitor renal function.")
    if values["wbc"] > 11:
        abnormal.append("Leukocytosis, evaluate for infection.")
    values["impression"] = " ".join(abnormal) if abnormal else "All values within normal limits."
    values["date"] = datetime.now().strftime("%Y-%m-%d")
    values["provider"] = provider
    values["cc"] = cc
    return template.format(**values)


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
    parser.add_argument("--output-dir", default="llm_documents")
    parser.add_argument("--count", type=int, default=100)
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    ccs = ["Chest pain", "Shortness of breath", "Headache", "Abdominal pain", "Fever", "Dizziness", "Cough", "Back pain"]
    for i in range(args.count):
        provider = f"Dr. Generated-{i}"
        cc = random.choice(ccs)
        if i % 2 == 0:
            content = generate_radiology_report(provider, cc)
            prefix = "radiology"
        else:
            content = generate_lab_summary(provider, cc)
            prefix = "lab"
        filename = os.path.join(args.output_dir, f"{prefix}_{i:04d}.pdf")
        create_pdf(filename, content)

    print(f"Generated {args.count} LLM-style documents in {args.output_dir}")


if __name__ == "__main__":
    main()
