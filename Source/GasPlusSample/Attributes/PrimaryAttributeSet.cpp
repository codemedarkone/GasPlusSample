#include "PrimaryAttributeSet.h"

#include "Net/UnrealNetwork.h"

UPrimaryAttributeSet::UPrimaryAttributeSet() = default;

void UPrimaryAttributeSet::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME_CONDITION_NOTIFY(UPrimaryAttributeSet, Health, COND_None, REPNOTIFY_Always);
    DOREPLIFETIME_CONDITION_NOTIFY(UPrimaryAttributeSet, Mana, COND_None, REPNOTIFY_Always);
    DOREPLIFETIME(UPrimaryAttributeSet, Stamina);
}

void UPrimaryAttributeSet::PreAttributeChange(const FGameplayAttribute& Attribute, float& NewValue)
{
    Super::PreAttributeChange(Attribute, NewValue);
    if (Attribute == GetHealthAttribute())
    {
        // Metadata: Replicate=true, GenerateHooks=true, SkipOnRep=false, ClampMin=0.0, ClampMax=100.0
        const float ClampedValue = FMath::Clamp(NewValue, 0.0, 100.0);
        NewValue = ClampedValue;
        // TODO: Add pre-clamp logic for Health if additional validation is required.
    }
    if (Attribute == GetManaAttribute())
    {
        // Metadata: Replicate=true, GenerateHooks=true, SkipOnRep=false, ClampMin=0.0, ClampMax=250.0
        const float ClampedValue = FMath::Clamp(NewValue, 0.0, 250.0);
        NewValue = ClampedValue;
        // TODO: Add pre-clamp logic for Mana if additional validation is required.
    }
    if (Attribute == GetStaminaAttribute())
    {
        // Metadata: Replicate=true, GenerateHooks=true, SkipOnRep=true, ClampMin=0.0, ClampMax=150.0
        const float ClampedValue = FMath::Clamp(NewValue, 0.0, 150.0);
        NewValue = ClampedValue;
        // TODO: Add pre-clamp logic for Stamina if additional validation is required.
    }
}

void UPrimaryAttributeSet::PostAttributeChange(const FGameplayAttribute& Attribute, float OldValue, float NewValue)
{
    Super::PostAttributeChange(Attribute, OldValue, NewValue);
    UE_UNUSED(OldValue);
    UE_UNUSED(NewValue);
    if (Attribute == GetHealthAttribute())
    {
        // Metadata: Replicate=true, GenerateHooks=true, SkipOnRep=false, ClampMin=0.0, ClampMax=100.0
        // TODO: Add post-clamp logic for Health (OldValue={OldValue}, NewValue={NewValue}).
    }
    if (Attribute == GetManaAttribute())
    {
        // Metadata: Replicate=true, GenerateHooks=true, SkipOnRep=false, ClampMin=0.0, ClampMax=250.0
        // TODO: Add post-clamp logic for Mana (OldValue={OldValue}, NewValue={NewValue}).
    }
    if (Attribute == GetStaminaAttribute())
    {
        // Metadata: Replicate=true, GenerateHooks=true, SkipOnRep=true, ClampMin=0.0, ClampMax=150.0
        // TODO: Add post-clamp logic for Stamina (OldValue={OldValue}, NewValue={NewValue}).
    }
}

void UPrimaryAttributeSet::OnRep_Health(const FGameplayAttributeData& OldValue)
{
    GAMEPLAYATTRIBUTE_REPNOTIFY(UPrimaryAttributeSet, Health, OldValue);
}

void UPrimaryAttributeSet::OnRep_Mana(const FGameplayAttributeData& OldValue)
{
    GAMEPLAYATTRIBUTE_REPNOTIFY(UPrimaryAttributeSet, Mana, OldValue);
}

