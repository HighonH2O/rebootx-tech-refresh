"""Quick check: query the knowledge base and print top matches.

Usage:
    python scripts/test_retrieval.py "python" "numpy pandas upgrade"
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.knowledge_service import KnowledgeService


def main() -> None:
    tech = sys.argv[1] if len(sys.argv) > 1 else "python"
    query = sys.argv[2] if len(sys.argv) > 2 else "numpy pandas dependency upgrade"

    ks = KnowledgeService()
    results = ks.retrieve(query=query, technology_type=tech, n_results=3)

    print(f"Query: '{query}'  (technology_type={tech})")
    print("=" * 60)
    if not results:
        print("No matches found.")
        return

    for i, doc in enumerate(results, start=1):
        meta = doc["metadata"]
        print(f"{i}. [score {doc['relevance_score']}] {meta.get('source')}")
        print(f"   topic={meta.get('topic')} | risk_hint={meta.get('risk_hint')} | checks={meta.get('validation_checks')}")
        print(f"   {doc['text'][:160]}...")
        print()


if __name__ == "__main__":
    main()
