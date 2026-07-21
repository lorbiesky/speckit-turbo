#!/usr/bin/env node
"use strict";

// Self-contained operational CLI.  The same file is copied to consumer
// projects together with yaml, so workflow control never needs Python.
const fs = require("node:fs");
const fsp = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");
const YAML = require("yaml");

const PACKAGE_ROOT = path.resolve(__dirname, "..");
const START = "<!-- speckit-turbo:start -->", END = "<!-- speckit-turbo:end -->";
const IGNORE_START = "# speckit-turbo:start", IGNORE_END = "# speckit-turbo:end", IGNORE_ENTRY = ".specify/visual-references/";
const SIGNALS = ["memory/constitution.md", "templates", "scripts"];
const LEGACY_FILES = ["doctor.py", "workflow_runtime.py", "version.py", "upgrade.sh"];
const REQUIRED_SKILLS = ["turbo", "turbo-status", "turbo-resume", "turbo-orchestrator", "turbo-product-owner", "turbo-architect", "turbo-implementation-specialist", "turbo-test-engineer", "turbo-code-reviewer", "turbo-constitution-facilitator", "turbo-visual-specifier", "turbo-tdd-coach"];

const exists = (file) => fs.existsSync(file);
const read = (file) => fs.readFileSync(file, "utf8");
const json = (file) => JSON.parse(read(file));
const writeJson = (file, value) => fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
const copy = (from, to) => fs.cpSync(from, to, { recursive: true, force: true });
const remove = (file) => fs.rmSync(file, { recursive: true, force: true });
const now = () => new Date().toISOString();

function fail(message, code = 2) { console.error(`Spec Kit Turbo: ${message}`); process.exit(code); }
function argValue(args, name) { const i = args.indexOf(name); return i < 0 ? undefined : args[i + 1]; }
function has(args, name) { return args.includes(name); }
function targetFrom(args) {
  const valueFlags = new Set(["--mode", "--spec-kit-version"]);
  for (let index = 0; index < args.length; index += 1) {
    if (valueFlags.has(args[index])) { index += 1; continue; }
    if (!args[index].startsWith("-")) return path.resolve(args[index]);
  }
  return path.resolve(".");
}
function profile(root) { return YAML.parse(read(path.join(root, ".specify/turbo/project.yml"))) || {}; }
function workflow(root, classification) {
  const dir = path.join(root, ".specify/turbo/runtime/workflows");
  for (const file of fs.readdirSync(dir).filter((item) => item.endsWith(".yml"))) {
    const value = YAML.parse(read(path.join(dir, file)));
    if (value.classification === classification) return value;
  }
  throw new Error(`No installed workflow handles classification '${classification}'`);
}
function structured(root) { return SIGNALS.filter((signal) => exists(path.join(root, ".specify", signal))); }
function integration(root) {
  if (exists(path.join(root, ".agents/skills")) && fs.readdirSync(path.join(root, ".agents/skills")).some((name) => name.startsWith("speckit-"))) return "codex";
  if (exists(path.join(root, ".github/prompts")) || exists(path.join(root, ".github/agents"))) return "copilot";
  if (exists(path.join(root, ".claude/commands"))) return "claude";
  return "unknown";
}
function managedIgnore(root) {
  const file = path.join(root, ".gitignore"), content = exists(file) ? read(file) : "";
  const start = content.indexOf(IGNORE_START), end = content.indexOf(IGNORE_END);
  if ((start >= 0) !== (end >= 0) || (start >= 0 && end < start)) throw new Error(".gitignore contains a malformed Spec Kit Turbo visual-reference block");
  const block = `${IGNORE_START}\n${IGNORE_ENTRY}\n${IGNORE_END}`;
  const next = start >= 0 ? content.slice(0, start) + block + content.slice(end + IGNORE_END.length) : content + (content && !content.endsWith("\n") ? "\n" : "") + block + "\n";
  if (next !== content) fs.writeFileSync(file, next);
}
function backup(turbo, version) {
  if (!exists(turbo)) return null;
  const destination = path.join(turbo, "backups", `${now().replace(/[-:.]/g, "")}-${version || "unknown"}`);
  fs.mkdirSync(destination, { recursive: true });
  for (const name of ["AGENTS.turbo.md", "doctor.py", "workflow_runtime.py", "version.py", "upgrade.sh", "manifest.json", "project.yml", "state.json", "runtime", "templates", "node-runtime", "turbo.js"]) {
    if (exists(path.join(turbo, name))) copy(path.join(turbo, name), path.join(destination, name));
  }
  return destination;
}
function migrateLegacy(turbo) {
  const removed = [];
  for (const name of LEGACY_FILES) {
    const file = path.join(turbo, name);
    if (exists(file)) { remove(file); removed.push(`.specify/turbo/${name}`); }
  }
  return removed;
}
function snapshot(root) {
  const temp = fs.mkdtempSync(path.join(os.tmpdir(), "speckit-turbo-"));
  const names = [".specify", ".agents", ".github", ".claude", "AGENTS.md", ".gitignore"];
  return { temp, names: names.map((name) => ({ name, present: exists(path.join(root, name)), source: path.join(temp, name) })).map((item) => { if (item.present) copy(path.join(root, item.name), item.source); return item; }) };
}
function restore(root, snap) { for (const item of snap.names) { remove(path.join(root, item.name)); if (item.present) copy(item.source, path.join(root, item.name)); } remove(snap.temp); }
function bootstrap(root, ref) {
  const command = process.env.SPECKIT_TURBO_BOOTSTRAP_COMMAND || `uv tool run --from git+https://github.com/github/spec-kit.git@${ref} specify init --here --integration codex --ignore-agent-tools`;
  const result = spawnSync(command, { cwd: root, shell: true, stdio: "inherit" });
  if (result.status !== 0) throw new Error(`Spec Kit bootstrap failed with exit code ${result.status}`);
}
function copyRuntime(root) {
  const turbo = path.join(root, ".specify/turbo"), runtime = path.join(turbo, "node-runtime");
  remove(runtime); fs.mkdirSync(path.join(runtime, "node_modules"), { recursive: true });
  copy(path.join(PACKAGE_ROOT, "src"), runtime);
  const yamlRoot = path.dirname(require.resolve("yaml/package.json"));
  copy(yamlRoot, path.join(runtime, "node_modules/yaml"));
  fs.writeFileSync(path.join(turbo, "turbo.js"), "#!/usr/bin/env node\nrequire('./node-runtime/cli.js').main();\n");
}
function install(args) {
  const root = targetFrom(args); if (!exists(root) || !fs.statSync(root).isDirectory()) fail(`Target directory does not exist: ${root}`);
  const requested = argValue(args, "--mode") || "auto", signals = structured(root);
  const mode = requested === "auto" ? (signals.length ? "existing" : "clean") : requested;
  if (mode === "clean" && signals.length) fail(`Refusing clean mode: structured Spec Kit installation detected (${signals.join(", ")})`);
  if (mode === "existing" && !signals.length) fail("Refusing existing mode: no structured Spec Kit installation detected");
  const turbo = path.join(root, ".specify/turbo"), oldManifest = exists(path.join(turbo, "manifest.json")) ? json(path.join(turbo, "manifest.json")) : null;
  if (exists(turbo) && !oldManifest && fs.readdirSync(turbo).length) fail("Refusing installation: .specify/turbo exists without a Turbo manifest");
  let ref = argValue(args, "--spec-kit-version") || oldManifest?.installation?.specKitVersion;
  let detected = mode === "existing" ? integration(root) : "codex";
  if (mode === "clean") {
    if (!ref) fail("Clean mode requires --spec-kit-version <ref>");
    const snap = snapshot(root);
    try { managedIgnore(root); bootstrap(root, ref); } catch (error) { restore(root, snap); fail(error.message, 1); }
    remove(snap.temp); detected = integration(root);
  }
  try { managedIgnore(root); } catch (error) { fail(error.message); }
  const saved = oldManifest ? backup(turbo, oldManifest.turboVersion) : null;
  const legacyRemoved = oldManifest ? migrateLegacy(turbo) : [];
  fs.mkdirSync(turbo, { recursive: true });
  fs.mkdirSync(path.join(root, ".agents/skills"), { recursive: true });
  for (const skill of fs.readdirSync(path.join(PACKAGE_ROOT, "skills")).filter((name) => name.startsWith("turbo"))) copy(path.join(PACKAGE_ROOT, "skills", skill), path.join(root, ".agents/skills", skill));
  copy(path.join(PACKAGE_ROOT, "schemas"), path.join(turbo, "runtime/schemas")); copy(path.join(PACKAGE_ROOT, "workflows"), path.join(turbo, "runtime/workflows"));
  fs.mkdirSync(path.join(turbo, "templates"), { recursive: true }); for (const name of ["constitution-interview.md", "constitution.draft.md", "visual-spec.md", "tdd-cycle.md"]) copy(path.join(PACKAGE_ROOT, "templates", name), path.join(turbo, "templates", name));
  copyRuntime(root);
  if (!exists(path.join(turbo, "project.yml"))) copy(path.join(PACKAGE_ROOT, "templates/project.yml"), path.join(turbo, "project.yml"));
  if (!exists(path.join(turbo, "state.json"))) copy(path.join(PACKAGE_ROOT, "templates/state.json"), path.join(turbo, "state.json"));
  const manifest = json(path.join(PACKAGE_ROOT, "manifest.json")); manifest.installation = { mode, integration: detected, specKitVersion: ref || null, bootstrap: mode === "clean", backup: saved ? path.relative(root, saved) : null }; if (legacyRemoved.length) manifest.legacyMigration = { removed: legacyRemoved, backup: saved ? path.relative(root, saved) : null, migratedAt: now() }; writeJson(path.join(turbo, "manifest.json"), manifest);
  const agents = path.join(root, "AGENTS.md"), content = exists(agents) ? read(agents) : "";
  if (!content.includes(START)) fs.writeFileSync(agents, `${content}${content && !content.endsWith("\n") ? "\n" : ""}${START}\n## Spec Kit Turbo\n\nUse \`$turbo\` to start or resume work. The local Node runtime is \`.specify/turbo/turbo.js\`; do not edit workflow state by hand.\n${END}\n`);
  console.log(`Spec Kit Turbo ${manifest.turboVersion} installed in ${root} (${mode}).`); if (detected !== "codex") console.warn(`Warning: '${detected}' integration is preserved; Turbo commands are Codex-first.`);
}

function phaseById(state, id) { const phase = state.phases.find((item) => item.id === id); if (!phase) throw new Error(`Unknown phase '${id}'`); return phase; }
function tddEnabled(config) { return Boolean(config.tdd && config.tdd.enabled === true); }
function tddState(state, config) {
  if (!state.tdd) state.tdd = { enabled: tddEnabled(config), status: tddEnabled(config) ? "not_started" : "skipped", artifactPath: ".specify/turbo/tdd-cycle.md", redEvidence: [], greenEvidence: [], refactorEvidence: [], exception: null };
  return state.tdd;
}
function facts(state, definition) { return new Set(state.phases.filter((phase) => phase.status === "completed" && phase.gate.passed || phase.status === "skipped" && phase.gate.passed && definition.get(phase.id)?.satisfies_on_skip).flatMap((phase) => definition.get(phase.id).provides || [])); }
function applies(condition, state, config) { if (!condition) return true; const visual = state.visualAnalysis || {}, inputs = visual.inputs || []; if (condition === "visual_input_present") return config.visual?.enabled !== false && inputs.length > 0; if (condition === "visual_input_absent_or_completed") return !inputs.length || ["completed", "skipped"].includes(visual.status); if (condition === "tdd_enabled") return tddEnabled(config); throw new Error(`Unsupported workflow condition '${condition}'`); }
function requirements(definition, config, state) {
  const result = [...(definition.gate.require || [])];
  for (const [condition, values] of Object.entries(definition.gate.require_when || {})) if (applies(condition, state, config)) result.push(...values);
  if (state.tdd?.exception?.approval === "approved") return result.filter((value) => !["red_test_evidence_recorded", "green_cycle_evidence_recorded", "refactor_evidence_recorded"].includes(value));
  return [...new Set(result)];
}
function advance(state, flow, config) {
  const defs = new Map(flow.phases.map((phase) => [phase.id, phase])); const done = facts(state, defs); tddState(state, config);
  for (const phase of state.phases) {
    if (["completed", "skipped"].includes(phase.status)) continue; const def = defs.get(phase.id);
    if (!applies(def.condition, state, config)) { phase.status = "skipped"; phase.gate.passed = true; phase.gate.reason = `Condition '${def.condition}' is not applicable.`; if (phase.id === "visual-analysis") state.visualAnalysis.status = "skipped"; if (def.id === "tdd-preparation") state.tdd.status = "skipped"; for (const provided of def.provides || []) if (def.satisfies_on_skip) done.add(provided); continue; }
    const missing = (def.preconditions || []).filter((fact) => !done.has(fact)); if (missing.length) { phase.status = "blocked"; phase.gate.reason = `Missing preconditions: ${missing.join(", ")}`; state.status = "blocked"; state.currentPhase = phase.id; state.nextAction = "Resolve the declared preconditions before resuming."; return; }
    phase.status = "active"; if (phase.id === "visual-analysis") state.visualAnalysis.status = "active"; if (phase.id === "tdd-preparation") state.tdd.status = "not_started"; state.status = "active"; state.currentPhase = phase.id; phase.gate.requirements = Object.fromEntries(requirements(def, config, state).map((key) => [key, phase.gate.requirements?.[key] || ""])); state.nextAction = `Complete '${phase.id}' and record evidence for every declared gate requirement.`; return;
  }
  state.status = "completed"; state.currentPhase = state.phases.at(-1).id; state.nextAction = "Workflow completed. Review the delivery summary and follow-ups.";
}
function runtime(args) {
  const root = path.resolve(argValue(args, "--path") || "."), filtered = args.filter((value, index) => value !== "--path" && args[index - 1] !== "--path"), command = filtered[0];
  const stateFile = path.join(root, ".specify/turbo/state.json");
  if (command === "start") {
    const classification = filtered[1], workId = argValue(filtered, "--work-id"); if (!classification || !workId) fail("workflow start requires <classification> and --work-id");
    const old = exists(stateFile) ? json(stateFile) : {}; if (old.workId && old.workId !== "replace-with-work-id" && !has(filtered, "--force")) fail("State already exists; use resume or --force");
    const flow = workflow(root, classification), inputs = filtered.flatMap((item, index) => item === "--visual-input" ? [filtered[index + 1]] : []).filter(Boolean), config = profile(root), enabled = tddEnabled(config);
    const state = { version: "1.0", workId, classification, workflow: flow.name, status: "draft", currentPhase: flow.phases[0].id, phases: flow.phases.map((def) => ({ id: def.id, status: "pending", owner: def.owner, artifacts: def.outputs || [], gate: { passed: null, evidence: [], requirements: {} } })), decisions: [], openQuestions: [], validations: [], deviations: [], tdd: { enabled, status: enabled ? "not_started" : "skipped", artifactPath: ".specify/turbo/tdd-cycle.md", redEvidence: [], greenEvidence: [], refactorEvidence: [], exception: null }, visualAnalysis: { status: "not_started", inputs, visualSpecPath: "visual-spec.md", persistedReferencesPath: ".specify/visual-references", confidence: "low", unresolvedQuestions: [], acceptanceCriteria: [] }, nextAction: "Start the first applicable workflow phase.", updatedAt: now() };
    advance(state, flow, profile(root)); writeJson(stateFile, state); return status(root, state, flow);
  }
  const state = json(stateFile), flow = workflow(root, state.classification), defs = new Map(flow.phases.map((phase) => [phase.id, phase]),); const config = profile(root); tddState(state, config);
  if (command === "status") { if (has(filtered, "--refresh") && !["completed", "cancelled", "paused"].includes(state.status)) { advance(state, flow, config); writeJson(stateFile, state); } return status(root, state, flow); }
  if (command === "complete") { const id = filtered[1], phase = phaseById(state, id); if (phase.status !== "active") fail(`Phase '${id}' is ${phase.status}, not active`); const def = defs.get(id), activeRequirements = requirements(def, config, state), evidence = {}; filtered.forEach((value, index) => { if (value === "--evidence") { const [key, ...rest] = (filtered[index + 1] || "").split("="); evidence[key] = rest.join("="); } }); for (const key of Object.keys(evidence)) if (!activeRequirements.includes(key)) fail(`Evidence references undeclared requirement '${key}'`); Object.assign(phase.gate.requirements, evidence); const missing = activeRequirements.filter((key) => !phase.gate.requirements[key]); if (missing.length) fail(`Missing evidence for: ${missing.join(", ")}`); phase.gate.evidence = Object.entries(phase.gate.requirements).map(([key, value]) => `${key}: ${value}`); phase.gate.passed = true; if (id === "visual-analysis") state.visualAnalysis.status = "completed"; if (id === "tdd-preparation") { state.tdd.status = "red_ready"; state.tdd.redEvidence = [phase.gate.requirements.red_test_evidence_recorded]; } if (id === "implementation" && state.tdd.enabled) { state.tdd.status = "completed"; state.tdd.greenEvidence = [phase.gate.requirements.green_cycle_evidence_recorded || "covered by exception"]; state.tdd.refactorEvidence = [phase.gate.requirements.refactor_evidence_recorded || "covered by exception"]; } const checkpoint = def.human_checkpoint === "always" || (def.human_checkpoint === "when_configured" && (config.workflow?.human_checkpoints || []).includes(id)); if (checkpoint) { phase.status = "blocked"; phase.checkpoint = { status: "awaiting_approval", note: "Human approval required by project profile." }; state.status = "paused"; state.nextAction = `Approve or reject the human checkpoint for '${id}'.`; } else { phase.status = "completed"; advance(state, flow, config); } writeJson(stateFile, state); return status(root, state, flow); }
  if (command === "exception") { const id = filtered[1], phase = phaseById(state, id); if (id !== "tdd-preparation" || phase.status !== "active") fail("TDD exception must be requested while tdd-preparation is active"); if (config.tdd?.allow_exception !== true) fail("TDD exceptions are disabled by project profile"); const reason = argValue(filtered, "--reason"), risk = argValue(filtered, "--risk"), alternativeValidation = argValue(filtered, "--validation"); if (!reason || !risk || !alternativeValidation) fail("TDD exception requires --reason, --risk and --validation"); state.tdd.exception = { reason, risk, alternativeValidation, approval: "pending" }; state.tdd.status = "exception"; phase.status = "blocked"; phase.checkpoint = { status: "awaiting_approval", note: "TDD exception requires human approval." }; state.status = "paused"; state.currentPhase = id; state.nextAction = "Approve or reject the documented TDD exception."; writeJson(stateFile, state); return status(root, state, flow); }
  if (command === "checkpoint") { const id = filtered[1], phase = phaseById(state, id); if (phase.checkpoint?.status !== "awaiting_approval") fail(`Phase '${id}' is not awaiting a human checkpoint`); const approved = has(filtered, "--approve"), note = argValue(filtered, "--note") || (approved ? "Approved by human." : "Rejected by human."); phase.checkpoint = { status: approved ? "approved" : "rejected", note }; if (approved) { if (state.tdd?.exception && id === "tdd-preparation") state.tdd.exception.approval = "approved"; phase.gate.passed = true; phase.status = "completed"; advance(state, flow, config); } else { if (state.tdd?.exception && id === "tdd-preparation") state.tdd.exception.approval = "rejected"; phase.status = "blocked"; state.status = "blocked"; state.currentPhase = id; state.nextAction = "Address the rejection, then resume."; } writeJson(stateFile, state); return status(root, state, flow); }
  if (command === "resume") { const phase = phaseById(state, state.currentPhase); if (state.status === "blocked") phase.status = "active"; advance(state, flow, config); writeJson(stateFile, state); return status(root, state, flow); }
  fail("workflow commands: start, status, complete, exception, checkpoint, resume");
}
function status(root, state, flow) { const phase = phaseById(state, state.currentPhase), def = flow.phases.find((item) => item.id === phase.id), config = exists(path.join(root, ".specify/turbo/project.yml")) ? profile(root) : {}; console.log(`${state.classification} / ${state.status} / ${state.currentPhase}\nOwner: ${phase.owner}\nTDD: ${state.tdd?.enabled ? state.tdd.status : "disabled"}\nGate requirements: ${requirements(def, config, state).join(", ")}\nNext action: ${state.nextAction}`); }
function doctor(args) {
  const root = targetFrom(args), strict = has(args, "--strict"), errors = [], warnings = [], ok = (m) => console.log(`✓ ${m}`), warn = (m) => { warnings.push(m); console.log(`! ${m}`); }, error = (m) => { errors.push(m); console.log(`✗ ${m}`); };
  exists(path.join(root, ".specify")) ? ok("Spec Kit directory detected") : error("Spec Kit directory .specify is missing");
  const turbo = path.join(root, ".specify/turbo"); exists(path.join(turbo, "turbo.js")) ? ok("Self-contained Node runtime is installed") : error("Node workflow runtime is missing");
  const names = exists(path.join(root, ".agents/skills")) ? fs.readdirSync(path.join(root, ".agents/skills")) : []; for (const name of REQUIRED_SKILLS) names.includes(name) ? null : error(`Required skill '${name}' is missing`);
  if (exists(path.join(turbo, "manifest.json"))) ok(`Spec Kit Turbo version ${json(path.join(turbo, "manifest.json")).turboVersion} installed`); else error("Missing Turbo manifest");
  if (exists(path.join(turbo, "project.yml"))) { const config = profile(root); if (String(config.project?.name || "").startsWith("change-me")) warn("project.yml still contains template placeholders"); if (!config.tdd) warn("project.yml has no tdd configuration; legacy projects keep TDD disabled until explicitly enabled"); if (config.tdd && typeof config.tdd.enabled !== "boolean") error("tdd.enabled must be a boolean"); if (config.tdd?.enabled === true && (!config.commands?.test || String(config.commands.test).includes("replace-with-"))) error("TDD is enabled but commands.test is missing or still a placeholder"); } else error("Missing .specify/turbo/project.yml");
  if (exists(path.join(turbo, "state.json")) && json(path.join(turbo, "state.json")).workId === "replace-with-work-id") warn("state.json still uses the template workId");
  const config = exists(path.join(turbo, "project.yml")) ? profile(root) : {}, visual = config.visual || {}, ignore = exists(path.join(root, ".gitignore")) ? read(path.join(root, ".gitignore")) : "";
  const ignoreStart = ignore.indexOf(IGNORE_START), ignoreEnd = ignore.indexOf(IGNORE_END), ignoreValid = ignoreStart >= 0 && ignoreEnd > ignoreStart && ignore.slice(ignoreStart, ignoreEnd).includes(IGNORE_ENTRY);
  if (visual.persist_references && !ignoreValid) error("Visual references are enabled but the managed .gitignore block is missing or invalid");
  const references = path.resolve(root, visual.references_path || ".specify/visual-references");
  if (!references.startsWith(`${root}${path.sep}`) && references !== root) error("visual.references_path must remain inside the project");
  if (exists(path.join(root, ".specify/memory/constitution.draft.md"))) warn("Constitution draft is present and must be approved before finalization");
  const state = exists(path.join(turbo, "state.json")) ? json(path.join(turbo, "state.json")) : null;
  if (state?.tdd?.status === "exception" && state.tdd.exception?.approval !== "approved") error("TDD exception is awaiting human approval");
  if (state?.tdd?.enabled && state.currentPhase === "implementation" && (!state.tdd.redEvidence?.length || !state.tdd.greenEvidence?.length || !state.tdd.refactorEvidence?.length) && state.tdd.exception?.approval !== "approved") error("Implementation is missing TDD red, green or refactor evidence");
  if (state?.tdd?.enabled && ["red_ready", "green", "refactored", "completed", "exception"].includes(state.tdd.status) && !exists(path.join(root, state.tdd.artifactPath || ".specify/turbo/tdd-cycle.md"))) error("TDD state has advanced but tdd-cycle.md is missing");
  for (const name of ["feature", "bugfix", "refactor", "maintenance", "hotfix"]) { const file = path.join(turbo, "runtime/workflows", `${name}.yml`); if (exists(file) && YAML.parse(read(file)).phases.some((phase) => phase.id === "implementation" || phase.id === "correction") && !YAML.parse(read(file)).phases.some((phase) => phase.id === "tdd-preparation")) error(`Workflow '${name}' has implementation without tdd-preparation`); }
  const backups = path.join(turbo, "backups"); if (exists(backups) && !ignore.includes(".specify/turbo/backups/")) warn("Turbo backups are not protected by .gitignore");
  console.log(`\nSummary: ${errors.length} error(s), ${warnings.length} warning(s).`); process.exit(errors.length || (strict && warnings.length) ? 1 : 0);
}
function usage(code = 0) { console.log(`Spec Kit Turbo\n\nUsage:\n  speckit-turbo init [directory] [--mode auto|clean|existing] [--spec-kit-version ref]\n  speckit-turbo doctor [directory] [--strict]\n  speckit-turbo upgrade [directory]\n  speckit-turbo version [directory]\n  speckit-turbo workflow --path . <start|status|complete|checkpoint|resume>`); process.exit(code); }
function main(args = process.argv.slice(2)) { const command = args[0] || "help"; try { if (["help", "--help", "-h"].includes(command)) usage(); if (command === "init") return install(args.slice(1)); if (command === "upgrade") return install(["--upgrade", ...args.slice(1)]); if (command === "doctor") return doctor(args.slice(1)); if (command === "version") { const root = path.resolve(args[1] || "."), manifest = exists(path.join(root, ".specify/turbo/manifest.json")) ? path.join(root, ".specify/turbo/manifest.json") : path.join(PACKAGE_ROOT, "manifest.json"); console.log(json(manifest).turboVersion); return; } if (command === "workflow") return runtime(args.slice(1)); usage(2); } catch (error) { fail(error.message, 1); } }
if (require.main === module) main(); module.exports = { main };
