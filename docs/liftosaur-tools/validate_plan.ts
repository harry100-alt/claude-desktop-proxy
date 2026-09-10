import * as fs from "fs";
import {
  PlannerProgram_evaluateText,
  PlannerProgram_evaluate,
  PlannerProgram_generateFullText,
} from "../src/pages/planner/models/plannerProgram";
import { PlannerTestUtils_finish, PlannerTestUtils_get } from "./utils/plannerTestUtils";
import { Settings_build } from "../src/models/settings";
import { Program_nextHistoryRecord } from "../src/models/program";
import { Stats_getEmpty } from "../src/models/stats";
import { IPlannerProgram } from "../src/types";

const programText = fs.readFileSync(process.argv[2], "utf8");

const planner: IPlannerProgram = { vtype: "planner", name: "Upper Body 3 Day", weeks: PlannerProgram_evaluateText(programText) };
const settings = Settings_build();
settings.units = "kg";
const evaluated = PlannerProgram_evaluate(planner, settings).evaluatedWeeks;
const errors: string[] = [];
evaluated.forEach((week, wi) =>
  week.forEach((day, di) => {
    if (!day.success) {
      errors.push(`Week ${wi + 1} Day ${di + 1}: ${day.error.message}`);
    }
  })
);
if (errors.length) {
  console.log("ERRORS:");
  errors.forEach((e) => console.log("  " + e));
  process.exit(1);
}
console.log("Parse/evaluate OK.");
evaluated[0].forEach((day, di) => {
  if (day.success) {
    console.log(`Day ${di + 1}: ${day.data.length} exercises`);
    day.data.forEach((ex) => {
      const sets = (ex.setVariations[0]?.sets ?? (ex as any).reuse?.exercise?.setVariations?.[0]?.sets ?? [])
        .map((s) => `${s.repRange?.numberOfSets}x${s.repRange?.maxrep} ${s.weight ? s.weight.value + s.weight.unit : ""} ${s.timer ? s.timer + "s" : ""}`)
        .join(", ");
      const wu = ex.warmupSets ? ex.warmupSets.map((w) => `${w.numberOfSets}x${w.reps} ${w.weight ? w.weight.value + w.weight.unit : (w.percentage ?? "") + "%"}`).join(", ") : "default";
      console.log(`  ${ex.fullName.padEnd(42)} ${sets.padEnd(22)} warmup: ${wu.padEnd(24)} superset: ${ex.superset ? JSON.stringify(ex.superset) : "-"}`);
    });
  }
});

// Simulate: complete every set of Day A, B, C with all prescribed reps, N rounds, and print the resulting program text
const rounds = parseInt(process.argv[3] || "2", 10);
let text = PlannerProgram_generateFullText(planner.weeks);
for (let round = 1; round <= rounds; round++) {
  for (let day = 1; day <= 3; day++) {
    const { program } = PlannerTestUtils_get(text);
    const rec = Program_nextHistoryRecord(program, settings, Stats_getEmpty(), day);
    const completedReps = rec.entries.map((e) => e.sets.map((s) => s.reps ?? 0));
    const { program: after } = PlannerTestUtils_finish(text, { completedReps }, settings, Stats_getEmpty(), day);
    text = PlannerProgram_generateFullText(after.planner!.weeks);
  }
}
console.log(`\nAfter ${rounds} full rounds with every prescribed rep completed:\n`);
console.log(text);
