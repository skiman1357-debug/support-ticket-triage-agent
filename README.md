---
title: Support Ticket Triage API
emoji: "🎫"
colorFrom: blue
colorTo: gray
sdk: docker
app_port: 7860
app_file: api.py
pinned: false
---

# Support Ticket Triage Agent

A portfolio application for the fictional CloudDesk service. FastAPI retrieves
knowledge documents using local CPU embeddings and asks an xAI model to classify
a ticket and draft a reply. Streamlit provides the user interface.

The application never sends replies or performs account actions. Human review
is flagged for sensitive cases and insufficient knowledge. Source IDs are checked
against retrieved documents; this does not verify every claim in the draft.

## API hosting

The Docker image uses Python 3.13, CPU-only PyTorch, one Uvicorn worker and port
7860. The embedding model is downloaded during the build and included in the
image. Startup loads it from that cache and embeds the six knowledge documents.
No persistent disk is needed for this read-only knowledge base.

Configure these **Secrets** in Hugging Face Space settings:

- `XAI_API_KEY`: your xAI API key.
- `TRIAGE_API_KEY`: the shared API authentication key.

Configure this **Variable**:

- `XAI_MODEL`: the model identifier verified in your local application.

Do not put secrets in the Dockerfile, README, Git repository or build arguments.
Public API documentation is available at `/docs`; `/health` is public.
`POST /triage` requires the `X-API-Key` header.

## Streamlit hosting

Use `app.py` with `requirements.txt` and Python 3.13. Set Streamlit secrets:

```toml
TRIAGE_API_URL = "https://YOUR-SPACE-SUBDOMAIN.hf.space"
TRIAGE_API_KEY = "SET_THE_SAME_KEY_AS_THE_API"
DEMO_ACCESS_CODE = "SET_A_SEPARATE_VISITOR_CODE"
```

Use the API base URL without `/triage`. Keep the xAI API key on the backend only.

## Validation

The `Container check` GitHub Actions workflow builds the image on Linux AMD64.
The Docker build runs the existing unit tests (24 discovered tests in the supplied
source). These mock retrieval and xAI. The workflow then starts the real server
with the cached embedding model, checks that `/health` reports six documents and
checks that a request without an API key returns 401. No xAI secrets are required
and no xAI request is made.

Run the workflow after committing the deployment files. A successful run is
required before treating the container as verified. This package was prepared
without a local Docker runtime; it is not a record of a successful build.

The workflow neither publishes an image nor deploys to Hugging Face. A real
authenticated end-to-end request remains to be checked after deployment.

## Limits

- Six synthetic knowledge documents and a small retrieval evaluation set.
- Similarity scores are not confidence probabilities.
- No global request rate limiter or spending cap is implemented.
- The demo access code should be shared selectively.
- Direct dependencies are version-pinned; transitive dependencies, the base image
  tag and model revision are not fully locked.

See `DEPLOYMENT_PL.md` for the next setup steps.
