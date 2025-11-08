# Spec Requirements: 2025-11-07-attribute-set-generator

## Requirements Discussion
- AttributeSet generation reads canonicalized DataAssets from `Content/Attributes/**` by default and writes native C++ output to `Source/GasPlusSample/Attributes/**`, while allowing overrides via `Config/GasPlus.AttributeGen.ini`, CLI switches, or an alternate destination such as `Plugins/GasPlus/Source/GasPlus/Public/Generated/Attributes/**` when teams choose to keep the plugin-driven files inside the plugin tree.
- Every generated AttributeSet emits replication flags, `OnRep` hooks, and `Pre/Post` clamp stubs so the outputs are compile-ready; DataAsset metadata keys such as `Replicate=false`, `GenerateHooks=false`, `ClampMin/ClampMax`, and `SkipOnRep=true` let authors opt out of the defaults when needed.
- A shared meta-attribute registry lives under `Source/GasPlusSample/Attributes/Meta/MetaAttributes.h(.cpp)` and is `#include`d by each generated AttributeSet so derived values (Damage, Heal, ShieldDelta) remain accessible without regenerating the helpers when individual sets change.
- Determinism is enforced by hashing each canonicalized DataAsset together with the generator template/tool version, writing a sidecar `*.generated.hash`, and only overwriting the target files when the hash changes; code regions are guarded by `// GASPLUS-PRESERVE:begin/end`, and CLI flags `--force`/`--no-preserve` allow manual overrides as needed.
- The tool focuses solely on AttributeSets (fields, replication, clamps, default inits, OnRep plumbing), meta-registry generation, and basic validation; GameplayEffects, Abilities, Cues, UI/input tooling, tag DB authoring, animation systems, and networking policy tuning are explicitly out of scope for this feature.
- `planning/visuals/file structure.png` documents the repository layout, confirming the `Plugins/GasPlus` tree, the `Source/GasPlusSample/Attributes` destination, and the project-root configuration files that the generator needs to honor.

## Requirements Summary
### Functional Requirements
- Consume Attribute schema DataAssets from `Content/Attributes/**`, respecting optional overrides for both input and output directories via an `.ini` or CLI so generated code can live in the game module or plugin as needed.
- Emit replication flags, `OnRep` hooks, and clamp scaffolding by default while honoring metadata-driven opt-outs (`Replicate`, `GenerateHooks`, `SkipOnRep`, clamp bounds) so designers keep full control per attribute.
- Generate and expose a standalone meta-attribute registry (`MetaAttributes.h/.cpp`) that every AttributeSet includes, keeping meta attributes stable and uninstall-safe.
- Guarantee deterministic writes with canonicalized DataAsset hashing that factors in the generator version, writes `*.generated.hash` files, and only updates C++ when the hash changes; support `// GASPLUS-PRESERVE` regions and `--force/--no-preserve` switches for manual edits.
- Keep the feature scope focused on AttributeSet wiring, validation metadata, and meta registry creation, leaving GameplayEffects, Abilities, Cues, UI/input tooling, tag services, animation, and network policy adjustments to future work.
