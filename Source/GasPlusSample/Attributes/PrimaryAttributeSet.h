#pragma once

#include "CoreMinimal.h"
#include "AttributeSet.h"
#include "AbilitySystemComponent.h"
// <Codex::Preserve Begin: HeaderIncludes>
// <Codex::Preserve End: HeaderIncludes>

#include "PrimaryAttributeSet.generated.h"

UCLASS()
class GASPLUSSAMPLE_API UPrimaryAttributeSet : public UAttributeSet
{
    GENERATED_BODY()

public:
    UPrimaryAttributeSet();

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
    virtual void PreAttributeChange(const FGameplayAttribute& Attribute, float& NewValue) override;
    virtual void PostAttributeChange(const FGameplayAttribute& Attribute, float OldValue, float NewValue) override;

    // GASPLUS-PRESERVE BEGIN UPrimaryAttributeSet.PublicMembers
    // Add additional member declarations here.
    // GASPLUS-PRESERVE END UPrimaryAttributeSet.PublicMembers

    // Attribute: Health
    // Metadata: Replicate=true, GenerateHooks=true, SkipOnRep=false, ClampMin=0.0, ClampMax=100.0
    // Current character health points.
    UPROPERTY(BlueprintReadOnly, Category="Vitals", ReplicatedUsing=OnRep_Health, meta=(ClampMin="0.0", ClampMax="100.0"))
    FGameplayAttributeData Health;
    ATTRIBUTE_ACCESSORS(UPrimaryAttributeSet, Health);

    // Attribute: Mana
    // Metadata: Replicate=true, GenerateHooks=true, SkipOnRep=false, ClampMin=0.0, ClampMax=250.0
    // Primary resource for abilities.
    UPROPERTY(BlueprintReadOnly, Category="Vitals", ReplicatedUsing=OnRep_Mana, meta=(ClampMin="0.0", ClampMax="250.0"))
    FGameplayAttributeData Mana;
    ATTRIBUTE_ACCESSORS(UPrimaryAttributeSet, Mana);

    // Attribute: Stamina
    // Metadata: Replicate=true, GenerateHooks=true, SkipOnRep=true, ClampMin=0.0, ClampMax=150.0
    // Short burst resource for sprinting.
    UPROPERTY(BlueprintReadOnly, Category="Vitals", Replicated, meta=(ClampMin="0.0", ClampMax="150.0"))
    FGameplayAttributeData Stamina;
    ATTRIBUTE_ACCESSORS(UPrimaryAttributeSet, Stamina);

    UFUNCTION()
    void OnRep_Health(const FGameplayAttributeData& OldValue);

    UFUNCTION()
    void OnRep_Mana(const FGameplayAttributeData& OldValue);
};
