# AGENTS.md — Generator-First Agents for UE5 Plugin

## Project Overview
This project implements a UE5 plugin using Spec‑Driven Development (SDD). The plugin provides zero‑overhead Gameplay Ability System enhancements by generating AttributeSets, Effects, Cues, and ability interfaces at editor time and exposing a clean runtime façade in C++. Heavy logic stays in editor‑time tools; runtime remains native GAS with full prediction and networking parity.

## Agent Roles
- **AttributeSet Generator Agent**  
  Generates C++ AttributeSets and clamping logic based on specs.

- **Effect & Cue Builder Agent**  
  Creates GameplayEffect and GameplayCue presets and validation utilities.

- **Runtime Façade Agent**  
  Implements lightweight prediction‑safe C++ wrappers and ASC extensions.

- **Input & AI Binder Agent**  
  Connects Enhanced Input ↔ Ability Tags; Behavior Tree ability nodes.

- **Validation Agent**  
  Enforces UE coding standards, naming rules, metadata, and spec parity.

## Workflow
1. Read feature spec and confirm public API signatures.
2. Generate class skeletons (.h first, minimal includes, forward declares).
3. Implement runtime in C++ only; expose Blueprint nodes when required.
4. Generate editor wizards and utilities for data setup.
5. Validate style, metadata, asset naming, and spec acceptance criteria.
6. Build + run automation tests + shipping benchmark.
7. Update docs and sample content.

## Build & Test Commands
### Build (Editor)
```bash
RunUAT BuildCookRun -project="GasPlusSample.uproject" -noP4 -platform=Win64 -clientconfig=Development -build
```

### Automation Tests
```bash
UE5Editor-Cmd.exe "GasPlusSample.uproject" -unattended -ExecCmds="Automation RunTests Plugin.*; Quit"
```

### Performance Benchmark (Shipping)
```bash
YourGame-Win64-Shipping.exe -benchmark -benchmarkseconds=300
```

## Quality Standards
- UE naming: `U/A/F/T/E`, bools start with `b`
- Class order: public → protected → private
- Braces on new line, always use braces on flow statements
- Minimal headers; include own header first
- UPROPERTY/UFUNCTION metadata present & categorized
- Only necessary Blueprint exposure; clean DisplayNames & tooltips
- Asset prefixes: `BP_`, `SM_`, `M_`, `T_`

## Deliverables
- Generated `.h/.cpp` for project source
- Editor utilities and wizards
- Sample assets and maps
- Automation tests & profiling logs
- Updated documentation

## Success Criteria
- No runtime performance overhead
- Correct replication/prediction behavior
- Clean Blueprint and asset UX
- Plugin removable without breaking generated gameplay code
