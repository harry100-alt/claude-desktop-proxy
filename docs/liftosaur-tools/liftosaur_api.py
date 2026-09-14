#!/usr/bin/env python3
"""Small Liftosaur REST API client (Premium feature).

Reads the key from the LIFTOSAUR_API_KEY environment variable. Never pass the key on the command line.

Usage:
  python3 liftosaur_api.py programs                 # list programs
  python3 liftosaur_api.py program [id] [out.txt]   # fetch a program's Liftoscript (default: current)
  python3 liftosaur_api.py push <file> [id]         # replace a program's text (default: current); keeps its name
  python3 liftosaur_api.py history [days] [out.json]# pull workout history (default 60 days) and print a review
  python3 liftosaur_api.py stats <file>             # program stats: weekly volume per muscle, duration estimate
"""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

BASE = "https://www.liftosaur.com/api/v1"


def key() -> str:
    k = os.environ.get("LIFTOSAUR_API_KEY", "").strip()
    if not k.startswith("lftsk_"):
        sys.exit("LIFTOSAUR_API_KEY is not set (expected a key starting with lftsk_).")
    return k


def call(method: str, path: str, body=None, params=None):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {key()}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} on {method} {path}: {e.read().decode()[:500]}")


# ---------- Liftoscript Workouts parsing ----------

SET_RE = re.compile(r"(\d+)x(\d+)(?:\s+([\d.]+)(kg|lb))?")


def parse_sets(section: str):
    """'1x8 20kg, 2x7 20kg' -> [(8, 20.0), (7, 20.0), (7, 20.0)]"""
    out = []
    for m in SET_RE.finditer(section):
        n, reps, w = int(m.group(1)), int(m.group(2)), float(m.group(3)) if m.group(3) else None
        out.extend([(reps, w)] * n)
    return out


def parse_record(text: str):
    """Parse one history record's Liftoscript Workouts text into a dict."""
    head, _, body = text.partition("exercises: {")
    meta = {}
    m = re.match(r"\s*(\S+)", head)
    meta["date"] = m.group(1) if m else ""
    for k in ("program", "dayName"):
        mm = re.search(k + r':\s*"([^"]*)"', head)
        meta[k] = mm.group(1) if mm else ""
    mm = re.search(r"duration:\s*(\d+)s", head)
    meta["duration_min"] = round(int(mm.group(1)) / 60) if mm else None
    exercises = []
    for line in body.strip().rstrip("}").strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(" / ")]
        name = parts[0]
        done = target = None
        for p in parts[1:]:
            if p.startswith("target:"):
                target = parse_sets(p)
            elif p.startswith("warmup:"):
                pass
            elif done is None and SET_RE.search(p):
                done = parse_sets(p)
        exercises.append({"name": name, "done": done or [], "target": target or []})
    return {**meta, "exercises": exercises}


def fetch_history(days: int):
    start = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    records, cursor = [], None
    while True:
        res = call("GET", "/history", params={"limit": 200, "startDate": start, "cursor": cursor})
        data = res.get("data", res)
        records.extend(data.get("records", []))
        if not data.get("hasMore"):
            break
        cursor = data.get("nextCursor")
    return records


def review(records):
    parsed = [parse_record(r["text"]) for r in records if r.get("text")]
    parsed.sort(key=lambda r: r["date"])
    print(f"{len(parsed)} workouts\n")
    per_ex = {}
    for w in parsed:
        print(f"== {w['date'][:10]}  {w['dayName'] or '?'}  {w['duration_min'] or '?'} min")
        for ex in w["exercises"]:
            done = ex["done"]
            tgt = ex["target"]
            d = ", ".join(f"{r}" + (f"@{w_:g}" if w_ is not None else "") for r, w_ in done) or "-"
            t = ""
            if tgt:
                t = f"   target {tgt[0][0]}x{len(tgt)}" + (f" @{tgt[0][1]:g}" if tgt[0][1] is not None else "")
            hit = "" if not tgt or not done else ("  OK" if all(r >= tr for (r, _), (tr, _) in zip(done, tgt)) and len(done) >= len(tgt) else "  MISSED")
            print(f"   {ex['name'][:44]:44} {d}{t}{hit}")
            per_ex.setdefault(ex["name"], []).append((w["date"][:10], done))
        print()
    print("== Per-exercise trend (date: reps@weight)")
    for name, sessions in per_ex.items():
        line = " | ".join(f"{d}: " + ",".join(f"{r}" + (f"@{w_:g}" if w_ is not None else "") for r, w_ in done) for d, done in sessions)
        print(f"  {name[:40]:40} {line}")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "programs":
        print(json.dumps(call("GET", "/programs"), indent=2))
    elif cmd == "program":
        pid = sys.argv[2] if len(sys.argv) > 2 else "current"
        res = call("GET", f"/programs/{pid}")
        data = res.get("data", res)
        text = data.get("text") or json.dumps(res, indent=2)
        if len(sys.argv) > 3:
            open(sys.argv[3], "w").write(text)
            print(f"wrote {sys.argv[3]} ({len(text)} chars)")
        else:
            print(text)
    elif cmd == "push":
        path = sys.argv[2]
        pid = sys.argv[3] if len(sys.argv) > 3 else "current"
        text = open(path).read()
        res = call("PUT", f"/programs/{pid}", body={"text": text})
        print("updated:", json.dumps(res)[:300])
    elif cmd == "history":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        recs = fetch_history(days)
        if len(sys.argv) > 3:
            json.dump(recs, open(sys.argv[3], "w"), indent=2)
            print(f"wrote {sys.argv[3]}")
        review(recs)
    elif cmd == "stats":
        text = open(sys.argv[2]).read()
        print(json.dumps(call("POST", "/program-stats", body={"programText": text}), indent=2))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
