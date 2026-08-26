#!/bin/bash
# SessionStart hook: injects the orchestration protocol into every session.
# Opt out with CDP_ORCHESTRATION=off, or by creating .claude/orchestration/DISABLED.
set -uo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
PROTOCOL="${CDP_PROTOCOL_PATH:-$ROOT/.claude/orchestration/protocol.md}"
LEDGER="$ROOT/state/orchestration.json"
DISABLED="${CDP_DISABLED_PATH:-$ROOT/.claude/orchestration/DISABLED}"

if [ "${CDP_ORCHESTRATION:-on}" = "off" ] || [ -f "$DISABLED" ]; then
  echo "ORCHESTRATION: disabled for this session (opt-out flag set)."
  echo "Proceed without the standing protocol unless the user asks for it."
  exit 0
fi

echo "=== STANDING ORCHESTRATION PROTOCOL (auto-loaded) ==="
echo
echo "This applies to every session in this repository by default."
echo "If the user explicitly says to skip, ignore, or override it, stand down"
echo "for that conversation and say so once. Otherwise follow it."
echo

if [ -r "$PROTOCOL" ]; then
  cat "$PROTOCOL"
else
  echo "WARNING: protocol file missing at $PROTOCOL"
fi

echo
echo "=== OPEN THREADS (state/orchestration.json) ==="
if [ -r "$LEDGER" ] && jq empty "$LEDGER" 2>/dev/null; then
  count=$(jq '[.threads[] | select(.status=="open" or .status=="blocked")] | length' "$LEDGER")
  if [ "$count" -eq 0 ]; then
    echo "None. Ledger last updated: $(jq -r '.updated' "$LEDGER")"
  else
    jq -r '.threads[] | select(.status=="open" or .status=="blocked")
           | "- [\(.status)] \(.id): \(.title)\n  branch: \(.branch // "n/a")\n  notes: \(.notes // "")"' "$LEDGER"
  fi
elif [ -e "$LEDGER" ]; then
  echo "WARNING: $LEDGER exists but is not valid JSON. Report this and do not overwrite it blindly."
else
  echo "No ledger yet. Create $LEDGER when you first record a thread."
fi

echo
echo "Opt-out: set CDP_ORCHESTRATION=off or create .claude/orchestration/DISABLED"
echo "=== END PROTOCOL ==="
exit 0
