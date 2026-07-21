---
name: turbo-visual-specifier
description: Analyze one or more attached frontend screenshots, produce an evidence-based visual specification with measurements and confidence, and derive traceable visual acceptance criteria without silently inventing missing behavior.
---

# Turbo Visual Specifier

## Purpose

Translate screenshots into implementation-ready visual requirements so the implementation agent does not need to repeatedly inspect the original image. This skill analyzes images; it does not generate or edit them.

## Inputs

- one or more attached screenshots;
- user context about screen, state, viewport, and intended behavior;
- repository structure, frontend conventions, design tokens, accessibility rules, and project profile;
- existing `spec.md`, `visual-spec.md`, and visual-analysis state when resuming.

## Outputs

- `visual-spec.md`;
- visual requirements and `VAC-*` acceptance criteria added to `spec.md`;
- image metadata, comparison notes, confidence, uncertainties, and blocking questions;
- optional persisted references only when `visual.persist_references` is enabled and Git ignore protection is verified;
- updated `visualAnalysis` state and next action.

## Workflow

1. Identify each image, its dimensions, available viewport/context, and whether it represents a screen, component, state, or comparison.
2. Inspect repository frontend structure and existing visual/accessibility conventions before inferring implementation details.
3. Record facts as `observed`; mark interpretations as `inferred`; use `unknown` when the image cannot support a claim.
4. Inventory hierarchy and components: page regions, containers, controls, text, icons, media, repeated items, overlays, and relationships.
5. Capture estimated dimensions, relative positions, spacing, alignment, colors, typography, borders, radii, shadows, density, and visual states. Label measurements as estimates when no reliable scale exists.
6. Compare multiple screenshots for viewport, state, content, or interaction differences. Do not merge differences without recording their context.
7. Infer only essential responsive behavior. Do not invent complete mobile, loading, empty, error, or hover screens absent from evidence; record them as unknown or hypothesis.
8. Evaluate keyboard access, focus visibility, accessible names, semantic roles, contrast, target size, and reading order when applicable.
9. Create `VAC-*` criteria that are observable and independently verifiable, covering structure, visual appearance, states, interaction, and accessibility.
10. Ask a question only when uncertainty materially changes implementation. Otherwise record the best inference, confidence, and validation consequence.
11. Persist source metadata, not images, by default. Before copying any image, verify the configured path with `git check-ignore`; if verification fails, do not copy and set visual analysis to `blocked`.

## Visual evidence format

Every important claim must identify:

- source image identifier;
- evidence type: `observed`, `inferred`, or `unknown`;
- confidence: `high`, `medium`, or `low`;
- implementation or validation consequence.

## Acceptance criteria

Use identifiers such as `VAC-001` and relate them to functional requirements. Each criterion must describe an observable result, relevant viewport/state, expected interaction or appearance, accessibility expectation when applicable, and validation evidence.

## Persistence safety

The default is text-only analysis. If `visual.persist_references` is true, use only `visual.references_path` inside the project. The directory must be protected by the managed `.gitignore` block and pass `git check-ignore -q <path>` before writing. Never use `git add` for visual references.

## Stop conditions

Stop with `blocked` when an image is unreadable/unavailable, critical screenshots contradict without context, a required visual decision is unresolved, or persistence safety cannot be verified. Do not claim visual completion from an unverified or silently assumed detail.

## Handoff

Provide the visual spec path, image metadata, component inventory, tokens, observed/inferred/unknown details, responsive/state findings, `VAC-*` mapping, accessibility findings, unresolved questions, confidence, and the next safe action.
