from typing import Literal

from pydantic import BaseModel, ConfigDict


class TriageResult(BaseModel):
    """Uporządkowany wynik analizy zgłoszenia."""

    model_config = ConfigDict(extra="forbid")

    category: Literal[
        "billing",
        "account_access",
        "technical",
        "security",
        "other",
    ]

    priority: Literal["low", "normal", "high", "urgent"]

    knowledge_sufficient: bool
    needs_human_review: bool
    review_reason: str | None
    suggested_reply: str
    source_ids: list[str]