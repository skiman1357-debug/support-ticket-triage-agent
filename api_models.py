from pydantic import BaseModel, ConfigDict

from triage_models import TriageResult


class KnowledgeSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    content: str


class TriageResponse(TriageResult):
    sources: list[KnowledgeSource]