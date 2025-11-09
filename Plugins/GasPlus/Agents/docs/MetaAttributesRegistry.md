# Meta-Attribute Registry Overview

The Task Group 3 update introduces a persistent meta-attribute registry so every generated `UAttributeSet` can route derived gameplay values (damage, healing, shield adjustments) in a consistent way. The registry lives under `Source/GasPlusSample/Attributes/Meta/` as a stable, engine-style C++ module that does **not** participate in generator diffing. This placement aligns with the directory boundaries diagram in [`AGENTS.md`](../../../../AGENTS.md), keeping generator output under `Source/GasPlusSample/Attributes/` while reserving the plugin-owned `/Plugins/GasPlus/Agents` tree for automation inputs and docs.

## Purpose and Naming Conventions

Meta-attributes act as *derived channels* that collect effect magnitudes before they are applied to primary stats. Each entry in the registry follows the `PascalCase` Unreal convention and mirrors the backing attribute name to keep aggregator lookups deterministic. For example:

- **Damage** – accumulates outgoing hit point deltas that will later drain Health or Shields.
- **Heal** – aggregates incoming restorative effects before clamping.
- **ShieldDelta** – tracks absorption changes that may bypass core health pools.

Because the registry is static, it can be `#include`d anywhere without triggering regeneration, and the accessor methods (`GetDamage`, `GetHeal`, `GetShieldDelta`) provide type-safe handles for gameplay code, editor tooling, and tests.

## Integration with Generated AttributeSets

The AttributeSet generator now emits `#include "Meta/MetaAttributes.h"` for every generated header so the registry is always available. This keeps the include order consistent with Unreal style (`CoreMinimal`, `AttributeSet`, `AbilitySystemComponent`, then project-local headers) and means any new attribute set can opt into meta-attribute routing without extra manual edits. When codegen runs inside a clean workspace, the generator verifies that `Meta/MetaAttributes.h/.cpp` exist and writes them once, only updating the files if their contents change.

Within each AttributeSet you can query the registry to coordinate derived behavior:

```cpp
#include "Meta/MetaAttributes.h"

using namespace GasPlusSample::Attributes::Meta;

void UCombatAttributeSet::PostAttributeChange(const FGameplayAttribute& Attribute, float OldValue, float NewValue)
{
    Super::PostAttributeChange(Attribute, OldValue, NewValue);

    const FMetaAttributeDefinition& DamageMeta = FMetaAttributesRegistry::Get().GetDamage();
    UE_UNUSED(DamageMeta);
    // Use DamageMeta.BackingAttributeName to dispatch to the correct primary stat.
}
```

## Extending the Registry from Tools

Editor utilities or automation tools can register new meta-attributes at runtime without touching the generated files. Call `FMetaAttributesRegistry::RegisterEditorExtension` during editor startup or just before codegen runs:

```cpp
using namespace GasPlusSample::Attributes::Meta;

void UMyAttributeAuthoringTool::RegisterCustomMeta()
{
    const FMetaAttributeDefinition OverchargeMeta(
        TEXT("Overcharge"),
        TEXT("Overcharge"),
        TEXT("Tracks temporary charge that should decay after a gameplay effect."));

    FMetaAttributesRegistry::RegisterEditorExtension(OverchargeMeta);
}
```

The registration helper guards against duplicates, so invoking it multiple times (for example during PIE restarts) is safe. Keep custom registry writes inside the project/module tree defined in `AGENTS.md` to preserve deterministic builds.

## Supported Attribute Metadata Keys

| Key            | Description                                                                                   | Example Value |
|----------------|-----------------------------------------------------------------------------------------------|---------------|
| `Replicate`    | Enables Unreal replication for the attribute (`DOREPLIFETIME` or `DOREPLIFETIME_CONDITION`).  | `true`        |
| `GenerateHooks`| Emits `PreAttributeChange`/`PostAttributeChange` clamp stubs.                                  | `false`       |
| `SkipOnRep`    | Keeps replication but skips the `OnRep_` notify wrapper.                                      | `true`        |
| `ClampMin`     | Minimum value enforced in `PreAttributeChange`.                                               | `0.0`         |
| `ClampMax`     | Maximum value enforced in `PreAttributeChange`.                                               | `250.0`       |

These metadata keys are documented inline in each generated AttributeSet and remain the primary knobs for designers when authoring attribute schemas.

## Code Examples

### OnRep Hook Pattern

```cpp
UFUNCTION()
void UPrimaryAttributeSet::OnRep_Health(const FGameplayAttributeData& OldValue)
{
    GAMEPLAYATTRIBUTE_REPNOTIFY(UPrimaryAttributeSet, Health, OldValue);
}
```

### PreClamp / PostClamp Stub Pattern

```cpp
void UPrimaryAttributeSet::PreAttributeChange(const FGameplayAttribute& Attribute, float& NewValue)
{
    Super::PreAttributeChange(Attribute, NewValue);
    if (Attribute == GetManaAttribute())
    {
        const float ClampedValue = FMath::Clamp(NewValue, 0.0f, 250.0f);
        NewValue = ClampedValue;
        // TODO: Add pre-clamp logic for Mana if additional validation is required.
    }
}

void UPrimaryAttributeSet::PostAttributeChange(const FGameplayAttribute& Attribute, float OldValue, float NewValue)
{
    Super::PostAttributeChange(Attribute, OldValue, NewValue);
    if (Attribute == GetManaAttribute())
    {
        // TODO: Add post-clamp logic for Mana (OldValue={OldValue}, NewValue={NewValue}).
    }
}
```

### Registry Include Pattern

```cpp
#pragma once

#include "CoreMinimal.h"
#include "AttributeSet.h"
#include "AbilitySystemComponent.h"
#include "Meta/MetaAttributes.h"
```

Placing the registry include after the engine headers preserves the layering described in `AGENTS.md` and ensures the meta definitions are available for any additional helper methods you add to the AttributeSet.
