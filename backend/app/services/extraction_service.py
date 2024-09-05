import json
import os
from typing import List, Optional
import httpx

from app.core.config import get_settings

settings = get_settings()

EXTRACTION_PROMPT = """You are a clinical entity extraction system. Given the following clinical text, extract all relevant clinical entities and return them in strict JSON format.

Extract the following entity types:
- diagnosis: Medical diagnoses and conditions
- medication: Drugs, medications, dosages
- procedure: Medical procedures, surgeries, therapies
- symptom: Patient-reported symptoms
- lab_result: Lab test names and results

Return JSON in this exact format:
{
  "entities": [
    {
      "entity_type": "diagnosis|medication|procedure|symptom|lab_result",
      "text": "exact text from document",
      "normalized_name": "standardized medical term",
      "confidence": 0.95
    }
  ]
}

Clinical text:
{text}
"""


class ExtractionService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.openai_key = settings.OPENAI_API_KEY
        self.openai_model = settings.OPENAI_MODEL
        self.anthropic_key = settings.ANTHROPIC_API_KEY
        self.anthropic_model = settings.ANTHROPIC_MODEL

    async def extract_entities(self, text: str) -> List[dict]:
        prompt = EXTRACTION_PROMPT.format(text=text[:8000])

        if self.provider == "openai" and self.openai_key:
            return await self._extract_openai(prompt)
        elif self.provider == "anthropic" and self.anthropic_key:
            return await self._extract_anthropic(prompt)
        else:
            return self._extract_mock(text)

    async def _extract_openai(self, prompt: str) -> List[dict]:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"},
                    json={
                        "model": self.openai_model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.0,
                        "max_tokens": 2000
                    },
                    timeout=60
                )
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return self._parse_json_response(content)
        except Exception as e:
            print(f"OpenAI extraction error: {e}")
            return []

    async def _extract_anthropic(self, prompt: str) -> List[dict]:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.anthropic_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.anthropic_model,
                        "max_tokens": 2000,
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    timeout=60
                )
                resp.raise_for_status()
                data = resp.json()
                content = data["content"][0]["text"]
                return self._parse_json_response(content)
        except Exception as e:
            print(f"Anthropic extraction error: {e}")
            return []

    def _parse_json_response(self, content: str) -> List[dict]:
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        try:
            data = json.loads(content)
            return data.get("entities", [])
        except json.JSONDecodeError:
            return []

    def _extract_mock(self, text: str) -> List[dict]:
        lower = text.lower()
        entities = []
        diagnosis_keywords = ["diabetes", "hypertension", "pneumonia", "fracture", "cancer", "asthma", "copd", "stroke"]
        medication_keywords = ["metformin", "insulin", "lisinopril", "aspirin", "atorvastatin", "amoxicillin"]
        procedure_keywords = ["surgery", "biopsy", "mri", "ct scan", "x-ray", "endoscopy", "colonoscopy"]
        symptom_keywords = ["chest pain", "shortness of breath", "fever", "nausea", "headache", "dizziness"]
        lab_keywords = ["glucose", "hemoglobin", "wbc", "creatinine", "cholesterol", "sodium"]

        for kw in diagnosis_keywords:
            if kw in lower:
                idx = lower.find(kw)
                entities.append({
                    "entity_type": "diagnosis",
                    "text": text[idx:idx+len(kw)],
                    "normalized_name": kw.title(),
                    "confidence": 0.85
                })
        for kw in medication_keywords:
            if kw in lower:
                idx = lower.find(kw)
                entities.append({
                    "entity_type": "medication",
                    "text": text[idx:idx+len(kw)],
                    "normalized_name": kw.title(),
                    "confidence": 0.9
                })
        for kw in procedure_keywords:
            if kw in lower:
                idx = lower.find(kw)
                entities.append({
                    "entity_type": "procedure",
                    "text": text[idx:idx+len(kw)],
                    "normalized_name": kw.title(),
                    "confidence": 0.8
                })
        for kw in symptom_keywords:
            if kw in lower:
                idx = lower.find(kw)
                entities.append({
                    "entity_type": "symptom",
                    "text": text[idx:idx+len(kw)],
                    "normalized_name": kw.title(),
                    "confidence": 0.75
                })
        for kw in lab_keywords:
            if kw in lower:
                idx = lower.find(kw)
                entities.append({
                    "entity_type": "lab_result",
                    "text": text[idx:idx+len(kw)],
                    "normalized_name": kw.title(),
                    "confidence": 0.8
                })
        return entities


extraction_service = ExtractionService()
