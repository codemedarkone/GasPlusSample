from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Mapping, Sequence

from Plugins.GasPlus.Agents.codegen.attribute_gen import (
    AttributeSetGenerator,
    GeneratorConfig,
)


MANIFEST_RELATIVE = Path("Plugins") / "GasPlus" / "Agents" / "codegen" / "manifest.json"
LOG_RELATIVE = (
    Path("Plugins") / "GasPlus" / "Agents" / "codegen" / "logs" / "attribute_gen.log"
)


def write_asset(tmp_path: Path, name: str, attributes: Sequence[Mapping[str, object]]):
    content_dir = tmp_path / "Content" / "Attributes"
    content_dir.mkdir(parents=True, exist_ok=True)
    asset_path = content_dir / f"{name}.json"
    payload = {
        "name": name,
        "className": f"U{name}AttributeSet",
        "moduleApi": "GASPLUSSAMPLE_API",
        "attributes": list(attributes),
    }
    asset_path.write_text(json.dumps(payload, indent=2))
    return asset_path


def run_generator(tmp_path: Path):
    output_root = tmp_path / "Source" / "GasPlusSample" / "Attributes"
    manifest_path = tmp_path / MANIFEST_RELATIVE
    log_path = tmp_path / LOG_RELATIVE
    config = GeneratorConfig(
        input_roots=[tmp_path / "Content" / "Attributes"],
        output_root=output_root,
        manifest_path=manifest_path,
        log_path=log_path,
        force=True,
    )
    generator = AttributeSetGenerator(config)
    generator.run()
    return output_root


def extract_property_spec(header: str, attribute_name: str) -> str:
    pattern = rf"UPROPERTY\(([^)]*)\)\s+FGameplayAttributeData {attribute_name};"
    match = re.search(pattern, header, re.MULTILINE | re.DOTALL)
    if not match:
        raise AssertionError(f"Property {attribute_name} not found in header")
    return match.group(1)


def manifest_path(tmp_path: Path) -> Path:
    return tmp_path / MANIFEST_RELATIVE


def log_path(tmp_path: Path) -> Path:
    return tmp_path / LOG_RELATIVE


def load_manifest(tmp_path: Path) -> Mapping[str, object]:
    return json.loads(manifest_path(tmp_path).read_text())
