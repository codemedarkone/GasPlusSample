
#pragma once

#include "CoreMinimal.h"
#include "Commandlets/Commandlet.h"
#include "GasPlusCommandlet.generated.h" // must be the LAST include

UCLASS()
class GASPLUSEDITOR_API UGasPlusCommandlet : public UCommandlet
{
    GENERATED_BODY()

public:
    UGasPlusCommandlet();

    virtual int32 Main(const FString &Params) override;
};

// #pragma once

// #include "Commandlets/Commandlet.h"
// #include "GasPlusCommandlet.generated.h" // must be the LAST include

// UCLASS()
// class GASPLUSEDITOR_API UGasPlusCommandlet : public UCommandlet
// {
//     GENERATED_BODY()

// public:
//     UGasPlusCommandlet();

//     virtual int32 Main(const FString &Params) override;
// };
