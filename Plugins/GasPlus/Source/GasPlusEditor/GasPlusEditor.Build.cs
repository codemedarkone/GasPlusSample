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
                "GameplayTags",
                "GasPlusSample"
            }
        );

        PrivateDependencyModuleNames.AddRange(
            new string[]
            {
                "GasPlus" // your runtime plugin module
            }
        );
    }
}
