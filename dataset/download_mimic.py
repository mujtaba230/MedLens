"""Helper to prepare MIMIC-IV clinical notes for ingestion.

Requires:
    1. PhysioNet account and credentialed access to MIMIC-IV
    2. wget or mimic direct download via physionet

Usage:
    python download_mimic.py --output-dir ./mimic_notes --limit 5000
"""
import os
import argparse
import csv
import json


def extract_notes_from_mimic(mimic_dir: str, output_dir: str, limit: int = 5000):
    """Read MIMIC NOTEEVENTS / discharge summaries and convert to JSON lines."""
    os.makedirs(output_dir, exist_ok=True)

    # MIMIC-IV note paths vary by version; adapt as needed
    note_paths = [
        os.path.join(mimic_dir, "note", "discharge.csv"),
        os.path.join(mimic_dir, "note", "radiology.csv"),
        os.path.join(mimic_dir, "note", "noteevents.csv"),
    ]

    count = 0
    for path in note_paths:
        if not os.path.exists(path):
            print(f"Skipping missing file: {path}")
            continue
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if count >= limit:
                    break
                text = row.get("text", row.get("TEXT", "")).strip()
                if not text:
                    continue
                note_type = row.get("category", row.get("CATEGORY", "note"))
                note_id = row.get("note_id", row.get("ROW_ID", f"note_{count}"))
                out = {
                    "note_id": note_id,
                    "note_type": note_type,
                    "text": text,
                    "subject_id": row.get("subject_id", row.get("SUBJECT_ID", "")),
                    "hadm_id": row.get("hadm_id", row.get("HADM_ID", "")),
                }
                with open(os.path.join(output_dir, f"{note_id}.json"), "w") as out_f:
                    json.dump(out, out_f)
                count += 1
                if count % 1000 == 0:
                    print(f"Exported {count} notes...")
    print(f"Done. Exported {count} notes to {output_dir}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mimic-dir", required=True, help="Path to downloaded MIMIC-IV root directory")
    parser.add_argument("--output-dir", default="mimic_notes")
    parser.add_argument("--limit", type=int, default=5000)
    args = parser.parse_args()
    extract_notes_from_mimic(args.mimic_dir, args.output_dir, args.limit)


if __name__ == "__main__":
    main()
