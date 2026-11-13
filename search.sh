#!/usr/bin/env bash
# P2: Bash wrapper for the mini search engine.
#
# Usage:
#   ./search.sh -d <folder> "<query>"   search the .txt files in <folder>
#   ./search.sh -h                      show this help

set -euo pipefail

cd "$(dirname "$0")"           # run from the project folder

usage() {
    echo "Usage:"
    echo "  ./search.sh -d <folder> \"<query>\"   search the .txt files in <folder>"
    echo "  ./search.sh -h                      show this help"
}

DOCS_DIR=""

while getopts ":d:h" option; do
    case "$option" in
        d) DOCS_DIR="$OPTARG" ;;
        h) usage; exit 0 ;;
        :) echo "Error: -$OPTARG needs a folder name." >&2; usage; exit 1 ;;
        *) echo "Error: unknown option -$OPTARG" >&2; usage; exit 1 ;;
    esac
done
shift $((OPTIND - 1))          # what is left is the query

if [ -z "$DOCS_DIR" ]; then
    echo "Error: no folder given. Use -d <folder>." >&2
    usage
    exit 1
fi

if [ $# -eq 0 ]; then
    echo "Error: no search query given." >&2
    usage
    exit 1
fi

QUERY="$*"

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
