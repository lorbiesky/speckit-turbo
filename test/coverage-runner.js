"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { main } = require("../src/cli.js");

function project(prefix) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), prefix));
  fs.mkdirSync(path.join(root, ".specify/memory"), { recursive: true });
  fs.writeFileSync(path.join(root, ".specify/memory/constitution.md"), "constitution\n");
  return root;
}

function evidenceFor(phase) {
  return Object.keys(phase.gate.requirements || {}).flatMap((key) => ["--evidence", `${key}=text|coverage evidence for ${key}`]);
}

function smokeWorkflow(root, classification) {
  main(["init", root, "--mode", "existing"]);
  const profilePath = path.join(root, ".specify/turbo/project.yml");
  fs.writeFileSync(profilePath, fs.readFileSync(profilePath, "utf8").replace("enabled: true\n  allow_exception", "enabled: false\n  allow_exception"));
  main(["workflow", "--path", root, "start", classification, "--work-id", `coverage-${classification}`]);
  for (let iteration = 0; iteration < 30; iteration += 1) {
    const statePath = path.join(root, ".specify/turbo/state.json");
    const state = JSON.parse(fs.readFileSync(statePath));
    if (state.status === "completed") return;
    const phase = state.phases.find((item) => item.id === state.currentPhase);
    assert.ok(phase);
    if (state.status === "paused") {
      main(["workflow", "--path", root, "checkpoint", phase.id, "--approve"]);
    } else {
      assert.equal(phase.status, "active");
      main(["workflow", "--path", root, "complete", phase.id, ...evidenceFor(phase)]);
    }
  }
  assert.fail(`${classification} did not complete in coverage runner`);
}

function expectFailure(args, pattern) {
  const previousExit = process.exit;
  process.exit = (code) => { throw new Error(`EXIT:${code}`); };
  try { main(args); assert.fail("expected CLI failure"); }
  catch (error) { assert.match(error.message, pattern); }
  finally { process.exit = previousExit; }
}

for (const classification of ["feature", "bugfix", "refactor", "discovery", "maintenance", "hotfix", "constitution"]) smokeWorkflow(project(`speckit-turbo-coverage-${classification}-`), classification);

const visualRoot = project("speckit-turbo-coverage-visual-");
main(["init", visualRoot, "--mode", "existing"]);
main(["workflow", "--path", visualRoot, "start", "feature", "--work-id", "coverage-visual", "--visual-input", "attached.png"]);
let visualState = JSON.parse(fs.readFileSync(path.join(visualRoot, ".specify/turbo/state.json")));
main(["workflow", "--path", visualRoot, "complete", "intake", ...evidenceFor(visualState.phases.find((phase) => phase.id === "intake"))]);
visualState = JSON.parse(fs.readFileSync(path.join(visualRoot, ".specify/turbo/state.json")));
assert.equal(visualState.currentPhase, "visual-analysis");
main(["workflow", "--path", visualRoot, "complete", "visual-analysis", ...evidenceFor(visualState.phases.find((phase) => phase.id === "visual-analysis"))]);

const copilotRoot = project("speckit-turbo-coverage-copilot-");
fs.mkdirSync(path.join(copilotRoot, ".github/prompts"), { recursive: true });
main(["init", copilotRoot, "--mode", "existing"]);
const claudeRoot = project("speckit-turbo-coverage-claude-");
fs.mkdirSync(path.join(claudeRoot, ".claude/commands"), { recursive: true });
main(["init", claudeRoot, "--mode", "existing"]);

const cleanRefusal = project("speckit-turbo-coverage-clean-refusal-");
expectFailure(["init", cleanRefusal, "--mode", "clean", "--spec-kit-version", "v-test"], /EXIT:/);
const existingRefusal = fs.mkdtempSync(path.join(os.tmpdir(), "speckit-turbo-coverage-existing-refusal-"));
expectFailure(["init", existingRefusal, "--mode", "existing"], /EXIT:/);
const cleanMissingRef = fs.mkdtempSync(path.join(os.tmpdir(), "speckit-turbo-coverage-clean-ref-") );
expectFailure(["init", cleanMissingRef, "--mode", "clean"], /EXIT:/);
const bootstrapFailure = fs.mkdtempSync(path.join(os.tmpdir(), "speckit-turbo-coverage-bootstrap-failure-"));
const previousFailureCommand = process.env.SPECKIT_TURBO_BOOTSTRAP_COMMAND;
process.env.SPECKIT_TURBO_BOOTSTRAP_COMMAND = "exit 7";
expectFailure(["init", bootstrapFailure, "--mode", "clean", "--spec-kit-version", "v-test"], /EXIT:/);
if (previousFailureCommand === undefined) delete process.env.SPECKIT_TURBO_BOOTSTRAP_COMMAND;
else process.env.SPECKIT_TURBO_BOOTSTRAP_COMMAND = previousFailureCommand;
const malformedIgnore = project("speckit-turbo-coverage-ignore-");
fs.writeFileSync(path.join(malformedIgnore, ".gitignore"), "# speckit-turbo:start\n");
expectFailure(["init", malformedIgnore, "--mode", "existing"], /EXIT:/);
const missingSkill = project("speckit-turbo-coverage-missing-skill-");
main(["init", missingSkill, "--mode", "existing"]);
fs.rmSync(path.join(missingSkill, ".agents/skills/turbo-feature"), { recursive: true });
expectFailure(["doctor", missingSkill, "--strict"], /EXIT:1/);
const upgradeRoot = project("speckit-turbo-coverage-upgrade-");
main(["init", upgradeRoot, "--mode", "existing"]);
for (const legacy of ["doctor.py", "workflow_runtime.py", "version.py", "upgrade.sh"]) fs.writeFileSync(path.join(upgradeRoot, ".specify/turbo", legacy), "legacy");
main(["upgrade", upgradeRoot]);
main(["upgrade", upgradeRoot]);
expectFailure(["workflow", "--path", upgradeRoot, "unknown"] , /EXIT:/);
const parseRoot = project("speckit-turbo-coverage-parse-");
main(["init", parseRoot, "--mode", "existing"]);
main(["workflow", "--path", parseRoot, "start", "feature", "--work-id", "coverage-parse"]);
let parseState = JSON.parse(fs.readFileSync(path.join(parseRoot, ".specify/turbo/state.json")));
const intake = parseState.phases.find((phase) => phase.id === "intake");
const intakeEvidence = evidenceFor(intake);
intakeEvidence[intakeEvidence.indexOf("--evidence") + 1] = "classified_as_feature={\"type\":\"artifact\",\"reference\":\".specify/memory/constitution.md#AC-001\",\"status\":\"passed\",\"result\":\"constitution inspected\"}";
main(["workflow", "--path", parseRoot, "complete", "intake", ...intakeEvidence]);
expectFailure(["workflow", "--path", parseRoot, "complete", "product-specification", "--evidence", "problem_and_outcome_defined={bad-json"], /EXIT:/);
parseState = JSON.parse(fs.readFileSync(path.join(parseRoot, ".specify/turbo/state.json")));
parseState.decisions.push({ id: "DEC-COVERAGE", summary: "Use the existing constitution as product context" });
fs.writeFileSync(path.join(parseRoot, ".specify/turbo/state.json"), `${JSON.stringify(parseState, null, 2)}\n`);
const productEvidence = evidenceFor(parseState.phases.find((phase) => phase.id === "product-specification"));
productEvidence[productEvidence.indexOf("--evidence") + 1] = "problem_and_outcome_defined=decision|DEC-COVERAGE|passed|decision recorded";
main(["workflow", "--path", parseRoot, "complete", "product-specification", ...productEvidence]);
expectFailure(["workflow", "--path", parseRoot, "complete", "product-specification", "--evidence", "problem_and_outcome_defined=artifact|missing.md|passed|missing"], /EXIT:/);
expectFailure(["doctor"], /EXIT:/);
expectFailure(["workflow", "--path", parseRoot, "start", "does-not-exist", "--work-id", "coverage-missing"], /EXIT:/);
expectFailure([], /EXIT:/);

const cleanRoot = fs.mkdtempSync(path.join(os.tmpdir(), "speckit-turbo-coverage-clean-"));
const previousBootstrap = process.env.SPECKIT_TURBO_BOOTSTRAP_COMMAND;
process.env.SPECKIT_TURBO_BOOTSTRAP_COMMAND = "mkdir -p .specify/memory .specify/templates .specify/scripts && touch .specify/memory/constitution.md";
try { main(["init", cleanRoot, "--mode", "clean", "--spec-kit-version", "v-test"]); }
finally {
  if (previousBootstrap === undefined) delete process.env.SPECKIT_TURBO_BOOTSTRAP_COMMAND;
  else process.env.SPECKIT_TURBO_BOOTSTRAP_COMMAND = previousBootstrap;
}

const previousExit = process.exit;
process.exit = (code) => { throw new Error(`EXIT:${code}`); };
try { main(["doctor", cleanRoot]); } catch (error) { assert.match(error.message, /EXIT:/); }
finally { process.exit = previousExit; }
