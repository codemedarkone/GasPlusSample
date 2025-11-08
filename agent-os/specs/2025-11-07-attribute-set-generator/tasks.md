# Task Breakdown: AttributeSet Generator

## Overview
Total Tasks: 12

## Task List

### AttributeSet Core Generation

#### Task Group 1: Input/output plumbing + replication metadata
**Dependencies:** None

- [ ] 1.0 Draft 2–8 focused tests that cover metadata opt-outs (Replicate, GenerateHooks, SkipOnRep, ClampMin, ClampMax) and verify default hooks/clamps are emitted.
  - [ ] 1.1 Use these tests to confirm metadata parsing and stub generation behaviors.
- [ ] 1.2 Implement canonicalized input discovery (default `Content/Attributes/**`) with override support via `Config/GasPlus.AttributeGen.ini` and CLI switches, falling back to plugin destination when configured.
- [ ] 1.3 Emit generated files to `Source/GasPlusSample/Attributes/**` by default, include override destinations, and surface errors when outputs cannot be written.
- [ ] 1.4 Generate AttributeSets that include replication flags, `OnRep` hooks, and pre/post clamp scaffolds while honoring metadata-driven opt-outs.
- [ ] 1.5 Keep generated headers clang-format compatible, following Unreal naming/indent conventions and documenting which **metadata keys** drove each generated hook/flag (`Replicate`, `GenerateHooks`, `SkipOnRep`, `ClampMin`, `ClampMax`).
- [ ] 1.6 Add a minimal **compile check** test ensuring one generated AttributeSet + Meta registry compiles after generation (golden test).

**Acceptance Criteria:**
- Input/output overrides resolve correctly and report failures.
- Generated AttributeSets include replication/clamp scaffolds by default and respect metadata opt-outs.
- Metadata keys are explicitly documented in generated headers.
- Minimal compile test passes.
- Tests 1.0 run and pass against the metadata logic only.

---

### Determinism, validation, and logging

#### Task Group 2: Hashing, manifest, and CLI feedback
**Dependencies:** Task Group 1

- [ ] 2.0 Draft 2–8 focused tests that assert hash reuse, preserve region handling, and force/skip-preserve flags behave deterministically.
  - [ ] 2.1 Use those tests to verify hash change detection prevents rewrites unless forced.
- [ ] 2.2 Compute canonical hashes for each DataAsset **plus generator + template version**, write `*.generated.hash` sidecars, and only rewrite outputs when hashes differ or `--force` is used.
- [ ] 2.3 Emit a manifest entry under `Plugins/GasPlus/Agents/codegen/manifest.json` listing:
  - input paths  
  - input hashes  
  - generator version  
  - template version  
  - output paths  
  - preserve region map  
  - elapsed time  
- [ ] 2.4 Log CLI-level feedback (hash status, preserved region detection, overrides, validation issues) so automation agents can consume success/failure deterministically.
- [ ] 2.5 Add tests covering `--dry-run`, `--force`, `--no-preserve`, and detection of `// GASPLUS-PRESERVE` blocks.

**Acceptance Criteria:**
- Hash sidecars and manifest updates occur only when necessary.
- Manifest schema includes versioning + preserve maps.
- `--force` / `--no-preserve` / `--dry-run` override flags behave as intended.
- Tests 2.0/2.1 pass, validating deterministic behavior and CLI feedback.

---

### Meta Registry & Documentation

#### Task Group 3: Meta-attribute helper and docs
**Dependencies:** Task Group 1

- [ ] 3.0 Draft 2–8 focused tests that confirm the MetaAttributes helper exposes Damage/Heal/ShieldDelta values and each AttributeSet includes it.
  - [ ] 3.1 Ensure tests show regenerated AttributeSets still compile/link against the shared registry without rerunning registry generation.
- [ ] 3.2 Generate `Source/GasPlusSample/Attributes/Meta/MetaAttributes.h(.cpp)` with derived attribute definitions and include it from every AttributeSet.
- [ ] 3.3 Document how meta attributes are named, defaulted, and wired so future automation tools can extend or validate them.
- [ ] 3.4 Reference the `planning/visuals/file structure.png` layout to justify target directories and config placement in the documentation.
- [ ] 3.5 Add a documentation table describing all metadata keys (`Replicate`, `GenerateHooks`, `SkipOnRep`, `ClampMin`, `ClampMax`) plus usage examples and generated stub examples (`OnRep_*`, PreClamp, PostClamp).

**Acceptance Criteria:**
- Meta registry compiles independently and stays stable even if individual sets regenerate.
- Tests 3.0/3.1 confirm registry usage and metadata coverage.
- Documentation includes metadata table + stub examples.
- Documentation mentions repo layout visual asset and config/hook expectations.

---

### QA & Testing Coordination

#### Task Group 4: Verification & automation prep
**Dependencies:** Task Groups 1–3

- [ ] 4.0 Review generated assets/tests and write up to 10 strategic tests that cover key metadata scenarios, hash validations, and registry includes (max total of 10 new tests).
- [ ] 4.1 Run only the focused tests from Task Groups 1–3 plus the new tests from 4.0, ensuring they pass without executing the entire suite.
- [ ] 4.2 Capture test results, hash logs, and manifest samples for automation reports so CI agents can validate the generator deterministically.  
- [ ] 4.3 Ensure CI artifacts align with `codegen-agent` output contract and are compatible with Codex routing/triggers.

**Acceptance Criteria:**
- No more than 10 new tests added; they all pass.
- Focused tests from earlier groups run successfully without full-suite execution.
- Reporting data (logs, manifest, hash statuses) is available for automation consumers.
