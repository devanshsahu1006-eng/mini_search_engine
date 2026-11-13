#!/usr/bin/env bash
# P2: Bash wrapper for the mini search engine.
# Usage: ./search.sh <folder> "<query>"

set -euo pipefail

cd "$(dirname "$0")"           # run from the project folder

if [ $# -lt 2 ]; then
    echo "Error: missing folder or query." >&2
    echo "Usage: ./search.sh <folder> \"<query>\"" >&2
    exit 1
fi

DOCS_DIR="$1"
shift
QUERY="$*"                     # everything after the folder is the query

if [ ! -d "$DOCS_DIR" ]; then
    echo "Error: folder '$DOCS_DIR' does not exist." >&2
    exit 1
fi

if [ ! -f main.py ]; then
    echo "Error: main.py not found." >&2
    exit 1
fi

echo "Searching '$DOCS_DIR' for: $QUERY"
python main.py "$DOCS_DIR" "$QUERY"
