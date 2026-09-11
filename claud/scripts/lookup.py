#!/usr/bin/env python3
"""
Search the generated ID tables by name, RuneLite constant, config name, or numeric id.

Examples:
  python3 lookup.py shark                 # any table, name contains "shark"
  python3 lookup.py -t items 385          # items table, exact id 385
  python3 lookup.py -t npcs "bank"        # npcs whose name/const contains "bank"
  python3 lookup.py -t objects "bank booth"
  python3 lookup.py -t varbits SPELLBOOK
  python3 lookup.py -t interfaces bankmain   # interface groups + children
  python3 lookup.py -t items --op Eat      # items that have an inventory op "Eat"
  python3 lookup.py -t items --exact "Rune scimitar"

Tables: items npcs objects animations varbits varps inventories spotanims sprites
        varclient dbtables interfaces ge
"""
import argparse
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")

TABLES = {
    "items": "items.csv", "npcs": "npcs.csv", "objects": "objects.csv",
    "animations": "animations.csv", "varbits": "varbits.csv", "varps": "varps.csv",
    "inventories": "inventories.csv", "spotanims": "spotanims.csv", "sprites": "sprites.csv",
    "varclient": "varclient.csv", "dbtables": "dbtables.csv", "ge": "ge_items.csv",
    "interfaces": ["interface_groups.csv", "interface_children.csv"],
}
DEFAULT_TABLES = ["items", "npcs", "objects", "animations", "varbits", "varps", "inventories", "interfaces"]
SEARCH_COLS = ("name", "runelite_const", "config_name", "comment", "child_const", "group_class")
ID_COLS = ("id", "group_id", "packed_id", "child_id")


def rows_of(fname):
    with open(os.path.join(DATA, fname), newline="", encoding="utf-8") as f:
        yield from csv.DictReader(f)


def matches(row, q, exact, op):
    if op:
        ops = (row.get("inventory_ops", "") + "|" + row.get("ground_ops", "") + "|" + row.get("ops", "")).lower()
        if op.lower() not in ops.split("|"):
            return False
        if not q:
            return True
    if q.isdigit():
        return any(row.get(c) == q for c in ID_COLS)
    ql = q.lower()
    for c in SEARCH_COLS:
        v = row.get(c)
        if not v:
            continue
        if exact and v.lower() == ql:
            return True
        if not exact and ql in v.lower():
            return True
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", nargs="?", default="")
    ap.add_argument("-t", "--table", action="append", help="table(s) to search; default: common ones")
    ap.add_argument("--exact", action="store_true", help="exact (case-insensitive) name match")
    ap.add_argument("--op", help="filter by right-click option, e.g. Eat, Bank, Chop down")
    ap.add_argument("-n", "--limit", type=int, default=60)
    ap.add_argument("--all-cols", action="store_true", help="print every column, not the short view")
    a = ap.parse_args()
    if not a.query and not a.op:
        ap.error("give a query and/or --op")

    tables = a.table or DEFAULT_TABLES
    shown = 0
    for t in tables:
        files = TABLES.get(t)
        if files is None:
            print(f"unknown table {t}; choose from {', '.join(TABLES)}", file=sys.stderr)
            return 2
        for fname in ([files] if isinstance(files, str) else files):
            hits = [r for r in rows_of(fname) if matches(r, a.query, a.exact, a.op)]
            if not hits:
                continue
            print(f"== {fname} ({len(hits)} hits)")
            for r in hits[: max(0, a.limit - shown)]:
                if a.all_cols:
                    print("  " + " | ".join(f"{k}={v}" for k, v in r.items() if v != ""))
                else:
                    short = [r.get("id") or r.get("packed_id") or r.get("group_id"),
                             r.get("name") or r.get("child_const") or r.get("runelite_const"),
                             r.get("runelite_const") if r.get("name") else r.get("group_class"),
                             r.get("inventory_ops") or r.get("ops") or r.get("comment") or ""]
                    print("  " + " | ".join(str(x) for x in short if x))
                shown += 1
            if shown >= a.limit:
                print(f"... limit {a.limit} reached, use -n to raise")
                return 0
    if shown == 0:
        print("no matches")
    return 0


if __name__ == "__main__":
    sys.exit(main())
