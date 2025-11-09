import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from . import utils


def test_replicated_attribute_emits_onrep(tmp_path):
    utils.write_asset(
        tmp_path,
        "Primary",
        [
            {
                "name": "Health",
                "metadata": {
                    "Replicate": True,
                },
            }
        ],
    )
    output_root = utils.run_generator(tmp_path)
    header = (output_root / "PrimaryAttributeSet.h").read_text()
    source = (output_root / "PrimaryAttributeSet.cpp").read_text()

    assert "ReplicatedUsing=OnRep_Health" in header
    assert "void OnRep_Health" in header
    assert "DOREPLIFETIME_CONDITION_NOTIFY(UPrimaryAttributeSet, Health" in source
    assert "GAMEPLAYATTRIBUTE_REPNOTIFY(UPrimaryAttributeSet, Health" in source


def test_skip_replication_metadata(tmp_path):
    utils.write_asset(
        tmp_path,
        "Secondary",
        [
            {
                "name": "Mana",
                "metadata": {
                    "Replicate": False,
                    "GenerateHooks": True,
                },
            }
        ],
    )
    output_root = utils.run_generator(tmp_path)
    header = (output_root / "SecondaryAttributeSet.h").read_text()
    source = (output_root / "SecondaryAttributeSet.cpp").read_text()

    spec = utils.extract_property_spec(header, "Mana")
    assert "Replicated" not in spec
    assert "OnRep_Mana" not in header
    assert "DOREPLIFETIME" not in source


def test_skip_onrep_metadata(tmp_path):
    utils.write_asset(
        tmp_path,
        "Tertiary",
        [
            {
                "name": "Stamina",
                "metadata": {
                    "Replicate": True,
                    "SkipOnRep": True,
                },
            }
        ],
    )
    output_root = utils.run_generator(tmp_path)
    header = (output_root / "TertiaryAttributeSet.h").read_text()
    source = (output_root / "TertiaryAttributeSet.cpp").read_text()

    spec = utils.extract_property_spec(header, "Stamina")
    assert "ReplicatedUsing=OnRep_Stamina" not in spec
    assert "Replicated" in spec
    assert "OnRep_Stamina" not in header
    assert "DOREPLIFETIME_CONDITION_NOTIFY" not in source
    assert "DOREPLIFETIME(UTertiaryAttributeSet, Stamina" in source


def test_clamp_metadata_generates_clamp_code(tmp_path):
    utils.write_asset(
        tmp_path,
        "Quaternary",
        [
            {
                "name": "Armor",
                "metadata": {
                    "ClampMin": 0.0,
                    "ClampMax": 100.0,
                },
            }
        ],
    )
    output_root = utils.run_generator(tmp_path)
    source = (output_root / "QuaternaryAttributeSet.cpp").read_text()

    assert "FMath::Clamp(NewValue, 0.0, 100.0)" in source


def test_generate_hooks_false_omits_pre_post_blocks(tmp_path):
    utils.write_asset(
        tmp_path,
        "Quinary",
        [
            {
                "name": "Shield",
                "metadata": {
                    "GenerateHooks": False,
                },
            }
        ],
    )
    output_root = utils.run_generator(tmp_path)
    source = (output_root / "QuinaryAttributeSet.cpp").read_text()

    assert "GetShieldAttribute" not in source


@pytest.mark.skipif(shutil.which("g++") is None, reason="g++ compiler is required")
def test_generated_code_compiles(tmp_path):
    utils.write_asset(
        tmp_path,
        "CompileCheck",
        [
            {
                "name": "Focus",
                "metadata": {
                    "Replicate": True,
                    "ClampMin": 0,
                },
            }
        ],
    )
    output_root = utils.run_generator(tmp_path)
    header_path = output_root / "CompileCheckAttributeSet.h"
    source_path = output_root / "CompileCheckAttributeSet.cpp"
    generated_header_path = output_root / "CompileCheckAttributeSet.generated.h"

    stub_include_root = tmp_path / "stubs"
    (stub_include_root / "Net").mkdir(parents=True, exist_ok=True)

    (stub_include_root / "CoreMinimal.h").write_text(
        """#pragma once\n\n#include <cfloat>\n#include <algorithm>\n\n#define GASPLUSSAMPLE_API\n#define UCLASS(...)\n#define UFUNCTION(...)\n#define UPROPERTY(...)\n#define GENERATED_BODY() using Super = UAttributeSet;\n#define UE_UNUSED(Expr) (void)(Expr)\n"""
    )
    attribute_stub = (
        "#pragma once\n\n"
        "#include <vector>\n\n"
        "using FLifetimeProperty = int;\n"
        "template <typename T>\n"
        "class TArray : public std::vector<T> {\n"
        "public:\n"
        "    using std::vector<T>::vector;\n"
        "};\n\n"
        "struct FGameplayAttributeData {\n"
        "    float CurrentValue = 0.0f;\n"
        "    float GetCurrentValue() const { return CurrentValue; }\n"
        "    void SetCurrentValue(float Value) { CurrentValue = Value; }\n"
        "};\n\n"
        "struct FGameplayAttribute {};\n\n"
        "inline bool operator==(const FGameplayAttribute&, const FGameplayAttribute&) {\n"
        "    return true;\n"
        "}\n\n"
        "struct FMath {\n"
        "    static float Clamp(float Value, float Min, float Max) {\n"
        "        return std::max(Min, std::min(Value, Max));\n"
        "    }\n"
        "};\n\n"
        "class UAttributeSet {\n"
        "public:\n"
        "    virtual ~UAttributeSet() = default;\n"
        "    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>&) const {}\n"
        "    virtual void PreAttributeChange(const FGameplayAttribute&, float&) {}\n"
        "    virtual void PostAttributeChange(const FGameplayAttribute&, float, float) {}\n"
        "};\n\n"
        "#define ATTRIBUTE_ACCESSORS(ClassName, PropertyName) \\\n"
        "    static FGameplayAttribute Get##PropertyName##Attribute() { return FGameplayAttribute(); } \\\n"
        "    float Get##PropertyName() const { return PropertyName.GetCurrentValue(); } \\\n"
        "    void Set##PropertyName(float NewValue) { PropertyName.SetCurrentValue(NewValue); } \\\n"
        "    void Init##PropertyName(float NewValue) { PropertyName.SetCurrentValue(NewValue); }\n"
        "#define GAMEPLAYATTRIBUTE_PROPERTY_GETTER(ClassName, PropertyName)\n"
        "#define GAMEPLAYATTRIBUTE_VALUE_GETTER(PropertyName)\n"
        "#define GAMEPLAYATTRIBUTE_VALUE_SETTER(PropertyName)\n"
        "#define GAMEPLAYATTRIBUTE_VALUE_INITTER(PropertyName)\n"
    )
    (stub_include_root / "AttributeSet.h").write_text(attribute_stub)
    (stub_include_root / "AbilitySystemComponent.h").write_text("#pragma once\n")
    (stub_include_root / "Net/UnrealNetwork.h").write_text(
        """#pragma once\n\n#define COND_None 0\n#define REPNOTIFY_Always 0\n#define DOREPLIFETIME(ClassName, PropertyName) do {} while (0)\n#define DOREPLIFETIME_CONDITION_NOTIFY(ClassName, PropertyName, Condition, NotifyPolicy) do {} while (0)\n#define GAMEPLAYATTRIBUTE_REPNOTIFY(ClassName, PropertyName, OldValue) do {} while (0)\n"""
    )
    (stub_include_root / "CompileCheckAttributeSet.generated.h").write_text("#pragma once\n")

    compile_dir = tmp_path / "compile"
    compile_dir.mkdir(parents=True, exist_ok=True)
    test_cpp = compile_dir / "test.cpp"
    test_cpp.write_text(
        """#include \"CompileCheckAttributeSet.h\"\n#include \"CompileCheckAttributeSet.cpp\"\nint main() { return 0; }\n"""
    )

    include_flags = [
        f"-I{stub_include_root}",
        f"-I{output_root}",
    ]
    result = subprocess.run(
        [
            "g++",
            "-std=c++17",
            "-c",
            str(test_cpp),
            "-o",
            str(compile_dir / "test.o"),
            *include_flags,
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(compile_dir),
    )

    assert result.returncode == 0, result.stderr
