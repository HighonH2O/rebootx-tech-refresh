"""In-process API tests using FastAPI TestClient (no persistent server needed).

Exercises the live endpoints end-to-end, including the startup lifespan
(knowledge ingestion), the assessment engine, and the scan-and-assess bridge.
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.main import app

REPO = str(Path(__file__).resolve().parents[1] / "repository_scanner" / "tests" / "fixtures" / "sample_repo")

passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name} {detail}")


with TestClient(app) as client:
    print("\n== GET /health ==")
    r = client.get("/health")
    check("status 200", r.status_code == 200, str(r.status_code))
    body = r.json()
    check("status ok", body.get("status") == "ok")
    check("knowledge documents loaded", body.get("knowledge_documents", 0) > 0, str(body.get("knowledge_documents")))
    print(f"  ollama_available={body.get('ollama_available')}  knowledge_documents={body.get('knowledge_documents')}")

    print("\n== GET /api/v1/knowledge/stats ==")
    r = client.get("/api/v1/knowledge/stats")
    check("status 200", r.status_code == 200, str(r.status_code))
    stats = r.json()
    check("chroma documents > 0", stats.get("chroma_documents", 0) > 0, str(stats.get("chroma_documents")))
    print(f"  total={stats.get('total_documents')}  chroma={stats.get('chroma_documents')}  by_type={stats.get('by_technology_type')}")

    print("\n== POST /api/v1/assess-upgrade (multi-language integration_details) ==")
    payload = {
        "technology_type": "database",
        "current_version": "PostgreSQL 13",
        "target_version": "PostgreSQL 15",
        "dependencies": ["sqlalchemy==1.4"],
        "environment": "production",
        "integration_details": [
            {"name": "Claims service", "consumer_technology": "java", "protocol": "JDBC", "owner_team": "Claims"},
            {"name": "Analytics ETL", "consumer_technology": "python", "protocol": "psycopg2", "owner_team": "Data"},
            {"name": "Reporting", "consumer_technology": "dotnet", "protocol": "ODBC", "owner_team": "BI"},
        ],
    }
    r = client.post("/api/v1/assess-upgrade", json=payload)
    check("status 200", r.status_code == 200, str(r.status_code))
    a = r.json()
    titles = [risk["title"] for risk in a.get("risks", [])]
    check("overall risk High/Critical", a.get("overall_risk") in {"High", "Critical"}, str(a.get("overall_risk")))
    check("heterogeneous risk present", any("Heterogeneous multi-language" in t for t in titles))
    check("cross-team risk present", any("Cross-team coordination" in t for t in titles))
    check("java driver risk present", any("Java (JDBC)" in t for t in titles))
    print(f"  overall={a.get('overall_risk')}  mode={a.get('analysis_mode')}  risks={len(titles)}")

    print("\n== POST /api/v1/scan-and-assess (scan sample repo) ==")
    r = client.post("/api/v1/scan-and-assess", json={"repo_path": REPO, "target_version": "PostgreSQL 16"})
    check("status 200", r.status_code == 200, str(r.status_code))
    combined = r.json()
    scan = combined.get("scan_result", {})
    assess = combined.get("assessment", {})
    check("scanner detected PostgreSQL", scan.get("database") == "PostgreSQL", str(scan.get("database")))
    check("dependency graph built", len(scan.get("dependency_graph", {}).get("nodes", [])) > 0)
    check("risk flags present", len(scan.get("risk_flags", [])) > 0)
    check("assessment produced risks", len(assess.get("risks", [])) > 0)
    print(f"  db={scan.get('database')}  deps={len(scan.get('dependencies', []))}  "
          f"graph_nodes={len(scan.get('dependency_graph', {}).get('nodes', []))}  "
          f"assessment_risks={len(assess.get('risks', []))}")

    print("\n== POST /api/v1/scan-and-assess (bad path -> 400) ==")
    r = client.post("/api/v1/scan-and-assess", json={"repo_path": "C:/does/not/exist", "target_version": "X"})
    check("status 400", r.status_code == 400, str(r.status_code))

print(f"\n================ RESULT: {passed} passed, {failed} failed ================")
sys.exit(1 if failed else 0)
