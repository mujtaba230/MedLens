from typing import List, Optional


# Simplified code mappings for demo. In production, use UMLS/ICD-10-CM/CPT APIs.
ICD10_MAPPING = {
    "diabetes": ["E11.9", "E10.9", "E11.65"],
    "hypertension": ["I10", "I11.9", "I15.9"],
    "pneumonia": ["J18.9", "J15.9", "J12.9"],
    "fracture": ["M84.40", "S42.001A", "S82.001A"],
    "cancer": ["C80.1", "C78.00", "C79.9"],
    "asthma": ["J45.909", "J45.901", "J45.20"],
    "copd": ["J44.9", "J44.1", "J43.9"],
    "stroke": ["I63.9", "I64", "I61.9"],
    "chest pain": ["R07.9", "R07.81", "I20.9"],
    "shortness of breath": ["R06.00", "R06.02", "R06.09"],
    "fever": ["R50.9", "R50.81", "R50.82"],
    "headache": ["R51", "G44.209", "G43.909"],
}

CPT_MAPPING = {
    "surgery": ["44970", "47562", "49650"],
    "biopsy": ["11100", "11101", "38500"],
    "mri": ["72148", "72158", "73221"],
    "ct scan": ["70450", "70460", "70470"],
    "x-ray": ["73060", "73070", "73562"],
    "endoscopy": ["43235", "43239", "45378"],
    "colonoscopy": ["45378", "45380", "45385"],
    "glucose": ["82947", "82948", "82950"],
    "hemoglobin": ["85025", "85027", "85018"],
    "wbc": ["85025", "85027", "85032"],
    "creatinine": ["82565", "82570", "82575"],
    "cholesterol": ["80061", "82465", "83718"],
    "sodium": ["84295", "84300", "84302"],
}

SNOMED_MAPPING = {
    "diabetes": ["44054006", "46635009"],
    "hypertension": ["38341003", "59621000"],
    "pneumonia": ["233604007", "882784001"],
    "fracture": ["58106000", "125605004"],
    "cancer": ["363346000", "269475001"],
    "asthma": ["195967001", "233678006"],
    "copd": ["13645005", "87433001"],
    "stroke": ["230690007", "422504002"],
    "metformin": ["68091002", "109076001"],
    "insulin": ["67866001", "325072002"],
    "lisinopril": ["108601001", "372567009"],
    "aspirin": ["7947003", "387458008"],
}

ICD10_NAMES = {
    "E11.9": "Type 2 diabetes mellitus without complications",
    "E10.9": "Type 1 diabetes mellitus without complications",
    "I10": "Essential (primary) hypertension",
    "J18.9": "Pneumonia, unspecified organism",
    "M84.40": "Pathological fracture, unspecified site",
    "C80.1": "Malignant (primary) neoplasm, unspecified",
    "J45.909": "Unspecified asthma, uncomplicated",
    "J44.9": "Chronic obstructive pulmonary disease, unspecified",
    "I63.9": "Cerebral infarction, unspecified",
    "R07.9": "Chest pain, unspecified",
    "R06.00": "Dyspnea, unspecified",
    "R50.9": "Fever, unspecified",
    "R51": "Headache",
}

CPT_NAMES = {
    "44970": "Laparoscopic appendectomy",
    "47562": "Laparoscopic cholecystectomy",
    "72148": "MRI lumbar spine without contrast",
    "70450": "CT head without contrast",
    "73060": "X-ray forearm",
    "43235": "Upper GI endoscopy, diagnostic",
    "45378": "Colonoscopy, diagnostic",
    "82947": "Glucose quantitative blood",
    "85025": "CBC with differential",
    "82565": "Creatinine blood",
    "80061": "Lipid panel",
    "84295": "Sodium serum",
}


class CodeMappingService:
    def map_entity(self, normalized_name: str, entity_type: str) -> List[dict]:
        lower = normalized_name.lower()
        results = []

        for keyword, codes in ICD10_MAPPING.items():
            if keyword in lower:
                for code in codes:
                    results.append({
                        "code_system": "ICD-10",
                        "code": code,
                        "name": ICD10_NAMES.get(code, keyword.title()),
                        "confidence": 0.85
                    })

        for keyword, codes in CPT_MAPPING.items():
            if keyword in lower:
                for code in codes:
                    results.append({
                        "code_system": "CPT",
                        "code": code,
                        "name": CPT_NAMES.get(code, keyword.title()),
                        "confidence": 0.8
                    })

        for keyword, codes in SNOMED_MAPPING.items():
            if keyword in lower:
                for code in codes:
                    results.append({
                        "code_system": "SNOMED-CT",
                        "code": code,
                        "name": keyword.title(),
                        "confidence": 0.75
                    })

        return results

code_mapping_service = CodeMappingService()
