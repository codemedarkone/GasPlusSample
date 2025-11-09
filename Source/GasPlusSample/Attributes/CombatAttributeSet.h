#pragma once

#include "CoreMinimal.h"
#include "AttributeSet.h"
#include "AbilitySystemComponent.h"

#include "CombatAttributeSet.generated.h"

UCLASS()
class GASPLUSSAMPLE_API UCombatAttributeSet : public UAttributeSet
{
    GENERATED_BODY()

public:
    UCombatAttributeSet();

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
    virtual void PreAttributeChange(const FGameplayAttribute& Attribute, float& NewValue) override;
    virtual void PostAttributeChange(const FGameplayAttribute& Attribute, float OldValue, float NewValue) override;

    // GASPLUS-PRESERVE BEGIN UCombatAttributeSet.PublicMembers
    // Add additional member declarations here.
    // GASPLUS-PRESERVE END UCombatAttributeSet.PublicMembers

    // Attribute: AttackPower
    // Metadata: Replicate=true, GenerateHooks=true, SkipOnRep=false, ClampMin=0.0
    // Scales outgoing damage.
    UPROPERTY(BlueprintReadOnly, Category="Combat", ReplicatedUsing=OnRep_AttackPower, meta=(ClampMin="0.0"))
    FGameplayAttributeData AttackPower;
    ATTRIBUTE_ACCESSORS(UCombatAttributeSet, AttackPower);

    // Attribute: DefensePower
    // Metadata: Replicate=false, GenerateHooks=true, SkipOnRep=false
    // Reduces incoming damage.
    UPROPERTY(BlueprintReadOnly, Category="Combat")
    FGameplayAttributeData DefensePower;
    ATTRIBUTE_ACCESSORS(UCombatAttributeSet, DefensePower);

    // Attribute: CriticalRate
    // Metadata: Replicate=true, GenerateHooks=false, SkipOnRep=false, ClampMin=0.0, ClampMax=1.0
    // Chance to critical hit.
    UPROPERTY(BlueprintReadOnly, Category="Combat", ReplicatedUsing=OnRep_CriticalRate, meta=(ClampMin="0.0", ClampMax="1.0"))
    FGameplayAttributeData CriticalRate;
    ATTRIBUTE_ACCESSORS(UCombatAttributeSet, CriticalRate);

    UFUNCTION()
    void OnRep_AttackPower(const FGameplayAttributeData& OldValue);

    UFUNCTION()
    void OnRep_CriticalRate(const FGameplayAttributeData& OldValue);
};
