"""CLI script to ingest knowledge files into ChromaDB."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.data.knowledge_loader import get_knowledge_stats, load_from_directory
from app.services.knowledge_service import KnowledgeService


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest RebootX knowledge files into ChromaDB")
    parser.add_argument("--stats", action="store_true", help="Show knowledge base stats without ingesting")
    parser.add_argument("--reset", action="store_true", help="Clear ChromaDB before ingesting (removes stale docs)")
    parser.add_argument("--dir", type=str, default=None, help="Override knowledge directory path")
    args = parser.parse_args()

    directory = Path(args.dir) if args.dir else None
    stats = get_knowledge_stats(directory)

    print("=" * 60)
    print("RebootX Knowledge Base Report")
    print("=" * 60)
    print(f"Knowledge directory:  {stats['knowledge_dir']}")
    print(f"Source files:         {stats['source_files']}")
    print(f"Total documents:      {stats['total_documents']}")
    print(f"By technology:        {stats['by_technology_type']}")
    print(f"By topic:             {stats['by_topic']}")
    print(f"By domain:            {stats['by_domain']}")
    print(f"By validation check:  {stats['by_validation_check']}")

    missing = stats["docs_missing_validation_checks"]
    if missing:
        print(f"\n[WARN] {len(missing)} document(s) have no validation_checks tagged:")
        for doc_id in missing:
            print(f"        - {doc_id}")
        print("       Add a validation_checks list so the readiness report can")
        print("       recommend focused checks (regression/build/integration/data/performance/rollback).")
    else:
        print("\n[OK] All documents have validation_checks tagged.")

    if args.stats:
        return

    documents = load_from_directory(directory)
    if not documents:
        print("\nNo documents found. Add JSON files to the knowledge/ directory.")
        sys.exit(1)

    service = KnowledgeService()
    if args.reset:
        service.reset_collection()
        print("\nCleared existing ChromaDB collection (--reset).")
    count = service.ingest_documents(documents)
    print(f"\nIngested {count} documents into ChromaDB.")
    print(f"ChromaDB total:      {service.document_count}")


if __name__ == "__main__":
    main()
