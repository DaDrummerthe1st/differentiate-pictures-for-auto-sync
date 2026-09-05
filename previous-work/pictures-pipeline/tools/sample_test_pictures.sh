#!/usr/bin/env bash
# WIP - not yet following tools/<name>/ + README + tests convention the rest
# of tools/ uses. Randomly samples pictures from a source folder into
# resources/test_pictures/ (already gitignored - see .gitignore), for
# exercising modules/test_main.py against a real, repeatable-ish photo set.
#
# Copies only, never moves - your library is never modified. Each copy is
# renamed with a numeric prefix to avoid collisions (different source folders
# can share a filename), and manifest.csv in the destination records every
# copy's exact original path, so nothing here loses track of where a picture
# came from.
#
# Usage:
#   tools/sample_test_pictures.sh <source-folder> [count]
#
# count defaults to 100.
set -euo pipefail

SOURCE_DIR="${1:-}"
COUNT="${2:-100}"

if [ -z "$SOURCE_DIR" ]; then
  echo "Usage: $0 <source-folder> [count=100]" >&2
  exit 1
fi
if [ ! -d "$SOURCE_DIR" ]; then
  echo "Not a folder: $SOURCE_DIR" >&2
  exit 1
fi

REPO_ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
DEST_DIR="$REPO_ROOT/resources/test_pictures"
MANIFEST="$DEST_DIR/manifest.csv"

mkdir -p "$DEST_DIR"

# Recursive, same extensions modules/test_main.py filters on.
mapfile -d '' -t all_images < <(find "$SOURCE_DIR" -type f \( \
    -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.bmp' -o -iname '*.webp' \
  \) -print0)

if [ "${#all_images[@]}" -eq 0 ]; then
  echo "No image files found under $SOURCE_DIR" >&2
  exit 1
fi

echo "Found ${#all_images[@]} image(s) under $SOURCE_DIR"

# Random sample of up to $COUNT, no duplicates.
mapfile -d '' -t sampled < <(printf '%s\0' "${all_images[@]}" | shuf -z -n "$COUNT")

echo "copied_filename,original_path" > "$MANIFEST"

i=0
for src in "${sampled[@]}"; do
  i=$((i + 1))
  index=$(printf '%04d' "$i")
  base=$(basename "$src")
  dest_name="${index}_${base}"
  cp "$src" "$DEST_DIR/$dest_name"
  escaped_src=${src//\"/\"\"}
  echo "${dest_name},\"${escaped_src}\"" >> "$MANIFEST"
done

echo "Copied ${#sampled[@]} picture(s) into $DEST_DIR"
echo "Manifest: $MANIFEST"
