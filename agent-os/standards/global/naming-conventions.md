# Naming Conventions

We follow Unreal’s prefix‑based naming. Use U.S. English.

## Type & Object Prefixes
- `U` — UObject‑derived classes (`UActorComponent`, `UTexture`)
- `A` — Actor‑derived classes (`ACharacter`)
- `S` — Slate widget classes (`SCompoundWidget`)
- `I` — Interfaces (`IAnalyticsProvider`)
- `F` — Most other structs/classes
- `T` — Templates (`TArray`, `TSharedPtr`)
- `E` — Enums (`enum class EWeaponType {...}`)

## Variables
- **Booleans** start with `b`: `bIsAlive`, `bPendingDestruction`.
- Use **PascalCase** for types and **UpperCamelCase** for members; avoid underscores except in macros.
- One declaration per line to allow per‑variable commenting.

## Macros
- Fully capitalized with underscores, prefixed with `UE_` when engine‑aligned: `UE_ENABLE_FOO`.

## Parameters
- Prefer `In`/`Out` hints when clarity helps, e.g., `OutResult`. For booleans, `bOut*`.

## Enums & Values
- Enum type: `EThing`.
- Scoped values: `EThing::Mode` or prefixed values like `ETeam::Team_Red` as team style dictates.
