#include "GasPlusCommandlet.h"
#include "Misc/Parse.h"

UGasPlusCommandlet::UGasPlusCommandlet()
{
    IsClient = false;
    IsEditor = true;
    LogToConsole = true;
}

int32 UGasPlusCommandlet::Main(const FString &Params)
{
    UE_LOG(LogTemp, Display, TEXT("GasPlusCommandlet running. Params: %s"), *Params);

    FString Preset;
    FParse::Value(*Params, TEXT("-Preset="), Preset);

    // TODO: run your preset logic
    return 0;
}
