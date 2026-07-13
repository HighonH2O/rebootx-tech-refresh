"""CLI to test automatic upgrade-input capture.

Usage:
    python scripts/capture.py local "C:/Coding Practice/rebootx"
    python scripts/capture.py github "https://github.com/tiangolo/fastapi" --target "0.115"
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models.schemas import CaptureRequest, SourceType
from app.services.capture_service import CaptureError, CaptureService


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture upgrade input from a project source")
    parser.add_argument("source_type", choices=["local", "github"], help="Where to capture from")
    parser.add_argument("location", help="Local folder path or GitHub repo URL")
    parser.add_argument("--target", default=None, help="Target version (optional)")
    parser.add_argument("--tech", default=None, help="Override technology type (optional)")
    parser.add_argument("--env", default="production", help="Environment (default: production)")
    args = parser.parse_args()

    request = CaptureRequest(
        source_type=SourceType(args.source_type),
        location=args.location,
        target_version=args.target,
        technology_type=args.tech,
        environment=args.env,
    )

    try:
        result = CaptureService().capture(request)
    except CaptureError as exc:
        print(f"[ERROR] {exc}")
        sys.exit(1)

    print(json.dumps(result.model_dump(), indent=2, default=str))


if __name__ == "__main__":
    main()
