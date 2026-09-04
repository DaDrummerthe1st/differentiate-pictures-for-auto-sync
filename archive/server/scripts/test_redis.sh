#!/usr/bin/env bash
# Disposable Redis container for running the test suite locally.
#
# Same reasoning as test_db.sh: docker-compose.yml's redis service never
# publishes its port to the host, so it's unreachable from a plain
# `uv run pytest` on the dev machine. This container is throwaway test
# infrastructure, not part of the deployed stack.
#
# Usage:
#   scripts/test_redis.sh up      # start, wait until ready
#   scripts/test_redis.sh down    # stop and remove
set -euo pipefail

NAME=photo_server_test_redis
IMAGE=redis:8.8-alpine
PORT=${TEST_REDIS_PORT:-6380}
PASSWORD=${TEST_REDIS_PASSWORD:-test}

case "${1:-}" in
  up)
    docker run -d --rm \
      --name "$NAME" \
      -p "127.0.0.1:${PORT}:6379" \
      "$IMAGE" redis-server --requirepass "$PASSWORD" >/dev/null
    echo "waiting for $NAME to accept connections..."
    until docker exec "$NAME" redis-cli -a "$PASSWORD" --no-auth-warning ping >/dev/null 2>&1; do
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
