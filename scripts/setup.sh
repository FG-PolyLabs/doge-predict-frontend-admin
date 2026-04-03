#!/usr/bin/env bash
# Clone or update all sibling repos for the doge-predict project.
set -euo pipefail

ORG="FG-PolyLabs"
REPOS=("doge-predict-backend" "doge-predict-frontend-public" "doge-predict-data")
PARENT="$(cd "$(dirname "$0")/../.." && pwd)"

for repo in "${REPOS[@]}"; do
  dir="$PARENT/$repo"
  if [ -d "$dir/.git" ]; then
    echo "  $repo: pulling latest..."
    git -C "$dir" pull --ff-only 2>/dev/null || echo "  $repo: pull skipped (not on tracking branch)"
  else
    echo "  $repo: cloning..."
    git clone "https://github.com/$ORG/$repo.git" "$dir"
  fi
done

echo ""
echo "All repos ready under $PARENT/"
