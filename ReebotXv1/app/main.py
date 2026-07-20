"""RebootX FastAPI Application — AI-Driven Tech Refresh Engine.

This is the entry point. It wires together:
- Knowledge loader (JSON files → validated docs)
- Knowledge service (ChromaDB vector store)
- Ollama service (local LLM)
- Assessment service (RAG orchestrator)
- Bridge service (scanner → assessment adapter)

Start with:
    uvicorn app.main:app --reload --port 8000
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.data.knowledge_loader import load_from_directory, get_knowledge_stats
from app.models.schemas import (
    HealthResponse,
    KnowledgeStatsResponse,
    ScanAndAssessRequest,
    UpgradeAssessment,
    UpgradeRequest,
)
from app.services.knowledge_service import KnowledgeService
from app.services.ollama_service import OllamaService
from app.services.assessment_service import AssessmentService
from app.services.bridge_service import BridgeService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Service Initialisation
# ---------------------------------------------------------------------------

knowledge_service = KnowledgeService()
ollama_service = OllamaService()
assessment_service = AssessmentService(knowledge_service, ollama_service)
bridge_service = BridgeService()


# ---------------------------------------------------------------------------
# Application Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(_: FastAPI):
    """On startup: load knowledge documents from disk and sync into ChromaDB."""
    documents = load_from_directory()
    if documents:
        count = knowledge_service.ingest_documents(documents)
        logger.info("Synced %d knowledge documents into ChromaDB", count)
    else:
        logger.warning("No knowledge documents found — KB will be empty")
    yield


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    description=(
        "RebootX — AI-Driven Tech Refresh Engine. "
        "Automated compatibility validation and integration risk assessment "
        "for database, EMR, Python, and MWAA upgrades. "
        "Combines a repository scanner (dependency graph) with RAG-powered "
        "AI analysis (ChromaDB + Ollama/Llama 3)."
    ),
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", tags=["Info"])
async def root():
    """Root endpoint — application info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "AI-Driven Tech Refresh Engine",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "assess_upgrade": "/assess-upgrade",
            "scan_and_assess": "/scan-and-assess",
            "knowledge_stats": "/knowledge/stats",
        },
    }


@app.get("/health", response_model=HealthResponse, tags=["Info"])
async def health_check():
    """Health check — reports Ollama status and knowledge base size."""
    ollama_up = await ollama_service.is_available()
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        ollama_available=ollama_up,
        knowledge_documents=knowledge_service.document_count,
    )


@app.post(
    "/assess-upgrade",
    response_model=UpgradeAssessment,
    tags=["Assessment"],
    summary="Run a compatibility assessment",
    description=(
        "Accepts an upgrade request with technology type, versions, "
        "dependencies, and integrations. Returns a structured risk "
        "assessment with identified risks and recommendations. "
        "Uses AI (Ollama/Llama 3) if available, falls back to rules."
    ),
)
async def assess_upgrade(request: UpgradeRequest):
    """Core assessment endpoint — accepts UpgradeRequest, returns UpgradeAssessment."""
    try:
        result = await assessment_service.assess(request)
        return result
    except Exception as exc:
        logger.error("Assessment failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Assessment failed: {exc}")


@app.post(
    "/scan-and-assess",
    response_model=dict,
    tags=["Assessment"],
    summary="Scan a repository and run assessment in one call",
    description=(
        "Bridge endpoint: scans the target repository using the "
        "Repository Scanner, auto-detects technology type and dependencies, "
        "then runs the full RAG-powered assessment pipeline. "
        "Returns both the scan results and the assessment."
    ),
)
async def scan_and_assess(request: ScanAndAssessRequest):
    """Bridge endpoint — scan repo → build UpgradeRequest → assess."""
    try:
        # Step 1: Scan the repo and build an UpgradeRequest
        scan_dict, upgrade_request = bridge_service.scan_and_build_request(
            repo_path=request.repo_path,
            target_version=request.target_version,
            current_version=request.current_version,
            environment=request.environment or "production",
        )

        # Step 2: Run the assessment
        assessment = await assessment_service.assess(upgrade_request)

        # Step 3: Return combined result
        return {
            "scan_result": scan_dict,
            "upgrade_request": upgrade_request.model_dump(),
            "assessment": assessment.model_dump(),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("Scan-and-assess failed: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scan-and-assess failed: {exc}")


@app.get(
    "/knowledge/stats",
    response_model=KnowledgeStatsResponse,
    tags=["Knowledge"],
    summary="Knowledge base statistics",
)
async def knowledge_stats():
    """Show knowledge base document counts by technology type."""
    stats = get_knowledge_stats()
    return KnowledgeStatsResponse(
        total_documents=knowledge_service.document_count,
        by_technology=stats,
    )


@app.post(
    "/knowledge/reload",
    tags=["Knowledge"],
    summary="Reload knowledge base from disk",
)
async def reload_knowledge():
    """Re-read knowledge JSON files and re-sync into ChromaDB."""
    knowledge_service.reset_collection()
    documents = load_from_directory()
    count = knowledge_service.ingest_documents(documents)
    return {
        "status": "reloaded",
        "documents_ingested": count,
    }
