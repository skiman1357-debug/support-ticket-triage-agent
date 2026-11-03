from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from api_security import require_api_key
from openai import APIConnectionError, APIStatusError, APITimeoutError
from pydantic import BaseModel, ConfigDict, Field

from semantic_search import KnowledgeSearch
from ticket_models import Ticket
from triage_agent import generate_triage
from triage_models import TriageResult
from api_models import KnowledgeSource, TriageResponse


class TicketRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    id: str = Field(min_length=1, max_length=100)
    subject: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=10000)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ładujemy model i dokumenty raz na start procesu serwera.
    app.state.search_engine = KnowledgeSearch()

    yield

    app.state.search_engine = None


app = FastAPI(
    title="Support Ticket Triage API",
    description=(
        "Classifies synthetic support tickets and prepares "
        "reply drafts using retrieved knowledge documents."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health(request: Request):
    search_engine = request.app.state.search_engine

    return {
        "status": "ok",
        "knowledge_documents": len(search_engine.documents),
    }


@app.post(
    "/triage",
    response_model=TriageResponse,
    dependencies=[Depends(require_api_key)],
)
def triage(payload: TicketRequest, request: Request):
    ticket = Ticket(
        id=payload.id,
        subject=payload.subject,
        message=payload.message,
    )

    search_engine = request.app.state.search_engine
    query = f"{ticket.subject}\n{ticket.message}"
    documents = search_engine.search(query, top_k=3)

    try:
        result = generate_triage(ticket, documents)

        documents_by_id = {
            document["id"]: document
            for document in documents
        }

        sources = [
            KnowledgeSource(
                id=source_id,
                title=documents_by_id[source_id]["title"],
                content=documents_by_id[source_id]["content"],
            )
            for source_id in result.source_ids
        ]

        return TriageResponse(
            **result.model_dump(),
            sources=sources,
        )

    except APITimeoutError as error:
        raise HTTPException(
            status_code=504,
            detail="AI service response timed out.",
        ) from error

    except APIConnectionError as error:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to the AI service.",
        ) from error

    except APIStatusError as error:
        raise HTTPException(
            status_code=502,
            detail="The AI service rejected the request.",
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=502,
            detail=(
                "The analysis could not be completed. "
                "Check server configuration and output validation."
            ),
        ) from error