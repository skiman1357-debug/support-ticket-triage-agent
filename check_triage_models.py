from pydantic import ValidationError

from triage_models import TriageResult


def main():
    example = {
        "category": "billing",
        "priority": "normal",
        "knowledge_sufficient": True,
        "needs_human_review": True,
        "review_reason": (
            "The billing team must verify the payment "
            "and authorize account reactivation."
        ),
        "suggested_reply": (
            "Please provide your invoice number or payment reference "
            "so the billing team can investigate the blocked access. "
            "Do not share full card details, passwords or security codes."
        ),
        "source_ids": ["KB-001"],
    }

    result = TriageResult.model_validate(example)

    print("=== POPRAWNY WYNIK ===")
    print(result.model_dump_json(indent=2))

    print("\n=== KONTROLA NIEPOPRAWNEGO PRIORYTETU ===")

    invalid_example = {
        **example,
        "priority": "super_urgent",
    }

    try:
        TriageResult.model_validate(invalid_example)
    except ValidationError as error:
        print("Kontrolowany błąd: odrzucono nieznany priorytet.")

        for detail in error.errors():
            print(f"Pole: {detail['loc']}")
            print(f"Powód: {detail['msg']}")


if __name__ == "__main__":
    main()