#!/usr/bin/env bash
# Disposable Selenium (Chrome) container for browser-level GUI tests.
#
# Same reasoning as server/scripts/test_db.sh / test_redis.sh: throwaway
# test infrastructure, not part of the deployed stack. Runs with
# --network host so the browser inside the container can reach the app
# under test at http://localhost:<port> on this machine (the app itself
# is started directly via .venv-test's uvicorn by the pytest fixture,
# not containerized, for this first minimal setup - see
# app/tests_selenium/conftest.py).
#
# Usage:
#   scripts/test_selenium.sh up      # start, wait until ready
#   scripts/test_selenium.sh down    # stop and remove
set -euo pipefail

NAME=mpv_test_selenium
IMAGE=selenium/standalone-chrome:latest
STATUS_URL=http://127.0.0.1:4444/status

case "${1:-}" in
  up)
    docker run -d --rm \
      --name "$NAME" \
      --network host \
      --shm-size=2g \
      "$IMAGE" >/dev/null
    echo "waiting for $NAME to accept connections..."
    until curl -fsS "$STATUS_URL" >/dev/null 2>&1; do
      sleep 0.5
    done
    echo "$NAME ready on 127.0.0.1:4444 (network host)"
    ;;
  down)
    docker stop "$NAME" >/dev/null
    ;;
  *)
    echo "usage: $0 {up|down}" >&2
    exit 1
    ;;
esac
