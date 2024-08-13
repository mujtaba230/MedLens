"""Generate synthetic clinical data using Faker for testing."""
import json
import random
import argparse
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

DIAGNOSES = [
    "Type 2 Diabetes Mellitus", "Essential Hypertension", "Community Acquired Pneumonia",
    "Chronic Obstructive Pulmonary Disease", "Atrial Fibrillation", "Major Depressive Disorder",
    "Osteoarthritis of the Knee", "Gastroesophageal Reflux Disease", "Hypothyroidism",
    "Chronic Kidney Disease Stage 3", "Heart Failure with Reduced Ejection Fraction",
    "Peripheral Neuropathy", "Hyperlipidemia", "Asthma", "Migraine without Aura"
]

MEDICATIONS = [
    "Metformin 500mg PO BID", "Lisinopril 10mg PO daily", "Atorvastatin 20mg PO qHS",
    "Amlodipine 5mg PO daily", "Aspirin 81mg PO daily", "Omeprazole 20mg PO daily",
    "Levothyroxine 75mcg PO daily", "Albuterol 90mcg inhaler PRN", "Sertraline 50mg PO daily",
    "Furosemide 40mg PO daily", "Warfarin 5mg PO daily", "Insulin Glargine 20 units SC qHS",
    "Glipizide 5mg PO BID", "Prednisone 10mg PO daily", "Gabapentin 300mg PO TID"
]

PROCEDURES = [
    "Chest X-ray PA and lateral", "CT scan abdomen with contrast",
    "Echocardiogram with Doppler", "Colonoscopy", "Upper endoscopy",
    "MRI lumbar spine without contrast", "ECG 12-lead", "Spirometry",
    "Bone density scan", "Liver ultrasound", "Mammography screening",
    "Stress test", "Biopsy skin lesion", "Lumbar puncture", "Thyroid ultrasound"
]

SYMPTOMS = [
    "Chest pain", "Shortness of breath", "Fatigue", "Headache", "Nausea",
    "Dizziness", "Cough", "Fever", "Weight loss", "Palpitations",
    "Lower back pain", "Joint stiffness", "Rash", "Abdominal pain", "Polyuria"
]

VITALS = [
    {"bp": "120/80", "hr": 72, "temp": 98.6, "rr": 16, "spo2": 98},
    {"bp": "145/92", "hr": 88, "temp": 99.2, "rr": 20, "spo2": 95},
    {"bp": "132/86", "hr": 76, "temp": 98.4, "rr": 18, "spo2": 97},
    {"bp": "110/70", "hr": 65, "temp": 97.8, "rr": 14, "spo2": 99},
    {"bp": "158/98", "hr": 95, "temp": 100.1, "rr": 22, "spo2": 92},
]


def generate_patient_record():
    dob = fake.date_of_birth(minimum_age=18, maximum_age=95)
    age = (datetime.now() - datetime(dob.year, dob.month, dob.day)).days // 365
    return {
        "patient_id": f"P-{fake.uuid4()[:8].upper()}",
        "name": fake.name(),
        "date_of_birth": dob.isoformat(),
        "age": age,
        "gender": random.choice(["M", "F", "Other"]),
        "mrn": fake.numerify(text="MRN-########"),
        "address": fake.address(),
        "phone": fake.phone_number(),
    }


def generate_encounter(patient_id: str):
    encounter_date = fake.date_between(start_date="-2y", end_date="today")
    encounter_type = random.choice(["Office Visit", "Emergency Department", "Inpatient Admission", "Telehealth", "Urgent Care"])
    provider = f"Dr. {fake.last_name()}, {random.choice(['MD', 'DO', 'NP', 'PA'])}"
    chief_complaint = random.choice(SYMPTOMS)
    vitals = random.choice(VITALS)

    # Generate 1-4 diagnoses
    dx_count = random.choices([1, 2, 3, 4], weights=[40, 35, 20, 5])[0]
    diagnoses = random.sample(DIAGNOSES, k=min(dx_count, len(DIAGNOSES)))

    # Generate 1-5 medications
    med_count = random.choices([0, 1, 2, 3, 4, 5], weights=[5, 20, 30, 25, 15, 5])[0]
    medications = random.sample(MEDICATIONS, k=min(med_count, len(MEDICATIONS)))

    # Generate 0-3 procedures
    proc_count = random.choices([0, 1, 2, 3], weights=[40, 30, 20, 10])[0]
    procedures = random.sample(PROCEDURES, k=min(proc_count, len(PROCEDURES)))

    return {
        "encounter_id": f"E-{fake.uuid4()[:8].upper()}",
        "patient_id": patient_id,
        "encounter_date": encounter_date.isoformat(),
        "encounter_type": encounter_type,
        "provider": provider,
        "chief_complaint": chief_complaint,
        "vitals": vitals,
        "hpi": fake.paragraph(nb_sentences=random.randint(3, 8)),
        "assessment_and_plan": fake.paragraph(nb_sentences=random.randint(2, 6)),
        "diagnoses": diagnoses,
        "medications": medications,
        "procedures": procedures,
    }


def generate_dataset(num_patients: int = 1000, encounters_per_patient: int = 3):
    records = []
    for _ in range(num_patients):
        patient = generate_patient_record()
        patient_encounters = [generate_encounter(patient["patient_id"]) for _ in range(encounters_per_patient)]
        records.append({
            "patient": patient,
            "encounters": patient_encounters
        })
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--patients", type=int, default=1000)
    parser.add_argument("--encounters", type=int, default=3)
    parser.add_argument("--output", default="synthetic_patients.json")
    args = parser.parse_args()

    dataset = generate_dataset(args.patients, args.encounters)
    with open(args.output, "w") as f:
        json.dump(dataset, f, indent=2)
    print(f"Generated {args.patients} patients with {args.encounters} encounters each → {args.output}")


if __name__ == "__main__":
    main()
