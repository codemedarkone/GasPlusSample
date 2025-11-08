# Product Roadmap

1. [ ] AttributeSet Generator – Offer a tool that ingests DataAssets and produces complete native AttributeSet headers/cpp with replication hooks and meta-attribute registries, so teams can define stats in data and immediately compile without hand-editing GAS boilerplate. `[M]`
2. [ ] Data-Driven Ability Base – Ship a configurable C++ ability class driven entirely by DataAssets (costs, tags, cooldowns, montages) so every ability shares consistent replication, cost, and prediction behavior while allowing designers to tweak via data. `[L]`
3. [ ] Effect Preset Builder – Provide preset-based creation (Instant, Infinite, Periodic) of GameplayEffects with guarded defaults and validation gates to ensure new effects meet duration/magnitude standards before they are saved. `[M]`
4. [ ] GameplayCue Preset Tool – Generate GameplayCue assets and notify classes from a single definition asset so visual/audio responses stay consistent and require minimal manual wiring. `[M]`
5. [ ] Runtime Façade API – Expose Blueprint/C++ helper functions (activate-by-tag, apply effect, query cooldowns) that encapsulate prediction-safe logic and give creators an easy surface for GAS interactions. `[M]`
6. [ ] Enhanced Input Binder – Map Input Actions to ability tags with multiplayer-aware bindings and prediction compatibility checks, ensuring input assignments work correctly in both client and server contexts. `[M]`
7. [ ] Validation Panel – Build an editor tab that scans replication flags, NetExecutionPolicy choices, tags, and DataAssets, surfaces blockers, and lets teams guard multiple builds before cooking. `[S]`
8. [ ] Debug Overlay – Add an in-game UMG widget that displays active ability states, tag stacks, cooldowns, and execution flow so teammates can quickly diagnose gameplay issues during testing. `[S]`
9. [ ] AI Ability Integration – Deliver Behavior Tree tasks/decorators that let AI agents activate abilities by tag while reusing the validation and runtime facades, keeping player and AI GAS behavior aligned. `[M]`

> Notes
> - Items are ordered to build foundational automation (AttributeSet + ability base) before layering effect/cue tooling, runtime helpers, and QA features.
> - Each entry represents an end-to-end deliverable (data, editor tooling, runtime/runtime tests) that can be verified through automated or manual checks.
