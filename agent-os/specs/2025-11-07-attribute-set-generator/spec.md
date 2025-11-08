# Specification: AttributeSet Generator

## Goal
Provide a deterministic attribute-set generator that turns DataAssets into full native AttributeSet headers/CPP (replication hooks, clamps, meta attributes) so teams can author stats in data and ship GAS code without manual boilerplate.

## User Stories
- As a GAS designer, I want to point the generator at `Content/Attributes/**` and get compile-ready AttributeSets in `Source/GasPlusSample/Attributes/**` so I can iterate on stats without hand-editing C++.
- As a gameplay engineer, I want the generator to emit replication and clamp scaffolding by default with metadata-based opt-outs so each attribute stays network-safe while letting me skip features when necessary.
- As a maintainer, I want determinism safeguards (hash sidecars, preserve regions, force overrides) so generated code is stable across teams and the plugin can be removed without unexpected churn.

## Specific Requirements

**Input/output control**
- Default to scanning canonicalized DataAssets under `Content/Attributes/**` and writing generated files to `Source/GasPlusSample/Attributes/**`.
- Allow alternative input/output paths through `Config/GasPlus.AttributeGen.ini` entries or CLI switches, including an optional plugin destination like `Plugins/GasPlus/Source/GasPlus/Public/Generated/Attributes/**`.
- Respect overrides per DataAsset to enable mixed source sets (game modules and plugin-derived sets) in the same project.
- Document configuration knobs for tool versioning, CLI flags, and canonicalization rules so future automation agents can rely on predictable file locations and formats.
- Surface validation errors when inputs are missing required metadata or directories cannot be written.

**Replication, hooks, and clamps**
- Emit replication flags plus `OnRep` hook stubs for every replicated attribute by default.
- Generate `PreAttributeChange`/`PostAttributeChange` clamp scaffolds with optional metadata keys such as `ClampMin`, `ClampMax`, `SkipOnRep`, `Replicate=false`, and `GenerateHooks=false` to opt features out.
- Include per-attribute metadata documentation in the generated headers so designers can see which flags were applied.
- Keep GASPLUS-PRESERVE regions around hand-maintained sections and honor `--force`/`--no-preserve` switches to allow manual tweaks without overwriting intentional edits.
- Ensure each generated file leans on Unreal coding standards (4-space indent, PascalCase types, `b` prefixes for bools) and clang-format compatibility.

**Meta-attribute registry**
- Emit a shared helper header/source pair at `Source/GasPlusSample/Attributes/Meta/MetaAttributes.h(.cpp)` exposing derived attributes (Damage, Heal, ShieldDelta) needed by effects.
- Include the meta registry in each AttributeSet so new sets immediately reference the stable derived values.
- Keep the registry generation orthogonal to individual AttributeSet rewrites so meta values remain stable even if sets are regenerated separately.
- Document how new meta attributes are defined (naming, default values, dependencies) for future automation layers.

**Determinism and validation**
- Hash canonicalized DataAsset contents plus generator tool metadata and write `*.generated.hash` alongside each output to detect unchanged inputs.
- Only rewrite C++ outputs when the hash changes or `--force` is supplied, ensuring byte-identical results across runs.
- Report hash mismatches, metadata inconsistencies, or missing templates as validation issues before writing files.
- Generate a manifest entry under `Plugins/GasPlus/Agents/codegen/manifest.json` listing inputs, hashes, and outputs for CI traceability.
- Provide clear CLI feedback (hash checks, preserved regions, overrides) so automation agents can signal success/failure deterministically.

## Visual Design

**`planning/visuals/file structure.png`**
- Shows the repo layout with `GasPlusSample` root, `Plugins/GasPlus` tree, and the `Source/GasPlusSample/Attributes` destination.
- Confirms locations for commandlets (`Plugins/GasPlus/Source/GasPlusEditor`) and generated code, reinforcing where the generator must read/write without crossing boundaries.
- Highlights configuration files near the workspace root (`AGENTS.md`, `.gitignore`, `.vscode`), helping reason about where `.ini` overrides and tool config belongs.
- Fidelity: high-level IDE screenshot of the file explorer, no interactive UI details to implement.

## Existing Code to Leverage

**GasPlus automation agents**
- `Plugins/GasPlus/Agents/codegen` already orchestrates deterministic generation; reuse its manifest format and hashing patterns to keep consistency between attribute and future generators.

**GasPlusEditor commandlets**
- `Plugins/GasPlus/Source/GasPlusEditor/GasPlusCommandlet.*` illustrates how editor tools discover config paths and run headless inside UE, offering a template for CLI args, logging, and sandbox awareness.

**Source/GasPlusSample/Attributes module**
- The target module already exists in the repo tree and follows Unreal module conventions; generated files can reuse its build settings, includes, and module declarations.

**Existing attribute metadata**
- Any current AttributeSet definitions (when available) inform how replication flags, clamp logic, and metadata naming should look to keep consistency with handwritten sets.

## Out of Scope
- GameplayEffects, GameplayAbilities, GameplayCues generation.
- UI tooling such as dashboards, input bindings, or in-editor widgets beyond config management.
- Tag database authoring, animation systems, network policy tuning, or runtime facade APIs.
- Runtime performance optimizations unrelated to attribute generation (e.g., tick budgets, AI load tests).
- Automatic ability or effect wiring; focus remains specifically on attribute definitions, replication scaffolding, and meta data.
