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
  const alias = command(packageBin, ["install", root, "--mode", "existing", "--upgrade"], ROOT);
  assert.equal(alias.status, 0, alias.stderr);
});

test("npm CLI exposes doctor and version without Python", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "speckit-turbo-doctor-"));
  fs.mkdirSync(path.join(root, ".specify/memory"), { recursive: true });
  fs.writeFileSync(path.join(root, ".specify/memory/constitution.md"), "constitution\n");
  assert.equal(command(packageBin, ["init", root, "--mode", "existing"], ROOT).status, 0);
  const doctor = command(packageBin, ["doctor", root], ROOT);
  assert.match(doctor.stdout, /Self-contained Node runtime is installed/);
  const version = command(packageBin, ["version", root], ROOT);
  assert.equal(version.status, 0);
  assert.match(version.stdout, /1\.0\.1/);
});

test("npm CLI bootstraps clean mode through the upstream command contract", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "speckit-turbo-clean-"));
  const bootstrap = "mkdir -p .specify/memory .specify/templates .specify/scripts && touch .specify/memory/constitution.md";
  const result = command(packageBin, ["init", root, "--mode", "clean", "--spec-kit-version", "v-test"], ROOT, { SPECKIT_TURBO_BOOTSTRAP_COMMAND: bootstrap });
  assert.equal(result.status, 0, result.stderr);
  assert.ok(fs.existsSync(path.join(root, ".specify/turbo/turbo.js")));
  assert.equal(JSON.parse(fs.readFileSync(path.join(root, ".specify/turbo/manifest.json"))).installation.mode, "clean");
});
