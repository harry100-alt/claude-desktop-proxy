yt = "https://www.youtube.com/watch?v="

# (liftosaur exercise line prefix, sets, weight+timer, warmup, superset, progress, main video id,
#  sub name, sub video id, cue)
DAYS = {
"A": {
 "desc": ["**First · never skip:** chest press, lat pulldown, cable row.",
          "**Middle · arms, paired:** incline curl + overhead extension.",
          "**Last · cut here if short on time:** lateral raise, shrug, hack squat.",
          "Machine taken? Do the next exercise and come back, or tap the exercise and swap to the substitute listed."],
 "ex": [
  ("Chest Press, Leverage Machine", "3x6", "35kg 120s", "1x8 50%, 1x4 75%", None, "dp(2.5kg, 6, 10)", "NwzUje3z0qY",
   "Flat dumbbell bench", "YQ2s_Y7g5Qk", "Handles at mid-chest height. Full stretch at the back, elbows about 45° from the body."),
  ("Lat Pulldown, Cable", "3x8", "40kg 120s", "1x6 60%", None, "dp(2.5kg, 8, 12)", "EUIri47Epcg",
   "Assisted pull-up", "8ygapPMYK1I", "Slight lean back, pull the bar to the upper chest, drive elbows down. Full stretch at the top."),
  ("Seated Row, Cable", "3x8", "40kg 120s", "none", None, "dp(2.5kg, 8, 12)", "UCXxvVItLoM",
   "Chest-supported row machine", "0UBRfiO4zDs", "Let the shoulder blades reach forward at the start, then pull to the lower ribs."),
  ("Incline Curl, Dumbbell", "4x8", "8kg 45s", "none", "A", "dp(2kg, 8, 12)", "aTYlqC_JacQ",
   "Standing dumbbell curl", "iixND1P2lik", "Bench at about 45°, arms hanging straight down and slightly back. Curl without moving the upper arm."),
  ("overhead: Triceps Extension, Cable", "4x10", "25kg 45s", "none", "A", "dp(2.5kg, 10, 15)", "kqidUIf1eJE",
   "Dumbbell overhead extension", "YbX7Wd8jQ-Q", "Overhead, rope. Face away from the stack, elbows by the ears, deep stretch behind the head each rep."),
  ("Lateral Raise, Dumbbell", "3x12", "6kg 60s", "none", None, "dp(1kg, 12, 15)", "3VcKaXpzqRo",
   "Cable lateral raise", "lq7eLC30b9w", "Slight forward lean, lead with the elbows, stop at shoulder height. Light weight, no swinging."),
  ("Shrug, Dumbbell", "3x10", "22kg 60s", "none", None, "dp(2kg, 10, 15)", "_t3lrPI6Ns4",
   "Barbell or Smith machine shrug", "M_MjF5Nm_h4", "Full stretch at the bottom, shrug straight up, hold 1 second at the top. No rolling."),
  ("Hack Squat, Leverage Machine", "3x8", "50kg 120s", "1x6 50%", None, "dp(10kg, 8, 12)", "rYgNArpwE7E",
   "Leg press", "yZmx_Ac3880", "Feet mid-platform, shoulder width. As deep as you can with heels down. Weight is plates only, not the sled."),
 ]},
"B": {
 "desc": ["**First · never skip:** incline press, chest-supported row, shoulder press.",
          "**Middle · arms, paired:** preacher curl + pushdown.",
          "**Last · cut here if short on time:** pec deck, leg curl.",
          "Machine taken? Do the next exercise and come back, or tap the exercise and swap to the substitute listed."],
 "ex": [
  ("Incline Bench Press, Dumbbell", "3x6", "12kg 120s", "1x8 50%, 1x4 75%", None, "dp(2kg, 6, 10)", "5CECBjd7HLQ",
   "Smith machine incline press", "8urE8Z8AMQ4", "30° bench. Deep stretch at upper-chest level, elbows about 45° out. Press up and slightly in."),
  ("Chest-Supported Row, Leverage Machine", "3x8", "35kg 120s", "1x6 60%", None, "dp(2.5kg, 8, 12)", "0UBRfiO4zDs",
   "Dumbbell row on an incline bench", "Nx0TzjgsI-0", "Chest glued to the pad. Pull elbows back and squeeze the shoulder blades together."),
  ("Shoulder Press, Leverage Machine", "3x8", "25kg 120s", "none", None, "dp(2.5kg, 8, 12)", "WvLMauqrnK8",
   "Seated dumbbell shoulder press", "HzIiNhHhhtA", "Start with handles at about chin height. Press up without flaring the ribs."),
  ("Preacher Curl, EZ Bar", "4x8", "15kg 45s", "none", "B", "dp(2.5kg, 8, 12)", "sxA__DoLsgo",
   "Preacher curl machine", "M_uPvGrMx_o", "Armpits on top of the pad. Lower almost to straight arms, then curl. No shoulder movement. Weight includes the bar, about 8 kg."),
  ("Triceps Pushdown, Cable", "4x10", "25kg 45s", "none", "B", "dp(2.5kg, 10, 15)", "6Fzep104f0s",
   "Skull crusher", "OQ4TWXkZjTc", "Elbows pinned to the sides. Push to lockout, let the forearms come up past 90° on the way back."),
  ("Pec Deck, Leverage Machine", "2x10", "35kg 60s", "none", None, "dp(2.5kg, 10, 15)", "O-OBCfyh9Fw",
   "Cable fly", "4mfLHnFL0Uw", "Handles at chest height. Open wide to a stretch, then bring the arms together with a slight elbow bend."),
  ("Seated Leg Curl, Leverage Machine", "3x8", "35kg 120s", "1x6 60%", None, "dp(5kg, 8, 12)", "Orxowest56U",
   "Lying leg curl", "n5WDXD_mpVY", "Pad just above the heels. Curl all the way down and control the return."),
 ]},
"C": {
 "desc": ["**First · never skip:** dumbbell bench, chin-up, one-arm row.",
          "**Middle · arms, paired:** Bayesian curl + dumbbell overhead extension.",
          "**Last · cut here if short on time:** reverse pec deck, shrug, leg press.",
          "Machine taken? Do the next exercise and come back, or tap the exercise and swap to the substitute listed."],
 "ex": [
  ("Bench Press, Dumbbell", "3x8", "14kg 120s", "1x8 50%, 1x4 75%", None, "dp(2kg, 8, 12)", "YQ2s_Y7g5Qk",
   "Machine chest press", "NwzUje3z0qY", "Shoulder blades back and down. Deep stretch beside the chest, press up and slightly in."),
  ("CHINUP", None, None, None, None, None, "9JC1EwqezGY",
   "Neutral-grip pulldown", "GRHLNfmr_oI", "Underhand grip, palms facing you, shoulder width. Weight here is the ASSISTANCE, lower is harder. Full hang, chin over the bar."),
  ("Bent Over One Arm Row, Dumbbell", "3x8", "16kg 120s", "none", None, "dp(2kg, 8, 12)", "k2kVniB5eQI",
   "Seated cable row", "UCXxvVItLoM", "Hand and knee on the bench. Let the dumbbell hang to a stretch, then row to the hip. No twisting."),
  ("Bicep Curl, Cable", "4x8", "12.5kg 45s", "none", "C", "dp(2.5kg, 8, 12)", "paM4Yo8fo8g",
   "Hammer curl", "XOEL4MgekYE", "Bayesian curl, one arm at a time. Low pulley behind you, step forward so the arm is stretched behind the torso. Upper arm fixed."),
  ("db: Triceps Extension, Dumbbell", "4x10", "16kg 45s", "none", "C", "dp(2kg, 10, 15)", "YbX7Wd8jQ-Q",
   "Skull crusher", "OQ4TWXkZjTc", "Both hands under one dumbbell, elbows pointing forward, lower behind the head to a deep stretch."),
  ("Reverse Fly, Leverage Machine", "3x12", "30kg 60s", "none", None, "dp(2.5kg, 12, 15)", "5YK4bgzXDp0",
   "Cable face pull", "-MODnZdnmAQ", "Chest on the pad, arms slightly bent, sweep the handles back until the arms are in line with the shoulders."),
  ("SHRUG_REUSE", None, None, None, None, None, "_t3lrPI6Ns4",
   "Barbell or Smith machine shrug", "M_MjF5Nm_h4", "Full stretch at the bottom, shrug straight up, hold 1 second at the top. No rolling."),
  ("Leg Press, Leverage Machine", "3x10", "80kg 120s", "1x8 50%", None, "dp(10kg, 10, 15)", "yZmx_Ac3880",
   "Leg extension", "m0FOpMEgero", "Feet shoulder width, lower until the thighs nearly touch the torso. Keep the lower back on the pad. Plates only, not the sled."),
 ]},
}

CHINUP = """Chin Up, Leverage Machine / 3x6 40kg 120s / warmup: 1x5 55kg / progress: custom() {~
  if (completedReps >= reps) {
    if (reps[1] < 10) {
      reps += 1
    } else {
      reps = 6
      weights -= 2.5kg
    }
  }
~}"""

out = []
out.append("""/// Upper-Body Hypertrophy, 3 days a week. Arms priority. Machines, no squat rack.
/// Paste this whole file into Liftosaur: Programs -> New program -> full text mode.
/// Starting weights assume roughly 75-85 kg with no lifting background. Adjust in week 1.

// **Read this first**
// * Mon / Wed / Fri, or any three non-consecutive days. A, B, C in order.
// * Each day: First group (press + pulls, never skip), then arms (paired, 45 sec between), then Last group (skippable).
// * Weeks 1 to 3: stop 3 to 4 reps short of failure. From week 4: 1 to 2 short. Last set of arm work can go to failure.
// * Progression is automatic: complete every prescribed rep and the app adds a rep next time, then weight at the top of the range.
// * Ramp-up sets are built in where needed. Nothing else needs a warm-up.
// * Every exercise lists a substitute with a video. Tap the exercise and use Swap if a machine is taken.
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
        out.append(f"// [▶ Watch]({yt}{vid}) · Sub: {subname} [▶ video]({yt}{subvid})")
        out.append(f"// {cue}")
        if name == "CHINUP":
            out.append(CHINUP)
        elif name == "SHRUG_REUSE":
            out.append("Shrug, Dumbbell / ...Shrug[1]")
        else:
            parts = [name, f"{sets} {wt}", f"warmup: {wu}"]
            if ss:
                parts.append(f"superset: {ss}")
            parts.append(f"progress: {prog}")
            out.append(" / ".join(parts))
        out.append("")

text = "\n".join(out).rstrip() + "\n"
open(__import__("sys").argv[1] if len(__import__("sys").argv) > 1 else "program.txt", "w").write(text)
print(text)
