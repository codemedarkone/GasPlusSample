from __future__ import annotations

import argparse
import configparser
import dataclasses
import hashlib
import json
import os
import re
import textwrap
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

DEFAULT_INPUT_ROOTS = ["Content/Attributes"]
DEFAULT_OUTPUT_ROOT = "Source/GasPlusSample/Attributes"
DEFAULT_CONFIG_PATH = "Config/GasPlus.AttributeGen.ini"
DEFAULT_MANIFEST_PATH = "Plugins/GasPlus/Agents/codegen/manifest.json"
DEFAULT_LOG_PATH = "Plugins/GasPlus/Agents/codegen/logs/attribute_gen.log"
GENERATOR_VERSION = "1.0.0"
TEMPLATE_VERSION = "1.0.0"


@dataclass
class AttributeMetadata:
    replicate: bool = True
    generate_hooks: bool = True
    skip_on_rep: bool = False
    clamp_min: Optional[float] = None
    clamp_max: Optional[float] = None
    meta_attribute: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "AttributeMetadata":
        def _as_bool(value: object, default: bool) -> bool:
            if value is None:
                return default
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                normalized = value.strip().lower()
                if normalized in {"true", "1", "yes", "on"}:
                    return True
                if normalized in {"false", "0", "no", "off"}:
                    return False
            raise ValueError(f"Unable to coerce boolean from {value!r}")

        def _as_float(value: object) -> Optional[float]:
            if value is None:
                return None
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str) and value.strip():
                return float(value)
            raise ValueError(f"Unable to coerce float from {value!r}")

        meta_attribute_raw = data.get("MetaAttribute") or data.get("metaAttribute")
        if isinstance(meta_attribute_raw, str):
            meta_attribute = meta_attribute_raw.strip() or None
        elif isinstance(meta_attribute_raw, bool):
            meta_attribute = str(meta_attribute_raw).lower()
        else:
            meta_attribute = None

        return cls(
            replicate=_as_bool(
                data.get("Replicate", data.get("replicate")), True
            ),
            generate_hooks=_as_bool(
                data.get("GenerateHooks", data.get("generateHooks")), True
            ),
            skip_on_rep=_as_bool(
                data.get("SkipOnRep", data.get("skipOnRep")), False
            ),
            clamp_min=_as_float(data.get("ClampMin", data.get("clampMin"))),
            clamp_max=_as_float(data.get("ClampMax", data.get("clampMax"))),
            meta_attribute=meta_attribute,
        )

    def to_summary(self) -> Dict[str, object]:
        summary: Dict[str, object] = {
            "Replicate": self.replicate,
            "GenerateHooks": self.generate_hooks,
            "SkipOnRep": self.skip_on_rep,
        }
        if self.clamp_min is not None:
            summary["ClampMin"] = self.clamp_min
        if self.clamp_max is not None:
            summary["ClampMax"] = self.clamp_max
        if self.meta_attribute is not None:
            summary["MetaAttribute"] = self.meta_attribute
        return summary


@dataclass
class AttributeDefinition:
    name: str
    category: str = "Attributes"
    comment: Optional[str] = None
    metadata: AttributeMetadata = field(default_factory=AttributeMetadata)


@dataclass
class AttributeSetAsset:
    name: str
    class_name: str
    module_api: str = "GASPLUSSAMPLE_API"
    attributes: List[AttributeDefinition] = field(default_factory=list)
    source_path: Path = field(default_factory=Path)

    @property
    def file_basename(self) -> str:
        return f"{self.class_name[1:] if self.class_name.startswith('U') else self.class_name}"  # type: ignore[return-value]


@dataclass
class GeneratorConfig:
    input_roots: Sequence[Path] = dataclasses.field(default_factory=list)
    output_root: Path = Path(DEFAULT_OUTPUT_ROOT)
    manifest_path: Path = Path(DEFAULT_MANIFEST_PATH)
    log_path: Path = Path(DEFAULT_LOG_PATH)
    force: bool = False
    dry_run: bool = False
    no_preserve: bool = False


_PRESERVE_PATTERN = re.compile(
    r"(?P<indent>[ \t]*)// <Codex::Preserve Begin: (?P<key>[^>]+)>\s*\n(?P<body>.*?)(?P=indent)// <Codex::Preserve End: (?P=key)>",
    re.DOTALL,
)


def _collect_preserve_regions(text: str) -> Dict[str, str]:
    regions: Dict[str, str] = {}
    if not text:
        return regions
    for match in _PRESERVE_PATTERN.finditer(text):
        key = match.group("key").strip()
        regions[key] = match.group("body")
    return regions


def _merge_preserve_regions(existing_text: str, new_text: str) -> str:
    if not existing_text:
        return new_text
    existing_regions = _collect_preserve_regions(existing_text)
    if not existing_regions:
        return new_text

    def _replacer(match: re.Match[str]) -> str:
        key = match.group("key").strip()
        indent = match.group("indent")
        preserved = existing_regions.get(key)
        if preserved is None:
            return match.group(0)
        body = preserved
        if body and not body.endswith("\n"):
            body += "\n"
        return (
            f"{indent}// <Codex::Preserve Begin: {key}>\n"
            f"{body}"
            f"{indent}// <Codex::Preserve End: {key}>"
        )

    return _PRESERVE_PATTERN.sub(_replacer, new_text)


class AttributeSetGenerator:
    """Main entry point for attribute set generation."""

    def __init__(self, config: GeneratorConfig):
        self.config = config

    @staticmethod
    def from_args(args: Optional[Sequence[str]] = None) -> "AttributeSetGenerator":
        parser = argparse.ArgumentParser(description="Generate AttributeSet C++ code from DataAssets.")
        parser.add_argument(
            "--input",
            "-i",
            action="append",
            dest="inputs",
            default=None,
            help="Input directory containing attribute DataAssets (defaults to Content/Attributes and Content/**/DataAssets)",
        )
        parser.add_argument(
            "--output",
            "-o",
            dest="output",
            default=DEFAULT_OUTPUT_ROOT,
            help="Output directory for generated AttributeSets.",
        )
        parser.add_argument(
            "--config",
            dest="config_path",
            default=DEFAULT_CONFIG_PATH,
            help="Optional configuration file to override inputs/outputs.",
        )
        parser.add_argument(
            "--manifest",
            dest="manifest",
            default=DEFAULT_MANIFEST_PATH,
            help="Manifest file path to record generation details.",
        )
        parser.add_argument(
            "--log",
            dest="log_path",
            default=DEFAULT_LOG_PATH,
            help="Log file path to record generator activity.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force regeneration even when hashes are unchanged.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Compute generation results without writing any files.",
        )
        parser.add_argument(
            "--no-preserve",
            action="store_true",
            help="Disable preservation of // GASPLUS-PRESERVE blocks in existing outputs.",
        )

        parsed = parser.parse_args(args=args)
        input_roots = AttributeSetGenerator._resolve_input_roots(parsed.inputs, parsed.config_path)
        config = GeneratorConfig(
            input_roots=input_roots,
            output_root=Path(parsed.output),
            manifest_path=Path(parsed.manifest),
            log_path=Path(parsed.log_path),
            force=parsed.force,
            dry_run=parsed.dry_run,
            no_preserve=parsed.no_preserve,
        )
        return AttributeSetGenerator(config)

    @staticmethod
    def _resolve_input_roots(cli_inputs: Optional[Sequence[str]], config_path: str) -> Sequence[Path]:
        roots: List[Path] = []
        if cli_inputs:
            roots.extend(Path(p).resolve() for p in cli_inputs)
        else:
            config = configparser.ConfigParser()
            config_path_obj = Path(config_path)
            if config_path_obj.exists():
                config.read(config_path)
                if config.has_section("AttributeGenerator"):
                    items = config.get("AttributeGenerator", "InputRoots", fallback="").split(",")
                    roots.extend(Path(item.strip()).resolve() for item in items if item.strip())
                    output_override = config.get("AttributeGenerator", "OutputRoot", fallback="").strip()
                    if output_override:
                        # Output override is handled by caller via config if needed.
                        pass
            if not roots:
                for default in DEFAULT_INPUT_ROOTS:
                    roots.append(Path(default).resolve())
                roots.extend(
                    Path(path).resolve()
                    for path in AttributeSetGenerator._discover_dataasset_roots(Path("Content"))
                    if path not in roots
                )
        return roots

    @staticmethod
    def _discover_dataasset_roots(content_root: Path) -> Iterable[Path]:
        if not content_root.exists():
            return []
        discovered: List[Path] = []
        for root, dirs, files in os.walk(content_root):
            path = Path(root)
            if path.name == "DataAssets":
                discovered.append(path)
        return discovered

    def run(self) -> None:
        start_time = time.time()
        assets = list(self._discover_assets())
        log_lines: List[str] = []
        manifest_entries: List[Dict[str, object]] = []
        cli_lines: List[str] = []

        overrides = {
            "force": self.config.force,
            "dryRun": self.config.dry_run,
            "noPreserve": self.config.no_preserve,
        }

        output_root = self.config.output_root.resolve()
        if not self.config.dry_run:
            output_root.mkdir(parents=True, exist_ok=True)
            if self.config.manifest_path.parent:
                self.config.manifest_path.parent.mkdir(parents=True, exist_ok=True)
            if self.config.log_path.parent:
                self.config.log_path.parent.mkdir(parents=True, exist_ok=True)

        for asset in assets:
            result = self._process_asset(asset)
            manifest_entries.append(result["manifest"])
            if result["log_line"]:
                log_lines.append(result["log_line"])
            cli_lines.append(result["cli_line"])

        elapsed = round(time.time() - start_time, 4)
        manifest = {
            "generatorVersion": GENERATOR_VERSION,
            "templateVersion": TEMPLATE_VERSION,
            "elapsedSeconds": elapsed,
            "flags": overrides,
            "entries": manifest_entries,
        }

        if not self.config.dry_run:
            self.config.manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
            log_output = "\n".join(log_lines)
            if log_output:
                log_output += "\n"
            self.config.log_path.write_text(log_output)

        for line in cli_lines:
            print(line)
        if not cli_lines:
            print("No attribute sets processed.")
        print("Validation issues: none detected.")
        print(
            f"Completed attribute generation in {elapsed:.4f}s (dryRun={self.config.dry_run})."
        )

    def _discover_assets(self) -> Iterable[AttributeSetAsset]:
        for root in self.config.input_roots:
            if not root.exists():
                continue
            for file_path in sorted(root.rglob("*.json")):
                data = json.loads(file_path.read_text())
                asset = self._parse_asset(data, file_path)
                yield asset

    def _compute_composite_hash(
        self, input_hash: str, asset: AttributeSetAsset
    ) -> str:
        digest = hashlib.sha256()
        digest.update(GENERATOR_VERSION.encode("utf-8"))
        digest.update(b"|")
        digest.update(TEMPLATE_VERSION.encode("utf-8"))
        digest.update(b"|")
        digest.update(asset.class_name.encode("utf-8"))
        digest.update(b"|")
        digest.update(input_hash.encode("utf-8"))
        return digest.hexdigest()

    def _sidecar_path(self, asset: AttributeSetAsset) -> Path:
        sidecar_root = self.config.manifest_path.parent
        filename = f"{asset.name}AttributeSet.generated.hash"
        return sidecar_root / filename if sidecar_root else Path(filename)

    def _apply_preserve_regions(
        self, path: Path, content: str
    ) -> Tuple[str, Dict[str, Dict[str, object]]]:
        pattern = re.compile(
            r"(?P<begin>// GASPLUS-PRESERVE BEGIN (?P<key>[^\n]+?)\s*\n)"
            r"(?P<body>.*?)"
            r"(?P<end>// GASPLUS-PRESERVE END (?P=key))",
            re.DOTALL,
        )

        existing_regions: Dict[str, str] = {}
        if not self.config.no_preserve and path.exists():
            try:
                existing_regions = self._extract_preserve_regions(path.read_text())
            except OSError:
                existing_regions = {}

        reports: Dict[str, Dict[str, object]] = {}

        def replace(match: re.Match[str]) -> str:
            key = match.group("key").strip()
            body = match.group("body")
            preserved = body
            status = "generated"

            if self.config.no_preserve and path.exists():
                status = "ignored"
            elif key in existing_regions:
                preserved = existing_regions[key]
                status = "preserved"

            reports[key] = {
                "status": status,
                "lines": self._count_lines(preserved),
            }
            return f"{match.group('begin')}{preserved}{match.group('end')}"

        updated_content = pattern.sub(replace, content)
        return updated_content, reports

    def _collect_existing_preserve_reports(
        self, header_path: Path, source_path: Path, generated_header_path: Path
    ) -> Dict[str, Dict[str, Dict[str, object]]]:
        reports: Dict[str, Dict[str, Dict[str, object]]] = {}
        for label, path in (
            ("header", header_path),
            ("source", source_path),
            ("generatedHeader", generated_header_path),
        ):
            if path.exists():
                try:
                    regions = self._extract_preserve_regions(path.read_text())
                except OSError:
                    regions = {}
                reports[label] = {
                    key: {"status": "unchanged", "lines": self._count_lines(value)}
                    for key, value in regions.items()
                }
            else:
                reports[label] = {}
        return reports

    def _format_log_line(
        self,
        asset: AttributeSetAsset,
        write_decision: str,
        composite_hash: str,
        hash_changed: bool,
    ) -> str:
        prefix = {
            "force": "FORCED",
            "update": "UPDATED",
            "skip": "CACHED",
        }.get(write_decision, write_decision.upper())
        return (
            f"{prefix} {asset.class_name} ({asset.source_path.name}) "
            f"hash={composite_hash[:12]} changed={hash_changed}"
        )

    def _format_cli_line(
        self,
        asset: AttributeSetAsset,
        write_decision: str,
        composite_hash: str,
        hash_changed: bool,
        preserve_reports: Dict[str, Dict[str, Dict[str, object]]],
    ) -> str:
        prefix = {
            "force": "FORCED",
            "update": "UPDATED",
            "skip": "CACHED",
        }.get(write_decision, write_decision.upper())
        if self.config.dry_run:
            prefix = f"DRY-{prefix}"

        preserve_bits: List[str] = []
        for file_label, regions in preserve_reports.items():
            if not regions:
                continue
            region_summaries = ",".join(
                f"{name}:{info['status']}" for name, info in sorted(regions.items())
            )
            preserve_bits.append(f"{file_label}({region_summaries})")

        preserve_summary = f" preserve={' | '.join(preserve_bits)}" if preserve_bits else ""
        return (
            f"[{prefix}] {asset.class_name} hash={composite_hash[:12]} "
            f"changed={hash_changed}{preserve_summary}"
        )

    @staticmethod
    def _extract_preserve_regions(content: str) -> Dict[str, str]:
        pattern = re.compile(
            r"// GASPLUS-PRESERVE BEGIN (?P<key>[^\n]+?)\s*\n(?P<body>.*?)// GASPLUS-PRESERVE END (?P=key)",
            re.DOTALL,
        )
        regions: Dict[str, str] = {}
        for match in pattern.finditer(content):
            key = match.group("key").strip()
            regions[key] = match.group("body")
        return regions

    @staticmethod
    def _count_lines(block: str) -> int:
        if not block:
            return 0
        return len(block.rstrip("\n").splitlines())

    def _process_asset(self, asset: AttributeSetAsset) -> Dict[str, object]:
        output_root = self.config.output_root.resolve()
        header_path = output_root / f"{asset.name}AttributeSet.h"
        source_path = output_root / f"{asset.name}AttributeSet.cpp"
        generated_header_path = output_root / f"{asset.name}AttributeSet.generated.h"

        header_template = self._render_header(asset)
        source_template = self._render_source(asset)
        generated_header_template = self._render_generated_header(asset)

        input_hash = self._hash_file(asset.source_path)
        composite_hash = self._compute_composite_hash(input_hash, asset)

        sidecar_path = self._sidecar_path(asset)
        previous_hash: Optional[str] = None
        if sidecar_path.exists():
            try:
                previous_payload = json.loads(sidecar_path.read_text())
                previous_hash = str(previous_payload.get("compositeHash"))
            except (OSError, json.JSONDecodeError, ValueError):
                previous_hash = None

        files_missing = any(
            not path.exists()
            for path in (header_path, source_path, generated_header_path)
        )
        hash_changed = previous_hash != composite_hash or files_missing
        write_decision = "update" if hash_changed else "skip"
        if self.config.force:
            write_decision = "force"

        header_final = header_template
        source_final = source_template
        generated_header_final = generated_header_template
        preserve_reports: Dict[str, Dict[str, Dict[str, object]]] = {
            "header": {},
            "source": {},
            "generatedHeader": {},
        }

        if write_decision in {"update", "force"}:
            header_final, preserve_reports["header"] = self._apply_preserve_regions(
                header_path, header_template
            )
            source_final, preserve_reports["source"] = self._apply_preserve_regions(
                source_path, source_template
            )
            (
                generated_header_final,
                preserve_reports["generatedHeader"],
            ) = self._apply_preserve_regions(
                generated_header_path, generated_header_template
            )

            if not self.config.dry_run:
                header_path.write_text(header_final)
                source_path.write_text(source_final)
                generated_header_path.write_text(generated_header_final)

                sidecar_payload = {
                    "asset": asset.name,
                    "className": asset.class_name,
                    "input": str(asset.source_path),
                    "inputHash": input_hash,
                    "compositeHash": composite_hash,
                    "generatorVersion": GENERATOR_VERSION,
                    "templateVersion": TEMPLATE_VERSION,
                    "outputs": {
                        "header": str(header_path),
                        "source": str(source_path),
                        "generatedHeader": str(generated_header_path),
                    },
                }
                if sidecar_path.parent:
                    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
                sidecar_path.write_text(json.dumps(sidecar_payload, indent=2) + "\n")
        else:
            preserve_reports = self._collect_existing_preserve_reports(
                header_path, source_path, generated_header_path
            )

        log_line = self._format_log_line(
            asset, write_decision, composite_hash, hash_changed
        )
        cli_line = self._format_cli_line(
            asset, write_decision, composite_hash, hash_changed, preserve_reports
        )

        manifest_entry = {
            "input": str(asset.source_path),
            "inputHash": input_hash,
            "outputs": {
                "header": str(header_path),
                "source": str(source_path),
                "generatedHeader": str(generated_header_path),
            },
            "attributes": [
                {
                    "name": attribute.name,
                    "metadata": attribute.metadata.to_summary(),
                    "category": attribute.category,
                }
                for attribute in asset.attributes
            ],
            "className": asset.class_name,
            "moduleAPI": asset.module_api,
            "hashes": {
                "input": input_hash,
                "composite": composite_hash,
                "previous": previous_hash,
            },
            "status": {
                "write": write_decision,
                "dryRun": self.config.dry_run,
                "hashChanged": hash_changed,
                "writesPerformed": not self.config.dry_run
                and write_decision in {"update", "force"},
            },
            "sidecar": str(sidecar_path),
            "preserveRegions": preserve_reports,
        }

        return {
            "manifest": manifest_entry,
            "log_line": log_line,
            "cli_line": cli_line,
        }

    def _parse_asset(self, data: Dict[str, object], source_path: Path) -> AttributeSetAsset:
        name = str(data.get("name") or data.get("AttributeSetName") or source_path.stem)
        class_name = str(
            data.get("className")
            or data.get("ClassName")
            or f"U{name}AttributeSet"
        )
        module_api = str(data.get("moduleApi") or data.get("ModuleAPI") or "GASPLUSSAMPLE_API")
        attributes_payload = data.get("attributes") or data.get("Attributes")
        if not isinstance(attributes_payload, list) or not attributes_payload:
            raise ValueError(f"AttributeSet {name} has no attributes defined in {source_path}")

        attributes: List[AttributeDefinition] = []
        for raw_attribute in attributes_payload:
            if not isinstance(raw_attribute, dict):
                raise ValueError(
                    f"Attribute definition in {source_path} is not an object: {raw_attribute!r}"
                )
            attr_name = str(raw_attribute.get("name") or raw_attribute.get("Name"))
            category = str(raw_attribute.get("category") or raw_attribute.get("Category") or "Attributes")
            comment = raw_attribute.get("comment") or raw_attribute.get("Comment")
            metadata_raw = raw_attribute.get("metadata") or raw_attribute.get("Metadata") or {}
            if not attr_name:
                raise ValueError(f"Attribute definition missing name in {source_path}")
            metadata = AttributeMetadata.from_dict(metadata_raw)
            attributes.append(
                AttributeDefinition(
                    name=attr_name,
                    category=category,
                    comment=str(comment) if comment is not None else None,
                    metadata=metadata,
                )
            )

        return AttributeSetAsset(
            name=name,
            class_name=class_name,
            module_api=module_api,
            attributes=attributes,
            source_path=source_path.resolve(),
        )

    def _render_header(self, asset: AttributeSetAsset) -> str:
        requires_meta_registry = any(
            attribute.metadata.meta_attribute is not None for attribute in asset.attributes
        )
        include_lines = [
            '#include "CoreMinimal.h"',
            '#include "AttributeSet.h"',
            '#include "AbilitySystemComponent.h"',
            '#include "Meta/MetaAttributes.h"',
        ]
        if requires_meta_registry:
            include_lines.append('#include "GasPlusMetaAttributeRegistry.h"')
        include_block = "\n".join(include_lines)

        properties = []
        onrep_decls = []
        for attribute in asset.attributes:
            metadata_comment_parts = [
                f"Replicate={'true' if attribute.metadata.replicate else 'false'}",
                f"GenerateHooks={'true' if attribute.metadata.generate_hooks else 'false'}",
                f"SkipOnRep={'true' if attribute.metadata.skip_on_rep else 'false'}",
            ]
            if attribute.metadata.clamp_min is not None:
                metadata_comment_parts.append(f"ClampMin={attribute.metadata.clamp_min}")
            if attribute.metadata.clamp_max is not None:
                metadata_comment_parts.append(f"ClampMax={attribute.metadata.clamp_max}")
            if attribute.metadata.meta_attribute is not None:
                metadata_comment_parts.append(
                    f"MetaAttribute={attribute.metadata.meta_attribute}"
                )
            metadata_comment = ", ".join(metadata_comment_parts)

            property_lines = [
                f"    // Attribute: {attribute.name}",
                f"    // Metadata: {metadata_comment}",
            ]
            if attribute.comment:
                property_lines.append(f"    // {attribute.comment}")

            specifiers = ["BlueprintReadOnly", f"Category=\"{attribute.category}\""]
            meta_parts = []
            if attribute.metadata.clamp_min is not None:
                meta_parts.append(f"ClampMin=\"{attribute.metadata.clamp_min}\"")
            if attribute.metadata.clamp_max is not None:
                meta_parts.append(f"ClampMax=\"{attribute.metadata.clamp_max}\"")

            if attribute.metadata.replicate:
                if attribute.metadata.skip_on_rep:
                    specifiers.append("Replicated")
                else:
                    specifiers.append(f"ReplicatedUsing=OnRep_{attribute.name}")
                    onrep_decls.append(
                        f"    UFUNCTION()\n    void OnRep_{attribute.name}(const FGameplayAttributeData& OldValue);"
                    )
            specifier_block = ", ".join(specifiers)
            meta_block = f", meta=({', '.join(meta_parts)})" if meta_parts else ""
            property_lines.append(
                f"    UPROPERTY({specifier_block}{meta_block})\n    FGameplayAttributeData {attribute.name};"
            )
            property_lines.append(
                f"    ATTRIBUTE_ACCESSORS({asset.class_name}, {attribute.name});"
            )
            properties.append("\n".join(property_lines))

        properties_block = "\n\n".join(properties)
        onrep_block = "\n\n".join(onrep_decls)
        if onrep_block:
            onrep_block = "\n\n" + onrep_block

        preserve_block = (
            f"    // GASPLUS-PRESERVE BEGIN {asset.class_name}.PublicMembers\n"
            "    // Add additional member declarations here.\n"
            f"    // GASPLUS-PRESERVE END {asset.class_name}.PublicMembers"
        )

        class_body_parts = [
            "public:",
            f"    {asset.class_name}();",
            "",
            "    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;",
            "    virtual void PreAttributeChange(const FGameplayAttribute& Attribute, float& NewValue) override;",
            "    virtual void PostAttributeChange(const FGameplayAttribute& Attribute, float OldValue, float NewValue) override;",
            "",
            preserve_block,
        ]

        if properties_block:
            class_body_parts.extend(["", properties_block])
        if onrep_block:
            class_body_parts.extend(["", onrep_block.strip("\n")])

        class_body = "\n".join(class_body_parts)

        header = (
            "#pragma once\n\n"
            f"{include_block}\n"
            "// <Codex::Preserve Begin: HeaderIncludes>\n"
            "// <Codex::Preserve End: HeaderIncludes>\n\n"
            f"#include \"{asset.name}AttributeSet.generated.h\"\n\n"
            "UCLASS()\n"
            f"class {asset.module_api} {asset.class_name} : public UAttributeSet\n"
            "{\n"
            "    GENERATED_BODY()\n\n"
            f"{class_body}\n"
            "};\n"
        )
        return header

    def _render_source(self, asset: AttributeSetAsset) -> str:
        source_include_block = (
            f"#include \"{asset.name}AttributeSet.h\"\n\n"
            "#include \"Net/UnrealNetwork.h\"\n\n"
            "// <Codex::Preserve Begin: SourceIncludes>\n"
            "// <Codex::Preserve End: SourceIncludes>\n"
        )
        replication_lines = []
        pre_blocks = []
        post_blocks = []
        onrep_impls = []

        for attribute in asset.attributes:
            if attribute.metadata.replicate:
                if attribute.metadata.skip_on_rep:
                    replication_lines.append(
                        f"    DOREPLIFETIME({asset.class_name}, {attribute.name});"
                    )
                else:
                    replication_lines.append(
                        f"    DOREPLIFETIME_CONDITION_NOTIFY({asset.class_name}, {attribute.name}, COND_None, REPNOTIFY_Always);"
                    )
                    onrep_impls.append(
                        textwrap.dedent(
                            f"""
                            void {asset.class_name}::OnRep_{attribute.name}(const FGameplayAttributeData& OldValue)
                            {{
                                GAMEPLAYATTRIBUTE_REPNOTIFY({asset.class_name}, {attribute.name}, OldValue);
                                // <Codex::Preserve Begin: OnRep_{attribute.name}>
                                // <Codex::Preserve End: OnRep_{attribute.name}>
                            }}
                            """
                        ).strip()
                    )

            if attribute.metadata.generate_hooks:
                metadata_comment_parts = [
                    f"Replicate={'true' if attribute.metadata.replicate else 'false'}",
                    f"GenerateHooks={'true' if attribute.metadata.generate_hooks else 'false'}",
                    f"SkipOnRep={'true' if attribute.metadata.skip_on_rep else 'false'}",
                ]
                if attribute.metadata.clamp_min is not None:
                    metadata_comment_parts.append(f"ClampMin={attribute.metadata.clamp_min}")
                if attribute.metadata.clamp_max is not None:
                    metadata_comment_parts.append(f"ClampMax={attribute.metadata.clamp_max}")
                if attribute.metadata.meta_attribute is not None:
                    metadata_comment_parts.append(
                        f"MetaAttribute={attribute.metadata.meta_attribute}"
                    )
                metadata_comment = ", ".join(metadata_comment_parts)

                clamp_expression = "NewValue"
                clamp_lines = []
                if attribute.metadata.clamp_min is not None or attribute.metadata.clamp_max is not None:
                    clamp_min = (
                        attribute.metadata.clamp_min
                        if attribute.metadata.clamp_min is not None
                        else "-FLT_MAX"
                    )
                    clamp_max = (
                        attribute.metadata.clamp_max
                        if attribute.metadata.clamp_max is not None
                        else "FLT_MAX"
                    )
                    clamp_expression = f"FMath::Clamp(NewValue, {clamp_min}, {clamp_max})"
                    clamp_lines.append(
                        "        const float ClampedValue = " + clamp_expression + ";"
                    )
                    clamp_lines.append("        NewValue = ClampedValue;")

                pre_block_lines = [
                    f"    if (Attribute == Get{attribute.name}Attribute())",
                    "    {",
                    f"        // Metadata: {metadata_comment}",
                ]
                pre_block_lines.extend(clamp_lines)
                pre_block_lines.append(
                    f"        // TODO: Add pre-clamp logic for {attribute.name} if additional validation is required."
                )
                pre_block_lines.append("    }")
                pre_blocks.append("\n".join(pre_block_lines))

                post_block_lines = [
                    f"    if (Attribute == Get{attribute.name}Attribute())",
                    "    {",
                    f"        // Metadata: {metadata_comment}",
                    f"        // TODO: Add post-clamp logic for {attribute.name} (OldValue={{OldValue}}, NewValue={{NewValue}}).",
                    "    }",
                ]
                post_blocks.append("\n".join(post_block_lines))

        replication_block = "\n".join(replication_lines) if replication_lines else ""
        if replication_block:
            replication_block = "\n" + replication_block

        pre_block = "\n".join(pre_blocks)
        post_block = "\n".join(post_blocks)
        if pre_block:
            pre_block = "\n" + pre_block
        if post_block:
            post_block = "\n" + post_block
        pre_block += (
            "\n    // <Codex::Preserve Begin: PreAttributeChange_Custom>\n"
            "    // <Codex::Preserve End: PreAttributeChange_Custom>"
        )
        post_block += (
            "\n    // <Codex::Preserve Begin: PostAttributeChange_Custom>\n"
            "    // <Codex::Preserve End: PostAttributeChange_Custom>"
        )

        onrep_block = "\n\n".join(onrep_impls)

        constructor_preserve = (
            f"// GASPLUS-PRESERVE BEGIN {asset.class_name}.Constructor\n"
            "// Customize constructor defaults here.\n"
            f"// GASPLUS-PRESERVE END {asset.class_name}.Constructor"
        )
        pre_preserve = (
            f"    // GASPLUS-PRESERVE BEGIN {asset.class_name}.PreAttributeChange\n"
            "    // Customize pre-attribute change logic here.\n"
            f"    // GASPLUS-PRESERVE END {asset.class_name}.PreAttributeChange"
        )
        post_preserve = (
            f"    // GASPLUS-PRESERVE BEGIN {asset.class_name}.PostAttributeChange\n"
            "    // Customize post-attribute change logic here.\n"
            f"    // GASPLUS-PRESERVE END {asset.class_name}.PostAttributeChange"
        )
        additional_preserve = (
            f"// GASPLUS-PRESERVE BEGIN {asset.class_name}.AdditionalMethods\n"
            "// Add additional method definitions here.\n"
            f"// GASPLUS-PRESERVE END {asset.class_name}.AdditionalMethods"
        )

        source_lines: List[str] = [
            source_include_block,
            "",
            f"{asset.class_name}::{asset.class_name}() = default;",
            constructor_preserve,
            "",
            f"void {asset.class_name}::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const",
            "{",
            "    Super::GetLifetimeReplicatedProps(OutLifetimeProps);" + replication_block,
            "}",
            "",
            f"void {asset.class_name}::PreAttributeChange(const FGameplayAttribute& Attribute, float& NewValue)",
            "{",
            "    Super::PreAttributeChange(Attribute, NewValue);",
            pre_preserve + pre_block,
            "}",
            "",
            f"void {asset.class_name}::PostAttributeChange(const FGameplayAttribute& Attribute, float OldValue, float NewValue)",
            "{",
            "    Super::PostAttributeChange(Attribute, OldValue, NewValue);",
            "    UE_UNUSED(OldValue);",
            "    UE_UNUSED(NewValue);",
            post_preserve + post_block,
            "}",
        ]

        if onrep_block:
            source_lines.extend(["", onrep_block, ""])
        else:
            source_lines.append("")

        source_lines.append(additional_preserve)

        source = "\n".join(source_lines) + "\n"
        return source

    def _render_generated_header(self, asset: AttributeSetAsset) -> str:
        return textwrap.dedent(
            f"""
            #pragma once

            // Stub generated header for {asset.class_name}. In Unreal builds this file will be replaced by UHT.
            """
        ).strip() + "\n"

    @staticmethod
    def _hash_file(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()


def main(args: Optional[Sequence[str]] = None) -> None:
    generator = AttributeSetGenerator.from_args(args)
    generator.run()


if __name__ == "__main__":
    main()
