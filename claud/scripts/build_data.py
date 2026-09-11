#!/usr/bin/env python3
"""
Fetch the current OSRS game-data sources and flatten them into CSV files under ../data/.

Sources (all public, all current-revision):
  * RuneLite gameval constants  - generated straight from the live cache by the RuneLite project
                                   (ItemID, NpcID, ObjectID, AnimationID, VarbitID, VarPlayerID,
                                    InterfaceID, InventoryID, SpotanimID, SpriteID, VarClientID, DBTableID)
  * Chisel (OSRS Wiki team)     - full item / npc / object definitions dumped from the cache
  * prices.runescape.wiki       - GE mapping: tradeable items, buy limits, alch values

Usage:
  python3 build_data.py            # download anything missing into ../raw, then build ../data
  python3 build_data.py --refresh  # re-download everything first

Only the Python standard library is used.
"""
import csv
import json
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "raw")
DATA = os.path.join(ROOT, "data")
UA = "osrs-bot-guide-builder/1.0 (personal research; contact via github harry100-alt)"

RL_BASE = "https://raw.githubusercontent.com/runelite/runelite/master/runelite-api/src/main/java/net/runelite/api/gameval/"
RL_FILES = [
    "ItemID.java", "NpcID.java", "ObjectID.java", "ObjectID1.java", "AnimationID.java",
    "VarbitID.java", "VarPlayerID.java", "InterfaceID.java", "InventoryID.java",
    "SpotanimID.java", "SpriteID.java", "VarClientID.java", "DBTableID.java",
]
CHISEL_BASE = "https://chisel.weirdgloop.org/moid/data_files/"
CHISEL_FILES = ["items.json", "npcs.json", "objects.json"]
PRICES_MAPPING = "https://prices.runescape.wiki/api/v1/osrs/mapping"


def fetch(url, dest, refresh):
    if os.path.exists(dest) and not refresh:
        return
    print(f"  downloading {url}")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        f.write(r.read())
    time.sleep(0.5)


def download_all(refresh):
    os.makedirs(os.path.join(RAW, "gameval"), exist_ok=True)
    os.makedirs(os.path.join(RAW, "chisel"), exist_ok=True)
    for name in RL_FILES:
        fetch(RL_BASE + name, os.path.join(RAW, "gameval", name), refresh)
    for name in CHISEL_FILES:
        fetch(CHISEL_BASE + name, os.path.join(RAW, "chisel", name), refresh)
    fetch(PRICES_MAPPING, os.path.join(RAW, "prices_mapping.json"), refresh)


CONST_RE = re.compile(r"^\s*public static final int (\w+) = (0x[0-9a-fA-F_]+|-?\d+);")
DOC_RE = re.compile(r"^\s*\*\s*(.*)$")
CLASS_RE = re.compile(r"^\s*public static final class (\w+)")


def parse_constants(path):
    """Return list of (const_name, value, javadoc_text) for a gameval file.
    Constants inside a nested class are prefixed "Class.NAME" (e.g. ItemID has Cert.* for noted
    ids and Placeholder.* for bank placeholders; DBTableID nests one class per table)."""
    out = []
    doc = []
    in_doc = False
    cls = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            m = CLASS_RE.match(line)
            if m:
                cls = m.group(1)
                continue
            if s.startswith("/**"):
                in_doc, doc = True, []
                continue
            if in_doc:
                if s.startswith("*/"):
                    in_doc = False
                    continue
                m = DOC_RE.match(line)
                if m and m.group(1):
                    doc.append(m.group(1).strip())
                continue
            m = CONST_RE.match(line)
            if m:
                val = int(m.group(2).replace("_", ""), 0)
                name = m.group(1) if cls is None else f"{cls}.{m.group(1)}"
                out.append((name, val, " ".join(doc)))
                doc = []
    return out


def parse_interfaces(path):
    """InterfaceID.java has flat group constants, then one nested class per group whose
    constants are packed ids (group << 16 | child)."""
    groups = []
    children = []
    cur = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = CLASS_RE.match(line)
            if m:
                cur = m.group(1)
                continue
            m = CONST_RE.match(line)
            if not m:
                continue
            val = int(m.group(2).replace("_", ""), 0)
            if cur is None:
                groups.append((m.group(1), val))
            else:
                children.append((cur, m.group(1), val >> 16, val & 0xFFFF, val))
    return groups, children


def write_csv(name, header, rows):
    os.makedirs(DATA, exist_ok=True)
    p = os.path.join(DATA, name)
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    print(f"  wrote {name:22s} {len(rows):>7,} rows")
    return len(rows)


def j(v):
    """Compact list/dict for a CSV cell."""
    if v is None:
        return ""
    if isinstance(v, (list, dict)):
        return json.dumps(v, separators=(",", ":"))
    return v


def ops(v):
    """Pipe-joined, POSITION PRESERVED: slot 1..5 == menu option 1..5 (empty slot = no option)."""
    v = list(v or [])
    while v and not v[-1]:
        v.pop()
    return "|".join(o or "" for o in v)


def main():
    refresh = "--refresh" in sys.argv
    print("fetching raw sources ...")
    download_all(refresh)

    print("parsing RuneLite gameval constants ...")
    gv = {}
    for name in RL_FILES:
        key = name.replace(".java", "")
        gv[key] = parse_constants(os.path.join(RAW, "gameval", name))
    gv["ObjectID"] += gv.pop("ObjectID1")  # ObjectID is split across two classes (Java size limit)

    # name lookup: id -> RuneLite constant name
    def const_map(key):
        """id -> constant name; top-level names win over nested (Cert./Placeholder.) ones."""
        m = {}
        for cname, val, _ in sorted(gv[key], key=lambda t: "." in t[0]):
            m.setdefault(val, cname)
        return m

    item_const = const_map("ItemID")
    npc_const = const_map("NpcID")
    obj_const = const_map("ObjectID")

    print("loading chisel + GE mapping ...")
    items = json.load(open(os.path.join(RAW, "chisel", "items.json"), encoding="utf-8"))
    npcs = json.load(open(os.path.join(RAW, "chisel", "npcs.json"), encoding="utf-8"))
    objs = json.load(open(os.path.join(RAW, "chisel", "objects.json"), encoding="utf-8"))
    ge = {r["id"]: r for r in json.load(open(os.path.join(RAW, "prices_mapping.json"), encoding="utf-8"))}

    counts = {}
    print("writing CSVs ...")
    rows = []
    for it in items:
        g = ge.get(it["id"], {})
        rows.append([
            it["id"], it["name"], item_const.get(it["id"], ""), it.get("configName", ""),
            int(bool(it.get("members"))), int(bool(it.get("tradeable"))), int(bool(it.get("exchange"))),
            it.get("stackable", 0), it.get("notedId", ""), it.get("placeholderId", ""),
            it.get("value", 0), g.get("highalch", ""), g.get("lowalch", ""), g.get("limit", ""),
            it.get("weight", 0), ops(it.get("invOps")), ops(it.get("ops")), it.get("examine", ""),
            j(it.get("params")),
        ])
    counts["items"] = write_csv("items.csv", [
        "id", "name", "runelite_const", "config_name", "members", "tradeable", "ge_tradeable",
        "stackable", "noted_id", "placeholder_id", "value", "high_alch", "low_alch", "ge_buy_limit",
        "weight_g", "inventory_ops", "ground_ops", "examine", "params"], rows)

    rows = []
    for n in npcs:
        st = n.get("stats") or [None] * 6
        rows.append([
            n["id"], n["name"], npc_const.get(n["id"], ""), n.get("configName", ""),
            n.get("combat", 0), n.get("size", 1), int(bool(n.get("isMinimapVisible"))),
            int(bool(n.get("isFollower"))), ops(n.get("ops")),
            *st, n.get("varbId", ""), n.get("varpIndex", ""), j(n.get("multiChildren")),
            n.get("category", ""), j(n.get("params")),
        ])
    counts["npcs"] = write_csv("npcs.csv", [
        "id", "name", "runelite_const", "config_name", "combat_level", "size", "on_minimap",
        "is_follower", "ops", "stat_attack", "stat_defence", "stat_strength", "stat_hitpoints",
        "stat_ranged", "stat_magic", "varbit_id", "varp_id", "multi_children", "category", "params"], rows)

    rows = []
    for o in objs:
        rows.append([
            o["id"], o["name"], obj_const.get(o["id"], ""), o.get("configName", ""),
            o.get("sizeX", 1), o.get("sizeY", 1), ops(o.get("ops")),
            int(bool(o.get("blocksProjectile"))), int(bool(o.get("obstructsGround"))),
            o.get("wallOrDoor", ""), o.get("varbId", ""), o.get("varpId", ""),
            j(o.get("multiChildren")), o.get("category", ""), o.get("mapSceneId", ""),
        ])
    counts["objects"] = write_csv("objects.csv", [
        "id", "name", "runelite_const", "config_name", "size_x", "size_y", "ops",
        "blocks_projectile", "obstructs_ground", "wall_or_door", "varbit_id", "varp_id",
        "multi_children", "category", "map_scene_id"], rows)

    simple = {
        "AnimationID": "animations.csv", "VarbitID": "varbits.csv", "VarPlayerID": "varps.csv",
        "InventoryID": "inventories.csv", "SpotanimID": "spotanims.csv", "SpriteID": "sprites.csv",
        "VarClientID": "varclient.csv", "DBTableID": "dbtables.csv",
    }
    for key, fname in simple.items():
        rows = [[val, cname, doc] for cname, val, doc in gv[key]]
        rows.sort(key=lambda r: r[0])
        counts[fname[:-4]] = write_csv(fname, ["id", "runelite_const", "comment"], rows)

    groups, children = parse_interfaces(os.path.join(RAW, "gameval", "InterfaceID.java"))
    counts["interface_groups"] = write_csv("interface_groups.csv", ["group_id", "runelite_const"],
                                           sorted([[v, n] for n, v in groups]))
    counts["interface_children"] = write_csv(
        "interface_children.csv",
        ["group_class", "child_const", "group_id", "child_id", "packed_id", "packed_hex"],
        [[c, n, g, ch, p, f"0x{p:08x}"] for c, n, g, ch, p in children])

    # GE-only table (small, handy for money-making / alch scripts)
    rows = [[r["id"], r["name"], int(bool(r.get("members"))), r.get("limit", ""), r.get("value", ""),
             r.get("highalch", ""), r.get("lowalch", ""), r.get("examine", "")] for r in ge.values()]
    rows.sort(key=lambda r: r[0])
    counts["ge_items"] = write_csv("ge_items.csv", ["id", "name", "members", "buy_limit", "value",
                                                    "high_alch", "low_alch", "examine"], rows)

    meta = {
        "built_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sources": {
            "runelite_gameval": RL_BASE,
            "chisel": CHISEL_BASE,
            "prices_mapping": PRICES_MAPPING,
        },
        "row_counts": counts,
    }
    with open(os.path.join(DATA, "BUILD_INFO.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print("done.")


if __name__ == "__main__":
    main()
