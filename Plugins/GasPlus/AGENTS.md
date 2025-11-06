# AGENTS.md — Codex Automation Agents for GAS+

> Automation spec for the Unreal Engine 5.6 project **GasPlusSample**, with the plugin **GasPlus**. Defines agent roles, boundaries, triggers, and CI/CD orchestration. Optimized for deterministic codegen, safe editor tooling, and performance parity with native GAS.

---

## 1) Purpose & Scope
This document tells Codex **what agents exist**, **what they own**, and **how they run**—from code generation and validation to docs, tests, and release packaging. It is source-controlled and reviewed like code, ensuring reproducible automation and auditable changes.

**Targets**
- Unreal Engine **5.6**
- Project name: **GasPlusSample**
- Plugin name: **GasPlus** (path: `/Plugins/GasPlus/`)
- Supports local dev, CI, and marketplace release flows

---

## 2) Agent Architecture Overview

| Layer | Tech | Responsibility |
|---|---|---|
| **Editor-Time Rail** | C++ commandlets, Python/Editor Utility | AttributeSet Generator, Effect & Cue Builders, Tag Guard |
| **Runtime Rail** | C++ only | ASC subclass, façade API, prediction & replication correctness |
| **Validation** | CLI/Python | Net policies, replication flags, schema checks |
| **Docs** | Markdown builder | Roadmap/Changelog/Quick Start regeneration |

Agents are **parallelizable** and operate in **directory sandboxes** to avoid cross-writes. Shared modules are read-only.

---

## 3) Directory Boundaries
Each agent executes under a dedicated working dir to maintain clean artifacts and logs.

```
/GasPlusSample/
  ├─ Plugins/
  │   └─ GasPlus/
  │        ├─ Agents/
  │        │   ├─ codegen/           
  │        │   ├─ validation/        
  │        │   ├─ editor/            
  │        │   ├─ qa/                
  │        │   └─ docs/              
  │        ├─ Source/
  │        │   ├─ GasPlus/           
  │        │   └─ GasPlusEditor/     
  │        ├─ Content/               
  │        └─ Scripts/               
  └─ Source/
       └─ GasPlusSample/Attributes/  
```

> **Write Policy**: Agents write only inside `/Plugins/GasPlus/Agents/<agent>` and designated project destinations (e.g., generated `UAttributeSet` files in `/Source/GasPlusSample/Attributes/`).

---

## 4) Determinism & Idempotency Rules

1. **Hash-based regen**: Inputs (schemas/DataAssets) are content-hashed. If hashes unchanged → skip write.
2. **Stable formatting**: Clang-format (or engine style) applied for consistent AST/diff.
3. **Pure functions**: Same inputs produce **byte-identical** outputs.
4. **Rollback on failure**: Partial writes use temp files; commit on successful validations only.
5. **No runtime reflection** in generated gameplay code; editor-time reflection only.

---

## 5) PR Labels → Agent Routing
Codex triggers agents from PR labels. Multiple labels may run **in parallel**.

| Label | Agent(s) | What runs |
|---|---|---|
| `epic2-codegen` | **codegen-agent** | AttributeSet/DataAbility C++ generation; GameplayEffect/GCCue stubs as configured |
| `epic2-editor` | **validation-agent** | Schema checks, replication flags, NetExecutionPolicies, tag registry validation |
| `epic2-qa` | **qa-agent** | Replication/prediction/unit tests, join-in-progress, perf smoke |
| `epic3-effects` | **editor-agent** | Effect Preset Builder commandlets / editor utilities |
| `epic11-cues` | **editor-agent** | GameplayCue Preset Tool generation |
| `epic12-dataability` | **codegen-agent**, **validation-agent** | Data-Driven Ability base generation & validation |
| `epic13-ai` | **qa-agent** | BT task/decorator nodes tests and AI load |
| `docs` / `epic10-docs` | **docs-agent** | Rebuild README, ROADMAP.md, CHANGELOG.md, Quick Start

> Tip: Add labels in your PR description or via repo automation. All agents are safe to re-run.

---

## 6) Agent Specs

### 6.1 codegen-agent
**Goal**: Generate deterministic native C++ from DataAssets/schemas.

**Inputs**
- Attribute schemas (DataAssets or JSON/YAML)
- Effect/Cue presets when configured

**Outputs**
- `/Source/GasPlusSample/Attributes/*.h/.cpp` with OnRep, Pre/Post hooks
- `PostGameplayEffectExecute` scaffolding for clamping/routing
- Generated registries: optional header for meta-attributes (e.g., Damage, Heal, ShieldDelta)

**Rules**
- No edits outside owned targets
- Emits manifest: `Plugins/GasPlus/Agents/codegen/manifest.json` (inputs, hashes, outputs)

**Exit Criteria**
- Compiles cleanly
- Determinism check passes (re-run → identical SHA256)

---

### 6.2 validation-agent
**Goal**: Prove network & replication correctness before merge.

**Checks**
- Replication flags for attributes and ASC properties
- NetExecutionPolicy alignment & prediction key usage
- Tag registry collisions and required tag presence
- DataAsset completeness + default magnitude/duration sanity

**Artifacts**
- `Plugins/GasPlus/Agents/validation/report.json` and human-readable `summary.md`

**Exit Criteria**
- No blockers; warnings allowed only with explicit waivers

---

### 6.3 editor-agent
**Goal**: Run editor utilities and wizards headless (CI) or interactive (local).

**Responsibilities**
- Effect Preset Builder (Instant/Infinite/Periodic, stacking, duration, magnitude)
- GameplayCue Preset Tool (tag, assets, notify class generation)
- Tag Registry Guard (create/merge missing gameplay tags)

**CI Invocation Examples**
```
UE_CMD="/path/UnrealEditor-Cmd.exe"
PROJECT="/path/GasPlusSample.uproject"
$UE_CMD "$PROJECT" -run=GasPlusCommandlet -Preset=Effects --quiet
```

---

### 6.4 qa-agent
**Goal**: Catch regressions in replication, prediction, and perf.

**Suites**
- Unit & functional tests for ASC/ability activation wrappers
- Join-in-progress & prediction key parity
- AI load test: ≥200 AI actors, target ≤0.1ms tick delta

**Artifacts**
- `/Saved/Tests/Reports/*` XML/JSON + `perf.md` summary

**Exit Criteria**
- All tests green, perf thresholds met, memory/network budgets unchanged

---

### 6.5 docs-agent
**Goal**: Keep docs in sync with shipped features.

**Responsibilities**
- Generate/update: `ROADMAP.md`, `CHANGELOG.md`, Quick Start
- Link Epics to README badges
- Extract deltas from PRD and feature files

**Artifacts**
- `Plugins/GasPlus/Agents/docs/out/*`

**Exit Criteria**
- No broken intra-repo links; Markdown lint passes

---

## 14) Glossary
- **ASC**: Ability System Component (Unreal GAS)
- **Meta-attributes**: Derived attributes used for effect routing (e.g., Damage, Heal, ShieldDelta)
- **JIP**: Join-in-progress networking scenario

---

# Repository Guidelines

## Project Structure & Module Organization
Source C++ lives in `Source/GasPlusSample/`, with `GasPlusSample.Build.cs` defining the primary game module and the `Target.cs` files controlling editor versus runtime builds. The gameplay plugin is isolated in `Plugins/GasPlus/Source/GasPlus`, split into `Public` and `Private` headers for Unreal’s include model. Game assets, including the `biggymap.umap` level, sit under `Content/`, while generated code, intermediates, and cooked binaries land in `Intermediate/` and `Binaries/Win64/`. Default configuration baselines are versioned in `Config/`, so update those files when shipping new input, engine, or gameplay settings.

## Build, Test, and Development Commands
Open the project for iterative work with `"%UE_ROOT%/Engine/Binaries/Win64/UnrealEditor.exe" GasPlusSample.uproject`, which hot-reloads most C++ edits. Produce an Editor build with `"%UE_ROOT%/Engine/Build/BatchFiles/Build.bat" GasPlusSampleEditor Win64 Development -project="%CD%/GasPlusSample.uproject"`. For a packaged gameplay build, run `"%UE_ROOT%/Engine/Build/BatchFiles/RunUAT.bat" BuildCookRun -project="%CD%/GasPlusSample.uproject" -build -stage -pak -targetplatform=Win64 -nop4`. Keep DerivedDataCache and Saved artifacts out of commits.

## Coding Style & Naming Conventions
Match Unreal Engine C++ conventions: 4-space indentation, braces on new lines, PascalCase types (`UGasPlusComponent`), camelCase locals, and `b` prefix for booleans. Expose reflected properties with `UPROPERTY` macros grouped by access and category, and place module-facing headers in `Public/`. Blueprint assets should use descriptive names that match their gameplay role (e.g., `BP_GasPlusAbility`). Run the editor’s `File > Refresh Visual Studio Project` after adding classes so generated headers stay in sync.

## Testing Guidelines
Author gameplay logic tests with Unreal’s automation framework; organize them under the `GasPlus` automation category. Execute them headless via `"%UE_ROOT%/Engine/Binaries/Win64/UnrealEditor.exe" GasPlusSample.uproject -ExecCmds="Automation RunTests GasPlus" -ReportExportPath="Saved/Automation" -unattended -nop4`. Validate plugin features in PIE and ensure new assets stream correctly from `Content/` without warnings. Record expected outcomes in the PR description when manual QA is required.

## Commit & Pull Request Guidelines
Prefer concise, imperative commit subjects (e.g., `Improve ability cooldown logging`) and keep commits scoped to one feature or fix. Reference related GitHub issues when available, and include follow-up notes for any temporary workarounds. Pull requests should summarize the gameplay impact, list test commands executed. Request review from the plugin maintainer for modifications under `Plugins/GasPlus/`.

---

*End of AGENTS.md for GasPlusSample / GasPlus*
