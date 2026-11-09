#!/usr/bin/env bash
# Installs this fork into Home Assistant OS via SSH and restarts HA Core.
# The previously installed integration is kept as /config/easee_backups/<timestamp>.
# Usage: scripts/deploy-ha.sh [--no-restart]
set -euo pipefail
HA_SSH="${HA_SSH:-root@homeassistant.fritz.box}"
TARGET="/config/custom_components/easee"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAMP="$(date +%Y%m%d-%H%M%S)"

backup_installed_version() {
  ssh "$HA_SSH" "mkdir -p /config/easee_backups && if [ -d $TARGET ]; then cp -a $TARGET /config/easee_backups/$STAMP; fi"
}

copy_integration() {
  tar -C "$REPO_ROOT/custom_components" --exclude=__pycache__ -cf - easee \
    | ssh "$HA_SSH" "rm -rf $TARGET.new && mkdir -p $TARGET.new && tar --no-same-owner -xf - -C $TARGET.new --strip-components=1 && rm -rf $TARGET && mv $TARGET.new $TARGET"
}

restart_core() {
  ssh "$HA_SSH" "ha core check && ha core restart"
}

backup_installed_version
copy_integration
if [ "${1:-}" != "--no-restart" ]; then restart_core; fi
echo "Deployed $(git -C "$REPO_ROOT" rev-parse --short HEAD) (backup: /config/easee_backups/$STAMP)"
