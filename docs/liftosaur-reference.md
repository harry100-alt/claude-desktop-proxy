# Liftosaur reference

Reference for answering "what can the Liftosaur app do and how do I do it". Liftosaur (by astashov, open source at github.com/astashov/liftosaur) runs on iOS, Android and the web (app plus a Web Editor at liftosaur.com). Programs are written in a text syntax called Liftoscript; the app then runs the program, tracks workouts and applies progression automatically.

Sources: the official Liftoscript docs (`liftosaur.com/docs/liftoscript`) and the app CHANGELOG (142 entries, 2022-02-19 to 2026-09-09). Where the two disagree the docs are preferred and the disagreement is noted. Anything not in those two sources is marked "not stated in sources". Equipment display names were taken from `src/models/exercise.ts` in the repo.

Notes specific to this user's own program (assisted chin-up handling, exercise-name table, the parser-based validator) live in [liftosaur-guide.md](liftosaur-guide.md) and are not repeated here.

Support: info@liftosaur.com, Discord, r/liftosaur.

---

## App features by screen

Navigation (since 2025-02-02): footer buttons are **Home** (history/calendar), **Program**, a **Dumbbell** button that starts a workout (tap again to return to an ongoing one), and **Me** (formerly Settings; Measurements moved under it). Each footer button resets the navigation stack. New users (fewer than 4 workouts) get "tour" modals on the workout screen, program editor and program exercise editor; the `?` icon top-right reopens them.

### Workout screen

Redesigned 2025-03-30: one tab per exercise at the top with per-exercise progress; each row is a set with reps and weight input fields prefilled from the program. Under each exercise there are graphs and history. Colour coding: green = success, red = failed, yellow = in rep range.

| Feature | How it works |
|---|---|
| Target column / e1RM column | The second column header cycles (swap icon) through variants; the last is the estimated 1RM of the set (semi-transparent until the set is completed). Uses completed reps/weight/RPE when available, else target values. |
| Complete a set | Tap the checkmark. Change the fields first only if you deviated from the program. |
| Edit a set | Swipe the set to edit the target or delete it. Long-press a set (about 1 second) opens the edit-set modal for this workout only. |
| Edit icon (pencil) | Opens the Liftoeditor in a bottom sheet with the current program day (since 2026-08-17). Earlier: an "Edit" modal listing every weight the exercise uses in the program with quick adjustment buttons and a Rep Max Calculator (2024-04-13), plus "Only in this workout" editing. |
| Swap exercise | Swap icon on the exercise. Replace for this workout only or for the whole program. See "Swapping and substitutes". |
| Add exercises | Exercise picker lets you add ad-hoc exercises (you set the sets yourself) or program exercises from the current program, used or unused, which come with their sets and run their progression on completion. Multi-select supported. Starred exercises, filters by muscle/type, sort by name or similar muscles (this replaced the old Substitute tab). Hidden equipment hides exercises by default; a checkmark in the filter section shows them again. |
| Supersets | Exercises in one `superset:` group alternate automatically: finish a set of A, the app switches to B, then C, then back to A. Shown as a coloured line under thumbnails and in the card. Supersets can be set in a program or in the workout. |
| Rest timer | Floating timer visible on every screen (tap it to return to the workout); tap to expand and add or reduce time or cancel. Adjustable also from Live Activity / Live Updates and Apple Watch. Per-exercise timers can be expressions using workout variables and `setIndex`. |
| Set timer and countdown | Time-based sets (`60s|30s`) show a set-timer modal. A countdown (Me -> Timers) starts near the end of the rest; the countdown is subtracted from the rest (with `30s|60s` and a 5s countdown you rest 55s then count down 5s). `30s|0s` disables the countdown for that exercise. Unilateral exercises run two set timers (left, then right) with a countdown between. |
| `auto` sets | Workout auto-advances to the next set when the rest ends (circuits, EMOM, Tabata). |
| Quick-add sets | Write `1+x5` in the program (changelog syntax, not in the docs) to get an "add another set" button after the last set; the modal asks reps and weight and marks the set complete. Since 2024-05-06 it is per set variation, so enable it on every week/day where you want it. |
| AMRAP | `+` after reps; the app asks how many reps you did. |
| RPE logging | `@8+` asks for your actual RPE after the set. Required RPE shows grey `@8`, logged RPE orange `@9`. Rich inputs step RPE by 0.5, reps by 1, weight by the next possible plate load. |
| Ask weight | `+` after the weight, or `?+`, asks what weight you actually used. |
| Notes | Per-workout notes: a note on the whole workout and on each exercise during the workout (2023-03-01), shown on History, Exercise Stats and graphs; Exercise Stats history can be filtered to records with notes. Persistent notes, all shown on the workout screen: program exercise descriptions (`//` in the program), exercise notes (Exercise Stats screen, e.g. form cues) and equipment notes (Available Equipment screen, e.g. bench angle). The previous workout's exercise note is shown for two months. |
| Pause | Pause button in the header stops the total workout timer; unpause the same way or by logging any set. |
| PRs | PR sets are highlighted in history and on Exercise Stats. |
| Plate calculator and rounding | Weights are rounded to attached equipment only at the end, during the workout. The original weight shows crossed out next to the rounded one; since 2026-07-17 the rounded weight is underlined and tapping it explains the calculation (1RM percentage, kg/lb conversion, bar weight, plates per side or closest fixed dumbbell, and whether "Is Assisting" is on, the usual cause of weights dropping to 0). |
| Equipment and 1RM links | On the workout screen, "Equipment" and (if used) "1RM" links open modals; plates can be defined right there. Tapping the exercise name or image opens Exercise Stats (graph with e1RM line using the Epley formula, PRs, history, 1RM, equipment, notes, unilateral flag, muscle overrides, "Two weights (count both)"); you can switch exercises on that screen. Graphs pinch-zoom, two-finger pan, double-tap to reset, and show vertical lines where the program changed. |
| Unilateral exercises | Reps per side; on by default for built-in unilateral exercises, override with "Is Unilateral" on Exercise Stats. Volume sums both sides, e1RM averages both sides. |
| Two-dumbbell volume | Since 2026-07-13 volume counts both dumbbells for paired-dumbbell exercises; toggle off per exercise with "Two weights (count both)". |
| Progress preview / Suppress | After all sets of an exercise, the progress changes are shown; tap "Suppress" to stop the progress logic running for that exercise this workout. `print()` output also appears here. |
| Live Activity / Live Updates | iOS lock screen and Dynamic Island (2025-11-23), Android lock screen and a chip near the clock (2025-11-25): timer, next exercise, set, reps, weights, plates; adjust rest timer or complete a set from there. Premium. |
| Ongoing workout reminder | Push notification if a workout is left open; delay set in Settings/Me -> Timers, default 15 minutes. |
| Ongoing workout sync | Since 2026-01-20 the in-progress workout syncs to the server, so you can continue it in the web app. |
| Finish | Congratulations screen: share image, "Text" export, create a program day from an ad-hoc workout, sync to Apple/Google Health (now automatic on finish). |
| No-program workouts | Ad-hoc workouts are possible without choosing a program; the picker opens automatically. A program day can be created from an ad-hoc workout afterwards. |

### Program screen

Redesigned 2025-06-07 with tabs for **Editing** and **Playground**, and four mode icons. Since 2026-08-09 the author is "embracing Liftoscript": the Edit Program Exercise screen is a bottom sheet with a native code editor that has a structured mode (tap values, use action pills, swipe between elements, per-element hints) and a freeform mode (double-tap text); freeform mode got autocompletion of exercise names, script variables and template names on 2026-09-01.

| Mode / feature | Details |
|---|---|
| Grid view (reorder icon) | Since 2026-08-28: calendar-like grid of the whole program. Repeat-range exercises appear as one strip across weeks; drag the strip end to extend the range. Long-tap-drag exercises within and across days, drag weeks to reorder; dragging a day drags it across all weeks. Pinch-zoom. Selecting an exercise highlights the template it reuses. Add several exercises from one picker. |
| Per-day UI mode | Form-based editing (default on phone since 2024-05-25). Originally could not define progress, update, descriptions or tags; since 2025-06-07 "everything you could do in full text mode is pretty much possible via UI". The author has said this mode may eventually be removed in favour of the grid. |
| Per-day text mode | Liftoscript for one day. Repeated exercises (`Name[1-4]`) are listed under the text input on repeated days but are not editable there. |
| Full text mode | The whole program as one text blob using `# Week` / `## Day` headers. The main mode in the Web Editor. Web Editor also has Find & Replace (regex) and multi-cursor. |
| Edit Program Exercise sheet | Edit sets, warmups, descriptions, progress and update logic; preview icon shows the exercise with all reuses filled in; tells you when progress is defined on another week/day and lets you jump there. Exercise variations can be added/removed/reordered/switched from its 3-dot menu. |
| Preview tab | Shows the whole program; since 2025-09-05 changes to 1RM, equipment and state variables made there are persisted (it used to be ephemeral). Tapping name or image opens Exercise Stats. |
| Playground | Ephemeral: try finishing sets to see how progress scripts behave without changing the program. Supports quick-add sets and long-press set editing. |
| Week stats | Sets per muscle group, hypertrophy/strength split for the program week. Muscle groups and set ranges are customisable in the "Planner Settings" modal and Me -> Muscle Groups. |
| Version history | Every save (web or app) creates a snapshot; up to 100 kept. "Versions" link in the Web Editor opens the list; any snapshot can be restored. |
| Saving | The Web Editor has an explicit Save button (no autosave since 2024-07-31). The app has pull-to-refresh and syncs on returning to foreground. |
| Share links | Public links look like `liftosaur.com/p/<id>`; links are immutable (any change produces a new link) and anyone can import them on the program selection screen. Since 2023-10-16 you must generate a new link to "save" changes to a linked program (URLs are limited to about 10K characters). Custom equipment is exported into the link. Importing a link with different units offers conversion. |
| Program images | Generate a shareable image of the program (choose columns/days). Picture icon in the Web Editor or the kebab menu on the Program screen. |
| AI prompt generator | `liftosaur.com/ai/prompt` ("AI Helper" in the site nav) builds a large prompt from the docs and examples for ChatGPT/Claude/Gemini; can also take a URL or Google Sheet. Paste errors back to the AI to fix them. |
| Choose Program | Filters by frequency, workout duration, experience; built-in and own programs in separate tabs; the site's `/programs` page has full descriptions and Liftoscript for every built-in program. New programs are converted to your unit setting on clone. |
| Replace exercise across program | UI for replacing an exercise in the whole program (in addition to Find & Replace). |

### History / Calendar (Home)

- Infinite scroll of workouts with the ongoing workout at the top (since 2025-04-09). A week calendar at the top swipes between weeks; tap it for a month calendar; tapping a workout there scrolls to it. Week starts Monday or Sunday (Settings).
- Current week description from the program is shown on the history screen.
- **Week Insights** card after each week: total sets, hypertrophy/strength split, sets per muscle group for the actual week (Premium).
- Open any past workout: share menu offers copy as text, share as image (Instagram; TikTok pending), "Sync to Apple/Google Health", and creating a program day from it. Set display is vertical with PR highlighting.
- Editing past workouts: not described explicitly in the sources beyond opening them; long-press set editing is documented for the current workout.
- **Export as text**: compact human-readable format from the finish screen ("Text" button) or a past workout's share menu.
- **Export as CSV**: not described explicitly; the import flow accepts "Liftosaur CSV", which implies an export exists, but the sources do not document it.
- **Full data export/import** (2022-02-19): export all data (history, settings, etc.) to a file and import it later; programs can also be exported and imported individually as files (backup or sharing). Where these live in the current Me screen is not stated in newer entries.
- **Import**: Me -> "Import history from other apps": Hevy CSV, and Liftosaur CSV. Since 2026-06-08 a preview screen shows the imported history, warnings (suspicious weights/reps, duplicates, odd dates), summary stats and custom exercises to be created; Me -> Recent Imports lists the last 5 imports with an undo for each (removes imported workouts and custom exercises created by that import unless used elsewhere). Strong import: not stated in sources.

### Me / Settings

| Item | Details |
|---|---|
| Units | kg or lb; new users are asked before choosing a program. Cloned programs convert to the chosen unit. Equipment can override the unit per equipment (e.g. a kg-plated machine in a lb gym); history shows that unit, graphs use the default unit. |
| Equipment (Available Equipment) | Since 2024-06-12 equipment is separate from the exercise: it defines only bar/plates/fixed weights and is optionally attached to an exercise for rounding and the plate calculator. Built-in kinds include Olympic Barbell, Standard Barbell, Fixed Dumbbells, Loaded Dumbbells. Custom equipment: name, fixed/non-fixed, plates, "Similar To" (picks the exercise image), custom unit, equipment notes. Built-in equipment can be hidden. Since 2025-08-13 exercises that never had equipment set get the matching equipment automatically (e.g. `Bench Press, Barbell` gets Barbell). |
| "Bodyweight for Bar" and "Is assisting?" | Per equipment. Bodyweight for Bar uses your bodyweight as the bar weight in the plate calculator. Is assisting makes plates reduce the total (assisted pull-up machines); the calculator shows plates to add to reduce the weight. Turning "Is assisting" on by accident is the usual reason weights show 0. Both apply to every exercise using that equipment. |
| Gyms | Create more gyms, each with its own equipment; assign equipment per exercise per gym; switch the current gym in Settings. Exercises without equipment in a gym use default rounding. |
| Exercises screen | Lists exercises in the current program and previously done ones, with filters; shows 1RM and attached equipment or default rounding per exercise. Opens Exercise Stats. |
| Exercise Stats | 1RM (tied to the exercise, shared across programs; readable as `rm1`), equipment per gym, default rounding, "Is Unilateral", "Two weights (count both)", "Override Muscles" (target = multiplier 1, synergist < 1), exercise notes, graphs (volume or max weight). |
| Custom exercises | Name only (no equipment since 2024-06-12). Muscles grouped by muscle group with images and an AI "Autofill" button, exercise type (pull/push/upper/lower/core/legs), notes, image uploaded from the phone (requires sign-up) or picked from the Image Library, or clone from an existing exercise. Image URLs can no longer be entered (existing ones keep working). `|` and `!` are not allowed in names (replaced by `-`). |
| Muscle Groups | Hide built-in groups and create new ones (e.g. Front/Side/Rear delts). |
| Timers | Default rest timer, superset rest timer (takes precedence over default; per-set timers beat both), countdown for time-based sets, ongoing-workout reminder delay. |
| Sounds | Volume slider and vibration toggle for the rest timer end (native apps). |
| Always On Display | Keeps the screen on during workouts (native apps). |
| Appearance | Dark mode: follows the system theme by default, override in Me -> Appearance. Text size slider (Aa) scales the whole app including icons and thumbnails, starting from the device font size. |
| Apple Health / Google Health Connect | Me -> Apple Health (or Google Health Connect). See "Integrations". |
| Apple Watch | Premium, iPhone, native iOS app 6.31 or later. Complete sets, see rest timers and upcoming exercises, set-timer modal; cannot modify the workout. Complications added 2026-06-17. |
| Recent Imports | Undo any of the last 5 history imports. |
| Rep Max Calculator | Near weight inputs: enter known weight, reps, RPE and target reps/RPE. Use RPE 10 for a true rep max. |

### Measurements

- Bodyweight, body fat, and body-part measurements (neck, chest, waist, biceps, thighs and the rest). Custom measurements: not stated in sources beyond the listed parts.
- Graphs with an optional moving-average line (useful for bodyweight and body fat). The `bodyweight` script variable returns the latest bodyweight moving average.
- Sleep & Nutrition screen (Me tab, since 2026-07-19): sleep duration, dietary calories and protein imported read-only from Apple Health / Google Health Connect on app open, aggregated daily, with trend graph and history; entries can be hidden and unhidden. Exposed via API/MCP as the `health` measurements category. Requires a native app update.
- Bodyweight/body fat (and, Apple Health only, waist) sync both ways with Apple Health / Google Health Connect.

### Account

- Sign in with Google, Apple or email. Account name is shown at Me -> Account (include it in support emails). Multiple local accounts can be created and switched between (2022-12-26).
- Subscription status and management on the Account screen (since 2026-06-13).
- Delete account: Settings/Me -> Account, wipes all data from Liftosaur servers.
- Offline mode: works without internet (built-in programs cannot be loaded and nothing syncs); syncs when online if logged in.
- Sync: rewritten 2024-07-31 (only changed data sent) and 2025-07-06 (better conflict resolution). Pull-to-refresh forces a fetch; foreground return also syncs.

---

## What is free vs Premium

The sources only call out the following as Premium:

| Feature | Source |
|---|---|
| REST API and MCP server | changelog 2026-03-08: "Both require a premium subscription." |
| Apple Watch app (and its complications) | changelog 2026-01-29: "If you have Premium and iPhone" |
| Live Activity / Dynamic Island (iOS) | changelog 2025-11-23 |
| Live Updates (Android) | changelog 2025-11-25 |
| Week Insights on the history screen | changelog 2024-11-30: "Premium-only feature" |

Pricing (2024-08-25): localized by country GDP per capita; US $5 monthly / $40 yearly / $80 lifetime (Turkey $2.5/$20/$40, Philippines $1/$8/$16). Everything else in this document is not stated as Premium in the sources; whether it is free is therefore not stated in sources. The user in the working guide is on the free tier and edits programs in the Web Editor.

---

## Liftoscript syntax reference

### Program structure

```
# Week 1
## Day 1
Squat / 5x5 / progress: lp(5lb)

## Day 2
Squat / 3x8

# Week 2
## Day 1
Squat / 5x4
```

- `# Name` starts a week, `## Name` a day (full text mode only; per-day text mode has no headers).
- Week and day descriptions are `//` comment lines directly above the `#`/`##` line; Markdown is allowed; day descriptions are reused by following days until overwritten (same rule as exercise descriptions). Week description shows on the history screen, day description on the workout screen.

```
// This is a description for week 1
// * Do this
// * Then do that
# Week 1

// This is a description for day 1
// **Very important to do this:**
## Day 1

Squat / 5x5 / progress: lp(5lb)
```

- When multi-week, finishing a workout moves to the next day of the week, then the first day of the next week.

### Exercise line

One exercise per line. Sections are separated by `/`. The exercise name comes first; the docs say the remaining sections can be in **any order**.

```
Bench Press / 3x5 80%
Incline Bench Press / 3x8-12 @8 / 90s
Skullcrusher / 3x15 @8
Lateral Raise / 3x15 @8
```

Section kinds:

| Section | Example | Notes |
|---|---|---|
| Sets | `3x8`, `1x5, 1x3, 1x1, 5x5` | Comma-separated set groups. A section with sets x reps is a set variation (see below). |
| Shared properties | `/ 20s 60%` | A section with only weight / percentage / RPE / timer applies to all sets, so you do not repeat it per group. |
| `warmup:` | `warmup: 1x5 45lb, 1x5 135lb, 1x3 80%` | |
| `progress:` | `progress: lp(5lb)` | |
| `update:` | `update: custom() {~ ... ~}` | |
| `superset:` | `superset: A` | |
| `used: none` | | Template, not run. |
| `id: tags(...)` | `id: tags(1, 100)` | |

Sets are optional since 2025-04-21: `Squat` alone is valid, as is a template with only warmup/progress.

Split long lines with a trailing `\`:

```
Squat / 1x5 @8 75% 120s, 3x8 @9 60s \
  / warmup: 1x5, 1x3, 1x1 \
  / progress: lp(5lb)
```

### Sets, reps, AMRAP, labels

```
Bench Press / 3x8
Bench Press / 3x8-12
Bench Press / 1x5, 1x3, 1x1, 5x5
Bench Press / 4x5, 1x5+ @8+
Squat / 4x5 (Main), 1x5+ (AMRAP) / progress: lp(5lb)
```

- `3x8-12` is a rep range (yellow if reps land inside the range, green at the top).
- `+` after reps = AMRAP (the app asks for reps done).
- `(Label)` after a set group = set label, 8 characters max.
- `1+x5` = quick-add sets enabled for that set variation (changelog only; not in the docs).

### Weights and RPE

```
Bench Press / 3x12 @8
Bench Press / 3x12 80%
Bench Press / 3x12 60kg
Bench Press / 1x5 @8, 1x3 @9, 1x1 @10, 5x5 50%
Bench Press / 3x8 / 100lb+
Bench Press / 1x6 70%+, 5x5 50%
Bench Press / 3x8 @8 ?+
Pull Up / 3x8 -40lb / progress: lp(5lb)
```

- No weight and no RPE: the weight field is empty and you enter it when completing the set (breaking change 2025-04-21; before that a 1RM percentage was inferred from reps/RPE).
- `@N` RPE alone: weight is computed from the RPE table as a percentage of 1RM (e.g. 12 reps @8 is 60% of 1RM; @10 for 12 reps is 65%).
- `N%` = percentage of the exercise's 1RM (`rm1`, set on Exercise Stats). `Nkg` / `Nlb` = absolute weight. Negative weights are allowed (e.g. `-5lb`, `-40lb`).
- `+` after a weight or percentage asks for the weight actually used. `?+` asks without prescribing a weight (weight inferred from 1RM/reps/RPE).
- `@8+` asks for the actual RPE after the set. Rep-range table: 1 to 24 reps, RPE 1 to 10.

### Timers

```
Bench Press / 1x12 20s 60%, 5x5 20s 60%
Plank / 3x1 60s|30s
Plank / 3x1 60s|?
Plank / 2x1 30s|60s, 1x1 30s+|60s
Power Clean / 5x5 135lb 60s|0s auto
Squat, Bodyweight / 8x1+ 20s|10s auto
```

- Bare `90s` = rest timer for those sets (overrides the default and superset default timers).
- `setTimer|restTimer` = active set timer then rest. `?` on the rest side keeps the global default rest. `+` after the set timer counts up past the target until you stop it and records the elapsed time.
- `auto` = auto-advance to the next set when the rest ends (EMOM, Tabata, circuits).
- Set timers are readable/writable in scripts as `setTime[n]` and `completedSetTime[n]` (docs; e.g. `setTime[1] += 5`).

### Warmups

```
Squat / 5x5 / warmup: 1x5 45lb, 1x5 135lb, 1x3 80%
Squat / 5x5 / warmup: none
```

Default warmups are added if you write nothing. Warmup percentages are of the **first working set's weight**, not 1RM. No timers or RPE in warmups.

### Equipment in the exercise name

```
Bench Press, Dumbbell / 3x5
```

Without a suffix the exercise's default equipment is used (e.g. Bench Press = Barbell). `Bench Press, Barbell` and `Bench Press, Dumbbell` are **different exercises** with separate history, 1RM and progression. Built-in equipment display names (from `equipmentName` in `src/models/exercise.ts`; the docs do not list them):

| Name after the comma | Internal id |
|---|---|
| `Barbell` | barbell |
| `Cable` | cable |
| `Dumbbell` | dumbbell |
| `Smith Machine` | smith |
| `Band` | band |
| `Kettlebell` | kettlebell |
| `Bodyweight` | bodyweight |
| `Leverage Machine` | leverageMachine |
| `Medicine Ball` | medicineball |
| `EZ Bar` | ezbar |
| `Trap Bar` | trapbar |

Whether a custom equipment name can be used after the comma is not stated in sources. Exercise names must match the built-in library or a custom exercise exactly (except `used: none` templates).

### Labels and exercise identity

```
main: Squat / 5x5 / progress: lp(5lb)
accessory: Squat / 3x8 / progress: dp(5lb, 8, 12)
lowrep: Bench Press / 3x3 / progress: dp(5lb, 3, 6)
highrep: Bench Press / 3x8 / progress: dp(5lb, 8, 12)
```

A label is a word before the name followed by `:`. Labelled and unlabelled (or differently labelled) instances are treated as **different exercises**, so each can have its own progression and state. Without labels, one exercise may have only one progression across the whole program; a second, different one is an error. For exercise variations (`A | B`) the label is taken from the first variation only.

### Descriptions

```
// Pause **2 seconds** at the bottom
Squat / 5x5 / progress: lp(5lb)

/// This comment is NOT shown to the user
// This description IS shown to the user during workout
Squat / 5x5 / progress: lp(5lb)
```

- `//` lines above an exercise are its description (Markdown, links work; consecutive lines make one description). `///` is hidden. Inside `{~ ~}` blocks `//` is a plain code comment.
- Descriptions are reused on following weeks/days until overwritten. An empty `//` line stops reuse from that week onward:

```
# Week 3
## Day 1
// 
Squat / 5x5 / progress: lp(5lb)
```

- Reuse another exercise's description with `// ...Squat`, `// ...Squat[3]` (day 3 of the current week) or `// ...Squat[3:2]` (week 3, day 2).
- Multiple descriptions: separate them with an empty line; the current one is marked `// !` and chosen via `descriptionIndex` (see Advanced descriptions).

### Supersets

```
Squat / 3x8 / superset: A
Deadlift / 3x8 / superset: A
Bent Over Row / 3x8 180s / superset: A
Bicep Curl / 3x8
```

`superset: GROUP_NAME`, any string. Members use the superset default rest timer (Me -> Timers) unless a set timer is given.

### Reuse `...Name`

```
Bench Press / 5x5 / progress: lp(5lb)
Squat / ...Bench Press
```

- Reuses sets/reps/weight/RPE/timer, warmups, **and progress and update scripts** (including `lp`/`dp`; since 2025-03-09). By default it looks for the source in any day of the current week; `...Bench Press[2]` = day 2 of the current week; `...Bench Press[2:1]` = week 2, day 1. A reuse that would match itself needs the `[day]` form (error: "There're several exercises matching, please be more specific with [week:day] syntax").
- Override any part after the reuse: `Bench Press / ...Squat / 150lb` or `... / progress: lp(5lb)`. To reuse everything except scripts, override with an empty script: `Squat / ...Bench Press / progress: custom() {~ ~}`.
- When a reused exercise progresses and its weight diverges from the source, the app **extracts the new value into an override** on the reusing line (`Squat / ...Bench Press / 185lb`). If the source progresses, all its reusers get overrides.
- An exercise with `|` variations cannot be a reuse target (it can be a consumer). Exercises with several set variations can be reused.

### Templates `used: none`

```
Squat / 1x10+, 3x10 / 70% / used: none / progress: lp(5lb)
Bench Press / ...Squat

T1 / used: none / 1x10+, 3x10 / 70% / progress: lp(5lb)
t1: Bench Press / ...T1

main / used: none / warmup: 1x5 45lb, 1x5 135lb / progress: lp(5lb)
Squat / 3x8 100lb / ...main
```

Templates are not run, never progress (so never break reuse), and need not be real exercise names.

### Repeat across weeks and ordering

```
Bench Press[1-5] / 3x8
Squat[1,1-4] / 3x8
Bench Press[2,1-4] / 3x8
Bicep Curl[3,1-4] / 3x8
```

`Name[fromWeek-toWeek]` repeats the line on the same day of those weeks (leave those days empty). `Name[order,fromWeek-toWeek]` or `Name[order]` fixes the position when repeats make ordering ambiguous. Combine with reuse: `Bench Press[1-4] / ...Squat` picks up each week's `Squat`.

### Progressions

```
Bench Press / 3x8 / progress: lp(5lb)
Bench Press / 3x8 / progress: none
```

Declare once per exercise anywhere in the program; it applies to all instances. `progress: none` disables it on a specific week/day (deloads). Built-ins:

| Form | Meaning |
|---|---|
| `lp(weight increase, increase attempts, current increase attempt, weight decrease, decrease attempts, current decrease attempt)` | Linear. Trailing args optional. Increase may be `5lb` or `5%`; a negative increase (`lp(-5lb)`) decreases, used for assisted machines. |
| `dp(weight increase, min reps, max reps)` | Double. Reps climb from min to max, then weight increases and reps reset. Increase may be `5%` or negative. Rep ranges supported since 2026-02-28. |
| `sum(reps threshold, weights increase)` | Adds weight when the sum of completed reps across all sets exceeds the threshold. |
| `custom(state...) {~ script ~}` | Full script. |
| `custom(state...) { ...Squat }` | Reuse another exercise's custom script (curly braces without tildes). |

```
Squat / 3x8 / progress: lp(5lb)
Squat / 3x8 / progress: lp(5lb, 2)
Squat / 3x8 / progress: lp(5lb, 2, 1)
Squat / 3x8 / progress: lp(5lb, 2, 1, 10lb, 3)
Squat / 3x8 / progress: lp(5%)
Bench Press / 3x8 / progress: dp(5lb, 8, 12)
Bench Press / 3x6 / progress: dp(5%, 6, 10)
Bench Press / 3x10+ / progress: sum(30, 5lb)
```

### Set variations

```
Squat / 5x3 / 6x2 / 10x1 / progress: custom() {~
  if (completedReps >= reps) {
    weights = weights[ns] + 5lb
  } else {
    setVariationIndex += 1
  }
~}
```

Several sets sections = set variations. The current one is marked with `!` (`Squat / 5x3 / ! 6x2 / 10x1`); the app moves the `!` as `setVariationIndex` changes.

### Exercise variations

```
Split Squat | ! Bulgarian Split Squat | Pistol Squat / 3x8 0lb
Split Squat | Bulgarian Split Squat | Pistol Squat / 3x8 / progress: custom() {~
  if (completedReps >= reps) {
    exerciseVariationIndex += 1
  }
~}
```

Movements separated by `|`; `!` marks the current (first by default). `exerciseVariationIndex` is 1-based and wraps around. Sets, reps, weights and progress are shared; `%` and RPE weights resolve against the current variation's own 1RM. Can also be switched by hand in the Edit Program Exercise sheet.

### `progress: custom()` vs `update: custom()`

| | `progress: custom()` | `update: custom()` |
|---|---|---|
| Runs | after the workout is finished (changes are previewed after the exercise's last set) | at workout start with `setIndex == 0`, then every time a set is tapped/edited |
| Changes | the program (weights, reps, timers, state, set/description/exercise variation, `rm1`, `numberOfSets`) for future workouts | only the current workout's not-yet-completed sets; cannot write state |
| Targeting | `weights[week:day:setvariation:set]` | `weights` or `weights[set]` only |
| Both may be on one exercise | yes | yes |

Reuse either with `{ ...Name }`.

### State variables, prompted variables, tags

```
Bench Press / 3x8 / progress: custom(attempt: 0, increment: 5lb) {~
  if (completedReps >= reps) {
    state.attempt += 1
    if (state.attempt > 3) {
      weights += state.increment
      state.attempt = 0
    }
  }
~}
Squat / 3x8 / progress: custom(increment: 10lb) { ...Bench Press }

Bench Press / 3x8 / progress: custom(shouldBumpWeight+: 0) {~
  if (shouldBumpWeight > 0) {
    weights += 5lb
  }
~}
```

- Declared in `custom(...)`, read as `state.name`, persisted between workouts, editable on the Preview tab / Edit modal.
- When reusing, omit variables whose values are unchanged; only overrides need listing.
- `name+: default` = user-prompted variable; the app asks for it after the last set. (The docs' example reads it as `shouldBumpWeight` without the `state.` prefix; this is quoted exactly.)
- Tags: `id: tags(1, 100)` (several tags per exercise, shared tags allowed). From another exercise's progress script, `state[1].rating = 10` writes that variable in every exercise carrying tag 1.

### Variables `amraps`, `logrpes`, `askweights`

```
Squat / 3x8 100lb / progress: custom() {~
  amraps = 1  // Mark all sets AMRAP
  askweights[ns] = 1 // Ask for the last set actual weight
~}
```

Same as the `+` suffixes; 0 disables, non-zero enables. Usable like `reps`/`weights` in progress and update scripts.

### Suppressing progress

At workout time, after all sets of an exercise, tap "Suppress" next to the progress-changes info to skip that exercise's progression this workout. In the program, `progress: none` on a week/day does the same permanently for that day.

---

## Script variables and functions

Indexes start at 1. Aliases: `w` = `weights`, `cw` = `completedWeights`, `r` = `reps`, `mr` = `minReps`, `cr` = `completedReps`, `ns` = `numberOfSets`. Comparing whole arrays (`completedReps >= reps`, `weights >= 50lb`) is true only if every element satisfies it.

### Readable (progress and update)

| Variable | Meaning |
|---|---|
| `weights[n]` | Program weight of set n after rounding (the target). Since 2025-03-30 this is **not** the completed weight. |
| `originalWeights[n]` | Program weight before rounding. |
| `completedWeights[n]` | Weight actually logged for set n. |
| `reps[n]` | Required (max) reps for set n. |
| `minReps[n]` | Min reps of a rep range; equals `reps[n]` if not a range. |
| `completedReps[n]` | Reps logged for set n. |
| `completedRepsLeft[n]` | Left-side reps for unilateral exercises. |
| `RPE[n]` | Required RPE (if set). |
| `completedRPE[n]` | Logged RPE (if Log RPE was on). |
| `timers[n]` | Explicit per-set rest timer, if any. |
| `setTime[n]`, `completedSetTime[n]` | Target and recorded active set timer (docs, set-timer section). |
| `rm1` | The exercise's 1RM. |
| `bodyweight` | Latest bodyweight moving average from Measurements. |
| `day` | Current day number, from 1. |
| `week` | Current week number, from 1. |
| `dayInWeek` | Index of the day inside the week, from 1. |
| `programNumberOfSets` | Sets prescribed by the program for this week/day. |
| `numberOfSets` / `ns` | Sets currently in the exercise (after adding/removing during the workout). |
| `completedNumberOfSets` | Sets with a checkmark. |
| `setVariationIndex` | Current set variation (1-based). |
| `exerciseVariationIndex` | Current exercise variation (1-based). |
| `descriptionIndex` | Current description (1-based). |
| `amraps[n]`, `logrpes[n]`, `askweights[n]` | 1/0 flags per set. |
| `setIndex` | **Update only**: the set just tapped; 0 on the initial run at workout start. Also usable in timer expressions (e.g. `setIndex == numberOfSets ? 90 : 180`). |
| `state.x` | State variables (readable in update scripts too). |
| `var.x` | Temporary variables local to one script run. |

### Writable in `progress: custom()`

`weights`, `reps`, `minReps`, `RPE`, `timers`, `amraps`, `logrpes`, `askweights` — all with optional target `[week:day:setvariation:set]`; `numberOfSets[week:day:setvariation]`; `rm1`; `setVariationIndex`; `exerciseVariationIndex`; `descriptionIndex`; `state.*`; `var.*`.

```
weights = 50lb             // same as weights[*:*:*:*] = 50lb
weights[5] = 50lb          // same as weights[*:*:*:5] = 50lb
weights[3:*:5] = 50lb      // same as weights[*:3:*:5] = 50lb
weights[2:3:*:*] += 5lb    // all sets on week 2 day 3
numberOfSets[2:*:2] = 3
rm1 = weights[1]
```

Omitted leading positions are `*`. Values may be numbers or expressions. State variable changes are not rounded; weights are rounded only at workout time.

### Writable in `update: custom()`

`weights`, `reps`, `minReps`, `RPE`, `timers`, `numberOfSets`, `amraps`, `logrpes`, `askweights`, each as `x` (all incomplete sets) or `x[set]`. Completed sets are ignored; `[week:day:...]` targeting is not allowed. Changing `numberOfSets` adds copies of the last set or deletes trailing unfinished sets. Adjust new/existing sets with `sets()`.

Note: the docs' generic "Assignment" section still says values can only be assigned to state variables; the sections above (and the examples) show the writable program variables, so treat that sentence as outdated.

### Types, operators, control flow

- Values: numbers, weights (`5lb`, `2.5kg`), percentages (`80%`, of 1RM), booleans from comparisons. No strings. Prefer `lb`/`kg` suffixes so unit conversion works.
- Math `+ - * / %` (modulo); comparison `> < <= >= == !=`; logical `&& || !`; ternary `cond ? a : b`; compound assignment `+= -= *= /=`.
- `if (...) { } else if (...) { } else { }`.
- Loops: `for (var.i in completedReps) { weights[var.i] = weights[var.i] + 5lb }` — `var.i` is the 1-based set index; the right side must be an array.
- Semicolons are optional (examples use both).

### Functions

| Function | Meaning |
|---|---|
| `rpeMultiplier(reps, rpe)` | Fraction of 1RM for reps (1-24) at RPE (1-10); e.g. `rpeMultiplier(13, 9)` = 0.6. |
| `floor(x)`, `ceil(x)`, `round(x)` | Rounding; work on numbers and weights. |
| `sum(...)`, `min(...)`, `max(...)` | Any mix of arrays, numbers, weights: `sum(completedReps)`, `min(10, completedReps)`, `max(reps, completedReps)`. |
| `increment(w)`, `decrement(w)` | Next/previous loadable weight per the exercise's equipment (same as the +/- keyboard buttons). |
| `roundWeight(w)` | Round to the nearest valid load for the equipment, e.g. `roundWeight(rm1 * 80%)`. |
| `calculate1RM(weight, reps)` | Epley estimate. |
| `calculateTrainingMax(weight, reps)` | Training max from a weight and reps (formula not stated). |
| `zeroOrGte(a, b)` | True if every element of `a` is 0 or >= the matching element of `b` (all non-skipped sets hit target). |
| `print(...)` | Debug output (numbers, weights, percentages only) shown in the playground or after the exercise's last set. |
| `sets(fromIndex, toIndex, minReps, maxReps, isAmrap, weight, timer, rpe, shouldLogRpe)` | Update scripts only. Rewrites sets in the index range; the docs say 9 arguments but every example passes 8 (`sets(2, 4, 6, 6, 0, 50lb, 8, 0)`); this discrepancy is in the docs themselves. |

`roundWeight`, `calculate1RM`, `calculateTrainingMax` and `zeroOrGte` appear only in the docs' function reference, not in the changelog; their introduction dates are unknown.

---

## Progression semantics

### Success and failure

- **lp**: "successful finishing of all sets and reps" counts one increase attempt; after `increase attempts` successes the weight goes up by the increase and the counter resets. If the decrease arguments are given, an unsuccessful workout counts one decrease attempt and after `decrease attempts` failures the weight drops by `weight decrease`. Without decrease arguments a failure does nothing visible except (implied) resetting nothing; the docs do not say whether a failure resets the increase-attempt counter.
- **dp**: on success reps rise by one (all sets) until max reps; the next success adds the weight increase and resets reps to min. On failure: not stated in the docs (the implication is nothing changes).
- **sum**: weight increases when the total completed reps across sets exceeds the threshold; otherwise nothing.
- A set counts as successful when completed reps >= required reps (green); rep ranges are "in range" (yellow) between min and max, and the docs do not state whether yellow counts as success for lp; for dp with ranges see below.

### Changelog entry, 2026-01-03, "Changes in progress - lp() and dp() behavior" (summary)

If the program omitted the weight (`Squat / 3x8 / progress: lp(5lb)`), lp and dp treated the program weight as 0lb and set it to 5lb after a success even though the user had logged e.g. 100lb. Two breaking changes fix this: (1) if the weight was not specified in the program, the completed weights are written into the program; (2) lp and dp now increment based on the **completed** weight, not the program's target weight.

### Changelog entry, 2026-02-28, "Improved Double Progression (dp) to support rep ranges" (summary)

dp auto-detects rep-range exercises (`3x8-12`) and progressively narrows the range from below until the top is reached, then increases the weight and resets. Non-range exercises (`3x8`) behave as before: reps from min to max, then bump weight and reset reps. If you adjusted the weight during a workout (e.g. the programmed weight was unavailable), the next increase is based on the weight actually used.

### When scripts run

- Progress (built-in or custom) runs when the workout is **finished**; the resulting changes are previewed after the exercise's last set with a "Suppress" link. Reused exercises whose values diverge get overrides written into the program text.
- Update scripts run at workout start (`setIndex == 0`) and after each set tap or edit.
- Timer expressions run after each set.

### Skipped or unlogged exercises

Not stated in the docs. The working guide (verified against source) records that an exercise left unlogged neither progresses nor regresses. The existence of `zeroOrGte` (treats 0 completed reps as "skipped") shows that skipped *sets* have `completedReps` of 0, so a custom `completedReps >= reps` check fails on a skipped set unless you use `zeroOrGte`. Ad-hoc exercises added from the picker as **program** exercises run their progression; ad-hoc (non-program) exercises do not have one.

### Other rules

- One progression per (label + name) across the whole program; the same exercise with different equipment is a different exercise.
- Reuse copies the progression; a reuser can override it.
- Templates (`used: none`) never progress.
- Rounding happens only at workout time; state variables are never rounded.

---

## Swapping and substitutes

Swap icon on the workout screen replaces an exercise for this workout only or for the whole program (2024-03-18). Two 2026 changelog entries define current behaviour:

**2026-08-11 "Swapping an exercise now adjusts the weights to match"**: previously only the exercise changed and the weights stayed (fine for 1RM-percentage programs, wrong for absolute weights). Now, for each set, the app searches your history for the exercise you swap **to**, finds the set closest in reps to the target, and converts that weight to the target reps and RPE; if reps and RPE match you get the weight you lifted last time. Sets with different reps each get their own weight (a 12/10/8 pyramid stays a pyramid). With no history it falls back to the exercise's 1RM, or its default starting weight if no 1RM is set (as percentage-based sets always did). Correcting the weight once creates history for the next swap. Warmups are rebuilt from the program's warmups for that exercise if defined, otherwise from its defaults.

**2026-08-12 "Improvements in exercise swapping during workout"**: recent swaps appear in a "Recent" section at the top of the picker. Restates the weight logic: latest weight for the same reps in history, else the closest reps and infer, else infer from 1RM; and the warmup rule above.

Substitutes in the picker: the old "Substitute" tab is now the "sort by similar muscles" filter (2025-08-10). Unused program exercises (defined in the program but not on any day, or `used: none`) can be added mid-workout with their sets and progression, which is the intended way to keep pre-programmed alternatives for busy machines. Whether a swapped-in exercise advances the original's progression is not stated in the changelog; the working guide records (from source) that by default it does not.

---

## Integrations

| Integration | What the sources say |
|---|---|
| REST API | Premium. Generate an API key in Settings (keys start `lftsk_` per the working guide). Create programs, log workouts, simulate progressions, pull stats; manage gyms/equipment and exercise data (1RM, muscle overrides, equipment, default rounding, unilateral flag, notes); read/record/edit/delete body measurements with custom dates; `health` category for sleep and nutrition. Docs at `liftosaur.com/docs/api`. |
| MCP server | Premium. Connect Claude, ChatGPT, Gemini etc. to create programs, tweak progressions, log workouts, analyse training; same measurement/equipment/exercise capabilities as the API. Docs at `liftosaur.com/docs/mcp`. |
| Apple Health | iOS 15+. Writes workouts (automatically on finish since 2026-01-24, optional "Ask for confirmation"; past workouts via the share menu) and bodyweight, body fat, waist. Reads bodyweight, body fat, waist into Measurements. Optional "Sync Sleep & Nutrition" imports sleep duration, calories, protein (read-only, on app open). Enable at Me -> Apple Health. |
| Google Health Connect | Android 14+. Same as Apple Health except waist circumference is Apple-only. Me -> Google Health Connect. |
| Apple Watch | Premium; native iOS app 6.31+. Complete sets, rest timers, upcoming exercises, set-timer modal, complications. No editing of the workout. |
| Live Activity / Live Updates | See Workout screen; Premium. |
| Hevy import | Me -> Import history from other apps -> Hevy, upload CSV; preview and undo flow as described under History. |
| Liftosaur CSV import | Same flow. |
| Strong import | Not stated in sources. |
| Export | Workout as text (finish screen "Text" button or past workout share menu); workout image for Instagram/TikTok or native share sheet; program image; program share link `liftosaur.com/p/<id>`; CSV export not described. |
| AI prompt generator | `liftosaur.com/ai/prompt`, see Program screen. |
| Website | `/programs` catalogue, Web Editor, Workout Planner (`/planner`), 1RM calculator, exercises pages (`/exercises/<equipment>-<name>`). |

---

## Feature timeline

Newest first. Entries marked (B) contain a breaking change or a syntax that older app versions will reject; if a user's app shows a syntax error, check whether their app predates the entry that introduced the construct. Native-app-only features need an App Store / Google Play update, not just a web refresh.

| Date | Title | Note |
|---|---|---|
| 2026-09-09 | Time-based exercises: Countdown and unilateral exercises support | native |
| 2026-09-01 | Autocompletion suggestions in freeform mode in Liftoscript editor | |
| 2026-08-28 | New grid view for structuring the program | |
| 2026-08-17 | Some Liftoeditor improvements | |
| 2026-08-12 | Improvements in exercise swapping during workout | |
| 2026-08-11 | Swapping an exercise now adjusts the weights to match | |
| 2026-08-10 | Text size now scales the whole app, and follows your device setting | |
| 2026-08-09 | Embrace Liftoscript, part 1: Redesign of the "Edit Program Exercise" screen | |
| 2026-07-19 | Added Sleep & Nutrition tracking | native |
| 2026-07-17 | Tap a crossed-out weight to see why it was rounded | |
| 2026-07-13 | More accurate volume for two-dumbbell exercises | (B) volume numbers double |
| 2026-07-10 | Added exercise variations (progression ladders) | (B) `|` and `!` reserved in names; `exerciseVariationIndex` |
| 2026-07-01 | Added time-based exercises and intervals/circuits support | native; `60s|30s`, `30s+`, `auto` |
| 2026-06-17 | Added Apple Watch complications | native |
| 2026-06-15 | Added API / MCP for body measurements | |
| 2026-06-14 | Added API / MCP for the equipment and exercise data | |
| 2026-06-13 | Added subscription management to the Account screen | |
| 2026-06-08 | Improved import history flow | |
| 2026-05-31 | New native iOS and Android apps | |
| 2026-05-02 | Huge update where nothing changed | rewrite; graphs look different |
| 2026-03-16 | Added "tour" modals | |
| 2026-03-08 | MCP Server and REST API | Premium |
| 2026-03-03 | Export workouts as text | |
| 2026-02-28 | Improved Double Progression (dp) to support rep ranges | (B) dp semantics |
| 2026-02-22 | New /programs page on the liftosaur.com site | |
| 2026-02-08 | Exerciser Picker by default now hides exercises with hidden equipment | |
| 2026-01-29 | Add Apple Watch Support | Premium; iOS app 6.31+ |
| 2026-01-24 | Workout now syncs to Apple/Google health when you finish a workout | |
| 2026-01-20 | The current ongoing workout now syncs to the server | |
| 2026-01-03 | Changes in progress - lp() and dp() behavior | (B) increments from completed weight |
| 2025-11-25 | Added Live Updates on Android | Premium; native |
| 2025-11-23 | Added Live Activity / Dynamic Island on iOS | Premium; native |
| 2025-11-09 | Added unilateral exercise support | `completedRepsLeft` |
| 2025-11-03 | Added ability to customize muscle groups | |
| 2025-11-01 | Add supersets | `superset: A` |
| 2025-10-13 | Override target/synergist muscles of exercises with custom synergist multipliers | |
| 2025-10-01 | Added estimated 1 Rep Max column to the workout screen | |
| 2025-09-24 | Improved custom exercises | (B) no image URLs |
| 2025-09-14 | Exercise and equipment notes | |
| 2025-09-05 | Preview tab on the Program screen now changes 1RM/Equipment/State vars | |
| 2025-09-04 | Add new variables - 'amraps', 'logrpes' and 'askweights' | |
| 2025-08-30 | Bar == Bodyweight and "Assisted" equipment | |
| 2025-08-26 | Dark Theme | native for full coverage |
| 2025-08-13 | Hiding equipment, and changes in default exercise equipment | (B) default equipment auto-set |
| 2025-08-10 | Redesign of the exercise picker | Substitute tab removed |
| 2025-07-06 | Improved syncing mechanism | |
| 2025-06-22 | Added bodyweight variable | `bodyweight` |
| 2025-06-21 | Added increment() and decrement() functions | |
| 2025-06-19 | AI prompt generator | |
| 2025-06-13 | Suppressing progress | |
| 2025-06-07 | Redesigned the "Program" screen | |
| 2025-04-24 | Redesigned "Choose Program" screen | |
| 2025-04-21 | Sets are now optional in the program | (B) no implicit 1RM% weight |
| 2025-04-17 | Add a way to create program days from Ad-hoc workouts | |
| 2025-04-13 | Add "programNumberOfSets" and "completedNumberOfSets" read-only variables | |
| 2025-04-09 | Tweaked the Calendar (Home screen) | |
| 2025-03-30 | New Workout Screen! | (B) `completedWeights` split from `weights` |
| 2025-03-09 | Big changes in Liftoscript reuse syntax | (B) `...X` reuses progress/update; templates need no real name |
| 2025-03-05 | Added negative weights support | |
| 2025-03-04 | Massive update where nothing is changed | Liftoscript engine rewrite |
| 2025-02-10 | Added calendar | |
| 2025-02-02 | Redesigning the navigation | |
| 2025-01-19 | Redesigned the sets, and added PRs to history/exercise stats | |
| 2025-01-17 | Share workouts on Social Media | |
| 2024-12-23 | Added a way to generate program images | |
| 2024-12-14 | Added day/week descriptions | |
| 2024-12-08 | Added `print` function | |
| 2024-12-07 | Added ongoing workout reminder push notification | native |
| 2024-11-30 | Added Week Insights | Premium |
| 2024-11-17 | Added some convenience shortcuts | |
| 2024-11-09 | Improve experience with kg units | |
| 2024-11-03 | Change numberOfSets in progress scripts | |
| 2024-10-11 | Apple Health and Google Health Connect integration | iOS 15+, Android 14+ |
| 2024-09-22 | Pausing a workout | |
| 2024-09-14 | Custom unit (lb/kg) for equipment | |
| 2024-08-25 | Introducing localized pricing | |
| 2024-08-10 | Custom Exercise Images | superseded 2025-09-24 |
| 2024-08-08 | Settings - Exercises screen | |
| 2024-08-03 | Program Version History | |
| 2024-07-31 | Updates related to syncing and program saving | Web Editor Save button |
| 2024-06-12 | Changed how equipment works and added multi-gym support | (B) equipment separated from exercise |
| 2024-05-25 | Add UI for tweaking programs | |
| 2024-05-06 | "Quick-add sets" is now per set variations | (B) |
| 2024-04-21 | Added rich reps / weight / rpe inputs | |
| 2024-04-20 | Added tags | `id: tags()`, `state[tag]` |
| 2024-04-17 | update - custom() improvements | (B) runs at `setIndex == 0` |
| 2024-04-15 | Added a bunch of new programs | 5/3/1 BBB, Monolith, nSuns, Madcow, PHUL, Greyskull |
| 2024-04-13 | Quickly change weights in a program exercise | |
| 2024-04-03 | All built-in programs are migrated to the new syntax | Liftoscript 2.0 default |
| 2024-04-01 | Loops | `for (var.i in ...)` |
| 2024-03-28 | Improved reusing of sets, reps, weight, RPE, timer and warmups | |
| 2024-03-18 | Redesigned exercise picker and ability to replace exercises from the workout and new editor screens. | Swap added |
| 2024-02-05 | New update - custom() syntax for updates after completed sets (in the "Experimental" programs) | |
| 2024-01-27 | New "Experimental" programs (aka "in-app Workout Planner") | Liftoscript 2.0 text programs |
| 2024-01-06 | Added ability to set 1 Rep Max for exercises | `rm1` |
| 2024-01-03 | Added "Full Program" mode to the Workout Planner | `# Week` / `## Day` |
| 2023-12-25 | Improved Program Preview in the app and Web Editor | |
| 2023-12-07 | You can now fully delete your account | |
| 2023-10-16 | Changed how Web Editor program links work | |
| 2023-09-27 | Offline mode | |
| 2023-09-22 | Moving Average on the Measurement Graphs | |
| 2023-09-20 | Added Rep Max Calculator | |
| 2023-09-02 | Added rep ranges support | `minReps` |
| 2023-08-31 | Added multi-week support | `week`, `dayInWeek` |
| 2023-08-22 | Added visual cues when rounding weights | |
| 2023-08-04 | Added RPE support | `RPE`, `completedRPE` |
| 2023-07-29 | Add better volume support | |
| 2023-07-27 | Import history from Hevy app | |
| 2023-07-24 | Make the rest timer adjustable | |
| 2023-07-16 | Improve exercise selection modal | |
| 2023-07-12 | Add Custom Equipment | |
| 2023-07-04 | Switched "reps x sets" to "sets x reps" on the history screen | |
| 2023-06-30 | Bodyfat tracking | |
| 2023-06-25 | Added Long Press to edit the quickly edit the sets in current workout | |
| 2023-06-24 | Made "Quick Add Set" supported in playgrounds | |
| 2023-06-13 | Added sound controls to iOS / Android apps | native |
| 2023-06-11 | Added a way to add labels to sets | 8 chars max |
| 2023-06-09 | Added new functions - sum, min and max | |
| 2023-05-24 | Added "Always On Display" in Settings | native |
| 2023-05-11 | Improved program exercise timer expressions | `setIndex` in timers |
| 2023-05-01 | More Liftoscript features | `%`, floor/ceil/round, `+=` etc. |
| 2023-04-30 | New Liftoscript Engine | (B) stricter parsing |
| 2023-04-22 | Quick add sets | `numberOfSets`, `ns` |
| 2023-04-19 | Program Exercise Descriptions | |
| 2023-04-09 | Edit state variables from workout screen | |
| 2023-03-30 | User entered state variables | |
| 2023-03-24 | Per Exercise Rest Timers | timer expressions |
| 2023-03-19 | Discord Server | |
| 2023-03-01 | Notes | workout and exercise notes |
| 2023-02-24 | Inspirations in the Advanced Edit Mode | |
| 2023-02-22 | Web Editor for programs | immutable share links |
| 2023-02-09 | Choose Programs screen redesign | |
| 2023-02-07 | Footer navigation | floating rest timer |
| 2023-01-21 | Exercise Stats | |
| 2023-01-15 | Program Preview | |
| 2023-01-11 | Graph Improvements | pinch-zoom |
| 2022-12-28 | Add Reuse Logic feature | old-model reuse |
| 2022-12-26 | New Account Management. | multiple local accounts |
| 2022-12-25 | Redesign. | |
| 2022-08-08 | Big changes in the equipment settings. | plates per equipment; fixed weights |
| 2022-06-04 | Add 1 Rep Max line to the exercises graphs. | Epley; toggle in Graphs settings |
| 2022-02-19 | Import/Export of all data and also specific programs. | file backup |

Entries before 2024-01-27 describe the old, pre-Liftoscript-2.0 program model ("Finish Day Script", "Extra Features" checkboxes, per-set Liftoscript expressions); the concepts carried over (variables, RPE, rep ranges, tags) but the UI they mention no longer exists.

### Known docs vs changelog discrepancies

| Topic | Docs | Changelog | Preferred |
|---|---|---|---|
| Update-script writable variables | weights, reps, minReps, RPE, timers, numberOfSets, amraps, logrpes, askweights | 2024-02-05 lists only reps, minReps, weights, RPE | Docs (newer additions) |
| Weight with no weight/RPE | empty, user enters it | 2025-04-21 says the same; earlier behaviour inferred 1RM% | Consistent |
| `sets()` argument count | says 9, examples pass 8 | not covered | Unresolved; copy the 8-argument examples |
| Quick-add sets `1+x5` | not documented | 2024-05-06 | Changelog only; may be legacy |
| `setTime` / `completedSetTime` | documented | not mentioned | Docs |
| Prompted state var read as `shouldBumpWeight` (no `state.`) | docs example | none | Quoted as written; unverified |
