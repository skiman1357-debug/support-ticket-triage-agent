import json
from pathlib import Path


KB_PATH = Path(__file__).resolve().parent / "data" / "knowledge_base.json"

ALLOWED_CATEGORIES = {
    "billing",
    "account_access",
    "technical",
    "security",
}


def load_knowledge_base(path=KB_PATH):
    path = Path(path)

    with path.open("r", encoding="utf-8-sig") as file:
        documents = json.load(file)

    if not isinstance(documents, list) or not documents:
        raise ValueError("Baza wiedzy musi być niepustą listą.")

    required_fields = ("id", "title", "category", "content")
    seen_ids = set()
    validated_documents = []

    for position, document in enumerate(documents, start=1):
        if not isinstance(document, dict):
            raise ValueError(
                f"Dokument {position}: wymagany jest obiekt JSON."
            )

        cleaned = {}

        for field in required_fields:
            value = document.get(field)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"Dokument {position}: brak poprawnego pola {field}."
                )

            cleaned[field] = value.strip()

        if cleaned["id"] in seen_ids:
            raise ValueError(
                f"Powtórzony identyfikator dokumentu: {cleaned['id']}"
            )

        if cleaned["category"] not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"Nieznana kategoria: {cleaned['category']}"
            )

        seen_ids.add(cleaned["id"])
        validated_documents.append(cleaned)

    return validated_documents