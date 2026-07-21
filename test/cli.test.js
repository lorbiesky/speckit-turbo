"use strict";

const assert = require("node:assert/strict");
const { execFileSync, spawnSync } = require("node:child_process");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");

const ROOT = path.resolve(__dirname, "..");
let packageBin;

function command(bin, args, cwd, env = {}) {
  return spawnSync(process.execPath, [bin, ...args], { cwd, encoding: "utf8", env: { ...process.env, ...env } });
}

test.before(() => {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), "speckit-turbo-npm-"));
  execFileSync("npm", ["pack", "--pack-destination", temp], { cwd: ROOT, stdio: "pipe" });
  const archive = fs.readdirSync(temp).find((file) => file.endsWith(".tgz"));
  execFileSync("npm", ["install", "--prefix", temp, path.join(temp, archive)], { stdio: "pipe" });
  packageBin = path.join(temp, "node_modules", ".bin", "speckit-turbo");
});

test("npm CLI initializes an existing project and runs the local Node runtime", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "speckit-turbo-project-"));
  fs.mkdirSync(path.join(root, ".specify/memory"), { recursive: true });
  fs.writeFileSync(path.join(root, ".specify/memory/constitution.md"), "constitution\n");
  const init = command(packageBin, ["init", root, "--mode", "existing"], ROOT, { PATH: "" });
  assert.equal(init.status, 0, init.stderr);
  assert.ok(fs.existsSync(path.join(root, ".specify/turbo/turbo.js")));
  assert.ok(fs.existsSync(path.join(root, ".specify/turbo/node-runtime/node_modules/yaml/package.json")));
  const runtime = command(path.join(root, ".specify/turbo/turbo.js"), ["workflow", "--path", root, "start", "feature", "--work-id", "npm-flow"], root, { PATH: "" });
  assert.equal(runtime.status, 0, runtime.stderr);
  assert.match(runtime.stdout, /feature \/ active \/ intake/);
  const complete = command(path.join(root, ".specify/turbo/turbo.js"), ["workflow", "--path", root, "complete", "intake", "--evidence", "classified_as_feature=classified", "--evidence", "scope_recorded=scope", "--evidence", "project_profile_loaded=profile"], root, { PATH: "" });
  assert.equal(complete.status, 0, complete.stderr);
  assert.match(complete.stdout, /feature \/ active \/ product-specification/);
  const upgrade = command(packageBin, ["upgrade", root], ROOT);
  assert.equal(upgrade.status, 0, upgrade.stderr);
});

test("npm CLI exposes doctor and version without Python", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "speckit-turbo-doctor-"));
  fs.mkdirSync(path.join(root, ".specify/memory"), { recursive: true });
  fs.writeFileSync(path.join(root, ".specify/memory/constitution.md"), "constitution\n");
  assert.equal(command(packageBin, ["init", root, "--mode", "existing"], ROOT).status, 0);
  const doctor = command(packageBin, ["doctor", root], ROOT);
  assert.notEqual(doctor.status, 0);
  assert.match(doctor.stdout, /Self-contained Node runtime is installed/);
  const version = command(packageBin, ["version", root], ROOT);
  assert.equal(version.status, 0);
  assert.match(version.stdout, /1\.0\.4/);
});

test("npm CLI bootstraps clean mode through the upstream command contract", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "speckit-turbo-clean-"));
  const bootstrap = "mkdir -p .specify/memory .specify/templates .specify/scripts && touch .specify/memory/constitution.md";
  const result = command(packageBin, ["init", root, "--mode", "clean", "--spec-kit-version", "v-test"], ROOT, { SPECKIT_TURBO_BOOTSTRAP_COMMAND: bootstrap });
  assert.equal(result.status, 0, result.stderr);
  assert.ok(fs.existsSync(path.join(root, ".specify/turbo/turbo.js")));
  assert.equal(JSON.parse(fs.readFileSync(path.join(root, ".specify/turbo/manifest.json"))).installation.mode, "clean");
});

test("npm upgrade backs up and removes only known legacy runtime files", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "speckit-turbo-legacy-"));
  fs.mkdirSync(path.join(root, ".specify/memory"), { recursive: true });
  fs.writeFileSync(path.join(root, ".specify/memory/constitution.md"), "constitution\n");
  assert.equal(command(packageBin, ["init", root, "--mode", "existing"], ROOT).status, 0);
  const turbo = path.join(root, ".specify/turbo");
  for (const name of ["doctor.py", "workflow_runtime.py", "version.py", "upgrade.sh"]) fs.writeFileSync(path.join(turbo, name), "legacy\n");
  fs.writeFileSync(path.join(turbo, "keep-me.txt"), "project-owned\n");
  assert.equal(command(packageBin, ["upgrade", root], ROOT).status, 0);
  for (const name of ["doctor.py", "workflow_runtime.py", "version.py", "upgrade.sh"]) assert.equal(fs.existsSync(path.join(turbo, name)), false);
  assert.equal(fs.readFileSync(path.join(turbo, "keep-me.txt"), "utf8"), "project-owned\n");
  const manifest = JSON.parse(fs.readFileSync(path.join(turbo, "manifest.json")));
  assert.deepEqual(manifest.legacyMigration.removed.sort(), [".specify/turbo/doctor.py", ".specify/turbo/upgrade.sh", ".specify/turbo/version.py", ".specify/turbo/workflow_runtime.py"].sort());
  assert.ok(fs.existsSync(path.join(root, manifest.installation.backup)));
});

function complete(root, phase, evidence) {
  const args = [path.join(root, ".specify/turbo/turbo.js"), "workflow", "--path", root, "complete", phase];
  for (const [key, value] of Object.entries(evidence)) args.push("--evidence", `${key}=${value}`);
  return command(args[0], args.slice(1), root);
}

function prepareFeatureThroughTdd(root) {
  assert.equal(command(path.join(root, ".specify/turbo/turbo.js"), ["workflow", "--path", root, "start", "feature", "--work-id", "tdd-flow"], root).status, 0);
  assert.equal(complete(root, "intake", { classified_as_feature: "classified", scope_recorded: "scope", project_profile_loaded: "profile" }).status, 0);
  assert.equal(complete(root, "product-specification", { problem_and_outcome_defined: "problem", testable_acceptance_criteria: "criteria", blocking_questions_resolved: "resolved", out_of_scope_declared: "scope" }).status, 0);
  assert.equal(complete(root, "technical-plan", { repository_evidence_cited: "repo", architecture_and_boundaries_defined: "boundaries", risks_and_mitigations_recorded: "risks", test_strategy_defined: "strategy" }).status, 0);
  assert.equal(complete(root, "task-decomposition", { every_acceptance_criterion_covered: "covered", dependencies_explicit: "deps", parallel_work_marked: "parallel", no_unresolved_spec_plan_conflicts: "consistent" }).status, 0);
}

test("TDD blocks implementation until red, green and refactor evidence exists", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "speckit-turbo-tdd-"));
  fs.mkdirSync(path.join(root, ".specify/memory"), { recursive: true });
  fs.writeFileSync(path.join(root, ".specify/memory/constitution.md"), "constitution\n");
  assert.equal(command(packageBin, ["init", root, "--mode", "existing"], ROOT).status, 0);
  prepareFeatureThroughTdd(root);
  const stateBeforeRed = JSON.parse(fs.readFileSync(path.join(root, ".specify/turbo/state.json")));
  assert.equal(stateBeforeRed.currentPhase, "tdd-preparation");
  const missingRed = complete(root, "tdd-preparation", { test_strategy_defined: "strategy" });
  assert.notEqual(missingRed.status, 0);
  assert.match(missingRed.stderr, /red_test_evidence_recorded/);
  assert.equal(complete(root, "tdd-preparation", { test_strategy_defined: "strategy", red_test_evidence_recorded: "test failed as expected" }).status, 0);
  const missingGreen = complete(root, "implementation", { implementation_matches_tasks: "matched", deviations_recorded: "none", repository_rules_followed: "yes" });
  assert.notEqual(missingGreen.status, 0);
  assert.match(missingGreen.stderr, /green_cycle_evidence_recorded/);
  assert.equal(complete(root, "implementation", { implementation_matches_tasks: "matched", deviations_recorded: "none", repository_rules_followed: "yes", green_cycle_evidence_recorded: "tests pass", refactor_evidence_recorded: "refactor validated" }).status, 0);
  const state = JSON.parse(fs.readFileSync(path.join(root, ".specify/turbo/state.json")));
  assert.equal(state.tdd.status, "completed");
  assert.equal(state.tdd.redEvidence[0], "test failed as expected");
});

test("TDD can be disabled explicitly and skips its phase", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "speckit-turbo-tdd-disabled-"));
  fs.mkdirSync(path.join(root, ".specify/memory"), { recursive: true });
  fs.writeFileSync(path.join(root, ".specify/memory/constitution.md"), "constitution\n");
  assert.equal(command(packageBin, ["init", root, "--mode", "existing"], ROOT).status, 0);
  const profilePath = path.join(root, ".specify/turbo/project.yml");
  fs.writeFileSync(profilePath, fs.readFileSync(profilePath, "utf8").replace("enabled: true\n  allow_exception", "enabled: false\n  allow_exception"));
  prepareFeatureThroughTdd(root);
  const state = JSON.parse(fs.readFileSync(path.join(root, ".specify/turbo/state.json")));
  assert.equal(state.tdd.enabled, false);
  assert.equal(state.tdd.status, "skipped");
  assert.equal(state.currentPhase, "implementation");
});

test("TDD exception remains paused until human approval", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "speckit-turbo-tdd-exception-"));
  fs.mkdirSync(path.join(root, ".specify/memory"), { recursive: true });
  fs.writeFileSync(path.join(root, ".specify/memory/constitution.md"), "constitution\n");
  assert.equal(command(packageBin, ["init", root, "--mode", "existing"], ROOT).status, 0);
  prepareFeatureThroughTdd(root);
  const runtime = path.join(root, ".specify/turbo/turbo.js");
  const exception = command(runtime, ["workflow", "--path", root, "exception", "tdd-preparation", "--reason", "config-only", "--risk", "low", "--validation", "lint"], root);
  assert.equal(exception.status, 0, exception.stderr);
  let state = JSON.parse(fs.readFileSync(path.join(root, ".specify/turbo/state.json")));
  assert.equal(state.status, "paused");
  assert.equal(state.tdd.exception.approval, "pending");
  const approved = command(runtime, ["workflow", "--path", root, "checkpoint", "tdd-preparation", "--approve"], root);
  assert.equal(approved.status, 0, approved.stderr);
  state = JSON.parse(fs.readFileSync(path.join(root, ".specify/turbo/state.json")));
  assert.equal(state.currentPhase, "implementation");
  const implementation = complete(root, "implementation", { implementation_matches_tasks: "matched", deviations_recorded: "exception documented", repository_rules_followed: "yes" });
  assert.equal(implementation.status, 0, implementation.stderr);
});

test("public documentation uses agent commands instead of Node workflow scripts", () => {
  const files = [
    path.join(ROOT, "README.md"),
    path.join(ROOT, "AGENTS.turbo.md"),
    ...fs.readdirSync(path.join(ROOT, "docs")).filter((name) => name.endsWith(".md")).map((name) => path.join(ROOT, "docs", name)),
    ...fs.readdirSync(path.join(ROOT, "skills")).flatMap((name) => [path.join(ROOT, "skills", name, "SKILL.md")]).filter((file) => fs.existsSync(file)),
  ];
  const text = files.map((file) => fs.readFileSync(file, "utf8")).join("\n");
  for (const forbidden of ["node .specify/turbo/turbo.js", "workflow --path", "--visual-input"]) assert.equal(text.includes(forbidden), false, `forbidden public command: ${forbidden}`);
  for (const shortcut of ["$turbo", "$turbo-feature", "$turbo-bugfix", "$turbo-refactor", "$turbo-discovery", "$turbo-maintenance", "$turbo-hotfix", "$turbo-constitution", "$turbo-status", "$turbo-resume"]) assert.equal(text.includes(shortcut), true, `missing shortcut: ${shortcut}`);
  for (const commandName of ["init", "doctor", "upgrade", "version"]) assert.equal(text.includes(`speckit-turbo@latest ${commandName}`), true, `missing npm command: ${commandName}`);
  assert.equal(text.includes("$speckit-"), true);
});
