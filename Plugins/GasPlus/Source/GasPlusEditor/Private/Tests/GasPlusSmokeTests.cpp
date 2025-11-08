#if WITH_AUTOMATION_TESTS

#include "Misc/AutomationTest.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FGasPlusSmoke_Builds,
    "Project.GasPlus.Smoke.Builds",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FGasPlusSmoke_Builds::RunTest(const FString &Parameters)
{
    TestTrue(TEXT("Basic truth holds"), true);
    return true;
}

#endif // WITH_AUTOMATION_TESTS
