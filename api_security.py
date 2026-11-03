import hmac
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader


ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_PATH, override=False)

key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
)


def require_api_key(
    supplied_key: str | None = Security(key_header),
):
    expected_key = os.getenv("TRIAGE_API_KEY", "").strip()

    if not expected_key:
        raise HTTPException(
            status_code=503,
            detail="API authentication is not configured.",
        )

    if not supplied_key or not hmac.compare_digest(
        supplied_key.encode("utf-8"),
        expected_key.encode("utf-8"),
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key.",
            headers={"WWW-Authenticate": "APIKey"},
        )