"""
CNINFO C-class registry offline lint (Era C Phase 4).

Checks config/cninfo_c_class_source_candidates.yaml and schemas/c_class/
for internal consistency.

Does NOT request CNINFO, does NOT modify config files.

Usage:
    python lab/lint_cninfo_c_class_registry.py
    python lab/lint_cninfo_c_class_registry.py --strict
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Set, Tuple

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_REGISTRY = os.path.join(BASE_DIR, "config", "cninfo_c_class_source_candidates.yaml")
DEFAULT_SCHEMAS_DIR = os.path.join(BASE_DIR, "schemas", "c_class")
DEFAULT_CSV = os.path.join(BASE_DIR, "outputs", "validation", "cninfo_c_class_registry_lint_report.csv")
DEFAULT_MD = os.path.join(BASE_DIR, "outputs", "validation", "cninfo_c_class_registry_lint_summary.md")

TOTAL_RULES = 14

VALID_SOURCE_LAYERS = frozenset({"company_profile"})
VALID_SOURCE_CATEGORIES = frozenset({
    "basic_profile",
    "industry_profile",
    "business_scope",
    "executive_profile",
    "share_capital_profile",
    "shareholder_profile",
    "dividend_financing_profile",
    "contact_profile",
    "security_profile",
})
VALID_RECOMMENDED_STATUS = frozenset({
    "candidate",
    "testing",
    "testing_stable_sample",
    "partial",
    "blocked",
    "deprecated",
})
# Era C Phase 4 P1 backfill: recommended_status may be testing; never above without approval.
CURRENT_PHASE_MAX_STATUS = "testing"
CURRENT_PHASE_ALLOWED_STATUS = frozenset({"candidate", "testing"})
REQUIRED_SCHEMA_FILES = [
    "c_company_profile_snapshot.schema.json",
    "c_company_basic_profile.schema.json",
    "c_executive_profile.schema.json",
    "c_share_capital_profile.schema.json",
    "c_shareholder_profile.schema.json",
    "c_profile_raw_snapshot.schema.json",
]
FORBIDDEN_SOURCE_IDS = frozenset({
    "cninfo_periodic_report_pdf",
    "cninfo_general_announcement_pdf",
    "cninfo_inquiry_reply_pdf",
    "cninfo_meeting_notice_pdf",
    "margin_trading",
    "block_trade",
    "equity_pledge",
    "shareholder_data",
    "disclosure_schedule",
    "restricted_shares_unlock",
    "abnormal_trading",
    "shareholder_change",
    "executive_shareholding",
    "fund_industry_allocation",
})


@dataclass
class Finding:
    rule_id: str
    severity: str
    target: str
    status: str
    message: str
    suggested_fix: str = ""

    def format_line(self) -> str:
        fix = f" suggested_fix={self.suggested_fix}" if self.suggested_fix else ""
        return f"{self.severity}  {self.rule_id}  {self.target}  {self.message}{fix}"


def _load_yaml(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _walk_verified_issues(obj: Any, path: str = "") -> List[Tuple[str, str]]:
    issues: List[Tuple[str, str]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            if k == "verified" and v is True:
                issues.append((p, "verified is true"))
            if k == "recommended_status" and v == "verified":
                issues.append((p, "recommended_status is verified"))
            issues.extend(_walk_verified_issues(v, p))
    elif isinstance(obj, list):
        if "verified" in obj:
            issues.append((path, "enum list contains verified"))
        for i, item in enumerate(obj):
            issues.extend(_walk_verified_issues(item, f"{path}[{i}]"))
    return issues


def _schema_has_verified_enum(schemas_dir: str) -> List[str]:
    hits: List[str] = []
    for name in REQUIRED_SCHEMA_FILES:
        path = os.path.join(schemas_dir, name)
        if not os.path.isfile(path):
            continue
        schema = _load_json(path)
        text = json.dumps(schema)
        if '"verified"' in text and "verified" in text:
            defs = schema.get("definitions") or {}
            for def_name, node in defs.items():
                enum = node.get("enum") or []
                if "verified" in enum:
                    hits.append(f"{name}#definitions.{def_name}")
    return hits


def _effective_required_keys(source: Dict[str, Any], defaults: Dict[str, Any]) -> List[str]:
    keys = source.get("required_keys")
    if keys is None:
        keys = defaults.get("required_keys") or []
    return list(keys) if isinstance(keys, list) else []


def _endpoint_is_null(endpoint: Any) -> bool:
    if endpoint is None or endpoint == "" or endpoint == "null":
        return True
    if isinstance(endpoint, dict):
        url = endpoint.get("url")
        return not url
    return False


def _endpoint_url(endpoint: Any) -> str:
    if isinstance(endpoint, dict):
        return str(endpoint.get("url") or "")
    return ""


def run_lint(registry_path: str, schemas_dir: str) -> List[Finding]:
    findings: List[Finding] = []
    registry = _load_yaml(registry_path)
    defaults = registry.get("defaults") or {}
    sources: List[Dict[str, Any]] = registry.get("sources") or []

    # R003 root verified
    if registry.get("verified") is True:
        findings.append(Finding(
            "R003", "FAIL", "registry", "FAIL",
            "root verified must be false",
            "Set verified: false",
        ))
    for path, msg in _walk_verified_issues(registry):
        findings.append(Finding(
            "R003", "FAIL", path, "FAIL", msg,
            "Remove verified usage",
        ))

    # R011 schema files
    missing_schemas = [
        name for name in REQUIRED_SCHEMA_FILES
        if not os.path.isfile(os.path.join(schemas_dir, name))
    ]
    if missing_schemas:
        findings.append(Finding(
            "R011", "FAIL", "schemas/c_class", "FAIL",
            f"Missing schema files: {', '.join(missing_schemas)}",
            "Add missing schema files",
        ))
    else:
        findings.append(Finding(
            "R011", "INFO", "schemas/c_class", "PASS",
            f"All {len(REQUIRED_SCHEMA_FILES)} schema files present",
        ))

    verified_enums = _schema_has_verified_enum(schemas_dir)
    for hit in verified_enums:
        findings.append(Finding(
            "R003", "FAIL", hit, "FAIL",
            "Schema enum contains verified",
            "Remove verified from enum",
        ))

    registry_ids: Set[str] = set()
    null_endpoints = 0
    populated_endpoints = 0
    status_counts: Dict[str, int] = {}

    for src in sources:
        sid = str(src.get("source_id") or "")
        target = sid or "(missing source_id)"

        # R001
        if not sid:
            findings.append(Finding(
                "R001", "FAIL", target, "FAIL",
                "Missing source_id",
                "Add source_id",
            ))
        elif sid in registry_ids:
            findings.append(Finding(
                "R001", "FAIL", sid, "FAIL",
                f"Duplicate source_id: {sid}",
                "Use unique source_id",
            ))
        else:
            registry_ids.add(sid)

        # R010
        if sid and not sid.startswith("cninfo_"):
            findings.append(Finding(
                "R010", "FAIL", sid, "FAIL",
                f"source_id must start with cninfo_, got {sid!r}",
                "Rename to cninfo_* prefix",
            ))

        # R012
        if sid in FORBIDDEN_SOURCE_IDS:
            findings.append(Finding(
                "R012", "FAIL", sid, "FAIL",
                f"Forbidden B/D source_id in C registry: {sid}",
                "Use C-class company_profile source_id only",
            ))

        # R002
        layer = src.get("source_layer")
        if layer not in VALID_SOURCE_LAYERS:
            findings.append(Finding(
                "R002", "FAIL", sid, "FAIL",
                f"source_layer must be company_profile, got {layer!r}",
                "Set source_layer: company_profile",
            ))

        # R004 / R005 recommended_status
        rec = src.get("recommended_status")
        status_counts[str(rec)] = status_counts.get(str(rec), 0) + 1
        if rec not in VALID_RECOMMENDED_STATUS:
            findings.append(Finding(
                "R004", "FAIL", sid, "FAIL",
                f"Invalid recommended_status: {rec!r}",
                f"Use one of {sorted(VALID_RECOMMENDED_STATUS)}",
            ))
        elif rec not in CURRENT_PHASE_ALLOWED_STATUS:
            findings.append(Finding(
                "R005", "FAIL", sid, "FAIL",
                f"Current phase max recommended_status is {CURRENT_PHASE_MAX_STATUS!r}, got {rec!r}",
                f"Use candidate or testing only",
            ))

        # R003 per source
        if src.get("verified") is True:
            findings.append(Finding(
                "R003", "FAIL", sid, "FAIL",
                "verified must be false",
                "Set verified: false",
            ))

        # R009
        cat = src.get("source_category")
        if cat not in VALID_SOURCE_CATEGORIES:
            findings.append(Finding(
                "R009", "FAIL", sid, "FAIL",
                f"Invalid source_category: {cat!r}",
                f"Use one of {sorted(VALID_SOURCE_CATEGORIES)}",
            ))

        # R007
        req_keys = _effective_required_keys(src, defaults)
        if not req_keys:
            findings.append(Finding(
                "R007", "FAIL", sid, "FAIL",
                "required_keys empty",
                "Declare required_keys with company_code and/or org_id",
            ))
        elif not any(k in req_keys for k in ("company_code", "org_id")):
            findings.append(Finding(
                "R007", "WARN", sid, "WARN",
                f"required_keys should include company_code or org_id: {req_keys}",
                "Add company_code or org_id to required_keys",
            ))

        # R008
        expected = src.get("expected_fields") or []
        if not expected:
            findings.append(Finding(
                "R008", "FAIL", sid, "FAIL",
                "expected_fields is empty",
                "Add expected_fields list",
            ))

        # R006 / R013 endpoint
        endpoint = src.get("endpoint")
        if _endpoint_is_null(endpoint):
            null_endpoints += 1
            if rec == "testing":
                findings.append(Finding(
                    "R013", "FAIL", sid, "FAIL",
                    "recommended_status=testing but endpoint.url is missing",
                    "Add endpoint.url from probe records or revert to candidate",
                ))
        else:
            populated_endpoints += 1
            if not isinstance(endpoint, dict):
                findings.append(Finding(
                    "R013", "WARN", sid, "WARN",
                    f"endpoint should be object with url; got {type(endpoint).__name__}",
                    "Use endpoint: { url, method, params_template, records_path }",
                ))
            elif not endpoint.get("records_path"):
                findings.append(Finding(
                    "R013", "WARN", sid, "WARN",
                    "endpoint missing records_path",
                    "Add records_path from probe evidence",
                ))

        # R014 derived_from_candidate (industry without endpoint)
        if sid == "cninfo_company_industry_profile":
            derived = src.get("derived_from_candidate")
            if _endpoint_is_null(endpoint) and not derived:
                findings.append(Finding(
                    "R014", "WARN", sid, "WARN",
                    "industry_profile has null endpoint but no derived_from_candidate",
                    "Add derived_from_candidate pointing to basic_profile",
                ))
            elif derived and not isinstance(derived, dict):
                findings.append(Finding(
                    "R014", "WARN", sid, "WARN",
                    "derived_from_candidate should be an object",
                    "Use { source_id, path, fields }",
                ))

    if sources and null_endpoints == len(sources):
        findings.append(Finding(
            "R006", "INFO", "registry", "PASS",
            f"All {null_endpoints} sources have endpoint=null (expected pre-probe)",
        ))
    elif populated_endpoints > 0:
        findings.append(Finding(
            "R006", "INFO", "registry", "PASS",
            f"{populated_endpoints}/{len(sources)} sources have endpoint populated; "
            f"{null_endpoints} still null",
        ))

    if sources and not any(f.rule_id == "R005" and f.severity == "FAIL" for f in findings):
        parts = ", ".join(f"{k}={v}" for k, v in sorted(status_counts.items()))
        findings.append(Finding(
            "R005", "INFO", "registry", "PASS",
            f"recommended_status within phase cap ({CURRENT_PHASE_MAX_STATUS}): {parts}",
        ))

    if registry_ids and not any(f.rule_id == "R001" and f.severity == "FAIL" for f in findings):
        findings.append(Finding(
            "R001", "INFO", "registry", "PASS",
            f"All {len(registry_ids)} source_id values are unique",
        ))

    return findings


def write_csv(path: str, findings: List[Finding]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fields = ["rule_id", "severity", "target", "status", "message", "suggested_fix"]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for fnd in findings:
            writer.writerow({
                "rule_id": fnd.rule_id,
                "severity": fnd.severity,
                "target": fnd.target,
                "status": fnd.status,
                "message": fnd.message,
                "suggested_fix": fnd.suggested_fix,
            })


def write_summary_md(
    path: str,
    findings: List[Finding],
    registry_path: str,
    schemas_dir: str,
    result: str,
    source_count: int,
) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fail_n = sum(1 for f in findings if f.severity == "FAIL")
    warn_n = sum(1 for f in findings if f.severity == "WARN")
    info_n = sum(1 for f in findings if f.severity == "INFO")
    fail_warn = [f for f in findings if f.severity in ("FAIL", "WARN")]

    lines = [
        "# CNINFO C 类 Registry Lint Summary",
        "",
        "## 1. 目的",
        "",
        "本地 **candidate YAML / JSON Schema** 一致性检查。",
        "**不请求 CNINFO**；不 probe endpoint；不写 verified。",
        "",
        "## 2. 输入",
        "",
        "| 来源 | 路径 |",
        "|------|------|",
        f"| C 类 candidate registry | `{os.path.relpath(registry_path, BASE_DIR)}` |",
        f"| Schemas | `{os.path.relpath(schemas_dir, BASE_DIR)}/` |",
        f"| 脚本 | `lab/lint_cninfo_c_class_registry.py` |",
        "",
        "## 3. 总体结果",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| total_rules | **{TOTAL_RULES}** |",
        f"| sources | **{source_count}** |",
        f"| fail | **{fail_n}** |",
        f"| warn | **{warn_n}** |",
        f"| info | **{info_n}** |",
        f"| result | **{result}** |",
        "",
        "## 4. 重点检查",
        "",
        "- **source_layer** = `company_profile`（R002）",
        "- **verified** 全部为 false（R003）",
        "- **recommended_status** 不超过 `testing`（R005；P1 backfill 后允许 candidate/testing）",
        "- **endpoint** 已回填 source 须有 `endpoint.url`（R013）",
        "- **industry_profile** 无 endpoint 时应有 `derived_from_candidate`（R014）",
        "- **无 B/D source_id 混入**（R012）",
        "",
        "## 5. 问题清单",
        "",
    ]
    if fail_warn:
        for fnd in fail_warn:
            lines.append(f"- **{fnd.severity}** `{fnd.rule_id}` `{fnd.target}`: {fnd.message}")
    else:
        lines.append("_无 FAIL / WARN。_")

    lines.extend([
        "",
        "## 6. 质量边界",
        "",
        "- Lint PASS **不代表** F10 endpoint 已确认。",
        "- **不代表** 字段已在 UI/DevTools 验证。",
        "- **不写 verified**。",
        "",
        "## 7. 下一步",
        "",
        "1. C 类 known-company live validation（600000 / 300001 / 688001）。",
        "2. basic_profile field mapping 与 mapper 草案。",
        "3. P2 source DevTools probe（executive / share_capital / shareholders）。",
        "",
        "## 附录",
        "",
        "详见 [cninfo_c_class_registry_lint_report.csv](cninfo_c_class_registry_lint_report.csv)。",
        "",
    ])
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def print_report(findings: List[Finding], source_count: int, strict: bool) -> int:
    fail_n = sum(1 for f in findings if f.severity == "FAIL")
    warn_n = sum(1 for f in findings if f.severity == "WARN")
    info_n = sum(1 for f in findings if f.severity == "INFO")

    if not findings:
        print("PASS  -  -  INFO  No issues found")
    else:
        for fnd in findings:
            print(fnd.format_line())

    result = "FAIL" if fail_n else "PASS"
    print(
        f"SUMMARY  rules={TOTAL_RULES}  sources={source_count}  "
        f"fail={fail_n}  warn={warn_n}  info={info_n}  result={result}"
    )

    if fail_n:
        return 1
    if strict and warn_n:
        return 1
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Lint C-class company profile candidate registry")
    parser.add_argument("--registry", default=DEFAULT_REGISTRY)
    parser.add_argument("--schemas-dir", default=DEFAULT_SCHEMAS_DIR)
    parser.add_argument("--output-csv", default=DEFAULT_CSV)
    parser.add_argument("--output-md", default=DEFAULT_MD)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    registry = _load_yaml(args.registry)
    source_count = len(registry.get("sources") or [])

    findings = run_lint(args.registry, args.schemas_dir)
    write_csv(args.output_csv, findings)
    fail_n = sum(1 for f in findings if f.severity == "FAIL")
    result = "FAIL" if fail_n else "PASS"
    write_summary_md(
        args.output_md, findings, args.registry, args.schemas_dir, result, source_count,
    )
    sys.exit(print_report(findings, source_count, args.strict))


if __name__ == "__main__":
    main()
