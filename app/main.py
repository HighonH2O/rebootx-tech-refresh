"""RebootX FastAPI application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.data.knowledge_loader import get_knowledge_stats, load_from_directory
from app.models.schemas import (
    CapturedInput,
    CaptureRequest,
    HealthResponse,
    KnowledgeDocumentInput,
    KnowledgeStatsResponse,
    UpgradeAssessment,
    UpgradeRequest,
)
from app.services.assessment_service import AssessmentService
from app.services.capture_service import CaptureError, CaptureService
from app.services.knowledge_service import KnowledgeService
from app.services.ollama_service import OllamaService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

knowledge_service = KnowledgeService()
ollama_service = OllamaService()
assessment_service = AssessmentService(knowledge_service, ollama_service)
capture_service = CaptureService()


@asynccontextmanager
async def lifespan(_: FastAPI):
    documents = load_from_directory()
    if documents:
        count = knowledge_service.ingest_documents(documents)
        logger.info("Synced %s knowledge documents into ChromaDB", count)
    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "RebootX – AI Driven Tech Refresh Engine. "
        "Automated compatibility validation and integration risk assessment for enterprise upgrades."
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


@app.get("/", tags=["General"])
async def root() -> dict:
    return {
        "message": "RebootX API is running",
        "docs": "/docs",
        "health": "/health",
        "assess": "POST /api/v1/assess-upgrade",
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
        ollama_available=await ollama_service.is_available(),
        knowledge_documents=knowledge_service.document_count,
    )


@app.post(
    "/api/v1/assess-upgrade",
    response_model=UpgradeAssessment,
    tags=["Assessment"],
    summary="Assess compatibility and integration risk for a proposed upgrade",
)
async def assess_upgrade(request: UpgradeRequest) -> UpgradeAssessment:
    try:
        return await assessment_service.assess(request)
    except Exception as exc:
        logger.exception("Assessment failed")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {exc}") from exc


@app.post(
    "/api/v1/capture-upgrade",
    response_model=CapturedInput,
    tags=["Capture"],
    summary="Auto-capture upgrade input from a local project or GitHub repo",
)
async def capture_upgrade(request: CaptureRequest) -> CapturedInput:
    try:
        return capture_service.capture(request)
    except CaptureError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Capture failed")
        raise HTTPException(status_code=500, detail=f"Capture failed: {exc}") from exc


@app.post(
    "/api/v1/capture-and-assess",
    response_model=UpgradeAssessment,
    tags=["Capture"],
    summary="Capture input from a source and immediately assess the upgrade",
)
async def capture_and_assess(request: CaptureRequest) -> UpgradeAssessment:
    try:
        captured = capture_service.capture(request)
    except CaptureError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Capture failed")
        raise HTTPException(status_code=500, detail=f"Capture failed: {exc}") from exc

    upgrade = UpgradeRequest(
        technology_type=captured.technology_type,
        current_version=captured.current_version,
        target_version=captured.target_version,
        dependencies=captured.dependencies,
        integrations=captured.integrations,
        environment=captured.environment,
        notes=f"Auto-captured from {captured.source_type.value}: {captured.location}. "
        f"Detected from: {', '.join(captured.detected_from)}.",
    )
    try:
        return await assessment_service.assess(upgrade)
    except Exception as exc:
        logger.exception("Assessment failed")
        raise HTTPException(status_code=500, detail=f"Assessment failed: {exc}") from exc


@app.post("/api/v1/reload-knowledge", tags=["Knowledge"])
async def reload_knowledge() -> dict:
    documents = load_from_directory()
    count = knowledge_service.ingest_documents(documents)
    stats = get_knowledge_stats()
    return {"status": "ok", "documents_loaded": count, "stats": stats}


@app.get("/api/v1/knowledge/stats", response_model=KnowledgeStatsResponse, tags=["Knowledge"])
async def knowledge_stats() -> KnowledgeStatsResponse:
    stats = get_knowledge_stats()
    return KnowledgeStatsResponse(
        total_documents=stats["total_documents"],
        chroma_documents=knowledge_service.document_count,
        source_files=stats["source_files"],
        by_technology_type=stats["by_technology_type"],
        by_topic=stats["by_topic"],
        knowledge_dir=stats["knowledge_dir"],
    )


@app.post("/api/v1/knowledge/documents", tags=["Knowledge"])
async def add_knowledge_document(doc: KnowledgeDocumentInput) -> dict:
    metadata = {
        "technology_type": doc.technology_type.value,
        "source": doc.source,
        "topic": doc.topic,
    }
    if doc.version_from:
        metadata["version_from"] = doc.version_from
    if doc.version_to:
        metadata["version_to"] = doc.version_to
    if doc.risk_hint:
        metadata["risk_hint"] = doc.risk_hint

    document = {"id": doc.id, "text": doc.text, "metadata": metadata}
    count = knowledge_service.ingest_documents([document])
    return {"status": "ok", "documents_loaded": count, "id": doc.id}
