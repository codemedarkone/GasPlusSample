# GAS+ - Unified Product Requirements Document (UE 5.6)

## Automation Manifest
- **Codex Automation Agents** handle the build pipeline: codegen, validation, editor tools, docs, and QA agents execute their domains in parallel where possible.
- **Routing** is driven by PR labels and file-path change detection so the right agents run without manual coordination.
- **Deterministic job boundaries** keep every agent constrained to `/Plugins/GasPlus/Agents/...` workspaces to avoid cross-writes and ensure reproducible outputs.

## Version
**1.1** - Includes Epics 11-13 and upgraded Epic 2

**Target Engine:** Unreal Engine 5.6  
**Plugin Name:** GAS+  
**Primary Goal:** Simplify the Gameplay Ability System without modifying or degrading its core performance, networking, or prediction model.

---

## 1. Product Vision
**GAS+** is a next-generation, zero-overhead layer on top of Unreal’s Gameplay Ability System (GAS).  
It merges **editor-time automation** with a **runtime-safe façade**, providing a faster, more intuitive workflow while maintaining all networking guarantees.

### Key Principles
- ✅ **Performance parity:** Native GAS paths only—no runtime reflection.
- ✅ **Networking fidelity:** Full support for prediction keys, NetExecutionPolicies, and join-in-progress.
- ✅ **Data-driven UX:** DataAssets for attributes, effects, cues, and abilities.
- ✅ **Modular adoption:** Works with existing GAS projects.
- ✅ **Designer-first tooling:** Code generators, wizards, and validation panels.

---

## 2. Problem Statement
Developers face steep setup costs and boilerplate in standard GAS usage:
- Complex replication and initialization.
- Manual creation of AttributeSets and GameplayEffects.
- Tedious GameplayCue management.
- Poor visibility into live ability states.
- Separate handling of player and AI activation logic.

**GAS+** eliminates these bottlenecks through code generation, presets, façade APIs, and debugging utilities—all with zero runtime overhead.

---

## 3. Core Objectives
| Objective | Description | Outcome |
|------------|--------------|----------|
| **Ease of use** | Replace boilerplate with automated workflows. | First ability created in <5 min. |
| **Safety** | Validation of replication and NetPolicies. | Zero warnings during cook. |
| **Performance** | Match native GAS runtime cost. | ≤0.05 ms/frame delta. |
| **Network correctness** | Align with UE’s prediction system. | 100% parity in tests. |
| **AI & Designer parity** | Player and AI use the same activation API. | Unified façade layer. |

---

## 4. Technical Architecture

### Dual-Rail Architecture
| Layer | Description | Implementation |
|--------|--------------|----------------|
| **Editor-Time Rail** | Heavy lifting—code and asset generation. | AttributeSet Generator, Effect & Cue Builders |
| **Runtime Rail** | Lightweight façade using native GAS APIs. | ASC subclass, BP library, Input & AI binders |

## 🧠 Implementation Language Strategy
To maximize performance and iteration speed, **GAS+ uses a hybrid implementation model**:

| Layer | Primary Implementation | Notes |
|--------|------------------------|-------|
| **Runtime Core (ASC, Attributes, Façade)** | **C++** | Critical paths, replication, prediction logic, and attribute math implemented in native code for maximum performance and determinism. |
| **Editor Tools (Wizards, Tag Guard, Cue Builder)** | **Blueprint / Editor Utility Widgets** | Editor-only; no runtime cost or packaged build impact. |
| **Data-Driven Abilities and Presets** | **C++ base + DataAssets** | Uses a native ability class for logic and lightweight DataAssets for configuration and balance. |
| **Debug & Visualization** | **Blueprint (UMG)** | Toggleable runtime overlay for development; stripped entirely in shipping builds. |

**Performance impact:** None. All runtime gameplay systems execute in compiled C++, with Blueprint layers used only for editor and setup utilities.
---

## 5. Key Systems Overview
### 5.1 AttributeSet Generator (Epic 2, Upgraded)
- Generates native C++ AttributeSets from DataAssets.
- Supports standard attributes and **meta-attributes** (Damage, Heal, ShieldDelta).
- Auto-generates `PostGameplayEffectExecute` for clamping and routing logic.
- Includes OnRep and Pre/Post hooks with hot reload.

**Benefits:** Saves time, ensures deterministic replication, and eliminates common logic errors.

---

### 5.2 Effect Preset Builder (Epic 3)
- Editor wizard for creating GameplayEffect assets (Instant / Infinite / Periodic).
- Provides stacking, duration, and magnitude presets.
- Auto-validates modifiers and tags.

---

### 5.3 GameplayCue Preset Tool (New Epic 11)
- `DA_GameplayCueDefinition` defines tag, assets, and cue behavior.
- Generates standard `GameplayCueNotify_*` BPs/C++ automatically.
- Integrates with Tag Registry Guard and Effect Preset Builder.
- 100% editor-only—no runtime cost.

---

### 5.4 Data-Driven Ability Base (New Epic 12)
- Introduces `UGASPlus_DataAbility`—a single C++ base class for all simple abilities.
- Configured entirely by `DA_AbilityDefinition` assets.
- Defines tags, costs, cooldowns, effects, and montages.
- Runtime uses cached hard references—no reflection or asset churn.

---

### 5.5 Runtime Façade (Epic 4)
- Blueprint + C++ library with prediction-safe wrappers:
  - GrantAbility
  - ActivateAbilityByTag
  - ApplyEffectToSelf/Target
- Fully NetExecutionPolicy-compliant.

---

### 5.6 Enhanced Input Binder (Epic 5)
- Connects Input Actions ↔ Ability Tags.
- Supports multiplayer, authority routing, and predictive activation.

---

### 5.7 AI & Behavior Tree Integration (New Epic 13)
- Adds BT task and decorator nodes for AI ability use:
  - `BTTask_ActivateAbilityByTag`
  - `BTDecorator_CanActivateTag`
- Thin façade over existing APIs—zero performance loss.

---

### 5.8 Validation Panel (Epic 7)
- Detects invalid NetExecutionPolicies and replication gaps.
- Outputs fix suggestions and integrates with Output Log.

---

### 5.9 Debug Overlay (Epic 8)
- In-game UMG widget showing active abilities, cooldowns, and tags.
- Toggleable at runtime; stripped from shipping builds.

---

### 5.10 Sample Content & Docs (Epics 9–10)
- Example Abilities: Fireball, Heal, Sprint.
- Full documentation, Quick Start, and video tutorials.

---

## 6. Performance & Networking
| Constraint | Strategy |
|-------------|-----------|
| **Zero runtime overhead** | Code/asset generation only at editor-time. |
| **Replication correctness** | Generated code uses standard ASC patterns. |
| **Prediction** | Built-in key management, parity with UE GAS. |
| **AI Load Testing** | Benchmarked with 200+ AI actors; tick delta ≤0.1ms. |

---

## 7. Milestones
| Milestone | Duration | Deliverables |
|------------|-----------|---------------|
| **Prototype (Month 1)** | 4 weeks | ASC subclass, basic façade, sample ability |
| **Alpha (Month 2)** | 6 weeks | AttributeSet & Effect generators |
| **Beta (Month 3)** | 6 weeks | Input binder, validation, debug, GameplayCue Preset Tool |
| **Launch (Month 4)** | 4 weeks | Data-Driven Abilities + AI BT nodes, Docs |
| **Post-Launch (v1.1)** | 2 weeks | Meta-Attribute logic upgrade rollout |

---

## 8. Testing & QA
- Automated unit tests for replication, prediction, and join-in-progress.
- Profiling benchmarks for frame time, memory allocation, and network traffic.
- Editor integration tests for generator and preset tools.
- 200-AI stress benchmark for BT nodes.

---

## 9. Risks & Mitigations
| Risk | Mitigation |
|------|-------------|
| UE 5.6 GAS API drift | Version macros and wrapper layer |
| Tag registry explosion | Auto-merge and tag reuse validation |
| DataAsset misconfiguration | Validation panel checks & fix suggestions |
| Editor complexity | Modular sub-plugins: Core, Editor, Debug |

---

## 10. Success Metrics
| KPI | Target |
|------|--------|
| Setup time reduction | 80% faster than vanilla GAS |
| Onboarding satisfaction | 9/10 |
| Performance parity | ≤1% runtime difference |
| Adoption | 1k+ installs in 3 months |

---

## 11. Deliverables
- `/Plugins/GASPlus/`
- `feature-breakdown.md`
- `task-list.md`
- `additional-task-list.md`
- Example project + docs
- Marketplace & GitHub releases

---

## 12. Future Extensions
- Visual Ability Graph Editor
- Multiplayer replay debugging
- AI ability planning (Behavior Tree expansions)
- GAS analytics overlay

---






---

## 🧳 Safe Removal & Project Portability

**Goal:** Ensure developers can remove the GAS+ plugin after generation while preserving all gameplay functionality and generated assets.

### Design Principles
GAS+ tools operate exclusively at **editor-time** or through **non-invasive extensions** of Unreal Engine’s built-in Gameplay Ability System.  
This guarantees that all generated assets and C++ code remain portable and independent of the plugin once created.

### Safe-to-Keep Assets
| System | Generated Type | Dependency | Safe After Removal | Notes |
|--------|----------------|-------------|---------------------|-------|
| **AttributeSet Generator** | `.h/.cpp` classes (UAttributeSet) | Core GAS | ✅ | Generated in `/Source/<Project>/Attributes/`; no plugin references. |
| **Effect Preset Builder** | GameplayEffect `.uasset` files | Core GAS | ✅ | Pure UE5 asset type; created by the editor tool. |
| **GameplayCue Preset Tool** | `GameplayCueNotify` BPs/C++ | Core GAS | ✅ | Generated from native classes; not dependent on plugin. |
| **Data-Driven Ability Base** | DataAssets (`DA_AbilityDefinition`) | GAS+ C++ class | ⚠️ *Partial* | Data assets remain usable; dependent class must be replaced if plugin removed. |
| **Façade BP Library** | BP function nodes | GAS+ library | ⚠️ *Partial* | Only nodes directly calling `UGASPlusBPLibrary` break; generated gameplay logic remains. |
| **Validation & Debug Tools** | Editor-only utilities | None | ✅ | No runtime dependencies; safe to delete anytime. |

### Technical Safeguards
- Generated code is written directly into your **project source**, not stored inside the plugin directory.  
- All `.uasset` types rely solely on Unreal’s built-in GameplayAbility, AttributeSet, and GameplayEffect systems.  
- The plugin never modifies existing GAS subsystems or core engine modules.

### Optional Future Feature – “Detach Mode”
A planned post-launch Epic (`Epic 14`) will introduce a **Detach Wizard**, automating dependency removal:
- Moves all generated classes into `/Source/<YourProject>/`.
- Rewrites any Blueprint references to Unreal-native classes.
- Runs a full compile & load validation pass.

### Summary
Removing GAS+ after asset generation will not affect your gameplay systems.  
Only direct calls to plugin classes (like the façade or data-ability base) would need minor refactoring.  
All generated AttributeSets, GameplayEffects, and GameplayCues remain 100% functional and compatible with Unreal Engine 5.6.


**End of PRD (GAS+ UE 5.6 v1.1)**
