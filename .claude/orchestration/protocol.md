# Orchestration Protocol

Single source of truth for how every session in this repository operates.
Edit this file to change the protocol — everything else points here.

## 1. Boot

At session start, read `state/orchestration.json` and report open threads
(`status` of `open` or `blocked`) before doing anything else. That ledger is
the only memory shared between conversations; nothing else survives.

## 2. Branch discipline

- Work on `claude/<topic>-<suffix>` branches. Never commit to the default branch.
- Push with `git push -u origin <branch>`.
- Do not open a pull request unless explicitly asked.

## 3. Verify before commit

Run and pass, every time, before any commit:

```
gofmt -l .        # must print nothing
go vet ./...
go build ./...
```

If a test suite exists later, it joins this list.

## 4. Handoff

Before ending a session that changed anything, update `state/orchestration.json`:

- Set `updated` to the current UTC timestamp.
- Add or update the thread you worked on.
- Record what the next session needs to know in `notes` — assume it has zero context.

Commit the ledger together with the work. An unrecorded thread is a lost thread.

## 5. Scope

Deliver what was asked. If part of the request is blocked, finish everything
else and say plainly what was left out and why. Do not widen scope
unprompted; raise a proposal instead.

## 6. Escalation

Make routine judgment calls without asking. Ask only when two readings of the
request lead to materially different work, or when proceeding either way could
be unsafe or destructive.
