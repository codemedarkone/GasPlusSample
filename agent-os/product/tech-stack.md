# Product Tech Stack

## Core Language & Engine
- **C++** (primary language for GAS+ plugin implementation) as the user stated, ensuring native performance and full access to Unreal’s gameplay systems.
- **Unreal Engine 5.6** (editor + runtime) which hosts the Gameplay Ability System, DataAsset workflows, and editor-only code generators.

## Gameplay Systems & Frameworks
- **Gameplay Ability System (GAS)** for Attributes, Effects, Cues, and Abilities, mirrored through the GasPlus plugin under `Plugins/GasPlus/Source`.
- **Data-Driven Configuration** via Unreal DataAssets (schemas, presets) to drive the AttributeSet Generator, Effect/ Cue builders, and Data-Driven Ability Base.

## Asset & Authoring Tooling
- **Unreal Editor Commandlets**/Utilities (editor agent patterns from `Plugins/GasPlus/Agents`) to run code generation, validation, and effect/cue builders.
- **UMG/Slate** for runtime overlays (Debug Overlay) and potential editor tools.
- **Behavior Trees & Blackboards** for AI Ability Integration tasks/decorators that activate GAS abilities.

## Runtime Helpers & Input
- **Runtime Façade API** wrappers (Blueprint + C++) to expose GAS actions safely to designers without re-implementing prediction concerns.
- **Enhanced Input System** to map Input Actions to ability tags with multiplayer/prediction awareness, especially for Win64 clients.

## Toolchain & Workflow
- **Visual Studio (latest supported version)** for building the C++ plugin and game modules via UnrealBuildTool.
- **Unreal Build Tool (UBT)** and **UE Command-Line Tools** for Editor builds, automation, and commandlet runs (e.g., `GasPlusCommandlet`).
- **Git** for source control alongside the project’s existing structure.

## Validation & Testing
- **Editor Validation Panel/Commandlets** to scan replication flags, tags, and DataAssets before cooking.
- **Unreal Automation Framework** for QA suites (functional, prediction, JIP) that run via `Automation RunTests GasPlus`.

## Platform Targets
- **Win64** (primary for development and packaging via BuildCookRun), matching the existing `Binaries/Win64` artifacts.

> Notes: This stack blends the user’s explicit choices (C++ + UE5) with the repo’s documented architecture (Agents, GAS plugin, DataAssets, tooling) to cover development, runtime, tooling, and testing surfaces.
