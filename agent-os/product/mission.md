# Product Mission

## Pitch
GAS+ is a productivity layer for Unreal Engine’s Gameplay Ability System that helps indie and hobbyist developers automate the repetitive setup of attributes, effects, cues, and abilities while keeping runtime performance identical to native GAS.

## Users

### Primary Customers
- **Indie/Hobbyist Unreal Developers:** Solo creators and small teams building GAS-heavy gameplay who need to move from idea to prototyping without wrestling with boilerplate.
- **Small Studios Shipping Multiplayer Experiences:** Teams that want consistent GAS behavior, safer replication, and fewer manual runtime risks.

### User Personas
**Indie Unreal Developer** (20–45)
- **Role:** Creator or solo dev designing gameplay systems with GAS.
- **Context:** Juggling design, coding, and iteration for a passion project or early-stage release.
- **Pain Points:** GAS requires repetitive C++ setup, fragile replication flags, and juggling multiple assets for basic abilities.
- **Goals:** Spend less time wiring attributes/effects and more time refining abilities, keeping builds stable and performant.

## The Problem

### Hard-to-Ship Gameplay Ability Systems
Creating GAS-based gameplay involves a lot of manual, error-prone work: AttributeSets, GameplayEffects, GameplayCues, and ability wiring all require careful setup and replication tuning, so each new ability can take days instead of hours. This slows iteration, raises the risk of regressions, and makes GAS feel inaccessible to individuals and small teams.

**Our Solution:** GAS+ automates the essential GAS plumbing through deterministic, editor-only generation and validation tools so creators can define abilities in data, trust the generated C++/assets, and ship gameplay faster without sacrificing performance.

## Differentiators

### Deterministic Automation Without Runtime Overhead
Unlike ad-hoc GAS helpers or third-party plugins that add runtime layers, GAS+ emits standalone native C++ and assets with repeatable hashes and editor-only generation, giving teams confidence that the code they ship matches the design intent and stays safe even if the plugin is removed. This yields predictable builds and meaningful time savings.

## Key Features

### Core Features
- **AttributeSet Generator:** Automatically produces native AttributeSets with replication hooks, clamps, and meta-attributes so creators can define stats in data and skip manual C++ setup.
- **Effect Preset Builder:** Lets designers author instant, infinite, or periodic GameplayEffects through guarded presets, ensuring safe defaults and automatic validation before cooking.
- **GameplayCue Preset Tool:** Converts simple definitions into standardized GameplayCue assets and notify classes, keeping visual audio responses consistent across abilities.

### Collaboration Features
- **Validation Panel:** Scans replication flags, NetExecutionPolicies, tags, and DataAssets, giving teams a shared checkpoint that stops broken GAS setups from reaching builds.
- **Debug Overlay:** A runtime UMG widget that shows ability states, tags, cooldowns, and execution flow so teammates can diagnose multiplayer behavior together.
- **Safe Auto-Generation & Idempotency:** Deterministic codegen means every team member can rerun generation without side effects, keeping diffs clean and merge conflicts rare.

### Advanced Features
- **Data-Driven Ability Base:** A universal C++ ability class configurable entirely via DataAssets (costs, tags, cooldowns, montages), reducing the need for bespoke ability classes.
- **Runtime Façade API:** Lightweight Blueprint/C++ helpers (activate by tag, apply effects, query cooldowns) that keep prediction-safe logic centralized.
- **Enhanced Input Binder:** Maps Input Actions to ability tags with multiplayer/prediction correctness baked in so inputs stay reliable in net games.
- **AI Ability Integration:** Behavior Tree tasks and decorators let AI activate abilities through tags, making GAS available to both player and AI pawns.
