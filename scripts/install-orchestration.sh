#!/bin/bash
# Install the orchestration protocol at USER level, so it applies to every
# conversation in every project on this machine — not just this repository.
#
#   ./scripts/install-orchestration.sh          install / update
#   ./scripts/install-orchestration.sh --remove uninstall
#
# Idempotent. Existing ~/.claude/settings.json hooks are preserved.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLAUDE_HOME="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
DEST_DIR="$CLAUDE_HOME/orchestration"
DEST_HOOK="$CLAUDE_HOME/hooks/orchestration-session-start.sh"
SETTINGS="$CLAUDE_HOME/settings.json"
HOOK_CMD='CDP_PROTOCOL_PATH="$HOME/.claude/orchestration/protocol.md" CDP_DISABLED_PATH="$HOME/.claude/orchestration/DISABLED" "$HOME/.claude/hooks/orchestration-session-start.sh"'

command -v jq >/dev/null || { echo "error: jq is required" >&2; exit 1; }

if [ "${1:-}" = "--remove" ]; then
  rm -f "$DEST_HOOK"
  if [ -f "$SETTINGS" ]; then
    tmp="$(mktemp)"
    jq --arg cmd "$HOOK_CMD" '
      if .hooks.SessionStart then
        .hooks.SessionStart |= (map(.hooks |= map(select(.command != $cmd)))
                                | map(select((.hooks | length) > 0)))
      else . end' "$SETTINGS" > "$tmp" && mv "$tmp" "$SETTINGS"
  fi
  echo "Removed global orchestration hook. $DEST_DIR left in place; delete it manually if unwanted."
  exit 0
fi

mkdir -p "$DEST_DIR" "$CLAUDE_HOME/hooks"
cp "$REPO/.claude/orchestration/protocol.md" "$DEST_DIR/protocol.md"
cp "$REPO/.claude/hooks/session-start.sh" "$DEST_HOOK"
chmod +x "$DEST_HOOK"

[ -f "$SETTINGS" ] || echo '{}' > "$SETTINGS"
jq empty "$SETTINGS" || { echo "error: $SETTINGS is not valid JSON; fix it first" >&2; exit 1; }

tmp="$(mktemp)"
jq --arg cmd "$HOOK_CMD" '
  .hooks //= {} |
  .hooks.SessionStart //= [] |
  if [.hooks.SessionStart[]?.hooks[]?.command] | index($cmd) then .
  else .hooks.SessionStart += [{"hooks": [{"type": "command", "command": $cmd}]}]
  end' "$SETTINGS" > "$tmp" && mv "$tmp" "$SETTINGS"

cat <<MSG
Installed global orchestration:
  protocol -> $DEST_DIR/protocol.md
  hook     -> $DEST_HOOK
  settings -> $SETTINGS (SessionStart entry added)

Every new conversation on this machine now loads the protocol.
Opt out per session with CDP_ORCHESTRATION=off, or permanently with:
  touch $DEST_DIR/DISABLED
Re-run this script after editing the protocol to push the update.
MSG
