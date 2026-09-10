# Liftosaur working guide

Read this before touching the Liftosaur program. It records what was learned the hard way so it does not need re-deriving.

For everything the app can do in general (features, full Liftoscript syntax, script variables, integrations, feature timeline) see `docs/liftosaur-reference.md`. This file is only about this user's program and workflow.

## Files

| File | What it is |
|---|---|
| `docs/upper-body-3-day.liftoscript` | The current program text. Source of truth for the app. |
| `docs/liftosaur-tools/gen_program.py` | Generates the program text from a data table. Edit the table, not the text. `python3 gen_program.py out.txt` |
| `docs/liftosaur-tools/validate_plan.ts` | Runs a program through Liftosaur's real parser and simulates N completed rounds. See "Validating" below. |
| `docs/liftosaur-tools/validate_subs.ts` | Swaps each hidden `used: none` substitute into a workout, completes it, and checks its progression fired. Also prints visible exercise counts per day. |
| `docs/upper-body-3-day-plan.md` / `.html` | The human-readable plan. Keep exercises, sets, and links in sync with the program. |
| `docs/liftosaur-reference.md` | General reference for the app and Liftoscript. Built from the official docs and changelog. |

## The user's setup

- Units: kg. Free tier. Programs are pasted into the web editor in full text mode at their private program page (`liftosaur.com/user/p/...`, login-only, cannot be fetched).
- Public share links look like `liftosaur.com/p/<id>` and can be fetched without login.
- REST API and MCP server both require Premium and an API key starting `lftsk_`. Do not ask the user to paste a key into chat.
- Chin-up weight is the machine assistance, so the program decrements it. Do not enable "Is assisting" or "Bodyweight for bar" in equipment settings, those apply to every Leverage Machine exercise.
- Substitutes are hidden `used: none` program exercises with their own weight and progression; each visible exercise's note names which one to pick after Swap Exercise. See the substitutes section.
- Group system: every exercise note starts with 🟢 MAIN (press and pulls, never skip), 🟠 ARMS (the pair), or ⚪ EXTRA (skippable). Exercises also carry `main:` / `arms:` / `extra:` labels. The user wants it obvious at a glance; do not add more tiers or rename them without asking.
- The app has no colour system for exercises. Red underlines in the editor are parse errors and the program will not save while they exist. Emoji in descriptions are the only visual tag that renders in the workout.
- The user's installed app may be older than the GitHub source used for validation. Prefer plain syntax: built-in `dp` over `custom()` scripts, full repeated lines over labelled `...reuse`. If the user reports red underlines, ask for the tap-to-see message and the exercise.

## How substitutes work (decided 2026-09-10, supersedes earlier approach)

Liftosaur's exercise picker can add or swap in **program exercises, used or unused**, and they arrive with their own sets, weights, timer, warm-ups and progression, which runs on completion (changelog 2025-07-19, "Redesign of the exercise picker"; verified in `NavModalExercisePicker.tsx` and by simulation in `docs/liftosaur-tools/validate_subs.ts`).

So the program has:

- The visible days with only the main exercises, 7 or 8 rows each.
- Directly under every visible exercise, its substitute as a hidden line: normal exercise syntax with `/ used: none /`, its own starting weight and `dp` progression, labelled `sub:`. Hidden lines never show in a day. The picker's From Program tab lists program exercises grouped by identity in document order, so each substitute appears immediately below its main exercise there. Two substitutes appear twice with identical lines (skull crusher, barbell shrug) and share one progression; the second copy is grouped at the first copy's position.
- Every substitute has its own `sub:` identity even when the same movement is a main exercise on another day (dumbbell bench, machine row, cable row, chest press, leg press, dumbbell overhead extension). Tested: a hidden copy that shares label, name and equipment with a visible exercise makes the app mark the visible one `used: none` too, removing it from its day. Never do that.
- Each visible exercise's note names exactly what to pick, e.g. "swap to *sub: Skullcrusher, EZ Bar*". The hidden line's own note says which main it substitutes for.
- Recent swaps are remembered per source exercise (`settings.recentExercises[fromKey]`) but the Recent section only appears on the Ad-hoc tab and offers ad-hoc rows, which do not progress. The user must use the From Program tab.

In the workout: tap the exercise, Swap Exercise, From Program tab, pick the `sub:` row under it. Do not pick the same name from the Ad-hoc tab or the Recent section; that path (`Progress_changeExercise`) only copies weights from history and runs no progression. Search in the picker matches exercise name and equipment, not the label.

Simulation result: all 15 hidden substitutes progressed after one completed session, and the three days still show 8, 7 and 8 exercises.

Rejected approaches, and why:

- Substitutes as visible lines under each main exercise. Works but doubles every day's list; the user rejected it as too cluttered.
- Exercise variations with `|`. All variations share one weight and one progression. No workout-screen control switches them.
- Ad-hoc swap only. Weights come from history but the substitute never progresses. This was the fallback before the picker feature was found.
- Switching apps. No free app has programmed substitutes with their own progression.

## Liftoscript essentials

Full reference: `https://www.liftosaur.com/doc/liftoscript` (curl works; Chromium does not, see below).

```
# Week 1
## Day A
// Description shown during the workout. Markdown works, links work.
// Multiple // lines make one description.
Exercise Name, Equipment / 3x8 40kg 120s / warmup: 1x6 60% / superset: A / progress: dp(2.5kg, 8, 12)
```

- Sections are separated by `/`. Order: name, sets, warmup, superset, progress. Weight and rest timer sit in the sets section.
- `///` is a hidden comment. `//` before `# Week` is the week description, before `## Day` the day description.
- `warmup: none` disables default warm-ups. `warmup: 1x8 50%, 1x4 75%` is percent of working weight. Absolute weights also work.
- `dp(increment, minReps, maxReps)`: each fully completed session adds one rep; at max it adds the increment and resets reps to min. Write the exercise at min reps, e.g. `3x8` for an 8 to 12 range. A negative increment works, used for assisted chin-ups: `dp(-2.5kg, 6, 10)` lowers the assistance. Since 2026-03 `dp` also accepts a written range like `3x8-12` and narrows it from below. Since 2026-01 `lp`/`dp` increment from the weight actually logged, not the programmed weight, so if the user changes a weight mid-workout the next increase builds on that.
- One progression per exercise across the whole program. Exercise identity is label + name + equipment, so `Triceps Extension, Cable` and `Triceps Extension, Dumbbell` are already different exercises (tested). Labels are only needed to split the same name and equipment, or as visible tags. Every exercise in the program carries a group label: `main:`, `arms:`, or `extra:`.
- Reuse: `Shrug, Dumbbell / ...Shrug[1]`. The `[day]` is required when the reusing line would match itself. An exercise with `|` variations cannot be a reuse target.
- `A | B` exercise variations share one weight and progression. Not suitable for substitutes with different loads.
- Custom progression is no longer used in the program. The equivalent script, kept for reference, was: `progress: custom() {~ if (completedReps >= reps) { if (reps[1] < 10) { reps += 1 } else { reps = 6; weights -= 2.5kg } } ~}`. It validated, but `dp(-2.5kg, 6, 10)` does the same with less to go wrong.

## Exercise names used

Names must match the library exactly. In the program each is prefixed with its group label (`main:`, `arms:`, `extra:`), omitted here. Equipment labels: `Barbell`, `Dumbbell`, `Cable`, `Leverage Machine`, `Smith Machine`, `EZ Bar`, `Bodyweight`, `Band`, `Kettlebell`, `Trap Bar`.

| Plan exercise | Liftosaur name |
|---|---|
| Machine chest press | `Chest Press, Leverage Machine` |
| Flat dumbbell bench | `Bench Press, Dumbbell` |
| Incline dumbbell press | `Incline Bench Press, Dumbbell` |
| Lat pulldown | `Lat Pulldown, Cable` |
| Seated cable row | `Seated Row, Cable` |
| Chest-supported row machine | `Chest-Supported Row, Leverage Machine` |
| One-arm dumbbell row | `Bent Over One Arm Row, Dumbbell` |
| Assisted chin-up | `Chin Up, Leverage Machine` |
| Machine shoulder press | `Shoulder Press, Leverage Machine` |
| Lateral raise | `Lateral Raise, Dumbbell` |
| Reverse pec deck | `Reverse Fly, Leverage Machine` |
| Pec deck | `Pec Deck, Leverage Machine` |
| Shrug | `Shrug, Dumbbell` |
| Incline curl | `Incline Curl, Dumbbell` |
| Preacher curl | `Preacher Curl, EZ Bar` |
| Bayesian curl | `Bicep Curl, Cable` |
| Overhead cable extension | `Triceps Extension, Cable` |
| Dumbbell overhead extension | `Triceps Extension, Dumbbell` |
| Pushdown | `Triceps Pushdown, Cable` |
| Hack squat | `Hack Squat, Leverage Machine` |
| Leg press | `Leg Press, Leverage Machine` |
| Seated leg curl | `Seated Leg Curl, Leverage Machine` |

Other names that exist if needed: `Skullcrusher`, `Hammer Curl`, `Face Pull`, `Chest Fly`, `Leg Extension`, `Lying Leg Curl`, `Pull Up`, `Triceps Dip`, `Bench Press Close Grip`. Full list: `grep -o 'name: "[^"]*"' src/models/exercise.ts` in the repo clone.

## Validating a program

The web editor cannot be driven from this environment: Chromium through the agent proxy gets `ERR_CONNECTION_RESET` on liftosaur.com even though curl works. Use the parser from the source instead.

```
cd <scratchpad>
git clone --depth 1 https://github.com/astashov/liftosaur.git
cd liftosaur
npm install --ignore-scripts --no-audit --no-fund      # about 4 minutes, run in background
printf 'export const content = "";\n' > src/generated/whatsnew.ts   # generated file the build normally creates
cp <repo>/docs/liftosaur-tools/validate_plan.ts test/
ts-node -T -r ./register-rn-web.js test/validate_plan.ts <program.txt> <rounds>
```

Global `ts-node` exists. `-T` skips type checking. The script prints `Parse/evaluate OK.` or the parser's error with line:column, then a per-exercise table, then the program text after N rounds with every rep completed, which shows whether progression fires.

Errors seen so far and their fixes:

- `There're several exercises matching, please be more specific with [week:day] syntax`: a `...Name` reuse matched itself. Add `[1]`.
- `No such exercise alt: Shrug at week: 1, day: 1`: a labelled reuse must repeat the equipment too, `...alt: Shrug, Barbell[1]`. Simpler to write the full line twice; identical lines for the same exercise are allowed.
- Equipment is not validated. `Hack Squat, Leverage Machine` is accepted even though the library lists only Barbell and Smith Machine for it. Any equipment name from the list works on any exercise.
- Same exercise with different equipment counts as a different exercise, so the same label on both is fine.
- Different progressions for the same exercise across days: add labels.

## Verifying video links

YouTube pages are blocked to fetchers, but the oEmbed endpoint returns the title and channel for any video ID:

```
curl -sS "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=<ID>&format=json"
```

A failure means the video is gone or private. Renaissance Periodization's exercise library clips are the default source, roughly one minute each.

## Regenerating everything after a plan change

1. Edit the table in `gen_program.py` and regenerate the program text.
2. Validate with 3 or more rounds.
3. Update the markdown and HTML plan to match, regenerate the single-page PDF with Playwright (`page.pdf` with height set to the document's `scrollHeight`).
4. Commit all of it on the working branch and push.
