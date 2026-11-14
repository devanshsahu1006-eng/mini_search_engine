#!/usr/bin/env bash
# P2: Bash wrapper for the mini search engine.
#
# Usage:
#   ./search.sh "<query>"               search every folder in the current directory
#   ./search.sh -d <folder> "<query>"   search only <folder>
#   ./search.sh -h                      show this help

set -euo pipefail

SCRIPT_DIR="$(dirname "$0")"   # where main.py lives

usage() {
    echo "Usage:"
    echo "  ./search.sh \"<query>\"               search every folder in the current directory"
    echo "  ./search.sh -d <folder> \"<query>\"   search only <folder>"
    echo "  ./search.sh -h                      show this help"
}

DOCS_DIR="."                   # default: the current directory

while getopts ":d:h" option; do
    case "$option" in
        d) DOCS_DIR="$OPTARG" ;;
        h) usage; exit 0 ;;
        :) echo "Error: -$OPTARG needs a folder name." >&2; usage; exit 1 ;;
        *) echo "Error: unknown option -$OPTARG" >&2; usage; exit 1 ;;
    esac
done
shift $((OPTIND - 1))          # what is left is the query

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

if [ ! -f "$SCRIPT_DIR/main.py" ]; then
    echo "Error: main.py not found." >&2
    exit 1
fi

echo "Searching '$DOCS_DIR' for: $QUERY"
python "$SCRIPT_DIR/main.py" "$DOCS_DIR" "$QUERY"
