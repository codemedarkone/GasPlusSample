# AttributeSet Generator Requirements

## Raw Idea
Feature Idea: AttributeSet Generator
Summary: Offer a tool that ingests DataAssets and produces complete native AttributeSet headers/cpp with replication hooks and meta-attribute registries, so teams can define stats in data and immediately compile without hand-editing GAS boilerplate.

## Product Context
- Mission focus: Help indie and hobbyist GAS developers automate boilerplate while keeping performance on par with native GAS (see `agent-os/product/mission.md`).
- Roadmap placement: First item after mission derived plan; part of the deterministic automation pipeline that unlocks downstream tooling (`agent-os/product/roadmap.md`).

## Workflow Pipeline (user-supplied)
1. Define Gameplay Data  
   Designers create Attribute, Effect, Ability, and Cue DataAssets. Tags, magnitudes, durations, and policies set here.
2. Run Codegen & Editor Tools  
   AttributeSet Generator emits native C++. Effect & Cue builders generate GameplayEffects and GameplayCue classes. Data-Driven Ability generator produces scaffolding. All outputs land in clean project locations, not plugin folders.
3. Validation Pass  
   Replication flags checked. NetExecutionPolicies verified. Tag collisions or missing tags flagged.
4. Runtime Integration  
   Abilities wired through façade helpers (activate by tag, apply effects, etc.). Inputs bound to ability tags. AI integrates via BT tasks/decorators.
5. Testing & QA  
   Run functional + prediction correctness tests. JIP (join-in-progress) validation. 200-AI perf stress test. Editor-time tests for codegen consistency.
6. Docs & Release  
   Regenerate Quick Start, Roadmap, Changelog. BuildCookRun smoke test. Ship plugin or game feature branch.

## Validation & Output Expectations (user text)
### Validation Goals
- Network correctness: All attributes replicated properly. NetExecutionPolicies valid. Prediction keys consistent.
- Data consistency: All DataAssets (attributes, abilities, effects, cues) complete. No missing tags, invalid modifiers, or conflicting tag definitions.
- Codegen stability: Generated C++ compiles with 0 warnings. Re-running codegen produces byte-identical output.
- Performance: Attribute math and ASC operations stay on native GAS paths. 200+ AI perf test stays under the 0.1 ms tick delta.

### Expected Outputs
- Generated C++ files (`/Source/<Project>/Attributes/*.h/.cpp`)
- DataAbility scaffolding
- Validation reports (JSON + markdown summaries)
- Effect/Cue assets (BP or C++ `GameplayCueNotifies`, validated GameplayEffects)
- Debug/diagnostic overlays
- CI artifacts (Test XML, `perf.md`, determinism hashes)

## Existing Tooling to Align With (user text)
- Core Unreal systems: Gameplay Ability System (Attributes, Effects, Ability activation & prediction), Enhanced Input (Mapping context, input actions, ability tags), Behavior Trees (custom ability activation tasks/decorators), Gameplay Tags manager (`.ini` integration).
- Editor Tools: Editor Utility Widgets (EUWs), Effect/Cue creation wizards, commandlets (including `GasPlusCommandlet`), data-driven workflows for Abilities/Effects/Attributes.
- Build & CI: `UnrealEditor-Cmd.exe` for headless runs, `Build.bat` pipelines, automation tests (prediction correctness, AI load tests).

## Questions & Answers
**Q1:** Could you describe or share any visuals for the AttributeSet Generator UI?
**A:** i have attached all of that

**Q2:** Are there existing editor tools or codepaths we should reuse (Effect Preset Builder, etc.)?
**A:** DataAssets checked for required fields. Generated C++ compiled and determinism hash verified.

## Visual Assets
- Checked `agent-os/specs/2025-11-07-attribute-set-generator/planning/visuals` with `Get-ChildItem -Recurse ...`; directory is empty.
- No mockups/screenshots were provided yet, so visual direction remains to be supplied.

## Reusability Opportunities
- Align with other GasPlus agents (AttributeSet + Effect/Cue builders) by reusing commandlet patterns and DataAsset validation pipelines.
- Leverage the Data-Driven Ability generator scaffolding and façade helpers to ensure generated AttributeSets integrate with existing activation/prediction helpers.
- Reference Validation Panel diagnostics and Debug Overlay data points when designing output reports.

## Scope Boundaries
**In Scope:**
- Deterministic AttributeSet C++ generation, including replication hooks and meta-attribute registries.
- Data validation gates (tags, policies, magnitudes) before generation.
- Integration hooks for runtime helpers (facade API, ability input binding, AI BT tasks) and downstream tooling (effects, cues).
**Out of Scope (for this spec):**
- Rebuilding Quick Start/Roadmap/Changelog (handled by docs agent).
- BuildCookRun packaging itself (handled by release workflows).
- Runtime debugging overlay creation (separate feature).

## Technical Considerations
- Generated files must land in game source directories (`/Source/GasPlusSample/Attributes`) not plugin folders to keep them standalone.
- Validation should produce both JSON (`report.json`) and Markdown (`summary.md`) artifacts for CI.
- Ensure determinism by hashing inputs and verifying byte-identical outputs before accepting a codegen run.
