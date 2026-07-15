#!/usr/bin/env bash
# Disposable Postgres container for running the test suite locally.
#
# Separate from docker-compose.yml's postgres service on purpose: that
# service never publishes its port to the host (see TODO.md 0.2's
# security line), so it's unreachable from a plain `uv run pytest` on the
# dev machine. This container is throwaway test infrastructure, not part
# of the deployed stack, and is fine to expose on localhost only.
#
# Usage:
#   scripts/test_db.sh up      # start, wait until ready
#   scripts/test_db.sh down    # stop and remove
set -euo pipefail

NAME=photo_server_test_pg
IMAGE=postgres:18.4-bookworm
PORT=${TEST_POSTGRES_PORT:-5433}
DB=${TEST_POSTGRES_DB:-photo_server_test}
USER=${TEST_POSTGRES_USER:-photo_server}
PASSWORD=${TEST_POSTGRES_PASSWORD:-test}

case "${1:-}" in
  up)
    docker run -d --rm \
      --name "$NAME" \
      -p "127.0.0.1:${PORT}:5432" \
      -e POSTGRES_DB="$DB" \
      -e POSTGRES_USER="$USER" \
      -e POSTGRES_PASSWORD="$PASSWORD" \
      "$IMAGE" >/dev/null
    echo "waiting for $NAME to accept connections..."
    until docker exec "$NAME" pg_isready -U "$USER" -d "$DB" >/dev/null 2>&1; do
      sleep 0.5
    done
    echo "$NAME ready on 127.0.0.1:${PORT}"
    ;;
  down)
    docker stop "$NAME" >/dev/null
    ;;
  *)
    echo "usage: $0 {up|down}" >&2
    exit 1
    ;;
esac
