using UnrealBuildTool;

public class GasPlusEditor : ModuleRules
{
    public GasPlusEditor(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(
            new string[]
            {
                "Core",
                "CoreUObject",
                "Engine",
                "UnrealEd",
                "Slate",
                "SlateCore",
                "Projects",
                "GameplayTasks",
                "GameplayTags",
                "GameplayAbilities",
                "EnhancedInput"

            }
        );

        PrivateDependencyModuleNames.AddRange(
            new string[]
            {
                "GasPlus" // your runtime plugin module
            }
        );
        // Usually defined for non-shipping Editor builds already, but harmless to force:
        PrivateDefinitions.Add("WITH_AUTOMATION_TESTS=1");
    }
}
