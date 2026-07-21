"""Repository Scanner V1 — CLI Entry Point.

Usage:
    python -m repository_scanner.main <repo_path>
    python -m repository_scanner.main                  # scans current directory

Output:
    Prints the scan result as formatted JSON to stdout.
"""

import json
import sys

from repository_scanner.services.scan_service import scan


def main():
    # Get repo path from command line, default to current directory
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."

    print(f"Scanning repository: {repo_path}")
    print("-" * 50)

    # Run the scan
    result = scan(repo_path)

    # Print formatted JSON output
    output = json.dumps(result.to_dict(), indent=2)
    print(output)

    # Print summary
    print("-" * 50)
    print(f"Files by language:   {result.languages}")
    print(f"Dependencies found:  {len(result.dependencies)}")
    print(f"Database detected:   {result.database or 'None'}")
    print(f"Risk flags:          {len(result.risk_flags)}")
    print(f"Graph nodes:         {len(result.graph_nodes)}")
    print(f"Graph edges:         {len(result.graph_edges)}")


if __name__ == "__main__":
    main()
