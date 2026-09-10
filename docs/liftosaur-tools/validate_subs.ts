import * as fs from "fs";
import { PlannerProgram_generateFullText } from "../src/pages/planner/models/plannerProgram";
import { PlannerTestUtils_get } from "./utils/plannerTestUtils";
import { Settings_build } from "../src/models/settings";
import {
  Program_evaluate,
  Program_nextHistoryRecord,
  Program_nextHistoryEntry,
  Program_getDayData,
  Program_getAllProgramExercises,
  Program_runAllFinishDayScripts,
  Program_getDayExercisesInOrder,
} from "../src/models/program";
import { Stats_getEmpty } from "../src/models/stats";

// Usage: validate_subs.ts <program.txt>
// For every `used: none` exercise: start Day 1, replace the first entry with that hidden exercise
// (what the in-workout Swap -> program exercise does), complete every prescribed rep, run the
// finish-day scripts, and print the hidden exercise's line before and after.
const text = fs.readFileSync(process.argv[2], "utf8");
const settings = Settings_build();
settings.units = "kg";
const { program } = PlannerTestUtils_get(text);
const evaluated = Program_evaluate(program, settings);
const hidden = Program_getAllProgramExercises(evaluated).filter((e) => e.notused);
console.log(`Hidden (used: none) exercises: ${hidden.length}`);
for (let d = 1; d <= 3; d++) {
  const vis = Program_getDayExercisesInOrder(evaluated, d);
  console.log(`Day ${d} visible in workout: ${vis.length} -> ${vis.map((e) => e.fullName.split(":")[0] + ":" + e.fullName.split(":")[1].split(",")[0]).join(" | ")}`);
}

// Replicate the picker's "From Program" tab: group by exercise key in document order (first occurrence wins).
{
  const week = evaluated.weeks[0];
  const seen = new Set<string>(); const order: string[] = [];
  for (const day of week.days) for (const ex of day.exercises) { if (!seen.has(ex.key)) { seen.add(ex.key); order.push(ex.fullName); } }
  console.log(`Picker From Program order (${order.length} rows):`);
  order.forEach((n, i) => console.log(`  ${String(i + 1).padStart(2)}. ${n}`));
}

const visibleDay1 = Program_getDayData(evaluated, 1);
let ok = 0;
for (const h of hidden) {
  const rec = Program_nextHistoryRecord(program, settings, Stats_getEmpty(), 1);
  const entry = Program_nextHistoryEntry(evaluated, visibleDay1, 0, h, Stats_getEmpty(), settings);
  rec.entries[0] = entry;
  for (const set of rec.entries[0].sets) {
    set.completedReps = set.reps;
    set.completedWeight = set.weight;
    set.isCompleted = true;
  }
  const { program: after } = Program_runAllFinishDayScripts(program, rec, Stats_getEmpty(), settings);
  const key = h.fullName.split(",")[0];
  const before = text.split("\n").find((l) => l.startsWith(key)) || "?";
  const afterText = PlannerProgram_generateFullText(after.planner!.weeks);
  const afterLine = afterText.split("\n").find((l) => l.startsWith(key)) || "?";
  const progressed = afterLine !== "?" && before !== afterLine;
  ok += progressed ? 1 : 0;
  console.log(`${progressed ? "PROGRESSED" : "UNCHANGED "} ${h.fullName}`);
  console.log(`    before: ${before.replace(/ \/ warmup.*$/, "")}`);
  console.log(`    after:  ${afterLine.replace(/ \/ warmup.*$/, "")}`);
}
console.log(`\n${ok}/${hidden.length} hidden exercises progressed after a completed session.`);
