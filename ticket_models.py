from dataclasses import dataclass


def validate_text(value, field_name, max_length):
    if not isinstance(value, str):
        raise ValueError(f"{field_name}: wymagana jest wartość tekstowa.")

    cleaned = value.strip()

    if not cleaned:
        raise ValueError(f"{field_name}: pole nie może być puste.")

    if len(cleaned) > max_length:
        raise ValueError(
            f"{field_name}: przekroczono limit {max_length} znaków."
        )

    return cleaned


@dataclass(frozen=True)
class Ticket:
    id: str
    subject: str
    message: str

    def __post_init__(self):
        limits = {
            "id": 100,
            "subject": 200,
            "message": 10000,
        }

        for field_name, max_length in limits.items():
            value = getattr(self, field_name)
            cleaned = validate_text(value, field_name, max_length)

            object.__setattr__(self, field_name, cleaned)