#include "CombatAttributeSet.h"

#include "Net/UnrealNetwork.h"

UCombatAttributeSet::UCombatAttributeSet() = default;

void UCombatAttributeSet::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME_CONDITION_NOTIFY(UCombatAttributeSet, AttackPower, COND_None, REPNOTIFY_Always);
    DOREPLIFETIME_CONDITION_NOTIFY(UCombatAttributeSet, CriticalRate, COND_None, REPNOTIFY_Always);
}

void UCombatAttributeSet::PreAttributeChange(const FGameplayAttribute& Attribute, float& NewValue)
{
    Super::PreAttributeChange(Attribute, NewValue);
    if (Attribute == GetAttackPowerAttribute())
    {
        // Metadata: Replicate=true, GenerateHooks=true, SkipOnRep=false, ClampMin=0.0
        const float ClampedValue = FMath::Clamp(NewValue, 0.0, FLT_MAX);
        NewValue = ClampedValue;
        // TODO: Add pre-clamp logic for AttackPower if additional validation is required.
    }
    if (Attribute == GetDefensePowerAttribute())
    {
        // Metadata: Replicate=false, GenerateHooks=true, SkipOnRep=false
        // TODO: Add pre-clamp logic for DefensePower if additional validation is required.
    }
}

void UCombatAttributeSet::PostAttributeChange(const FGameplayAttribute& Attribute, float OldValue, float NewValue)
{
    Super::PostAttributeChange(Attribute, OldValue, NewValue);
    UE_UNUSED(OldValue);
    UE_UNUSED(NewValue);
    if (Attribute == GetAttackPowerAttribute())
    {
        // Metadata: Replicate=true, GenerateHooks=true, SkipOnRep=false, ClampMin=0.0
        // TODO: Add post-clamp logic for AttackPower (OldValue={OldValue}, NewValue={NewValue}).
    }
    if (Attribute == GetDefensePowerAttribute())
    {
        // Metadata: Replicate=false, GenerateHooks=true, SkipOnRep=false
        // TODO: Add post-clamp logic for DefensePower (OldValue={OldValue}, NewValue={NewValue}).
    }
}

void UCombatAttributeSet::OnRep_AttackPower(const FGameplayAttributeData& OldValue)
{
    GAMEPLAYATTRIBUTE_REPNOTIFY(UCombatAttributeSet, AttackPower, OldValue);
}

void UCombatAttributeSet::OnRep_CriticalRate(const FGameplayAttributeData& OldValue)
{
    GAMEPLAYATTRIBUTE_REPNOTIFY(UCombatAttributeSet, CriticalRate, OldValue);
}

