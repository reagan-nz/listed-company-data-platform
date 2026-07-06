"""
CNINFO D-class registry YAML offline lint (Era C Phase 3).

Checks config/cninfo_d_class_source_registry_draft.yaml for internal consistency
against layer/table mapping, status model, and schemas/d_class/ file presence.

Does NOT request CNINFO, does NOT write files, does NOT connect to a database.

Usage:
    python lab/lint_cninfo_d_class_registry.py
    python lab/lint_cninfo_d_class_registry.py --registry config/cninfo_d_class_source_registry_draft.yaml
    python lab/lint_cninfo_d_class_registry.py --schemas-dir schemas/d_class --strict
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_REGISTRY = os.path.join(BASE_DIR, "config", "cninfo_d_class_source_registry_draft.yaml")
DEFAULT_SCHEMAS_DIR = os.path.join(BASE_DIR, "schemas", "d_class")

EXPECTED_SOURCE_IDS = frozenset({
    "disclosure_schedule",
    "restricted_shares_unlock",
    "block_trade",
    "margin_trading",
    "abnormal_trading",
    "equity_pledge",
    "shareholder_change",
    "executive_shareholding",
    "shareholder_data",
    "fund_industry_allocation",
})

VALID_SOURCE_LAYERS = frozenset({
    "company_event",
    "company_metric_daily",
    "company_metric_periodic",
    "disclosure_schedule",
    "industry_aggregate",
})

VALID_TARGET_TABLES = frozenset({
    "d_company_event",
    "d_company_metric_daily",
    "d_company_metric_periodic",
    "d_disclosure_schedule",
    "d_industry_aggregate",
})

VALID_OPTIONAL_TARGET_TABLES = frozenset({
    "d_event_party_detail",
    "d_company_metric_daily",
})

LAYER_TO_TABLE = {
    "company_event": "d_company_event",
    "company_metric_daily": "d_company_metric_daily",
    "company_metric_periodic": "d_company_metric_periodic",
    "disclosure_schedule": "d_disclosure_schedule",
    "industry_aggregate": "d_industry_aggregate",
}

REQUIRED_PATHS = [
    "source_id",
    "source_name",
    "source_layer",
    "source_category",
    "target_logical_table",
    "api.url",
    "api.method",
    "api.records_path",
    "status.recommended_status",
    "status.verified",
    "mapping.raw_record_required",
]

COMPANY_LEVEL_SOURCES = EXPECTED_SOURCE_IDS - {"fund_industry_allocation"}


@dataclass
class Finding:
    rule_id: str
    source_id: str
    severity: str  # FAIL, WARN, INFO
    message: str
    suggested_fix: str = ""

    def format_line(self) -> str:
        sid = self.source_id or "-"
        fix = f" suggested_fix={self.suggested_fix}" if self.suggested_fix else ""
        return f"{self.severity}  {self.rule_id}  {sid}  {self.message}{fix}"


def _get_path(obj: Dict[str, Any], path: str) -> Any:
    cur: Any = obj
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _collect_raw_names(field_group: Any) -> List[str]:
    names: List[str] = []
    if not isinstance(field_group, list):
        return names
    for item in field_group:
        if isinstance(item, dict) and item.get("raw"):
            names.append(str(item["raw"]))
        elif isinstance(item, str):
            names.append(item)
    return names


def lint_registry(
    registry_path: str,
    schemas_dir: str,
) -> List[Finding]:
    findings: List[Finding] = []

    if not os.path.isfile(registry_path):
        findings.append(Finding("R000", "-", "FAIL", f"Registry file not found: {registry_path}",
                                "Create or fix --registry path"))
        return findings

    with open(registry_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    sources = data.get("sources") or []
    if not isinstance(sources, list):
        findings.append(Finding("R000", "-", "FAIL", "sources must be a list"))
        return findings

    # R001 source_id uniqueness
    seen_ids: List[str] = []
    for src in sources:
        sid = src.get("source_id")
        if not sid:
            continue
        if sid in seen_ids:
            findings.append(Finding("R001", sid, "FAIL", "Duplicate source_id",
                                    "Remove or rename duplicate entry"))
        seen_ids.append(sid)

    # R019 coverage
    found_ids = {s.get("source_id") for s in sources if s.get("source_id")}
    missing = EXPECTED_SOURCE_IDS - found_ids
    extra = found_ids - EXPECTED_SOURCE_IDS
    for sid in sorted(missing):
        findings.append(Finding("R019", sid, "FAIL", "Expected testing_stable_sample source missing from registry",
                                "Add source entry to YAML"))
    for sid in sorted(extra):
        findings.append(Finding("R019", sid, "WARN", "Unexpected source_id not in Phase 2 ten-source list",
                                "Remove or document as candidate"))

    # R005 no verified token in recommended_status values (scan sources only)
    for src in sources:
        sid = str(src.get("source_id", ""))
        rec = _get_path(src, "status.recommended_status")
        if rec == "verified":
            findings.append(Finding("R004", sid, "FAIL", "recommended_status must not be verified",
                                    "Use testing_stable_sample"))

    for src in sources:
        sid = str(src.get("source_id", "?"))

        # R002 required fields
        for path in REQUIRED_PATHS:
            val = _get_path(src, path)
            if val is None or val == "":
                findings.append(Finding("R002", sid, "FAIL", f"Missing required field: {path}",
                                        f"Add {path} to source"))

        # R003 verified false
        if _get_path(src, "status.verified") is not False:
            findings.append(Finding("R003", sid, "FAIL", "status.verified must be false",
                                    "Set status.verified: false"))

        # R006 source_layer
        layer = src.get("source_layer")
        if layer and layer not in VALID_SOURCE_LAYERS:
            findings.append(Finding("R006", sid, "FAIL", f"Invalid source_layer: {layer}",
                                    f"Use one of {sorted(VALID_SOURCE_LAYERS)}"))

        # R007 target table
        target = src.get("target_logical_table")
        if target and target not in VALID_TARGET_TABLES:
            findings.append(Finding("R007", sid, "FAIL", f"Invalid target_logical_table: {target}",
                                    f"Use one of {sorted(VALID_TARGET_TABLES)}"))

        opt_target = src.get("optional_target_logical_table")
        if opt_target and opt_target not in VALID_OPTIONAL_TARGET_TABLES:
            findings.append(Finding("R007", sid, "WARN", f"Unusual optional_target_logical_table: {opt_target}",
                                    "Document in mapping review"))

        # R008 layer-table mapping
        if layer in LAYER_TO_TABLE and target and target != LAYER_TO_TABLE[layer]:
            findings.append(Finding(
                "R008", sid, "FAIL",
                f"source_layer {layer} requires target_logical_table {LAYER_TO_TABLE[layer]}, got {target}",
                f"Set target_logical_table: {LAYER_TO_TABLE[layer]}",
            ))

        # R009 R010 records_path
        records_path = _get_path(src, "api.records_path")
        if sid == "disclosure_schedule":
            if records_path != "prbookinfos":
                findings.append(Finding("R010", sid, "WARN", f"disclosure_schedule records_path should be prbookinfos, got {records_path}",
                                        "Set api.records_path: prbookinfos"))
        elif sid == "abnormal_trading":
            if records_path != "marketList":
                findings.append(Finding("R009", sid, "WARN", f"abnormal_trading records_path should be marketList, got {records_path}",
                                        "Set api.records_path: marketList"))
        elif sid in EXPECTED_SOURCE_IDS and records_path != "data.records":
            findings.append(Finding("R009", sid, "WARN", f"Expected records_path data.records, got {records_path}",
                                    "Set api.records_path: data.records"))

        # R022 api.method
        method = _get_path(src, "api.method")
        if method and str(method).upper() not in ("POST", "GET"):
            findings.append(Finding("R022", sid, "FAIL", f"Invalid api.method: {method}",
                                    "Use POST or GET"))

        # R016 raw_record_required
        if _get_path(src, "mapping.raw_record_required") is not True:
            findings.append(Finding("R016", sid, "FAIL", "mapping.raw_record_required must be true",
                                    "Set mapping.raw_record_required: true"))

        # R015 field group duplicates
        fields = src.get("fields") or {}
        all_raw: Dict[str, str] = {}
        for group in ("confirmed", "raw_only", "uncertain", "candidate"):
            for name in _collect_raw_names(fields.get(group)):
                if name in all_raw and all_raw[name] != group:
                    findings.append(Finding(
                        "R015", sid, "WARN",
                        f"Field {name} appears in both {all_raw[name]} and {group}",
                        "Deduplicate fields groups",
                    ))
                all_raw[name] = group
        for name in fields.get("not_visible_on_ui") or []:
            if name in all_raw:
                findings.append(Finding("R015", sid, "INFO", f"Field {name} also listed in {all_raw[name]}",
                                        "Consider single classification"))

        # R017 R018 company_code_available
        cca = src.get("company_code_available")
        if sid == "fund_industry_allocation":
            if cca is not False:
                findings.append(Finding("R017", sid, "FAIL", "fund_industry_allocation company_code_available must be false",
                                        "Set company_code_available: false"))
        elif sid in COMPANY_LEVEL_SOURCES:
            if cca is not True:
                findings.append(Finding("R018", sid, "FAIL", f"{sid} company_code_available should be true",
                                        "Set company_code_available: true"))

        # R020 recommended_status
        rec_status = _get_path(src, "status.recommended_status")
        if rec_status and rec_status != "testing_stable_sample":
            findings.append(Finding("R020", sid, "WARN", f"recommended_status is {rec_status}, expected testing_stable_sample",
                                    "Align with Phase 2 stability result"))

        # R023 fund exclude
        if sid == "fund_industry_allocation":
            exclude = (_get_path(src, "mapping.exclude_from_schemas") or [])
            if "d_company_event" not in exclude:
                findings.append(Finding("R023", sid, "WARN", "mapping.exclude_from_schemas should include d_company_event",
                                        "Add exclude_from_schemas"))

        # R011 R012 shareholder_change modes
        if sid == "shareholder_change":
            modes = src.get("supported_modes") or []
            type_values: Set[str] = set()
            for m in modes:
                if isinstance(m, dict):
                    params = m.get("params") or {}
                    if isinstance(params, dict) and "type" in params:
                        type_values.add(str(params["type"]))
            has_inc = "inc" in type_values
            has_desc = "desc" in type_values
            if not has_inc or not has_desc:
                findings.append(Finding("R011", sid, "FAIL", "shareholder_change must define type=inc and type=desc modes",
                                        "Add supported_modes for inc and desc"))
            if "dec" in type_values:
                findings.append(Finding("R012", sid, "FAIL", "shareholder_change must not use type=dec",
                                        "Use type=desc for decrease"))

        # R013 executive_shareholding
        if sid == "executive_shareholding":
            modes = src.get("supported_modes") or []
            mode_text = json.dumps(modes, ensure_ascii=False)
            if "timeMark" not in mode_text or "varyType" not in mode_text:
                findings.append(Finding("R013", sid, "FAIL", "executive_shareholding must document timeMark and varyType modes",
                                        "Add supported_modes with timeMark and varyType"))

        # R014 margin_trading
        if sid == "margin_trading":
            modes = src.get("supported_modes") or []
            has_primary = any(
                (m.get("mode_id") == "detailList_default" or m.get("role") == "primary")
                for m in modes if isinstance(m, dict)
            )
            if not has_primary:
                findings.append(Finding("R014", sid, "FAIL", "margin_trading must define detailList_default as primary",
                                        "Add supported_modes detailList_default role primary"))
            mode_text = json.dumps(modes, ensure_ascii=False)
            if "market" in mode_text.lower():
                if "auxiliary" not in mode_text and "observation" not in mode_text:
                    findings.append(Finding("R014", sid, "WARN", "market summary mode should be marked auxiliary/observation",
                                            "Set role: auxiliary_observation_only on market mode"))

        # R021 schema file exists
        if target:
            schema_file = os.path.join(schemas_dir, f"{target}.schema.json")
            if not os.path.isfile(schema_file):
                findings.append(Finding("R021", sid, "FAIL", f"Missing schema file: {schema_file}",
                                        "Create schemas/d_class/{target}.schema.json"))

    return findings


def print_report(findings: List[Finding], source_count: int, strict: bool) -> int:
    fail_n = sum(1 for f in findings if f.severity == "FAIL")
    warn_n = sum(1 for f in findings if f.severity == "WARN")
    info_n = sum(1 for f in findings if f.severity == "INFO")

    if not findings:
        print("PASS  -  -  INFO  No issues found")
    else:
        for f in findings:
            print(f.format_line())

    result = "FAIL" if fail_n else "PASS"
    print(f"SUMMARY  sources={source_count}  fail={fail_n}  warn={warn_n}  info={info_n}  result={result}")

    if fail_n:
        return 1
    if strict and warn_n:
        return 1
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CNINFO D-class registry YAML offline lint")
    parser.add_argument("--registry", default=DEFAULT_REGISTRY, help="Path to registry YAML draft")
    parser.add_argument("--schemas-dir", default=DEFAULT_SCHEMAS_DIR, help="Directory of JSON Schema files")
    parser.add_argument("--strict", action="store_true", help="Treat WARN as failure exit code")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    registry_path = os.path.abspath(args.registry)
    schemas_dir = os.path.abspath(args.schemas_dir)

    with open(registry_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    source_count = len(data.get("sources") or [])

    findings = lint_registry(registry_path, schemas_dir)
    exit_code = print_report(findings, source_count, args.strict)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
