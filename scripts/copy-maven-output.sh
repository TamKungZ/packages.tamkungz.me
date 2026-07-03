#!/usr/bin/env bash
set -euo pipefail

SOURCE="${1:-build/maven-repo}"

if [ ! -d "$SOURCE" ]; then
  echo "Source folder not found: $SOURCE"
  echo "Usage: ./scripts/copy-maven-output.sh /path/to/build/maven-repo"
  exit 1
fi

cp -a "$SOURCE"/. .
echo "Copied Maven output from: $SOURCE"
echo "Now run:"
echo "  git add ."
echo "  git commit -m 'Publish Maven artifacts'"
echo "  git push"
