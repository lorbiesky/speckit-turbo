"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");
const { main } = require("../src/cli.js");

function project(prefix) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), prefix));
  fs.mkdirSync(path.join(root, ".specify/memory"), { recursive: true });
  fs.writeFileSync(path.join(root, ".specify/memory/constitution.md"), "constitution\n");
  return root;
}

test("source CLI covers install, local workflow, upgrade and version paths", () => {
  const root = project("speckit-turbo-source-");
  main(["init", root, "--mode", "existing"]);
  assert.equal(fs.existsSync(path.join(root, ".specify/turbo/AGENTS.turbo.md")), true);
  main(["workflow", "--path", root, "start", "feature", "--work-id", "source-flow"]);
  main(["workflow", "--path", root, "complete", "intake", "--evidence", "classified_as_feature=text|classified", "--evidence", "scope_recorded=text|scope", "--evidence", "project_profile_loaded=text|profile"]);
  main(["workflow", "--path", root, "status", "--refresh"]);
  main(["upgrade", root]);
  main(["version", root]);
});

test("source CLI covers clean bootstrap and doctor failure reporting", () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "speckit-turbo-source-clean-"));
  const previousBootstrap = process.env.SPECKIT_TURBO_BOOTSTRAP_COMMAND;
  process.env.SPECKIT_TURBO_BOOTSTRAP_COMMAND = "mkdir -p .specify/memory .specify/templates .specify/scripts && touch .specify/memory/constitution.md";
  try {
    main(["init", root, "--mode", "clean", "--spec-kit-version", "v-test"]);
  } finally {
    if (previousBootstrap === undefined) delete process.env.SPECKIT_TURBO_BOOTSTRAP_COMMAND;
    else process.env.SPECKIT_TURBO_BOOTSTRAP_COMMAND = previousBootstrap;
  }
  const previousExit = process.exit;
  process.exit = (code) => { throw new Error(`EXIT:${code}`); };
  try { assert.throws(() => main(["doctor", root]), /EXIT:/); } finally { process.exit = previousExit; }
});
