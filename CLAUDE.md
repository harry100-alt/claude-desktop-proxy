# claude-desktop-proxy

A Go CLI that launches multiple Claude Desktop windows, each with an isolated
`--user-data-dir` profile. Single package, stdlib only, no dependencies.

Build and check with:

```
gofmt -l .        # must print nothing
go vet ./...
go build ./...
```

## Standing orchestration

**Every session in this repository follows `.claude/orchestration/protocol.md`
by default.** The `SessionStart` hook loads it automatically along with the open
threads in `state/orchestration.json`; this section is the fallback so the
protocol still applies if hooks are unavailable.

Read the protocol at the start of the session and follow it.

### Opting out

The protocol is the default, not a mandate. Stand down for a conversation when:

- The user says so in the conversation ("skip the protocol", "ignore
  orchestration", "one-off"). Acknowledge once, then work without it.
- `CDP_ORCHESTRATION=off` is set in the environment.
- `.claude/orchestration/DISABLED` exists.

Opting out is per-conversation and never edits the protocol. To change the
protocol itself, edit `.claude/orchestration/protocol.md` — every future session
picks the change up automatically.
