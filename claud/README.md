# OSRS bot-scripting knowledge pack

Everything in this folder was built from the **current main-game data** (RuneLite's generated
constants and the OSRS Wiki team's cache dumps) so it matches a private server that runs the
latest OSRS revision. See `data/BUILD_INFO.json` for the exact build date.

| Path | What it is |
|---|---|
| `GUIDE.md` | The guide sheet: how bots work, the game model (ticks, coordinates, entities, varbits, widgets, menus, inventories, skills, combat), script patterns, data reference, cheat sheets of common IDs, private-server caveats, sources. |
| `data/*.csv` | Flat ID tables generated from the cache: items, NPCs, objects, animations, varbits, varps, inventories, spotanims, sprites, client vars, DB tables, interface groups/children, GE items. |
| `raw/gameval/*.java` | RuneLite's generated constant classes (grep-able; drop straight into a Java project). |
| `scripts/build_data.py` | Re-downloads the sources and rebuilds `data/`. Run it after a game update. |
| `scripts/lookup.py` | Command-line search across the tables. |
| `templates/` | Compilable skeletons: RuneLite plugin (tick state machine), DreamBot, OSBot. |

## Quick start

```bash
# find ids
python3 scripts/lookup.py shark
python3 scripts/lookup.py -t objects --op "Chop down" "yew"
python3 scripts/lookup.py -t interfaces bankmain
python3 scripts/lookup.py -t varbits prayer_protectfrommelee

# refresh after a game update (needs internet, ~60 MB download)
python3 scripts/build_data.py --refresh
```

## Working with an AI coding agent

Point the agent at this folder. The useful instruction is: *"Look ids up in `data/*.csv` with
`scripts/lookup.py` instead of guessing; read `GUIDE.md` sections 2 and 3 before writing a
script; use `templates/` as the starting shape."* The CSVs are plain text, so any agent can grep them.

## Caveats

* IDs are tied to the cache revision. If your private server is behind the main game, ids above
  the server's max will not exist and a few may have moved. `GUIDE.md` §6 explains how to check.
* Custom content on a private server (new items, NPCs, shops) is not in here. Its ids usually sit
  above the official maximum for that table (listed in `GUIDE.md` §6).
* `raw/chisel/` and `raw/prices_mapping.json` are not committed (46 MB). `build_data.py` re-fetches them.
