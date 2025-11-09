import hashlib

from . import utils


def test_manifest_metadata_summary_includes_all_flags(tmp_path):
    utils.write_asset(
        tmp_path,
        "MetaSummary",
        [
            {
                "name": "Energy",
                "metadata": {
                    "Replicate": True,
                    "GenerateHooks": False,
                    "SkipOnRep": False,
                    "ClampMin": 5.0,
                    "ClampMax": 50.0,
                },
            }
        ],
    )
    utils.run_generator(tmp_path)

    manifest = utils.load_manifest(tmp_path)
    entry = manifest["entries"][0]
    metadata = entry["attributes"][0]["metadata"]

    assert metadata == {
        "Replicate": True,
        "GenerateHooks": False,
        "SkipOnRep": False,
        "ClampMin": 5.0,
        "ClampMax": 50.0,
    }


def test_input_hash_matches_asset_contents(tmp_path):
    asset_path = utils.write_asset(
        tmp_path,
        "HashCheck",
        [
            {
                "name": "Resolve",
                "metadata": {
                    "Replicate": True,
                    "ClampMin": 0,
                },
            }
        ],
    )
    utils.run_generator(tmp_path)

    manifest = utils.load_manifest(tmp_path)
    entry = manifest["entries"][0]

    expected_hash = hashlib.sha256(asset_path.read_bytes()).hexdigest()
    assert entry["inputHash"] == expected_hash


def test_manifest_contains_generator_versions(tmp_path):
    utils.write_asset(
        tmp_path,
        "Versioned",
        [
            {
                "name": "Speed",
                "metadata": {
                    "Replicate": False,
                },
            }
        ],
    )
    utils.run_generator(tmp_path)

    manifest = utils.load_manifest(tmp_path)
    assert manifest["generatorVersion"] == "1.0.0"
    assert manifest["templateVersion"] == "1.0.0"
    assert manifest["entries"]


def test_preserve_regions_retained_after_regeneration(tmp_path):
    utils.write_asset(
        tmp_path,
        "Preserve",
        [
            {
                "name": "Barrier",
                "metadata": {
                    "Replicate": True,
                    "ClampMin": 0,
                    "ClampMax": 1,
                },
            }
        ],
    )
    output_root = utils.run_generator(tmp_path)
    header_path = output_root / "PreserveAttributeSet.h"
    source_path = output_root / "PreserveAttributeSet.cpp"

    header_text = header_path.read_text().replace(
        "// <Codex::Preserve Begin: HeaderIncludes>\n// <Codex::Preserve End: HeaderIncludes>",
        "// <Codex::Preserve Begin: HeaderIncludes>\n#include \"CustomPreserve.h\"\n// <Codex::Preserve End: HeaderIncludes>",
    )
    header_path.write_text(header_text)

    source_placeholder = (
        "    // <Codex::Preserve Begin: PostAttributeChange_Custom>\n"
        "    // <Codex::Preserve End: PostAttributeChange_Custom>"
    )
    source_replacement = (
        "    // <Codex::Preserve Begin: PostAttributeChange_Custom>\n"
        "    UE_LOG(LogTemp, Verbose, TEXT(\"Preserved Hook\"));\n"
        "    // <Codex::Preserve End: PostAttributeChange_Custom>"
    )
    source_text = source_path.read_text().replace(source_placeholder, source_replacement)
    source_path.write_text(source_text)

    utils.run_generator(tmp_path)

    header_after = header_path.read_text()
    source_after = source_path.read_text()

    assert header_after.count("CustomPreserve.h") == 1
    assert "UE_LOG(LogTemp, Verbose, TEXT(\"Preserved Hook\"));" in source_after


def test_meta_attribute_registry_include_emitted(tmp_path):
    utils.write_asset(
        tmp_path,
        "MetaAttr",
        [
            {
                "name": "Damage",
                "metadata": {
                    "Replicate": True,
                    "MetaAttribute": "OutgoingDamage",
                },
            }
        ],
    )
    output_root = utils.run_generator(tmp_path)

    header = (output_root / "MetaAttrAttributeSet.h").read_text()
    assert "#include \"GasPlusMetaAttributeRegistry.h\"" in header
    assert "MetaAttribute=OutgoingDamage" in header

    manifest = utils.load_manifest(tmp_path)
    manifest_metadata = manifest["entries"][0]["attributes"][0]["metadata"]
    assert manifest_metadata["MetaAttribute"] == "OutgoingDamage"


def test_generation_log_contains_entries(tmp_path):
    utils.write_asset(
        tmp_path,
        "Logging",
        [
            {
                "name": "Vitality",
                "metadata": {
                    "Replicate": True,
                },
            }
        ],
    )
    utils.run_generator(tmp_path)

    log_contents = utils.log_path(tmp_path).read_text()
    assert "Generated ULoggingAttributeSet" in log_contents


def test_metadata_comment_lists_flags(tmp_path):
    utils.write_asset(
        tmp_path,
        "Comment",
        [
            {
                "name": "Armor",
                "metadata": {
                    "Replicate": False,
                    "GenerateHooks": True,
                    "SkipOnRep": True,
                    "ClampMin": -10,
                    "ClampMax": 200,
                },
            }
        ],
    )
    output_root = utils.run_generator(tmp_path)
    header = (output_root / "CommentAttributeSet.h").read_text()

    assert "Metadata: Replicate=false, GenerateHooks=true, SkipOnRep=true, ClampMin=-10.0, ClampMax=200.0" in header
