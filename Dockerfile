FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HF_HOME=/home/appuser/.cache/huggingface \
    TOKENIZERS_PARALLELISM=false \
    OMP_NUM_THREADS=2 \
    MKL_NUM_THREADS=2 \
    OPENBLAS_NUM_THREADS=2

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 appuser

WORKDIR /home/appuser/app
COPY requirements-api.txt ./requirements-api.txt

# Install the CPU wheel first. It also satisfies torch==2.15.0 in requirements.
RUN python -m pip install --no-cache-dir \
        --index-url https://download.pytorch.org/whl/cpu "torch==2.15.0+cpu" \
    && python -m pip install --no-cache-dir -r requirements-api.txt "httpx==0.28.1" \
    && python -m pip check \
    && python -c "import torch; assert torch.version.cuda is None, torch.__version__"

USER appuser

# Cache the public embedding model in the image, without any API secrets.
RUN python -c "from sentence_transformers import SentenceTransformer; m = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device='cpu'); m.encode(['Build smoke test'])"

# Runtime uses the model already downloaded during the build.
ENV HF_HUB_OFFLINE=1

COPY --chown=appuser:appuser api.py api_models.py api_security.py ./
COPY --chown=appuser:appuser ticket_models.py triage_agent.py triage_models.py ./
COPY --chown=appuser:appuser semantic_search.py knowledge_base.py ./
COPY --chown=appuser:appuser data/knowledge_base.json ./data/knowledge_base.json
COPY --chown=appuser:appuser test_api.py test_triage_validation.py ./

# These existing tests mock retrieval and xAI; no real API call is made.
RUN python -m unittest discover -v

EXPOSE 7860
HEALTHCHECK --interval=30s --timeout=5s --start-period=120s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:7860/health', timeout=4)"

CMD ["python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
