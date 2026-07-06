#!/usr/bin/env bash
set -euo pipefail

SOURCE="${1:-build/maven-repo}"
TARGET_DIR="${2:-maven}"

if [ ! -d "$SOURCE" ]; then
  echo "Source folder not found: $SOURCE"
  echo "Usage: ./scripts/copy-maven-output.sh /path/to/build/maven-repo [target-dir]"
  exit 1
fi

mkdir -p "$TARGET_DIR"
cp -a "$SOURCE"/. "$TARGET_DIR"/
echo "Copied Maven output from: $SOURCE"
echo "to: $TARGET_DIR"
echo "Now run:"
echo "  git add ."
echo "  git commit -m 'Publish Maven artifacts'"
echo "  git push"
