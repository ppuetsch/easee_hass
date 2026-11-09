#!/usr/bin/env bash
# Runs the test suite in a Linux container on a Docker host (HA's test harness needs Linux).
# Usage: scripts/test-remote.sh [pytest args...]
set -euo pipefail
DOCKER_HOST_SSH="${DOCKER_HOST_SSH:-root@docker.fritz.box}"
IMAGE="easee-hass-test"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

ensure_image() {
  if ! ssh "$DOCKER_HOST_SSH" "docker image inspect $IMAGE >/dev/null 2>&1"; then
    ssh "$DOCKER_HOST_SSH" "docker build -t $IMAGE -" < "$REPO_ROOT/scripts/Dockerfile.test"
  fi
}

run_tests() {
  tar -C "$REPO_ROOT" --exclude=__pycache__ -cf - custom_components tests pyproject.toml \
    | ssh "$DOCKER_HOST_SSH" "docker run --rm -i -e PYTHONUNBUFFERED=1 $IMAGE sh -c 'tar --no-same-owner -xf - && timeout ${TEST_TIMEOUT_SECONDS:-300} python -m pytest tests -q -p no:cacheprovider $*'"
}

ensure_image
run_tests "$@"
