# UPROPERTY & UFUNCTION Guide

## UPROPERTY
- Declare properties with `UPROPERTY(...)` to integrate with reflection/serialization.
- Choose the narrowest specifiers needed (e.g., `VisibleAnywhere`, `EditDefaultsOnly`, `BlueprintReadOnly`).
- Organize with `Category="Subsystem|Feature"` and use `meta = (ClampMin = "0", ClampMax = "1")` etc. when helpful.
- Use `DisplayName` to present clear, designer‑friendly names (avoid internal prefixes).

**Example**

```cpp
UPROPERTY(EditDefaultsOnly, Category="Combat|Weapon", meta=(ClampMin="0"))
float FireRate = 5.f;
```

## UFUNCTION
- Mark Blueprint access deliberately: `BlueprintCallable` vs `BlueprintPure`.
- Use `Category` to group functions logically; prefer verbs: `Combat|Fire`.

**Example**

```cpp
UFUNCTION(BlueprintCallable, Category="Combat|Fire")
void StartFiring();
```
