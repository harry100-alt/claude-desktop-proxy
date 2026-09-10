yt = "https://www.youtube.com/watch?v="

# (liftosaur exercise line prefix, sets, weight+timer, warmup, superset, progress, main video id,
#  sub name, sub video id, cue)
DAYS = {
"A": {
 "desc": ["🟢 **main:** chest press, lat pulldown, cable row.",
          "🟠 **arms:** incline curl + overhead extension, paired.",
          "⚪ **extra:** lateral raise, shrug, hack squat. Cut here if short on time.",
          "Machine taken? Tap the exercise, Swap Exercise, and pick the one named in its note from the program list. It brings its own weight and progression."],
 "ex": [
  ("main: Chest Press, Leverage Machine", "3x6", "35kg 120s", "1x8 50%, 1x4 75%", None, "dp(2.5kg, 6, 10)", "NwzUje3z0qY",
   "swap to *main: Bench Press, Dumbbell*", "YQ2s_Y7g5Qk", "Handles at mid-chest height. Full stretch at the back, elbows about 45° from the body."),
  ("main: Lat Pulldown, Cable", "3x8", "40kg 120s", "1x6 60%", None, "dp(2.5kg, 8, 12)", "EUIri47Epcg",
   "swap to *sub: Pull Up*", "8ygapPMYK1I", "Slight lean back, pull the bar to the upper chest, drive elbows down. Full stretch at the top."),
  ("main: Seated Row, Cable", "3x8", "40kg 120s", "none", None, "dp(2.5kg, 8, 12)", "UCXxvVItLoM",
   "swap to *main: Chest-Supported Row*", "0UBRfiO4zDs", "Let the shoulder blades reach forward at the start, then pull to the lower ribs."),
  ("arms: Incline Curl, Dumbbell", "4x8", "8kg 45s", "none", "A", "dp(2kg, 8, 12)", "aTYlqC_JacQ",
   "swap to *sub: Bicep Curl, Dumbbell*", "iixND1P2lik", "Bench at about 45°, arms hanging straight down and slightly back. Curl without moving the upper arm."),
  ("arms: Triceps Extension, Cable", "4x10", "25kg 45s", "none", "A", "dp(2.5kg, 10, 15)", "kqidUIf1eJE",
   "swap to *arms: Triceps Extension, Dumbbell*", "YbX7Wd8jQ-Q", "Overhead, rope. Face away from the stack, elbows by the ears, deep stretch behind the head each rep."),
  ("extra: Lateral Raise, Dumbbell", "3x12", "6kg 60s", "none", None, "dp(1kg, 12, 15)", "3VcKaXpzqRo",
   "swap to *sub: Lateral Raise, Cable*", "lq7eLC30b9w", "Slight forward lean, lead with the elbows, stop at shoulder height. Light weight, no swinging."),
  ("extra: Shrug, Dumbbell", "3x10", "22kg 60s", "none", None, "dp(2kg, 10, 15)", "_t3lrPI6Ns4",
   "swap to *sub: Shrug, Barbell*", "M_MjF5Nm_h4", "Full stretch at the bottom, shrug straight up, hold 1 second at the top. No rolling."),
  ("extra: Hack Squat, Leverage Machine", "3x8", "50kg 120s", "1x6 50%", None, "dp(10kg, 8, 12)", "rYgNArpwE7E",
   "swap to *extra: Leg Press*", "yZmx_Ac3880", "Feet mid-platform, shoulder width. As deep as you can with heels down. Weight is plates only, not the sled."),
 ]},
"B": {
 "desc": ["🟢 **main:** incline press, chest-supported row, shoulder press.",
          "🟠 **arms:** preacher curl + pushdown, paired.",
          "⚪ **extra:** pec deck, leg curl. Cut here if short on time.",
          "Machine taken? Tap the exercise, Swap Exercise, and pick the one named in its note from the program list. It brings its own weight and progression."],
 "ex": [
  ("main: Incline Bench Press, Dumbbell", "3x6", "12kg 120s", "1x8 50%, 1x4 75%", None, "dp(2kg, 6, 10)", "5CECBjd7HLQ",
   "swap to *sub: Incline Bench Press, Smith Machine*", "8urE8Z8AMQ4", "30° bench. Deep stretch at upper-chest level, elbows about 45° out. Press up and slightly in."),
  ("main: Chest-Supported Row, Leverage Machine", "3x8", "35kg 120s", "1x6 60%", None, "dp(2.5kg, 8, 12)", "0UBRfiO4zDs",
   "swap to *sub: Incline Row, Dumbbell*", "Nx0TzjgsI-0", "Chest glued to the pad. Pull elbows back and squeeze the shoulder blades together."),
  ("main: Shoulder Press, Leverage Machine", "3x8", "25kg 120s", "none", None, "dp(2.5kg, 8, 12)", "WvLMauqrnK8",
   "swap to *sub: Shoulder Press, Dumbbell*", "HzIiNhHhhtA", "Start with handles at about chin height. Press up without flaring the ribs."),
  ("arms: Preacher Curl, EZ Bar", "4x8", "15kg 45s", "none", "B", "dp(2.5kg, 8, 12)", "sxA__DoLsgo",
   "swap to *sub: Preacher Curl, Leverage Machine*", "M_uPvGrMx_o", "Armpits on top of the pad. Lower almost to straight arms, then curl. No shoulder movement. Weight includes the bar, about 8 kg."),
  ("arms: Triceps Pushdown, Cable", "4x10", "25kg 45s", "none", "B", "dp(2.5kg, 10, 15)", "6Fzep104f0s",
   "swap to *sub: Skullcrusher, EZ Bar*", "OQ4TWXkZjTc", "Elbows pinned to the sides. Push to lockout, let the forearms come up past 90° on the way back."),
  ("extra: Pec Deck, Leverage Machine", "2x10", "35kg 60s", "none", None, "dp(2.5kg, 10, 15)", "O-OBCfyh9Fw",
   "swap to *sub: Chest Fly, Cable*", "4mfLHnFL0Uw", "Handles at chest height. Open wide to a stretch, then bring the arms together with a slight elbow bend."),
  ("extra: Seated Leg Curl, Leverage Machine", "3x8", "35kg 120s", "1x6 60%", None, "dp(5kg, 8, 12)", "Orxowest56U",
   "swap to *sub: Lying Leg Curl*", "n5WDXD_mpVY", "Pad just above the heels. Curl all the way down and control the return."),
 ]},
"C": {
 "desc": ["🟢 **main:** dumbbell bench, chin-up, one-arm row.",
          "🟠 **arms:** Bayesian curl + dumbbell overhead extension, paired.",
          "⚪ **extra:** reverse pec deck, shrug, leg press. Cut here if short on time.",
          "Machine taken? Tap the exercise, Swap Exercise, and pick the one named in its note from the program list. It brings its own weight and progression."],
 "ex": [
  ("main: Bench Press, Dumbbell", "3x8", "14kg 120s", "1x8 50%, 1x4 75%", None, "dp(2kg, 8, 12)", "YQ2s_Y7g5Qk",
   "swap to *main: Chest Press, Leverage Machine*", "NwzUje3z0qY", "Shoulder blades back and down. Deep stretch beside the chest, press up and slightly in."),
  ("CHINUP", None, None, None, None, None, "9JC1EwqezGY",
   "swap to *sub: Lat Pulldown, Cable*", "GRHLNfmr_oI", "Underhand grip, palms facing you, shoulder width. Weight here is the ASSISTANCE, lower is harder. Full hang, chin over the bar."),
  ("main: Bent Over One Arm Row, Dumbbell", "3x8", "16kg 120s", "none", None, "dp(2kg, 8, 12)", "k2kVniB5eQI",
   "swap to *main: Seated Row, Cable*", "UCXxvVItLoM", "Hand and knee on the bench. Let the dumbbell hang to a stretch, then row to the hip. No twisting."),
  ("arms: Bicep Curl, Cable", "4x8", "12.5kg 45s", "none", "C", "dp(2.5kg, 8, 12)", "paM4Yo8fo8g",
   "swap to *sub: Hammer Curl*", "XOEL4MgekYE", "Bayesian curl, one arm at a time. Low pulley behind you, step forward so the arm is stretched behind the torso. Upper arm fixed."),
  ("arms: Triceps Extension, Dumbbell", "4x10", "16kg 45s", "none", "C", "dp(2kg, 10, 15)", "YbX7Wd8jQ-Q",
   "swap to *sub: Skullcrusher, EZ Bar*", "OQ4TWXkZjTc", "Both hands under one dumbbell, elbows pointing forward, lower behind the head to a deep stretch."),
  ("extra: Reverse Fly, Leverage Machine", "3x12", "30kg 60s", "none", None, "dp(2.5kg, 12, 15)", "5YK4bgzXDp0",
   "swap to *sub: Face Pull*", "-MODnZdnmAQ", "Chest on the pad, arms slightly bent, sweep the handles back until the arms are in line with the shoulders."),
  ("SHRUG_REUSE", None, None, None, None, None, "_t3lrPI6Ns4",
   "swap to *sub: Shrug, Barbell*", "M_MjF5Nm_h4", "Full stretch at the bottom, shrug straight up, hold 1 second at the top. No rolling."),
  ("extra: Leg Press, Leverage Machine", "3x10", "80kg 120s", "1x8 50%", None, "dp(10kg, 10, 15)", "yZmx_Ac3880",
   "swap to *sub: Leg Extension*", "m0FOpMEgero", "Feet shoulder width, lower until the thighs nearly touch the torso. Keep the lower back on the pad. Plates only, not the sled."),
 ]},
}

SUBS = [
  # (line, video id, cue)
  ("sub: Pull Up, Leverage Machine / 3x6 40kg 120s / warmup: 1x5 55kg / progress: dp(-2.5kg, 6, 10)", "8ygapPMYK1I",
   "Assisted pull-up, overhand. Weight is the ASSISTANCE, lower is harder. Substitute for the lat pulldown."),
  ("sub: Lat Pulldown, Cable / 3x8 40kg 120s / warmup: 1x6 60% / progress: dp(2.5kg, 8, 12)", "GRHLNfmr_oI",
   "Neutral-grip pulldown, V-handle. Substitute for the chin-up."),
  ("sub: Bicep Curl, Dumbbell / 4x8 10kg 45s / warmup: none / progress: dp(2kg, 8, 12)", "iixND1P2lik",
   "Standing dumbbell curl. Substitute for the incline curl."),
  ("sub: Hammer Curl, Dumbbell / 4x8 10kg 45s / warmup: none / progress: dp(2kg, 8, 12)", "XOEL4MgekYE",
   "Substitute for the Bayesian cable curl."),
  ("sub: Preacher Curl, Leverage Machine / 4x8 25kg 45s / warmup: none / progress: dp(2.5kg, 8, 12)", "M_uPvGrMx_o",
   "Preacher curl machine. Substitute for the EZ bar preacher curl."),
  ("sub: Skullcrusher, EZ Bar / 4x10 15kg 45s / warmup: none / progress: dp(2.5kg, 10, 15)", "OQ4TWXkZjTc",
   "Weight includes the bar, about 8 kg. Substitute for the pushdown or the dumbbell overhead extension."),
  ("sub: Lateral Raise, Cable / 3x12 7.5kg 60s / warmup: none / progress: dp(1kg, 12, 15)", "lq7eLC30b9w",
   "Leaning cable lateral raise, one arm at a time. Substitute for the dumbbell lateral raise."),
  ("sub: Shrug, Barbell / 3x10 40kg 60s / warmup: none / progress: dp(5kg, 10, 15)", "M_MjF5Nm_h4",
   "Barbell or Smith machine shrug, total including the bar. Substitute for the dumbbell shrug."),
  ("sub: Incline Bench Press, Smith Machine / 3x6 30kg 120s / warmup: 1x8 50%, 1x4 75% / progress: dp(2.5kg, 6, 10)", "8urE8Z8AMQ4",
   "Total including the bar. Substitute for the incline dumbbell press."),
  ("sub: Incline Row, Dumbbell / 3x8 12kg 120s / warmup: none / progress: dp(2kg, 8, 12)", "Nx0TzjgsI-0",
   "Chest on an incline bench, dumbbells. Substitute for the chest-supported row machine."),
  ("sub: Shoulder Press, Dumbbell / 3x8 10kg 120s / warmup: none / progress: dp(2kg, 8, 12)", "HzIiNhHhhtA",
   "Seated dumbbell shoulder press. Substitute for the machine shoulder press."),
  ("sub: Chest Fly, Cable / 2x10 12.5kg 60s / warmup: none / progress: dp(2.5kg, 10, 15)", "4mfLHnFL0Uw",
   "Weight per side. Substitute for the pec deck."),
  ("sub: Lying Leg Curl, Leverage Machine / 3x8 35kg 120s / warmup: 1x6 60% / progress: dp(5kg, 8, 12)", "n5WDXD_mpVY",
   "Substitute for the seated leg curl."),
  ("sub: Face Pull, Cable / 3x12 20kg 60s / warmup: none / progress: dp(2.5kg, 12, 15)", "-MODnZdnmAQ",
   "Rope, pull to the face with elbows high. Substitute for the reverse pec deck."),
  ("sub: Leg Extension, Leverage Machine / 3x10 35kg 120s / warmup: 1x8 50% / progress: dp(2.5kg, 10, 15)", "m0FOpMEgero",
   "Substitute for the leg press."),
]

CHINUP = "main: Chin Up, Leverage Machine / 3x6 40kg 120s / warmup: 1x5 55kg / progress: dp(-2.5kg, 6, 10)"

out = []
out.append("""/// Upper-Body Hypertrophy, 3 days a week. Arms priority. Machines, no squat rack.
/// Paste this whole file into Liftosaur: Programs -> New program -> full text mode.
/// Starting weights assume roughly 75-85 kg with no lifting background. Adjust in week 1.

// **Read this first**
// * Mon / Wed / Fri, or any three non-consecutive days. A, B, C in order.
// * Every exercise note starts with a colour. 🟢 MAIN = presses and pulls, never skip. 🟠 ARMS = the pair, 45 sec between. ⚪ EXTRA = delts, flyes, legs, cut these if short on time.
// * Weeks 1 to 3: stop 3 to 4 reps short of failure. From week 4: 1 to 2 short. Last set of arm work can go to failure.
// * Progression is automatic: complete every prescribed rep and the app adds a rep next time, then weight at the top of the range.
// * Ramp-up sets are built in where needed. Nothing else needs a warm-up.
// * Every exercise note names its substitute and shows a video for both. Machine taken? Tap the exercise, Swap Exercise, pick the named one from the program list. It brings its own weight and progression.
// * Outside the gym: 1.6 to 2.2 g protein per kg, small calorie surplus, 3 to 5 g creatine daily, 7 to 9 hours sleep.
# Week 1
""")

for day, d in DAYS.items():
    out.append("")
    for line in d["desc"]:
        out.append("// " + line)
    out.append(f"## Day {day}")
    out.append("")
    for (name, sets, wt, wu, ss, prog, vid, subname, subvid, cue) in d["ex"]:
        group = name.split(":")[0] if ":" in name else ("main" if name == "CHINUP" else "extra")
        dot = {"main": "🟢 MAIN", "arms": "🟠 ARMS", "extra": "⚪ EXTRA"}[group]
        out.append(f"// {dot} · [▶ Watch]({yt}{vid}) · Sub: {subname} [▶ video]({yt}{subvid})")
        out.append(f"// {cue}")
        if name == "CHINUP":
            out.append(CHINUP)
        elif name == "SHRUG_REUSE":
            out.append("extra: Shrug, Dumbbell / 3x10 22kg 60s / warmup: none / progress: dp(2kg, 10, 15)")
        else:
            parts = [name, f"{sets} {wt}", f"warmup: {wu}"]
            if ss:
                parts.append(f"superset: {ss}")
            parts.append(f"progress: {prog}")
            out.append(" / ".join(parts))
        out.append("")

out.append("/// Hidden substitutes. They do not appear in any day. In a workout, tap Swap Exercise and pick one")
out.append("/// from the program exercises list: it comes with its own weight, sets, timer and progression.")
for (line, vid, cue) in SUBS:
    out.append(f"// ⚪ SUB · [▶ Watch]({yt}{vid})")
    out.append(f"// {cue}")
    out.append(line.replace(" / progress:", " / used: none / progress:"))
    out.append("")
text = "\n".join(out).rstrip() + "\n"
open(__import__("sys").argv[1] if len(__import__("sys").argv) > 1 else "program.txt", "w").write(text)
print(text)
