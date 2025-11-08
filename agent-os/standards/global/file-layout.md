# File Layout & Headers

## File Naming
- Match type names: `AExampleActor.h/.cpp`, `UHealthComponent.h/.cpp`.
- One public type per file unless closely coupled.

## Header Inclusion
- In `.cpp`, include **your own header first** to catch missing dependencies.
- Then local/project headers, then engine/third‑party headers.
- Prefer forward declarations in headers; include in `.cpp`.

## Class Skeleton
Public interface first, then protected, then private.

```cpp
UCLASS()
class PROJECT_API AExampleActor : public AActor
{
    GENERATED_BODY()

public:
    AExampleActor();

protected:
    virtual void BeginPlay() override;

private:
    void UpdateInternalState();
};
```
