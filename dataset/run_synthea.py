"""Wrapper to generate synthetic patient records using Synthea.

Requires Synthea installed: https://github.com/synthetichealth/synthea
Usage:
    python run_synthea.py --population 1000 --output-dir ./synthea_output
"""
import os
import argparse
import subprocess
import json
import glob


def run_synthea(population: int, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    cmd = [
        "java", "-jar", "synthea.jar",
        "-p", str(population),
        "--exporter.fhir.export", "false",
        "--exporter.csv.export", "true",
        "-o", output_dir,
    ]
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True, cwd=output_dir)
    except FileNotFoundError:
        print("ERROR: Synthea not found. Please download synthea.jar from https://github.com/synthetichealth/synthea/releases")
        print(f"Expected at: {os.path.join(output_dir, 'synthea.jar')}")
        raise


def convert_synthea_to_json(csv_dir: str, output_file: str):
    """Convert Synthea CSV output into our JSON patient format."""
    import csv

    patients = []
    patient_path = os.path.join(csv_dir, "patients.csv")
    encounters_path = os.path.join(csv_dir, "encounters.csv")
    conditions_path = os.path.join(csv_dir, "conditions.csv")
    medications_path = os.path.join(csv_dir, "medications.csv")
    procedures_path = os.path.join(csv_dir, "procedures.csv")

    if not os.path.exists(patient_path):
        print(f"No patients.csv found in {csv_dir}")
        return

    with open(patient_path) as f:
        reader = csv.DictReader(f)
        patient_rows = list(reader)

    for p in patient_rows:
        patient_id = p.get("Id", p.get("PATIENT", ""))
        record = {
            "patient_id": patient_id,
            "name": f"{p.get('FIRST', '')} {p.get('LAST', '')}",
            "gender": p.get("GENDER", ""),
            "birth_date": p.get("BIRTHDATE", ""),
            "address": f"{p.get('ADDRESS', '')}, {p.get('CITY', '')}, {p.get('STATE', '')}",
            "encounters": [],
            "diagnoses": [],
            "medications": [],
            "procedures": [],
        }

        # Pull related rows
        for path, key in [(encounters_path, "encounters"),
                           (conditions_path, "diagnoses"),
                           (medications_path, "medications"),
                           (procedures_path, "procedures")]:
            if os.path.exists(path):
                with open(path) as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get("PATIENT") == patient_id or row.get("PATIENT") == patient_id:
                            record[key].append(dict(row))

        patients.append(record)

    with open(output_file, "w") as f:
        json.dump(patients, f, indent=2)
    print(f"Converted {len(patients)} Synthea patients to {output_file}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--population", type=int, default=1000)
    parser.add_argument("--output-dir", default="synthea_output")
    parser.add_argument("--json-out", default="synthea_patients.json")
    args = parser.parse_args()

    run_synthea(args.population, args.output_dir)

    # Find the CSV subdirectory Synthea creates
    csv_dirs = glob.glob(os.path.join(args.output_dir, "*/csv"))
    if csv_dirs:
        convert_synthea_to_json(csv_dirs[0], args.json_out)
    else:
        print("No CSV output found. Check Synthea output.")


if __name__ == "__main__":
    main()
