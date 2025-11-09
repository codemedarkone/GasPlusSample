import json
from pathlib import Path

from Plugins.GasPlus.Agents.codegen.attribute_gen import (
    AttributeSetGenerator,
    GeneratorConfig,
)


def _make_config(tmp_path: Path, force: bool = False, **overrides) -> GeneratorConfig:
    output_root = tmp_path / "Source" / "GasPlusSample" / "Attributes"
    manifest_path = tmp_path / "Plugins" / "GasPlus" / "Agents" / "codegen" / "manifest.json"
    log_path = tmp_path / "Plugins" / "GasPlus" / "Agents" / "codegen" / "logs" / "attribute_gen.log"
    defaults = dict(
        input_roots=[tmp_path / "Content" / "Attributes"],
        output_root=output_root,
        manifest_path=manifest_path,
        log_path=log_path,
        force=force,
    )
    defaults.update(overrides)
    return GeneratorConfig(**defaults)


def _write_asset(tmp_path: Path, name: str, *, health: int = 100) -> Path:
    content_dir = tmp_path / "Content" / "Attributes"
    content_dir.mkdir(parents=True, exist_ok=True)
    asset_path = content_dir / f"{name}.json"
    payload = {
        "name": name,
        "className": f"U{name}AttributeSet",
        "moduleApi": "GASPLUSSAMPLE_API",
        "attributes": [
            {
                "name": "Health",
                "metadata": {
                    "Replicate": True,
                    "ClampMin": 0,
                    "ClampMax": health,
                },
            }
        ],
    }
    asset_path.write_text(json.dumps(payload, indent=2))
    return asset_path


def _load_manifest(manifest_path: Path) -> dict:
    return json.loads(manifest_path.read_text())


def test_hash_reuse_skips_write(tmp_path):
    _write_asset(tmp_path, "Primary", health=125)
    config = _make_config(tmp_path)
    generator = AttributeSetGenerator(config)
    generator.run()

    manifest_first = _load_manifest(config.manifest_path)
    entry_first = manifest_first["entries"][0]
    assert entry_first["status"]["write"] == "update"

    header_path = config.output_root / "PrimaryAttributeSet.h"
    initial_mtime = header_path.stat().st_mtime_ns

    generator = AttributeSetGenerator(config)
    generator.run()

    manifest_second = _load_manifest(config.manifest_path)
    entry_second = manifest_second["entries"][0]
    assert entry_second["status"]["write"] == "skip"
    assert entry_second["status"]["hashChanged"] is False
    assert header_path.stat().st_mtime_ns == initial_mtime


def test_change_detection_updates_hash(tmp_path):
    asset_path = _write_asset(tmp_path, "Primary", health=125)
    config = _make_config(tmp_path)
    AttributeSetGenerator(config).run()

    manifest_first = _load_manifest(config.manifest_path)
    first_hash = manifest_first["entries"][0]["hashes"]["composite"]

    payload = json.loads(asset_path.read_text())
    payload["attributes"][0]["metadata"]["ClampMax"] = 200
    asset_path.write_text(json.dumps(payload, indent=2))

    AttributeSetGenerator(config).run()
    manifest_second = _load_manifest(config.manifest_path)
    entry_second = manifest_second["entries"][0]

    assert entry_second["hashes"]["composite"] != first_hash
    assert entry_second["status"]["write"] == "update"
    assert entry_second["status"]["hashChanged"] is True


def test_preserve_regions_are_maintained(tmp_path):
    _write_asset(tmp_path, "Primary", health=150)
    config = _make_config(tmp_path)
    AttributeSetGenerator(config).run()

    source_path = config.output_root / "PrimaryAttributeSet.cpp"
    source_text = source_path.read_text()
    begin = "    // GASPLUS-PRESERVE BEGIN UPrimaryAttributeSet.PreAttributeChange"
    end = "    // GASPLUS-PRESERVE END UPrimaryAttributeSet.PreAttributeChange"
    assert begin in source_text and end in source_text
    custom_line = "    float CustomValue = 42.0f;\n"
    replacement = (
        f"{begin}\n"
        "    // Customize pre-attribute change logic here.\n"
        f"{custom_line}"
        f"{end}"
    )
    source_text = source_text.replace(
        f"{begin}\n    // Customize pre-attribute change logic here.\n{end}",
        replacement,
    )
    source_path.write_text(source_text)

    manifest_before = _load_manifest(config.manifest_path)
    first_hash = manifest_before["entries"][0]["hashes"]["composite"]

    AttributeSetGenerator(config).run()
    manifest_after = _load_manifest(config.manifest_path)
    entry_after = manifest_after["entries"][0]

    assert entry_after["hashes"]["composite"] == first_hash
    assert entry_after["status"]["write"] == "skip"

    payload = json.loads((tmp_path / "Content" / "Attributes" / "Primary.json").read_text())
    payload["attributes"][0]["metadata"]["ClampMax"] = 300
    (tmp_path / "Content" / "Attributes" / "Primary.json").write_text(
        json.dumps(payload, indent=2)
    )

    AttributeSetGenerator(config).run()
    manifest_third = _load_manifest(config.manifest_path)
    entry_third = manifest_third["entries"][0]

    assert entry_third["status"]["write"] == "update"
    preserve_status = entry_third["preserveRegions"]["source"][
        "UPrimaryAttributeSet.PreAttributeChange"
    ]["status"]
    assert preserve_status == "preserved"
    assert "float CustomValue = 42.0f;" in source_path.read_text()


def test_no_preserve_flag_discards_regions(tmp_path):
    _write_asset(tmp_path, "Primary", health=175)
    config = _make_config(tmp_path)
    AttributeSetGenerator(config).run()

    source_path = config.output_root / "PrimaryAttributeSet.cpp"
    begin = "    // GASPLUS-PRESERVE BEGIN UPrimaryAttributeSet.PreAttributeChange"
    end = "    // GASPLUS-PRESERVE END UPrimaryAttributeSet.PreAttributeChange"
    custom_line = "    float CustomValue = 99.0f;\n"
    source_text = source_path.read_text().replace(
        f"{begin}\n    // Customize pre-attribute change logic here.\n{end}",
        f"{begin}\n    // Customize pre-attribute change logic here.\n{custom_line}{end}",
    )
    source_path.write_text(source_text)

    payload = json.loads((tmp_path / "Content" / "Attributes" / "Primary.json").read_text())
    payload["attributes"][0]["metadata"]["ClampMax"] = 250
    (tmp_path / "Content" / "Attributes" / "Primary.json").write_text(
        json.dumps(payload, indent=2)
    )

    config_no_preserve = _make_config(tmp_path, no_preserve=True, force=True)
    AttributeSetGenerator(config_no_preserve).run()

    updated_source = source_path.read_text()
    assert "CustomValue" not in updated_source

    manifest = _load_manifest(config_no_preserve.manifest_path)
    status = manifest["entries"][0]["preserveRegions"]["source"][
        "UPrimaryAttributeSet.PreAttributeChange"
    ]["status"]
    assert status == "ignored"


def test_dry_run_produces_no_outputs(tmp_path, capsys):
    _write_asset(tmp_path, "Primary", health=125)
    config = _make_config(tmp_path, dry_run=True)
    AttributeSetGenerator(config).run()

    captured = capsys.readouterr()
    assert "DRY" in captured.out
    assert not config.output_root.exists()
    assert not config.manifest_path.exists()
    sidecar_root = config.manifest_path.parent / "PrimaryAttributeSet.generated.hash"
    assert not sidecar_root.exists()


def test_force_overrides_cached_hash(tmp_path):
    _write_asset(tmp_path, "Primary", health=125)
    config = _make_config(tmp_path)
    AttributeSetGenerator(config).run()

    manifest_first = _load_manifest(config.manifest_path)
    first_hash = manifest_first["entries"][0]["hashes"]["composite"]

    forced_config = _make_config(tmp_path, force=True)
    AttributeSetGenerator(forced_config).run()

    manifest_second = _load_manifest(forced_config.manifest_path)
    entry_second = manifest_second["entries"][0]
    assert entry_second["status"]["write"] == "force"
    assert entry_second["hashes"]["composite"] == first_hash
    assert entry_second["status"]["writesPerformed"] is True
