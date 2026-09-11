# OSRS Bot Scripting Guide Sheet

Built from the current main-game cache (see `data/BUILD_INFO.json` for the date). Everything with a
number in this document was read from the generated tables in `data/` or from the RuneLite API
source, not from memory. Where something is framework-specific or uncertain it says so.

Contents

1. How OSRS bots work and which route fits a private server
2. The game model (what a script can see and do)
   - 2.1 Ticks and timing
   - 2.2 Coordinates: world, region, scene, local, plane, instances
   - 2.3 Entities: players, NPCs, objects, ground items, projectiles
   - 2.4 Definitions, transforms and "null" names
   - 2.5 Interaction: right-click options, menu actions, `menuAction()` arguments
   - 2.6 Item containers (inventories) and equipment slots
   - 2.7 Varps and varbits (player state)
   - 2.8 Widgets and interfaces (UI), dialogs, bank UI
   - 2.9 Skills and experience
   - 2.10 Animations and idle detection
   - 2.11 Movement, collision, run energy, doors
   - 2.12 Banking
   - 2.13 Combat essentials
   - 2.14 Game state, login, disconnects
3. Writing a script: the tick state machine and what not to do
4. Looking human: timing and behaviour basics
5. Data reference: every table in `data/`, column meanings, item params
6. Private-server caveats: revision, custom ids, verifying in game
7. Sources and how to refresh
8. Appendix: cheat sheets of common ids (generated)

---

## 1. How OSRS bots work and which route fits a private server

Three families of bot exist. Which one you can use is decided by the client your server ships.

| Family | How it sees the game | How it acts | Examples |
|---|---|---|---|
| **Injection / reflection clients** | Load the official game client and hook its fields (NPC lists, inventory, varps). | Simulate mouse/keyboard on the real client, or invoke menu actions directly. | DreamBot, OSBot, TRiBot, RuneMate |
| **RuneLite-fork plugins** | RuneLite already exposes the whole game model through `net.runelite.api.Client`. A plugin reads it on the client thread. | Stock RuneLite has no input API; automation forks add one (`menuAction` helpers, packet senders, mouse movers). | Microbot, EthanVann's plugin utils, Devious, OpenOSRS-era forks |
| **Colour / pixel bots** | Screenshots only: colour matching, OCR, template matching. | OS-level mouse and keyboard. | Custom Python (pyautogui/OpenCV), AutoHotkey |

**For a private server, work out which client you have:**

1. **It is a RuneLite fork** (most modern private servers with an "OSRS-like" client). Use the
   plugin route. Everything in section 2 maps 1:1 onto `net.runelite.api`, and the ids in `data/`
   are exactly what `npc.getId()`, `object.getId()`, `client.getVarbitValue()` return. If the fork is
   built from a Microbot-style base you also get ready-made helpers (`Rs2Npc`, `Rs2GameObject`,
   `Rs2Inventory`, `Rs2Bank`, `Rs2Walker`, `Rs2Widget` and friends). If it is a plain RuneLite fork,
   you drive the game with `client.menuAction(...)` (section 2.5) or a small mouse helper.
2. **It is a decompiled/"deob" client with source** (older RSPS style, often a Java project you can
   build). Then you can add automation directly inside the client: you have the NPC array, the
   inventory array and the packet sender in front of you. The ids and mechanics here still apply as
   long as the server runs the current revision.
3. **It is a closed client you cannot modify.** Then you are limited to colour bots, and the id
   tables only help for wiki-style knowledge (names, options, what drops where). Most of section 2
   still explains what you are looking at on screen.

Commercial frameworks (DreamBot, OSBot, TRiBot) load the *official* client, so they do not connect
to private servers unless the server has explicitly built support for them. The templates for
them in `templates/` are there for API-shape reference and for the rare server that does.

---

## 2. The game model

### 2.1 Ticks and timing

| Constant | Value | Notes |
|---|---:|---|
| Game tick | **600 ms** | Every server-side action resolves on tick boundaries: attacks, skilling rolls, movement, eating. |
| Client tick | 20 ms | Render/input loop; irrelevant to game logic. |
| Walking speed | 1 tile / tick | Running is 2 tiles / tick. |
| Food eat delay | 3 ticks | You can't eat again for 3 ticks (karambwan is separate and combos). |
| Weapon speed | item param 14 | Ticks between attacks. Whip = 4, scimitar = 4, 2h = 7, shortbow = 3 (rapid 2). |
| Logout timer | 5 min idle | Official servers; private servers vary. |

Practical rules:

* Count in ticks, not milliseconds. RuneLite gives `client.getTickCount()` and a `GameTick` event.
* Only one meaningful action per tick reaches the server. Queueing five clicks in one tick is
  pointless and looks robotic.
* "Wait until X" loops should be tick-based with a maximum (e.g. give up after 10 ticks).

### 2.2 Coordinates

**World coordinates** are `(x, y, plane)`. `x` grows east, `y` grows north, `plane` is 0–3
(ground floor is 0). Lumbridge castle courtyard is around `(3222, 3218, 0)`.

| Concept | Size | Formula / notes |
|---|---:|---|
| Tile | 1×1 | Smallest unit. Entities stand on a tile; big NPCs occupy `size × size` with the reported tile at the south-west corner. |
| Chunk | 8×8 tiles | Used for instance templating. |
| Region | 64×64 tiles | `regionId = ((x >> 6) << 8) \| (y >> 6)`. Lumbridge = 12850. Region x = `regionId >> 8`, region y = `regionId & 0xFF`. |
| Scene | 104×104 tiles | What the client has loaded around you. `client.getBaseX()/getBaseY()` is the scene's SW corner; `sceneX = worldX - baseX`. Extended scene is 184×184. |
| Local point | 128 units per tile | `LocalPoint` is scene-relative and sub-tile; tile centre is at `+64`. Used for projections and `menuAction` on objects. |
| Planes | 4 | Objects/NPCs on another plane are irrelevant; always filter by `getPlane()`. |

**Instances** (raids, boss rooms, some quests) copy 8×8 chunks from template regions into a
temporary area. `WorldPoint.fromLocalInstance(client, localPoint)` converts back to the template's
real world coordinates so region-based logic keeps working. `client.getTopLevelWorldView().isInstance()`
tells you if you are in one.

Distance: use Chebyshev (`max(|dx|, |dy|)`) for "how many tiles away" — that is what
`WorldPoint.distanceTo` returns and what melee range means.

### 2.3 Entities

| Type | RuneLite class | Key fields | Notes |
|---|---|---|---|
| Local player | `Player` via `client.getLocalPlayer()` | `getWorldLocation()`, `getAnimation()`, `getPoseAnimation()`, `getInteracting()`, `getHealthRatio()/getHealthScale()`, `getCombatLevel()`, `getPlayerComposition()` (equipment ids) | Animation `-1` = not animating. Pose animation ≠ idle pose means moving. |
| NPC | `NPC` | `getId()`, `getIndex()`, `getName()`, `getCombatLevel()`, `getWorldLocation()`, `getInteracting()`, `getComposition()`, `getAnimation()`, `isDead()` | **Index** is the per-world slot (0–32767), unique while spawned; **id** is the definition (`data/npcs.csv`). Menu actions on NPCs take the *index*. |
| Game object | `GameObject` (also `WallObject`, `GroundObject`, `DecorativeObject`) | `getId()`, `getWorldLocation()`, `getLocalLocation()`, `getSceneMinLocation()`, `getSizeX()/Y()`, `getOrientation()` | Trees, rocks, booths, doors. Doors are usually `WallObject`s. Found by walking `Scene.getTiles()[plane][x][y]`. |
| Ground item | `TileItem` | `getId()`, `getQuantity()`, tile from the `Tile` it sits on | Events: `ItemSpawned` / `ItemDespawned`. Ownership/visibility timers exist on the official game. |
| Projectile | `Projectile` | `getId()` (spotanim), `getInteracting()`, `getRemainingCycles()` | Useful for boss mechanics and prayer switching. |
| Graphics object | `GraphicsObject` | `getId()`, `getLocation()` | Ground spot animations (spells landing, traps). |
| Hitsplat | `HitsplatApplied` event | `getHitsplat().getAmount()`, `getHitsplatType()` | On any actor. |

Health without an exact number: NPCs/players only expose `healthRatio` and `healthScale` while a
health bar is showing. `currentHp ≈ ratio / scale × maxHp` (max HP for NPCs is `stat_hitpoints` in
`data/npcs.csv`). `ratio == 0` means dead/dying.

### 2.4 Definitions, transforms and "null" names

Every id in `data/` is a **definition** (cache config). One definition can have many live
instances (all the `Tree` id 1276 objects in Lumbridge). Two things make ids trickier than they look:

**Transforms (multi-children).** Some NPC and object ids are *containers* whose real appearance is
chosen at runtime by a varbit or varp. Example: a quest NPC id that turns into a different NPC after
a quest, or a farming patch object that becomes "Herbs (grown)". In the CSVs these have `varbit_id`
(or `varp_id`) set and a `multi_children` list. In RuneLite, `NPCComposition.transform()` and
`ObjectComposition.getImpostor()` resolve to the currently displayed child; scripts should
compare against the *transformed* id's name/options, not the container id. Note `-1` entries in
`multi_children` mean "nothing shown for that value".

**Null names.** Rows named `null` are real ids that are never shown as a name: noted item
variants (e.g. `386 = Cert.SHARK`, the noted shark), bank placeholders (`Placeholder.*`), hidden
objects, and layout-only NPCs. Noted ids matter for banking: withdraw-as-note gives you the
`noted_id` from `data/items.csv`. Placeholder ids matter only for bank-tab logic.

**Categories.** `category` in the item/NPC/object tables is a cache category id (used by shops and
by the client for grouping). It is not a skill or a type; treat it as an opaque group key.

### 2.5 Interaction: options, menu actions and `menuAction()`

Every NPC, object and item definition has up to five right-click **options** (ops), stored in
slot order. In the CSVs they are pipe-joined **with position preserved**: `Bank|Collect` means
slot 1 = Bank, slot 2 = Collect; `|Chop down` would mean slot 2 = Chop down with slot 1 empty.
Items have `inventory_ops` (when in your inventory: `Eat|Drop`) and `ground_ops` (on the floor:
`Take`). The *slot number* is what the client sends, so "first option" is meaningful even when the
text changes between revisions.

RuneLite `MenuAction` ids (what `client.menuAction(...)` and `MenuOptionClicked` use):

| Target | Slot 1 | Slot 2 | Slot 3 | Slot 4 | Slot 5 | Use item / spell on |
|---|---:|---:|---:|---:|---:|---|
| Game object | 3 | 4 | 5 | 6 | 1001 | item 1, widget/spell 2 |
| NPC | 9 | 10 | 11 | 12 | 13 | item 7, widget/spell 8 |
| Ground item | 18 | 19 | 20 | 21 | 22 | item 16, widget/spell 17 |
| Player | 44 | 45 | 46 | 47 | 48 (…51 for 8 slots) | item 14, widget/spell 15 |
| Widget button | 39 | 40 | 41 | 42 | 43 | — |
| Widget component op (modern UI, inventory items, bank items) | **57 `CC_OP`** (op index passed separately) | | | | | `WIDGET_TARGET_ON_WIDGET` 58 |
| Walk here | 23 `WALK` | | | | | |
| Continue dialog | 30 `WIDGET_CONTINUE` | | | | | |
| Close widget | 26 | | | | | |
| Item on item | 31 | | | | | |

Legacy `ITEM_FIRST_OPTION` (33–38) still exist but the live client uses `CC_OP` on the inventory
widget for item ops.

`client.menuAction(p0, p1, action, id, itemId, option, target)` argument meaning by action type:

| Action | `p0` | `p1` | `id` | `itemId` |
|---|---|---|---|---|
| `GAME_OBJECT_*` | object scene X | object scene Y | object id | -1 |
| `NPC_*` | 0 | 0 | **npc index** | -1 |
| `GROUND_ITEM_*` | scene X | scene Y | item id | -1 |
| `WALK` | scene X | scene Y | 0 | -1 |
| `CC_OP` (widget op) | child index inside the component (`-1` if none; inventory slot for items) | **packed component id** | op number (1-based) | item id (or -1) |
| `WIDGET_CONTINUE` | child index or -1 | packed component id | 0 | -1 |
| `WIDGET_TARGET_ON_*` | as target type | | as target type | `client.setSelectedSpellWidget` etc. first |

(`option` and `target` strings are cosmetic for the server but keep them accurate; some forks and
anti-cheat logs check them.)

**Packed component id** = `(groupId << 16) | childId`. All packed ids are precomputed in
`data/interface_children.csv`. Inventory items live in component `149:0` = **9764864**, slot =
inventory index 0–27.

### 2.6 Item containers (inventories) and equipment slots

`client.getItemContainer(id)` → `ItemContainer` with `getItems()` (array of `Item{id, quantity}`;
`id == -1` empty). Common container ids (`data/inventories.csv`, RuneLite `InventoryID`):

| Id | Name | Contents |
|---:|---|---|
| 93 | `INV` | Backpack, 28 slots |
| 94 | `WORN` | Equipment, 14 slots (below) |
| 95 | `BANK` | Bank, ordered as displayed (tabs are ranges of this) |
| 90 | `TRADEOFFER` | Your side of a trade |
| 516 | `LOOTING_BAG` | Looting bag |
| 626 | `SEED_VAULT` | Seed vault |
| 526–531, 537–538 | `GE_OFFER_0..7` | GE offer slots |
| 3, 4, 13, … | `GENERALSHOP*` | Shop stock containers |

Equipment slot indexes (RuneLite `EquipmentInventorySlot`):

| Slot | 0 | 1 | 2 | 3 | 4 | 5 | 7 | 9 | 10 | 12 | 13 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| | Head | Cape | Amulet | Weapon | Body | Shield | Legs | Gloves | Boots | Ring | Ammo |

(6 = arms, 8 = hair, 11 = jaw are appearance-only.) Equipment UI is interface group 387
(`Wornitems`), slot components `SLOT0..` start at child 15.

Events: `ItemContainerChanged` fires when any container changes; check `getContainerId()`.

### 2.7 Varps and varbits

A **varp** (player variable) is a 32-bit int the server pushes to the client (about 5.7 k of them).
A **varbit** is a named bit-slice of a varp: `(varpIndex, lsb, msb)`, value =
`(varp >> lsb) & ((1 << (msb - lsb + 1)) - 1)`. The mapping from varbit id to (varp, lsb, msb) is in
the cache; RuneLite resolves it for you (`client.getVarbitValue(id)`, `client.getVarpValue(id)`).
`data/varbits.csv` and `data/varps.csv` give you the **names and ids**; the slice mapping is not
included because it is revision-specific and your client already knows it.

Event: `VarbitChanged` (fires for both varps and varbits; check `getVarbitId()`/`getVarpId()`).

Frequently used (all verified against the current constants):

| Kind | Id | Name | Meaning |
|---|---:|---|---|
| varp | 173 | `OPTION_RUN` | 1 = run enabled |
| varp | 300 | `SA_ENERGY` | Special attack energy 0–1000 (1000 = 100%) |
| varp | 301 | `SA_ATTACK` | 1 = special attack armed |
| varp | 43 | `COM_MODE` | Attack style index (0–3) for the current weapon type |
| varp | 102 | `POISON` | > 0 poisoned, ≥ 1000000 venomed (negative = immunity timer) |
| varbit | 4070 | `SPELLBOOK` | 0 standard, 1 ancient, 2 lunar, 3 arceuus |
| varbit | 4103 | `QUICKPRAYER_ACTIVE` | Quick prayers on |
| varbit | 4104–4129 | `PRAYER_*` | Individual prayers, 1 = active (thick skin 4104 … piety 4129) |
| varbit | 5464 / 5465 / 5466 | `PRAYER_RIGOUR` / `AUGURY` / `PRESERVE` | |
| varbit | 275 / 276 / 2668 | `AUTOCAST_SET` / `AUTOCAST_SPELL` / `AUTOCAST_DEFMODE` | Autocast state |
| varbit | 25 / 24 | `STAMINA_ACTIVE` / `STAMINA_DURATION` | Stamina potion |
| varbit | 3981 | `ANTIFIRE_POTION` | |
| varbit | 3958 | `BANK_WITHDRAWNOTES` | 1 = withdraw as note |
| varbit | 6590 | `BANK_QUANTITY_TYPE` | Selected quantity button (1/5/10/X/All) |
| varbit | 3960 | `BANK_REQUESTEDQUANTITY` | The "X" amount |
| varbit | 3755 | `BANK_LEAVEPLACEHOLDERS` | Placeholders toggle |
| varbit | 4150 | `BANK_CURRENTTAB` | Open bank tab |
| varbit | 4067 | `SLAYER_MASTER` | |
| varbit | 1777 | `IRONMAN` | Account mode |

Run energy is **not** a varp: `client.getEnergy()` returns 0–10000 (divide by 100 for %).
Real and boosted skill levels are separate client arrays (2.9), not varps.

### 2.8 Widgets and interfaces

The UI is a tree of **widgets**. A widget is addressed by `(groupId, childId)` or the packed id.
`client.getWidget(group, child)` returns `null` when the interface is not loaded; `isHidden()`
tells you whether it is currently visible. Children of a component (e.g. dialog options, bank item
slots) are *dynamic children*: `widget.getChildren()` / `getChild(i)`.

Key interface groups (`data/interface_groups.csv`; children in `interface_children.csv`):

| Group | Name | What |
|---:|---|---|
| 548 | `TOPLEVEL` | Fixed-mode root |
| 161 | `TOPLEVEL_OSRS_STRETCH` | Resizable classic root |
| 164 | `TOPLEVEL_PRE_EOC` | Resizable modern root |
| 162 | `CHATBOX` | Chat area; `Chatbox.INPUT` 162:57 (child 57), lines from 162:59 |
| 149 | `INVENTORY` | Backpack; items in `Inventory.ITEMS` 149:0 (packed 9764864) |
| 387 | `WORNITEMS` | Equipment tab |
| 12 | `BANKMAIN` | Bank window (see 2.12) |
| 15 | `BANKSIDE` | Your inventory while the bank is open; items in `Bankside.ITEMS` 15:3 (983043) |
| 192 | `BANK_DEPOSITBOX` | Deposit box UI |
| 231 | `CHAT_LEFT` | **NPC dialog** (NPC head on the left): `TEXT` 231:6, `CONTINUE` 231:5, `NAME` 231:4 |
| 217 | `CHAT_RIGHT` | **Player dialog**: `TEXT` 217:6, `CONTINUE` 217:5 |
| 219 | `CHATMENU` | **Option dialog**: `OPTIONS` 219:1, option *n* = dynamic child *n* (child 0 is the title) |
| 229 | `MESSAGEBOX` | Plain message: `TEXT` 229:3, `CONTINUE` 229:4 |
| 193 | `OBJECTBOX` | Item-with-text dialog: `ITEM` 193:1, `TEXT` 193:2 |
| 233 | `LEVELUP_DISPLAY` | Level-up popup, `CONTINUE` 233:3 |
| 270 | `SKILLMULTI` | "Make X" / production menu |
| 541 | `PRAYERBOOK` | Prayer tab |
| 218 | `MAGIC_SPELLBOOK` | Spellbook tab |
| 320 | `STATS` | Skills tab |
| 593 | `COMBAT_INTERFACE` | Attack styles + special attack |
| 160 | `ORBS` | HP/prayer/run/special orbs |
| 182 | `LOGOUT` | Logout tab |
| 300 / 301 | `SHOPMAIN` / `SHOPSIDE` | Shop window / your inventory in a shop |
| 335 / 334 | `TRADEMAIN` / `TRADECONFIRM` | Trade screens |
| 465 / 467 / 402 | `GE_OFFERS` / `GE_OFFERS_SIDE` / `GE_COLLECT` | Grand Exchange |
| 378 | `WELCOME_SCREEN` | "Click here to play" |
| 595 | `WORLDMAP` | |

Dialog handling pattern: check 231/217/229/193 for a visible `CONTINUE` child → send
`WIDGET_CONTINUE` on it (or press space); check 219 for options → pick the dynamic child whose text
matches → `WIDGET_CONTINUE` with `p0 = optionIndex`, `p1 = 219:1 packed`. Level-up popups (233)
and "make X" (270) interrupt skilling loops and must be handled or the script stalls.

### 2.9 Skills and experience

Skill index order (RuneLite `Skill` ordinal = server skill id):

| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Attack | Defence | Strength | Hitpoints | Ranged | Prayer | Magic | Cooking | Woodcutting | Fletching | Fishing | Firemaking |

| 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Crafting | Smithing | Mining | Herblore | Agility | Thieving | Slayer | Farming | Runecraft | Hunter | Construction | Sailing |

Client accessors: `getRealSkillLevel(skill)`, `getBoostedSkillLevel(skill)`,
`getSkillExperience(skill)`; event `StatChanged`. Max XP per skill is 200,000,000; max real level 99,
virtual 126.

XP required for level *L*: `floor( Σ_{l=1}^{L-1} floor( l + 300 · 2^(l/7) ) / 4 )`.

| Level | XP | Level | XP |
|---:|---:|---:|---:|
| 1 | 0 | 75 | 1,210,421 |
| 10 | 1,154 | 80 | 1,986,068 |
| 20 | 4,470 | 85 | 3,258,594 |
| 30 | 13,363 | 90 | 5,346,332 |
| 40 | 37,224 | 92 | 6,517,253 |
| 50 | 101,333 | 95 | 8,771,558 |
| 60 | 273,742 | 99 | 13,034,431 |
| 70 | 737,627 | 126 | 188,884,740 |

Combat level: `base = 0.25 × (Defence + Hitpoints + floor(Prayer / 2))`,
`melee = 0.325 × (Attack + Strength)`, `ranged = 0.325 × floor(1.5 × Ranged)`,
`magic = 0.325 × floor(1.5 × Magic)`, `combat = floor(base + max(melee, ranged, magic))`.

### 2.10 Animations and idle detection

`Actor.getAnimation()` is `-1` when nothing is playing. Skilling animations loop while the action
continues and drop to `-1` a tick or two after the resource depletes, so the standard idle test is
"animation == -1 **and** pose animation == idle pose for ≥ 2 ticks" (a single idle tick happens
between swings). Player animation ids for common activities (`data/animations.csv`):

| Activity | Id | Constant |
|---|---:|---|
| Woodcutting, bronze / iron / steel / black / mithril / adamant / rune axe | 879 / 877 / 875 / 873 / 871 / 869 / 867 | `HUMAN_WOODCUTTING_*_AXE` |
| Woodcutting, dragon / infernal axe | 2846 / 2117 | |
| Mining, bronze / iron / steel / mithril / adamant / rune pickaxe | 625 / 626 / 627 / 629 / 628 / 624 | `HUMAN_MINING_*_PICKAXE` |
| Mining, dragon / infernal pickaxe | 642 / 4482 | (`_WALL` and `_NOREACHFORWARD` variants exist per pickaxe) |
| Fishing (rod cast) | 622 | `HUMAN_FISHING_CASTING` |
| Cooking | 896 | `HUMAN_COOKING` |
| Smithing (anvil) | 898 | `HUMAN_SMITHING` |
| Fletching | 1248 | `HUMAN_FLETCHING` |
| Runecrafting | 791 | `HUMAN_RUNECRAFT` |
| Pickpocket | 881 | `HUMAN_PICKPOCKET` |
| Eat | 829 | `HUMAN_EAT` |
| Death | 836 | `HUMAN_DEATH` |
| Walk / run (pose animations) | 819 / 824 | `HUMAN_WALK_F` / `HUMAN_RUNNING` |

Many activities (fishing with nets/harpoons, agility obstacles, combat with each weapon type) have
their own ids: search `animations.csv` by constant name, or read `getAnimation()` in game once.

### 2.11 Movement, collision, run energy, doors

* **Click-to-walk** is a `WALK` menu action on a scene tile; the server pathfinds up to ~25 tiles
  reliably and stops at the nearest reachable tile. Longer trips need waypoints or a web-walker
  (Microbot and DreamBot ship one; stock RuneLite does not).
* **Collision map**: `client.getTopLevelWorldView().getCollisionMaps()[plane].getFlags()[sceneX][sceneY]`.
  Flags (RuneLite `CollisionDataFlag`): `0x2` north blocked, `0x8` east, `0x20` south, `0x80` west,
  diagonals `0x1/0x4/0x10/0x40`, `0x100` object on tile, `0x200000` floor blocked (water),
  `0x40000` floor decoration, `BLOCK_MOVEMENT_FULL` = all of those. Line-of-sight flags are the
  movement flags shifted left 9 (`0x400` north … `0x10000` west, `0x20000` full).
* **Run energy**: `client.getEnergy()` 0–10000. Toggle with the orb (group 160) or by `CC_OP`
  on the run orb; state in varp 173. Stamina in varbits 24/25.
* **Doors and gates** are `WallObject`s with an `Open` option; closed/open are different object ids
  (search `objects.csv` for the name and check the option). Always re-check the door id after
  interacting because the id flips.
* **Stairs/ladders** change plane; wait for `getPlane()` to change before continuing.

### 2.12 Banking

Open: interact with a bank booth (`Bank` is slot 1 on booths/chests, some also have `Collect` and
`Deposit-box`), a banker NPC (`Bank` op), or a deposit box (`Deposit`). Detect open with
`client.getWidget(12, 0) != null && !isHidden()` (the `Bankmain.UNIVERSE` 12:1 component is also
used). Bank contents are container 95; items shown in `Bankmain.ITEMS` 12:12 (packed 786444), one
dynamic child per slot in bank order.

Buttons (`Bankmain`, group 12; use `CC_OP` op 1 unless noted):

| Child | Packed | Constant | Action |
|---:|---:|---|---|
| 47 | 786479 | `DEPOSITINV` | Deposit inventory |
| 49 | 786481 | `DEPOSITWORN` | Deposit worn items |
| 25 | 786457 | `NOTE` | Toggle withdraw-as-note (state varbit 3958) |
| 29 / 31 / 33 / 35 / 37 | 786461 / 786463 / 786465 / 786467 / 786469 | `QUANTITY1/5/10/X/ALL` | Quantity buttons (state varbit 6590) |
| 40 | 786472 | `PLACEHOLDER` | Placeholders toggle |
| 42 | 786474 | `SEARCH` | Search |
| 10 | 786442 | `TABS` | Tab bar (dynamic children) |

Withdrawing an item is `CC_OP` on `Bankmain.ITEMS` with `p0 = slot`, `p1 = 786444`, `itemId = item`,
and the op index selecting the right-click entry (1 = current quantity mode, then Withdraw-1, -5,
-10, -X, -All, -All-but-one, … the exact order is in the item's menu; read it from
`client.getMenuEntries()` once and hard-code the index). Depositing from `Bankside.ITEMS` 15:3
(packed 983043) works the same way. DreamBot/OSBot/Microbot wrap all of this (`Bank.withdraw(id, n)`).

### 2.13 Combat essentials

* **Attack speed** in ticks is item param 14 (`params` column, `data/items.csv`). Attack-style
  changes (varp 43) can alter it (rapid = −1 tick).
* **Bonuses** are item params 0–4 (attack: stab, slash, crush, magic, ranged), 5–9 (defence, same
  order), 10 melee strength, 11 prayer, 12 ranged strength, 65 magic damage %.
* **NPC stats** are in `data/npcs.csv` (`stat_attack … stat_magic`, `combat_level`, `size`).
  Attack/defence bonuses of NPCs are in the `params` column of the NPC row for those that have them.
* **Targeting**: `client.getLocalPlayer().getInteracting()` is the actor you are attacking;
  `npc.getInteracting() == localPlayer` means it is on you. Filter candidates by
  `npc.getInteracting() == null || == localPlayer` to avoid crashing others' kills.
* **Prayer flicking** works on tick boundaries: toggle within the same tick as the hit lands.
  Prayer state is the varbit set in 2.7; the prayer book is group 541.
* **Special attack**: varp 300 energy, varp 301 armed; the button is in group 593.
* **Poison / venom**: varp 102. **Multi-combat**: shown by the client's multi icon; there is no
  single varbit for it in the generated constants, so use the wiki region lists or the map area
  flags if you need it.
* **Aggression / safety**: hitsplat events give damage taken per tick; a simple "eat below X HP
  and stop if food is gone" guard should exist in every combat script.

### 2.14 Game state, login, disconnects

`client.getGameState()`: `LOGIN_SCREEN` 10, `LOGGING_IN` 20, `LOADING` 25 (region change),
`LOGGED_IN` 30, `CONNECTION_LOST` 40, `HOPPING` 45. `GameStateChanged` fires on transitions.
`LOADING` happens every time you cross into a new scene; scripts that cache object references
must drop them on `LOADING` because the scene is rebuilt. Random events exist only on the
official game; a private server may or may not implement them.

---

## 3. Writing a script

The pattern that works for every framework is a **tick-driven state machine**:

```
every game tick:
    if not logged in or paused: return
    observe   -> read player state, inventory, nearby entities, open widgets
    decide    -> pick a state from what you observed (do not trust your previous state blindly)
    act       -> issue at most ONE action, record the tick you did it on
    wait      -> do nothing until the action has had time to complete (n ticks), then re-observe
```

Rules that save the most debugging time:

1. **Derive state from the world, not from memory.** "Inventory full → go bank" beats a flag you
   set three states ago. Re-check every tick; the world changes under you (someone takes the tree,
   a level-up dialog opens, you get disconnected).
2. **One action per tick, with a randomised gap of 1–3 ticks between actions.**
3. **Handle interrupts first**: dialogs (2.8), level-ups, `LOADING`, low HP, full/empty inventory,
   missing tool. Put them at the top of the tick handler.
4. **Timeouts on every wait.** If the animation never starts within ~5 ticks, re-issue or change
   target; increment a failure counter and stop after N failures instead of spam-clicking forever.
5. **Never sleep on the client thread** (RuneLite plugins). Sleeping freezes rendering and the event
   bus. DreamBot/OSBot run your loop on their own thread, so `sleep` is fine there.
6. **Filter by plane and reachability** before choosing a target. The nearest tree may be on the
   other side of a fence.
7. **Log ticks and decisions.** A one-line log per state change makes bugs obvious.
8. **Use names for readability, ids for matching.** Compare `getId()` against constants pulled from
   `data/`, not `getName()` strings, but keep the name in the constant so the code reads well
   (`ObjectID.TREE`, `NpcID.BANKER_LUMBRIDGE_…`).

`templates/runelite-plugin/ExampleBotPlugin.java` is this pattern written out for a chop-and-bank
loop; `templates/dreambot` and `templates/osbot` show the same loop in those APIs.

---

## 4. Looking human (behavioural basics)

Detection on a private server is whatever the owners bolted on. It ranges from nothing to
click-timing heuristics to staff watching. What is cheap to do and always helps:

* Reaction delays drawn from a skewed distribution (e.g. 150–900 ms after the trigger, long tail),
  not fixed 600 ms.
* Occasional idle pauses (10–60 s) and longer breaks (a few minutes per hour).
* Vary targets: not always the exact nearest tree; pick from the closest 2–3.
* Move the mouse along curved paths if the client actually renders a cursor path (injection
  clients do; `menuAction` calls do not, which is one reason forks that use packets are easier to
  spot server-side by timing alone).
* Camera nudges and interface tab flips at random intervals.
* Do not bot on a schedule that never varies, and do not run 24/7.

---

## 5. Data reference

All tables are UTF-8 CSV with a header row and `\n` line endings. Empty cell = not applicable.

### `items.csv` (34,603 rows)

| Column | Meaning |
|---|---|
| `id`, `name` | Cache id and display name (`null` = never displayed: noted, placeholder, hidden) |
| `runelite_const` | RuneLite `ItemID.*` constant; `Cert.X` = noted variant of X, `Placeholder.X` = bank placeholder |
| `config_name` | Jagex internal name from the cache |
| `members`, `tradeable`, `ge_tradeable` | 1/0 flags |
| `stackable` | 1 = stacks in inventory |
| `noted_id`, `placeholder_id` | Ids of the noted / placeholder variants |
| `value` | Shop value; `high_alch` / `low_alch` from the GE mapping (tradeables only); `ge_buy_limit` |
| `weight_g` | Weight in grams (÷1000 for kg) |
| `inventory_ops`, `ground_ops` | Right-click options in slot order (2.5) |
| `examine` | Examine text |
| `params` | Raw cache params as JSON `{paramId: value}` (see below) |

Item params seen so far (Jagex ids; verified on the whip/shark/logs rows):

| Param | Meaning |
|---:|---|
| 0–4 | Attack bonus: stab, slash, crush, magic, ranged |
| 5–9 | Defence bonus: stab, slash, crush, magic, ranged |
| 10 | Melee strength |
| 11 | Prayer bonus |
| 12 | Ranged strength |
| 14 | Attack speed (ticks) |
| 65 | Magic damage (%) |
| 434 / 436 | Primary requirement: skill id (2.9 order) / level, e.g. whip `434:0, 436:70` = Attack 70 |
| 451–458 | `OC_ITEM_OP1..8` used-on-widget option labels |
| others | Unknown / cosmetic; see RuneLite `ParamID.java` for the ones it names |

### `npcs.csv` (16,576 rows)

`id`, `name`, `runelite_const`, `config_name`, `combat_level`, `size` (tiles per side),
`on_minimap`, `is_follower` (pets), `ops` (slot order), `stat_attack`, `stat_defence`,
`stat_strength`, `stat_hitpoints`, `stat_ranged`, `stat_magic`, `varbit_id` / `varp_id` +
`multi_children` (transforms, 2.4), `category`, `params`.

### `objects.csv` (62,510 rows)

`id`, `name`, `runelite_const`, `config_name`, `size_x`, `size_y`, `ops`, `blocks_projectile`,
`obstructs_ground`, `wall_or_door` (cache "interact type"), `varbit_id` / `varp_id` +
`multi_children`, `category`, `map_scene_id` (minimap icon).

### Other tables

| File | Rows | Columns |
|---|---:|---|
| `animations.csv` | 14,491 | `id`, `runelite_const`, `comment` |
| `varbits.csv` | 13,245 | `id`, `runelite_const`, `comment` |
| `varps.csv` | 2,935 | `id`, `runelite_const`, `comment` |
| `inventories.csv` | 1,029 | item container ids |
| `spotanims.csv` | 4,022 | graphics/spot-animation ids (projectiles, spell effects) |
| `sprites.csv` | 8,560 | UI sprite ids |
| `varclient.csv` | 1,508 | client-side vars (camera, chat settings) |
| `dbtables.csv` | 18,107 | `Table.COLUMN` ids of the cache DB tables (quests, music, areas …) |
| `interface_groups.csv` | 969 | `group_id`, `runelite_const` |
| `interface_children.csv` | 26,405 | `group_class`, `child_const`, `group_id`, `child_id`, `packed_id`, `packed_hex` |
| `ge_items.csv` | 4,662 | tradeable items with `buy_limit`, `value`, `high_alch`, `low_alch` |

### Searching

```bash
python3 scripts/lookup.py "rune scimitar"                  # default tables
python3 scripts/lookup.py -t objects --op Mine "iron"      # objects with Mine option containing "iron"
python3 scripts/lookup.py -t npcs 2042 --all-cols          # every column for npc id 2042
python3 scripts/lookup.py -t interfaces Chatmenu           # dialog option widget children
grep -i "yew" data/objects.csv | grep "Chop down"          # plain grep works too
```

The raw RuneLite constant classes in `raw/gameval/` can be copied into a Java project as-is
(package `net.runelite.api.gameval`) if your client's API does not already ship them.

---

## 6. Private-server caveats

**Check the revision first.** The tables were built from the live game (see `BUILD_INFO.json`).
Highest id per table in this build:

| Table | Max id |
|---|---:|
| items | 34602 |
| npcs | 16575 |
| objects | 62509 |
| animations | 14497 |
| varbits | 20396 |
| varps | 5731 |

Ways to confirm your server matches:

1. Examine a recently released item or NPC in game and compare the id (RuneLite's developer tools,
   or any `::` debug command the server offers). If ids near the top of the tables exist and match,
   you are on the same revision.
2. If the server ships its own cache, dump it with RuneLite's `cache` module
   (`net.runelite.cache.Cache -c <cachedir> -items <out>` etc.) or OpenRS2's tools, then diff
   names against `data/`. `scripts/build_data.py` can be pointed at your own JSON dumps by
   replacing the files in `raw/chisel/`.
3. **Custom content** (server-specific items, NPCs, shops, zones) will not be in these tables. Its
   ids normally sit above the official max for that table; some servers instead overwrite unused
   official ids, which is why you should verify anything odd in game.
4. Server-side behaviour (drop tables, XP rates, skilling success rates, whether random events or
   the GE exist) is the server's own code. The wiki describes the official game only.
5. Widget layouts are cache data too, so if the server uses the official cache the group/child ids
   here are right; if it ships custom interfaces, read them with RuneLite's widget inspector.

---

## 7. Sources and refreshing

| Source | Used for | URL |
|---|---|---|
| RuneLite `runelite-api` gameval | All `*ID` constants (generated from the live cache by the RuneLite team) | https://github.com/runelite/runelite/tree/master/runelite-api/src/main/java/net/runelite/api/gameval |
| RuneLite API javadocs | `Client`, `MenuAction`, `CollisionDataFlag`, `Experience` | https://static.runelite.net/runelite-api/apidocs/ |
| Chisel (OSRS Wiki team) | Item/NPC/object definitions dumped from the cache (`items.json`, `npcs.json`, `objects.json`) | https://chisel.weirdgloop.org/moid/ |
| prices.runescape.wiki mapping | GE tradeables, buy limits, alch values | https://prices.runescape.wiki/api/v1/osrs/mapping |
| OSRS Wiki cache log | What changed per game update | https://oldschool.runescape.wiki/w/RuneScape:Cache |
| OSRS Wiki ID pages | Human lookup | https://oldschool.runescape.wiki/w/Item_IDs (also NPC_IDs, Object_IDs) |
| OpenRS2 archive | Every historical cache revision, for servers behind the main game | https://archive.openrs2.org/ |
| osrsbox-db | Older JSON db with monster drop tables (stale since 2021; not used here) | https://github.com/osrsbox/osrsbox-db |

Refresh after a game update:

```bash
python3 scripts/build_data.py --refresh
```

It downloads ~60 MB, rewrites `data/`, and stamps `data/BUILD_INFO.json`.

---

## 8. Appendix: cheat sheets (generated from `data/`)

Every id below came from the tables in this folder. Where several ids share a name (many `Tree`
objects, many `Bank booth`s), the first ~20 are listed; use `lookup.py` for the rest. Options are
in slot order.

### Items


#### Currency & tools

| ID | Name | RuneLite const | Noted ID | Stackable | GE limit | High alch |
|---:|---|---|---:|:-:|---:|---:|
| 995 | Coins | `COINS` |  | y |  |  |
| 13204 | Platinum token | `PLATINUM` |  | y |  |  |
| 1925 | Bucket | `BUCKET_EMPTY` | 1926 |  | 13000 | 1 |
| 946 | Knife | `KNIFE` | 947 |  | 40 | 3 |
| 590 | Tinderbox | `TINDERBOX` | 591 |  | 40 | 1 |
| 2347 | Hammer | `HAMMER` | 2348 |  | 40 | 1 |
| 1755 | Chisel | `CHISEL` | 1756 |  | 40 | 1 |
| 1733 | Needle | `NEEDLE` |  | y | 40 | 1 |
| 1734 | Thread | `THREAD` |  | y | 18000 | 1 |
| 227 | Vial of water | `VIAL_WATER` | 228 |  | 13000 | 1 |
| 954 | Rope | `ROPE` | 955 |  | 250 | 10 |
| 952 | Spade | `SPADE` | 953 |  | 40 | 1 |
| 1785 | Glassblowing pipe | `GLASSBLOWINGPIPE` | 1786 |  | 40 | 1 |
| 233 | Pestle and mortar | `PESTLE_AND_MORTAR` | 234 |  | 40 | 2 |
| 10006 | Bird snare | `HUNTING_OJIBWAY_BIRD_SNARE` |  | y | 250 | 3 |
| 10008 | Box trap | `HUNTING_BOX_TRAP` |  | y | 250 | 19 |
| 303 | Small fishing net | `NET` | 304 |  | 40 | 3 |
| 307 | Fishing rod | `FISHING_ROD` | 308 |  | 40 | 3 |
| 309 | Fly fishing rod | `FLY_FISHING_ROD` | 310 |  | 40 | 3 |
| 311 | Harpoon | `HARPOON` | 312 |  | 40 | 3 |
| 301 | Lobster pot | `LOBSTER_POT` | 302 |  | 40 | 12 |
| 314 | Feather | `FEATHER` |  | y | 30000 | 1 |
| 313 | Fishing bait | `FISHING_BAIT` |  | y | 8000 | 1 |
| 1351 | Bronze axe | `BRONZE_AXE` | 1352 |  | 40 | 9 |
| 1349 | Iron axe | `IRON_AXE` | 1350 |  | 40 | 33 |
| 1353 | Steel axe | `STEEL_AXE` | 1354 |  | 40 | 120 |
| 1355 | Mithril axe | `MITHRIL_AXE` | 1356 |  | 40 | 312 |
| 1357 | Adamant axe | `ADAMANT_AXE` | 1358 |  | 40 | 768 |
| 1359 | Rune axe | `RUNE_AXE` | 1360 |  | 40 | 7680 |
| 6739 | Dragon axe | `DRAGON_AXE` | 6740 |  | 40 | 33000 |
| 1265 | Bronze pickaxe | `BRONZE_PICKAXE` | 1266 |  | 40 | 1 |
| 1267 | Iron pickaxe | `IRON_PICKAXE` | 1268 |  | 40 | 84 |
| 1269 | Steel pickaxe | `STEEL_PICKAXE` | 1270 |  | 40 | 300 |
| 1273 | Mithril pickaxe | `MITHRIL_PICKAXE` | 1274 |  | 40 | 780 |
| 1271 | Adamant pickaxe | `ADAMANT_PICKAXE` | 1272 |  | 40 | 1920 |
| 1275 | Rune pickaxe | `RUNE_PICKAXE` | 1276 |  | 40 | 19200 |
| 11920 | Dragon pickaxe | `DRAGON_PICKAXE` | 11921 |  | 40 | 58770 |

#### Food & potions

| ID | Name | RuneLite const | Noted ID | Stackable | GE limit | High alch |
|---:|---|---|---:|:-:|---:|---:|
| 315 | Shrimps | `SHRIMP` | 316 |  | 6000 | 3 |
| 333 | Trout | `TROUT` | 334 |  | 6000 | 6 |
| 329 | Salmon | `SALMON` | 330 |  | 6000 | 18 |
| 361 | Tuna | `TUNA` | 362 |  | 6000 | 24 |
| 379 | Lobster | `LOBSTER` | 380 |  | 6000 | 42 |
| 373 | Swordfish | `SWORDFISH` | 374 |  | 6000 | 48 |
| 7946 | Monkfish | `MONKFISH` | 7947 |  | 13000 | 138 |
| 385 | Shark | `SHARK` | 386 |  | 10000 | 102 |
| 391 | Manta ray | `MANTARAY` | 392 |  | 10000 | 120 |
| 13441 | Anglerfish | `ANGLERFISH` | 13442 |  | 10000 | 270 |
| 3144 | Cooked karambwan | `TBWT_COOKED_KARAMBWAN` | 3145 |  | 10000 | 150 |
| 2309 | Bread | `BREAD` | 2310 |  | 6000 | 7 |
| 1891 | Cake | `CAKE` | 1892 |  | 6000 | 30 |
| 2289 | Plain pizza | `PLAIN_PIZZA` | 2290 |  | 10000 | 24 |
| 6685 | Saradomin brew(4) | `_4DOSEPOTIONOFSARADOMIN` | 6686 |  | 2000 | 120 |
| 3024 | Super restore(4) | `_4DOSE2RESTORE` | 3025 |  | 2000 | 180 |
| 2434 | Prayer potion(4) | `_4DOSEPRAYERRESTORE` | 2435 |  | 2000 | 114 |
| 12695 | Super combat potion(4) | `_4DOSE2COMBAT` | 12696 |  | 2000 | 150 |
| 2444 | Ranging potion(4) | `_4DOSERANGERSPOTION` | 2445 |  | 2000 | 216 |
| 5952 | Antidote++(4) | `ANTIDOTE__4` | 5953 |  | 4000 | 216 |
| 12625 | Stamina potion(4) | `_4DOSESTAMINA` | 12626 |  | 2000 | 240 |
| 23685 | Divine super combat potion(4) | `_4DOSEDIVINECOMBAT` | 23686 |  | 2000 | 150 |

#### Logs

| ID | Name | RuneLite const | Noted ID | Stackable | GE limit | High alch |
|---:|---|---|---:|:-:|---:|---:|
| 1511 | Logs | `LOGS` | 1512 |  | 15000 | 2 |
| 1521 | Oak logs | `OAK_LOGS` | 1522 |  | 15000 | 12 |
| 1519 | Willow logs | `WILLOW_LOGS` | 1520 |  | 15000 | 24 |
| 6333 | Teak logs | `TEAK_LOGS` | 6334 |  | 13000 | 18 |
| 1517 | Maple logs | `MAPLE_LOGS` | 1518 |  | 15000 | 48 |
| 6332 | Mahogany logs | `MAHOGANY_LOGS` | 8836 |  | 11000 | 30 |
| 1515 | Yew logs | `YEW_LOGS` | 1516 |  | 12000 | 96 |
| 1513 | Magic logs | `MAGIC_LOGS` | 1514 |  | 12000 | 192 |
| 19669 | Redwood logs | `REDWOOD_LOGS` | 19670 |  | 12000 | 270 |

#### Ores & bars

| ID | Name | RuneLite const | Noted ID | Stackable | GE limit | High alch |
|---:|---|---|---:|:-:|---:|---:|
| 436 | Copper ore | `COPPER_ORE` | 437 |  | 13000 | 1 |
| 438 | Tin ore | `TIN_ORE` | 439 |  | 13000 | 1 |
| 440 | Iron ore | `IRON_ORE` | 441 |  | 13000 | 10 |
| 442 | Silver ore | `SILVER_ORE` | 443 |  | 13000 | 45 |
| 453 | Coal | `COAL` | 454 |  | 13000 | 27 |
| 444 | Gold ore | `GOLD_ORE` | 445 |  | 30000 | 90 |
| 447 | Mithril ore | `MITHRIL_ORE` | 448 |  | 13000 | 97 |
| 449 | Adamantite ore | `ADAMANTITE_ORE` | 450 |  | 4500 | 240 |
| 451 | Runite ore | `RUNITE_ORE` | 452 |  | 4500 | 1920 |
| 2349 | Bronze bar | `BRONZE_BAR` | 2350 |  | 10000 | 4 |
| 2351 | Iron bar | `IRON_BAR` | 2352 |  | 10000 | 16 |
| 2353 | Steel bar | `STEEL_BAR` | 2354 |  | 10000 | 60 |
| 2355 | Silver bar | `SILVER_BAR` | 2356 |  | 10000 | 90 |
| 2357 | Gold bar | `GOLD_BAR` | 2358 |  | 10000 | 180 |
| 2359 | Mithril bar | `MITHRIL_BAR` | 2360 |  | 10000 | 180 |
| 2361 | Adamantite bar | `ADAMANTITE_BAR` | 2362 |  | 10000 | 384 |
| 2363 | Runite bar | `RUNITE_BAR` | 2364 |  | 10000 | 3000 |

#### Raw fish

| ID | Name | RuneLite const | Noted ID | Stackable | GE limit | High alch |
|---:|---|---|---:|:-:|---:|---:|
| 317 | Raw shrimps | `RAW_SHRIMP` | 318 |  | 15000 | 3 |
| 321 | Raw anchovies | `RAW_ANCHOVIES` | 322 |  | 13000 | 9 |
| 335 | Raw trout | `RAW_TROUT` | 336 |  | 15000 | 6 |
| 331 | Raw salmon | `RAW_SALMON` | 332 |  | 15000 | 18 |
| 359 | Raw tuna | `RAW_TUNA` | 360 |  | 15000 | 24 |
| 377 | Raw lobster | `RAW_LOBSTER` | 378 |  | 15000 | 42 |
| 371 | Raw swordfish | `RAW_SWORDFISH` | 372 |  | 15000 | 48 |
| 7944 | Raw monkfish | `RAW_MONKFISH` | 7945 |  | 13000 | 138 |
| 383 | Raw shark | `RAW_SHARK` | 384 |  | 15000 | 102 |
| 13439 | Raw anglerfish | `RAW_ANGLERFISH` | 13440 |  | 15000 | 270 |
| 3142 | Raw karambwan | `TBWT_RAW_KARAMBWAN` | 3143 |  | 13000 | 120 |

#### Runes & essence

| ID | Name | RuneLite const | Noted ID | Stackable | GE limit | High alch |
|---:|---|---|---:|:-:|---:|---:|
| 556 | Air rune | `AIRRUNE` |  | y | 50000 | 2 |
| 555 | Water rune | `WATERRUNE` |  | y | 50000 | 2 |
| 557 | Earth rune | `EARTHRUNE` |  | y | 50000 | 2 |
| 554 | Fire rune | `FIRERUNE` |  | y | 50000 | 2 |
| 558 | Mind rune | `MINDRUNE` |  | y | 18000 | 1 |
| 559 | Body rune | `BODYRUNE` |  | y | 18000 | 1 |
| 564 | Cosmic rune | `COSMICRUNE` |  | y | 18000 | 30 |
| 562 | Chaos rune | `CHAOSRUNE` |  | y | 18000 | 54 |
| 561 | Nature rune | `NATURERUNE` |  | y | 18000 | 108 |
| 563 | Law rune | `LAWRUNE` |  | y | 18000 | 144 |
| 560 | Death rune | `DEATHRUNE` |  | y | 25000 | 108 |
| 9075 | Astral rune | `ASTRALRUNE` |  | y | 25000 | 30 |
| 565 | Blood rune | `BLOODRUNE` |  | y | 25000 | 240 |
| 566 | Soul rune | `SOULRUNE` |  | y | 25000 | 180 |
| 21880 | Wrath rune | `WRATHRUNE` |  | y | 25000 | 300 |
| 7936 | Pure essence | `BLANKRUNE_HIGH` | 7937 |  | 30000 | 2 |
| 1436 | Rune essence | `BLANKRUNE` | 1437 |  | 20000 | 2 |

#### Teleports & jewellery

| ID | Name | RuneLite const | Noted ID | Stackable | GE limit | High alch |
|---:|---|---|---:|:-:|---:|---:|
| 8007 | Varrock teleport | `POH_TABLET_VARROCKTELEPORT` |  | y | 15000 | 1 |
| 8008 | Lumbridge teleport | `POH_TABLET_LUMBRIDGETELEPORT` |  | y | 10000 | 1 |
| 8009 | Falador teleport | `POH_TABLET_FALADORTELEPORT` |  | y | 15000 | 1 |
| 8010 | Camelot teleport | `POH_TABLET_CAMELOTTELEPORT` |  | y | 15000 | 1 |
| 8011 | Ardougne teleport | `POH_TABLET_ARDOUGNETELEPORT` |  | y | 10000 | 1 |
| 8013 | Teleport to house | `POH_TABLET_TELEPORTTOHOUSE` |  | y | 15000 | 1 |
| 2552 | Ring of dueling(8) | `RING_OF_DUELING_8` | 2553 |  | 15000 | 765 |
| 3853 | Games necklace(8) | `NECKLACE_OF_MINIGAMES_8` | 3854 |  | 10000 | 630 |
| 11978 | Amulet of glory(6) | `AMULET_OF_GLORY_6` | 11979 |  | 10000 | 10575 |
| 1712 | Amulet of glory(4) | `AMULET_OF_GLORY_4` | 1713 |  | 10000 | 10575 |
| 11980 | Ring of wealth (5) | `RING_OF_WEALTH_5` | 11981 |  | 10000 | 10575 |
| 11968 | Skills necklace(6) | `JEWL_NECKLACE_OF_SKILLS_6` | 11969 |  | 10000 | 12120 |
| 11972 | Combat bracelet(6) | `JEWL_BRACELET_OF_COMBAT_6` | 11973 |  | 10000 | 12624 |
| 2570 | Ring of life | `RING_OF_LIFE` | 2571 |  | 10000 | 2115 |
| 4251 | Ectophial | `ECTOPHIAL` |  |  |  |  |

#### Bones & herbs

| ID | Name | RuneLite const | Noted ID | Stackable | GE limit | High alch |
|---:|---|---|---:|:-:|---:|---:|
| 526 | Bones | `BONES` | 527 |  | 3000 | 1 |
| 532 | Big bones | `BIG_BONES` | 533 |  | 3000 | 1 |
| 536 | Dragon bones | `DRAGON_BONES` | 537 |  | 7500 | 96 |
| 22124 | Superior dragon bones | `DRAGON_BONES_SUPERIOR` | 22125 |  | 7500 | 96 |
| 199 | Grimy guam leaf | `UNIDENTIFIED_GUAM` | 200 |  | 13000 | 7 |
| 207 | Grimy ranarr weed | `UNIDENTIFIED_RANARR` | 208 |  | 11000 | 18 |
| 3051 | Grimy snapdragon | `UNIDENTIFIED_SNAPDRAGON` | 3052 |  | 11000 | 12 |
| 219 | Grimy torstol | `UNIDENTIFIED_TORSTOL` | 220 |  | 11000 | 15 |
| 249 | Guam leaf | `GUAM_LEAF` | 250 |  | 13000 | 1 |
| 257 | Ranarr weed | `RANARR_WEED` | 258 |  | 11000 | 15 |
| 3000 | Snapdragon | `SNAPDRAGON` | 3001 |  | 11000 | 35 |
| 269 | Torstol | `TORSTOL` | 270 |  | 11000 | 45 |

#### Common gear

| ID | Name | RuneLite const | Noted ID | Stackable | GE limit | High alch |
|---:|---|---|---:|:-:|---:|---:|
| 1333 | Rune scimitar | `RUNE_SCIMITAR` | 1334 |  | 70 | 15360 |
| 4587 | Dragon scimitar | `DRAGON_SCIMITAR` | 4588 |  | 70 | 60000 |
| 4151 | Abyssal whip | `ABYSSAL_WHIP` | 4152 |  | 70 | 72000 |
| 1127 | Rune platebody | `RUNE_PLATEBODY` | 1128 |  | 70 | 39000 |
| 1163 | Rune full helm | `RUNE_FULL_HELM` | 1164 |  | 70 | 21120 |
| 1079 | Rune platelegs | `RUNE_PLATELEGS` | 1080 |  | 70 | 38400 |
| 1201 | Rune kiteshield | `RUNE_KITESHIELD` | 1202 |  | 70 | 32640 |
| 861 | Magic shortbow | `MAGIC_SHORTBOW` | 862 |  | 18000 | 960 |
| 892 | Rune arrow | `RUNE_ARROW` |  | y | 11000 | 240 |
| 2503 | Black d'hide body | `BLACK_DRAGONHIDE_BODY` | 2504 |  | 70 | 8088 |
| 2497 | Black d'hide chaps | `BLACK_DRAGONHIDE_CHAPS` | 2498 |  | 70 | 3732 |
| 23609 | Ava's accumulator | `BR_ANMA_50_REWARD` | 23610 |  |  |  |
| 6570 | Fire cape | `TZHAAR_CAPE_FIRE` |  |  |  |  |
| 23597 | Dragon defender | `BR_DRAGON_PARRYINGDAGGER` | 23598 |  |  |  |
| 27185 | Rune defender | `BR_RUNE_PARRYINGDAGGER` |  |  |  |  |
| 23593 | Barrows gloves | `BR_HUNDRED_GAUNTLETS_LEVEL_10` | 23594 |  |  |  |
| 11840 | Dragon boots | `DRAGON_BOOTS` | 11841 |  | 70 | 12000 |
| 6737 | Berserker ring | `BERZERKER_RING` | 6738 |  | 8 | 6000 |
| 6585 | Amulet of fury | `ENCHANTED_ONYX_AMULET` | 6586 |  | 8 | 121200 |
| 12926 | Toxic blowpipe | `TOXIC_BLOWPIPE_LOADED` |  |  |  |  |
| 11907 | Trident of the Seas | `TOTS_CHARGED` |  |  |  |  |
| 4675 | Ancient staff | `STAFF_OF_ZAROS` | 4676 |  | 70 | 60000 |
| 1381 | Staff of air | `STAFF_OF_AIR` | 1382 |  | 125 | 900 |
| 1383 | Staff of water | `STAFF_OF_WATER` | 1384 |  | 125 | 900 |
| 1385 | Staff of earth | `STAFF_OF_EARTH` | 1386 |  | 125 | 900 |
| 1387 | Staff of fire | `STAFF_OF_FIRE` | 1388 |  | 125 | 900 |

### Objects and NPCs

#### Bank booths, chests, GE booths (objects with op Bank)

54 ids match. Options are shown in slot order (slot 1 = first menu option).

| Name | Options (slot order) | IDs |
|---|---|---|
| Bank booth | Bank / Collect | 6084, 8139, 8140, 10355, 10517, 10583, 11338, 14367, 16642, 16700, 18491, 20325, 22819, 24101, 24347, 25808, 27718, 27719, 27720, 27721 … +14 more |
| Grand Exchange booth | Bank / Collect | 10060 |
| Bank booth | Bank / Collect / Deposit-box | 10357, 10584, 27254, 27260, 27263, 27265, 27267, 27292 |
| Bank Booth | Bank / Collect | 12798 |
| Bank chest | Bank / Collect | 29321, 53014, 53015, 57958, 58128, 58129, 58663, 62187 |
| Grand Exchange booth | Bank / Collect / Deposit-box | 30390 |
| Bank booth | Bank | 42837 |

#### Bank deposit boxes (objects with op Deposit)

18 ids match. Options are shown in slot order (slot 1 = first menu option).

| Name | Options (slot order) | IDs |
|---|---|---|
| Bank Deposit Box | Deposit | 10529, 29103, 29104, 29327, 30268, 32665, 34344, 36086, 39239, 50902, 57331, 57996 |
| Bank deposit box | Deposit | 25937, 26254, 29105, 29106, 31726, 41723 |

#### Trees (objects with op Chop down)

101 ids match. Options are shown in slot order (slot 1 = first menu option).

| Name | Options (slot order) | IDs |
|---|---|---|
| Tree | Chop down | 1276, 1277, 1278, 1279, 1280, 1330, 1331, 1332, 3879, 3881, 3882, 3883, 9730, 9731, 9732, 9733, 14308, 14309, 36672, 36674 … +22 more |
| Dead tree | Chop down | 1282, 1283, 1284, 1285, 1286, 1289, 1290, 1291, 1365, 1383, 1384, 5902, 5903, 5904, 42907, 51766, 62208, 62210, 62212, 62214 |
| Maple tree | Chop down | 4674, 10832, 36681, 40754 |
| Magic tree | Chop down / Inspect / Guide | 8409 |
| Maple tree | Chop down / Inspect / Guide | 8444 |
| Oak tree | Chop down / Inspect / Guide | 8467 |
| Willow tree | Chop down / Inspect / Guide | 8488 |
| Yew tree | Chop down / Inspect / Guide | 8513 |
| Mahogany tree | Chop down | 9034, 36688, 40760 |
| Teak tree | Chop down | 9036, 15062, 36686, 40758 |
| Oak tree | Chop down | 9734, 10820, 37969, 42395, 42831, 51772, 55913 |
| Tree | Chop down / Talk to | 10041 |
| Willow tree | Chop down | 10819, 10829, 10831, 10833 |
| Hollow tree | Chop down | 10821, 10830 |
| Yew tree | Chop down | 10822, 36683, 40756, 42391, 57790 |
| Magic tree | Chop down | 10834, 36685 |
| Mahogany tree | Chop down / Inspect / Guide | 30417 |
| Teak tree | Chop down / Inspect / Guide | 30445 |

#### Mining rocks (objects with op Mine)

68 ids match. Options are shown in slot order (slot 1 = first menu option).

| Name | Options (slot order) | IDs |
|---|---|---|
| Rocks | Mine | 2704, 4437, 4438, 10081, 11390, 11391, 11392, 18961, 26873, 26874, 28890, 29738, 33253, 36202, 37946, 41549, 41550, 48921, 51486, 51488 … +8 more |
| Coal rocks | Mine | 4676, 11366, 11367, 36204 |
| Copper rocks | Mine | 10079, 10943, 11161, 37944 |
| Tin rocks | Mine | 10080, 11360, 11361, 37945 |
| Clay rocks | Mine | 11362, 11363 |
| Iron rocks | Mine | 11364, 11365, 36203, 42833 |
| Silver rocks | Mine | 11368, 11369, 36205 |
| Gold rocks | Mine | 11370, 11371, 36206 |
| Mithril rocks | Mine | 11372, 11373, 36207 |
| Adamantite rocks | Mine | 11374, 11375, 36208 |
| Runite rocks | Mine | 11376, 11377, 36209 |
| Gem rocks | Mine | 11380, 11381 |
| Sandstone rocks | Mine | 11386 |
| Granite rocks | Mine | 11387 |
| Amethyst crystals | Mine | 11388, 11389 |
| Daeyalt Essence | Mine | 39095 |

#### Processing objects: furnace, anvil, range, altar, spinning wheel, loom

228 ids match. Options are shown in slot order (slot 1 = first menu option).

| Name | Options (slot order) | IDs |
|---|---|---|
| Cooking range | Cook | 114, 8750, 16641, 16893, 32739 |
| Altar | Pray-at | 409, 2640, 4008, 6552, 8749, 10639, 10640, 14860, 19145, 20377, 26257, 28455, 29941, 31624, 34837, 39642, 41650, 42163, 43089, 43097 … +6 more |
| Loom | Weave | 787, 8717, 30936, 58651 |
| Furnace | Smelt | 2030, 3294, 4304, 6189, 11010, 12100, 12809, 16469, 16657, 24009, 26300, 28565, 33504, 36555, 39241, 43895, 47927, 48171, 50698, 51509 … +4 more |
| Anvil | Smith | 2031, 2097, 4306, 6150, 22725, 28563, 31623, 32215, 39242, 40725, 44911, 51501, 56368, 58657, 61859 |
| Range | Inspect | 2859 |
| Furnace | Search | 2966 |
| Cooking range |  | 4172, 22154, 41423 |
| Spinning wheel | Spin | 4309, 8748, 14889, 20365, 21304, 25824, 26143, 55330, 56964, 58649 |
| Furnace |  | 6190, 11009, 18525, 18526, 21879, 22721, 30157, 40949, 42824, 43891 |
| Range | Cook | 7183, 7184, 9682, 9736, 12102, 12611, 21792, 22713, 22714, 25730, 26181, 27516, 27517, 27724, 31631, 35980, 36077, 37728, 39391, 39458 … +6 more |
| Altar | Pray-at / Standard spellbook / Ancient spellbook / Lunar spellbook / Arceuus spellbook | 7814 |
| Furnace | Use | 10082, 37947 |
| Altar | Pray / Remove | 13179, 13180, 13181, 13182, 13183, 13184, 13185, 13186, 13187, 13188, 13189, 13190, 13191, 13192, 13193, 13194, 13195, 13196, 13197, 13198 … +8 more |

#### Agility / misc objects: ladders, stairs, doors, gates (first 20 of each)

2473 ids match. Options are shown in slot order (slot 1 = first menu option).

| Name | Options (slot order) | IDs |
|---|---|---|
| Door | Open | 3, 4, 22, 24, 59, 81, 82, 92, 93, 99, 102, 131, 136, 532, 553 … +423 more |
| Ladder | Climb-down | 10, 133, 287, 2147, 2269, 2408, 2590, 2605, 2797, 2812, 2871, 3617, 4158, 4189, 4644 … +162 more |
| Ladder | Climb-up | 11, 60, 101, 132, 195, 2148, 2268, 2405, 2410, 2517, 2592, 2641, 2796, 2833, 2872 … +196 more |
| Gate | Open | 37, 38, 47, 48, 52, 53, 89, 90, 94, 95, 166, 167, 190, 883, 1558 … +165 more |
| Gate | Go-through | 39 |
| Gate |  | 49, 50, 1570, 1739, 1740, 4313, 9142, 11332, 11333, 12818, 16492, 16493, 39513, 41601, 41863 … +40 more |
| Stairs | Climb-up | 54, 56, 96, 2617, 2853, 4622, 4623, 4626, 4627, 4756, 6085, 6087, 6089, 6842, 9138 … +75 more |
| Stairs | Climb-down | 55, 57, 98, 2187, 2190, 2616, 4620, 4621, 4624, 4625, 4755, 6086, 6088, 6090, 6841 … +87 more |
| Large door | Open / Knock-at | 71, 72 |
| Large door | Open | 73, 74, 134, 135, 1511, 1513, 1517, 1518, 1521, 1524, 2416, 3489, 3490, 3743, 4629 … +42 more |
| Trapdoor | Open | 100, 1579, 1580, 2446, 3432, 4174, 4471, 4472, 4712, 4879, 4888, 5055, 5799, 5800, 5801 … +25 more |
| Trapdoor |  | 105, 106, 2445, 12777, 12778, 12872, 20136, 20137, 20138, 20139, 20140, 20141, 20142, 20143, 20144 … +12 more |

#### Fishing spots (NPCs)

170 ids match. Options are shown in slot order (slot 1 = first menu option).

| Name | Options (slot order) | IDs |
|---|---|---|
| Rod Fishing spot | Lure / Bait | 394, 1506, 1507, 1508, 1509, 1512, 1513, 1515, 1516, 1526, 1527, 1529, 1531, 3417, 3418, 7463, 7464, 7468, 8524, 12774 … +9 more |
| Fishing spot | Fish | 635, 4712, 4713, 4714, 16341 |
| Fishing spot | Small Net / Bait | 1497, 1498, 1514, 1517, 1518, 1521, 1523, 1524, 1525, 1528, 1532, 1544, 3913, 7155, 7459, 7462, 7467, 7469, 7947, 10653 … +6 more |
| Fishing spot | Net / Bait | 1499, 1500, 1530, 10513 |
| Fishing spot | Cage / Harpoon | 1510, 1519, 1522, 1533, 2146, 3657, 3914, 5820, 7199, 7460, 7465, 7470, 7946, 9173, 9174, 10515, 10635, 12777, 14039, 15070 … +8 more |
| Fishing spot | Net / Harpoon | 1511, 4316, 5821, 8525, 8526, 8527, 10514, 16343 |
| Fishing spot | Big Net / Harpoon | 1520, 1534, 3419, 3915, 4476, 4477, 5233, 5234, 7200, 7461, 7466, 9171, 9172, 12775, 12776, 14037, 14523, 15067, 15068, 15069 … +6 more |
| Fishing spot | Cage | 1535, 1536 |
| Fishing spot | Use-rod | 1542, 7323 |
| Fishing spot | Bait | 2653, 2654, 2655, 4079, 4080, 4081, 4082, 4928, 6488, 6784, 15384, 16337, 16342 |
| Fishing spot | Net | 3317, 4710, 4711, 9478, 13912 |
| Fishing spot | Small Net | 6731, 7730, 7731, 7732, 7733 |
| Rod Fishing spot | Bait | 6825, 7676 |
| Fishing spot | Catch | 8523 |
| Fishing spot | Harpoon | 10565, 10568, 10569, 15074, 15078, 15081, 15085 |
| Fishing spot | Small Net / Big Net | 10686, 10687, 10688 |
| Fishing spot | Cast | 12267, 13329 |
| Fishing spot | Small net / Bait | 16338 |
| Fishing spot | Big net / Harpoon | 16339 |

#### Bankers (NPCs)

106 ids match. Options are shown in slot order (slot 1 = first menu option).

| Name | Options (slot order) | IDs |
|---|---|---|
| Banker | Talk-to / Bank / Collect | 766, 1479, 1480, 1613, 1618, 1633, 1634, 2117, 2118, 2119, 2292, 2293, 2368, 2369, 2633, 2897, 2898, 3089, 3090, 3091 … +76 more |
| Ghost banker | Talk-to / Bank / Collect | 3003 |
| Emerald Benedict | Talk-to / Bank / Collect | 3194 |
| Banker tutor | Talk-to / Bank / Collect | 3227 |
| Banker | Talk-to | 3318, 9484 |
| Fadli | Talk-to / Bank / Collect / Buy | 3340 |
| Sirsal Banker | Talk-to / Bank / Collect | 3843 |
| Gnome banker | Talk-to / Bank / Collect | 6084 |
| Banker |  | 8666, 16525 |

#### Common training / thieving NPCs

994 ids match. Options are shown in slot order (slot 1 = first menu option).

| Name | Options (slot order) | IDs |
|---|---|---|
| Nechryael | Attack | 8, 11 |
| Zombie | Attack | 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37 … +72 more |
| Skeleton | Attack | 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81 … +53 more |
| Rock Crab | Attack | 100, 102 |
| Hellhound | Attack | 104, 105, 135, 3133, 7256, 7877 |
| Ogre | Attack | 136, 1153, 2095, 2096, 2233 |
| Black demon | Attack | 240, 1432, 2048, 2049, 2050, 2051, 2052, 5874, 5875, 5876, 5877, 6357 … +6 more |
| Green dragon | Attack | 260, 261, 262, 263, 264, 7868, 7869, 7870, 8082, 13010, 13488 |
| Blue dragon | Attack | 265, 266, 267, 268, 269, 5878, 5879, 5880, 5881, 5882, 8083, 14103 … +1 more |
| Man | Talk-to | 385, 4268, 4269, 4270, 4271, 4272, 6776, 7281, 7919, 7920, 9658, 13679 |
| Guard | Attack / Pickpocket | 397, 398, 399, 400, 1546, 1547, 1548, 1549, 1550, 3010, 3011, 3254 … +74 more |
| Kurask | Attack | 410, 411 |
| Gargoyle | Attack | 412, 413, 1543 |
| Abyssal demon | Attack | 415, 416, 7241, 11239 |
| Dust devil | Attack | 423, 7249, 11238 |
| Bloodveld | Attack | 484, 485, 486, 487, 3138 |
| Goblin | Talk-to / Attack | 655, 656, 657, 658, 659, 660, 661, 662, 663, 664, 665, 666 … +5 more |
| Goblin | Attack | 674, 2245, 2246, 2247, 2248, 2249, 2484, 2485, 2486, 2487, 2488, 2489 … +44 more |
| Bandit | Talk-to / Attack / Pickpocket | 690, 695, 734, 736 |
| Bandit | Talk-to | 691, 692, 693, 694 |
| Bandit | Talk-to / Attack / Pickpocket / Lure / Knock-Out | 735, 737 |
| Zombie | Talk-to / Attack | 880 |
| Guard | Attack | 995, 3361, 5141, 6575, 6576, 6579, 6580, 6581, 6582, 6583, 6699, 6700 … +24 more |
| Guard |  | 998, 999, 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009 … +65 more |
| Rat |  | 1020, 1021, 1022, 4593, 4610, 4611, 4612, 4613, 4614, 4615, 4616, 4617 … +3 more |
| Bandit | Attack | 1026, 6605, 11063, 11064, 11065, 13283, 13284, 13285, 13286, 13287, 13288, 13289 … +1 more |
| Cave horror | Attack | 1047, 1048, 1049, 1050, 1051 |
| Guard | Talk-to | 1099, 1100, 1111, 1112, 1113, 1147, 1371, 1372, 1551, 1552, 1949, 1950 … +39 more |
| Man | Talk-to / Attack | 1118 |
| Woman | Talk-to / Attack | 1119, 1130, 1131, 1139, 1140, 1141, 1142 |
| Man |  | 1138, 8858, 8859, 8860, 8861, 8862, 9657, 10672, 10673, 10945, 11032 |
| Chicken | Attack | 1173, 1174, 2804, 2805, 2806, 3316, 3661, 3662, 9488, 10494, 10495, 10496 … +3 more |
| Zombie |  | 1784, 5507, 5583 |
| Skeleton |  | 1785, 3584, 8139, 8140 |
| Guard | Talk-to / Watch-shouting | 1947, 1948 |
| Lesser demon | Attack | 2005, 2006, 2007, 2008, 2018, 3982, 7247, 7248, 7656, 7657, 7664, 7865 … +7 more |
| Greater demon | Attack | 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 7244, 7245, 7246, 7871 … +3 more |
| Moss giant | Attack | 2090, 2091, 2092, 2093, 3851, 3852, 7262, 12844, 12845, 12846, 12847, 14422 |
| Hill Giant | Attack | 2098, 2099, 2100, 2101, 2102, 2103, 7261, 10374, 10375, 10376, 12848, 12849 … +4 more |
| Guard | Talk-to / Attack | 2316, 2317, 4099, 4100, 4660, 4661, 4662, 4663, 4664, 4665, 4666, 4667 … +8 more |
| Rat | Attack | 2492, 2513, 2854, 2855, 4594, 13624 |
| Flesh Crawler | Attack | 2498, 2499, 2500 |
| Giant rat | Attack | 2510, 2511, 2512, 2856, 2857, 2858, 2859, 2860, 2861, 2862, 2863, 2864 … +5 more |
| Cow | Attack | 2790, 2791, 2793, 2795, 6401 |
| Cow calf | Attack | 2792, 2794, 2801 |
| Man | Talk-to / Attack / Pickpocket | 3014, 3106, 3107, 3108, 3109, 3110, 3264, 3265, 3298, 3652, 6815, 6818 … +6 more |
| Woman | Talk-to / Attack / Pickpocket | 3015, 3111, 3112, 3113, 3268, 3299, 6990, 6991, 6992, 10728, 11053, 11054 … +1 more |
| Farmer | Attack / Pickpocket | 3114, 3243, 3244, 11918, 11919, 11920, 11921 |
| Farmer |  | 3245, 3250, 3251, 3672, 6959, 6960, 6961 |
| Man | Attack / Pickpocket | 3261 |
