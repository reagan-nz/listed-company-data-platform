"""
CNINFO B-class registry offline lint (Era C Phase 3).

Checks config/cninfo_b_class_source_registry_draft.yaml,
config/cninfo_announcement_categories.yaml, schemas/b_class/, and
fixtures/b_class/ for internal consistency.

Does NOT request CNINFO, does NOT modify config files.

Usage:
    python lab/lint_cninfo_b_class_registry.py
    python lab/lint_cninfo_b_class_registry.py --strict
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from dataclasses import dataclass
from glob import glob
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_REGISTRY = os.path.join(BASE_DIR, "config", "cninfo_b_class_source_registry_draft.yaml")
DEFAULT_CATEGORIES = os.path.join(BASE_DIR, "config", "cninfo_announcement_categories.yaml")
DEFAULT_SCHEMAS_DIR = os.path.join(BASE_DIR, "schemas", "b_class")
DEFAULT_FIXTURES_DIR = os.path.join(BASE_DIR, "fixtures", "b_class")
DEFAULT_CSV = os.path.join(BASE_DIR, "outputs", "validation", "cninfo_b_class_registry_lint_report.csv")
DEFAULT_MD = os.path.join(BASE_DIR, "outputs", "validation", "cninfo_b_class_registry_lint_summary.md")

TOTAL_RULES = 23

VALID_SOURCE_LAYERS = frozenset({"document_corpus"})
VALID_SOURCE_CATEGORIES = frozenset({
    "periodic_report_pdf",
    "announcement_pdf",
    "inquiry_reply_pdf",
    "meeting_notice_pdf",
    "board_resolution_pdf",
    "shareholder_meeting_material_pdf",
    "other_document_pdf",
})
VALID_RECOMMENDED_STATUS = frozenset({
    "candidate",
    "testing",
    "testing_stable_sample",
    "partial",
    "blocked",
    "deprecated",
})
PERIODIC_SOURCE_ID = "cninfo_periodic_report_pdf"
NON_PERIODIC_KNOWN_SOURCES = frozenset({
    "cninfo_inquiry_reply_pdf",
    "cninfo_meeting_notice_pdf",
    "cninfo_general_announcement_pdf",
})
REQUIRED_PERIODIC_EXCLUSIONS = [
    "摘要",
    "问询函",
    "回复公告",
    "说明会",
    "提示性公告",
    "披露提示性公告",
    "延期披露",
]
REQUIRED_SCHEMA_FILES = [
    "b_document.schema.json",
    "b_raw_file.schema.json",
    "b_document_version.schema.json",
    "b_document_section.schema.json",
    "b_document_chunk.schema.json",
    "b_document_citation_span.schema.json",
    "b_document_parse_run.schema.json",
    "b_event_document_link.schema.json",
]
D_CLASS_SOURCE_IDS = frozenset({
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
    "ipo_query",
    "szse_calendar",
})
CREATED_FROM_PERIODIC = "phase1_report_retrieval"
CREATED_FROM_NON_PERIODIC = "offline_known_document_benchmark"


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


def _get_path(obj: Dict[str, Any], path: str) -> Any:
    cur: Any = obj
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _load_yaml(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _load_jsonl_glob(pattern: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for path in sorted(glob(pattern)):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    return records


def _schema_enum(schema: Dict[str, Any], def_name: str) -> Set[str]:
    defs = schema.get("definitions") or {}
    node = defs.get(def_name) or {}
    enum = node.get("enum")
    if isinstance(enum, list):
        return {str(v) for v in enum}
    return set()


def _document_property_enum(schema: Dict[str, Any], prop: str) -> Set[str]:
    props = schema.get("properties") or {}
    node = props.get(prop) or {}
    if "$ref" in node:
        ref = node["$ref"]
        if ref.startswith("#/definitions/"):
            return _schema_enum(schema, ref.split("/")[-1])
    enum = node.get("enum")
    if isinstance(enum, list):
        return {str(v) for v in enum}
    return set()


def _walk_verified_issues(obj: Any, path: str = "") -> List[Tuple[str, str]]:
    issues: List[Tuple[str, str]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            if k == "verified" and v is True:
                issues.append((p, "verified is true"))
            if k == "recommended_status" and v == "verified":
                issues.append((p, "recommended_status is verified"))
            if k in ("recommended_status", "registry_status") and isinstance(v, str) and v == "verified":
                issues.append((p, f"{k} is verified"))
            issues.extend(_walk_verified_issues(v, p))
    elif isinstance(obj, list):
        if "verified" in obj:
            issues.append((path, "enum list contains verified"))
        for i, item in enumerate(obj):
            issues.extend(_walk_verified_issues(item, f"{path}[{i}]"))
    return issues


def _collect_route_source_ids(categories_data: Dict[str, Any]) -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = []
    cats = categories_data.get("categories") or {}
    for cat_key, cat in cats.items():
        if isinstance(cat, dict):
            route = cat.get("route_to") or {}
            sid = route.get("source_id")
            if sid:
                pairs.append((cat_key, sid))
    excluded = categories_data.get("excluded_from_periodic_routing") or {}
    for ex_key, ex in excluded.items():
        if isinstance(ex, dict):
            route = ex.get("route_to") or {}
            sid = route.get("source_id")
            if sid:
                pairs.append((f"excluded.{ex_key}", sid))
    return pairs


def _document_group(doc: Dict[str, Any]) -> str:
    cf = doc.get("created_from", "")
    if cf == CREATED_FROM_PERIODIC:
        return "periodic"
    if cf == CREATED_FROM_NON_PERIODIC:
        return "non_periodic"
    if doc.get("pdf_url"):
        return "periodic"
    return "non_periodic"


def run_lint(
    registry_path: str,
    categories_path: str,
    schemas_dir: str,
    fixtures_dir: str,
) -> List[Finding]:
    findings: List[Finding] = []
    registry = _load_yaml(registry_path)
    categories = _load_yaml(categories_path)
    sources: List[Dict[str, Any]] = registry.get("sources") or []

    document_schema = _load_json(os.path.join(schemas_dir, "b_document.schema.json"))
    raw_file_schema = _load_json(os.path.join(schemas_dir, "b_raw_file.schema.json"))
    parse_run_schema = _load_json(os.path.join(schemas_dir, "b_document_parse_run.schema.json"))

    doc_type_enum = _document_property_enum(document_schema, "document_type")
    retrieval_enum = _document_property_enum(document_schema, "retrieval_status")
    classification_enum = _document_property_enum(document_schema, "classification_status")
    download_enum = _schema_enum(raw_file_schema, "download_status")
    parse_status_enum = _schema_enum(parse_run_schema, "parse_status")

    registry_ids: Set[str] = set()
    for src in sources:
        sid = src.get("source_id")
        if not sid:
            continue
        # R001
        if sid in registry_ids:
            findings.append(Finding(
                "R001", "FAIL", sid, "FAIL",
                f"Duplicate source_id: {sid}",
                "Use unique source_id per source",
            ))
        registry_ids.add(sid)

        # R002
        layer = src.get("source_layer")
        if layer not in VALID_SOURCE_LAYERS:
            findings.append(Finding(
                "R002", "FAIL", sid, "FAIL",
                f"source_layer must be document_corpus, got {layer!r}",
                "Set source_layer: document_corpus",
            ))

        # R004
        cat = src.get("source_category")
        if cat not in VALID_SOURCE_CATEGORIES:
            findings.append(Finding(
                "R004", "FAIL", sid, "FAIL",
                f"Invalid source_category: {cat!r}",
                f"Use one of {sorted(VALID_SOURCE_CATEGORIES)}",
            ))

        # R005
        for field in ("source_id", "source_name", "source_layer", "source_category"):
            if not src.get(field):
                findings.append(Finding(
                    "R005", "FAIL", sid, "FAIL",
                    f"Missing required field: {field}",
                    f"Add {field}",
                ))
        if not src.get("document_type_candidates"):
            findings.append(Finding(
                "R005", "FAIL", sid, "FAIL",
                "Missing document_type_candidates",
                "Add document_type_candidates list",
            ))
        if _get_path(src, "status.recommended_status") is None:
            findings.append(Finding(
                "R005", "FAIL", sid, "FAIL",
                "Missing status.recommended_status",
                "Add status.recommended_status",
            ))
        if _get_path(src, "status.verified") is None:
            findings.append(Finding(
                "R005", "FAIL", sid, "FAIL",
                "Missing status.verified",
                "Add status.verified: false",
            ))

        # R003 per source
        if _get_path(src, "status.verified") is True:
            findings.append(Finding(
                "R003", "FAIL", sid, "FAIL",
                "status.verified must be false",
                "Set status.verified: false",
            ))
        rec = _get_path(src, "status.recommended_status")
        if rec == "verified":
            findings.append(Finding(
                "R003", "FAIL", sid, "FAIL",
                "recommended_status must not be verified",
                "Use candidate/testing/testing_stable_sample/etc.",
            ))

        # R006
        if rec and rec not in VALID_RECOMMENDED_STATUS:
            findings.append(Finding(
                "R006", "FAIL", sid, "FAIL",
                f"Invalid recommended_status: {rec!r}",
                f"Use one of {sorted(VALID_RECOMMENDED_STATUS)}",
            ))

        # R007
        if sid == PERIODIC_SOURCE_ID:
            if rec != "testing_stable_sample":
                findings.append(Finding(
                    "R007", "FAIL", sid, "FAIL",
                    f"cninfo_periodic_report_pdf must be testing_stable_sample, got {rec!r}",
                    "Set status.recommended_status: testing_stable_sample",
                ))
        else:
            if rec != "candidate":
                findings.append(Finding(
                    "R007", "WARN", sid, "WARN",
                    f"Non-periodic source should be candidate, got {rec!r}",
                    "Keep candidate until independently validated",
                ))

        # R012
        if sid in NON_PERIODIC_KNOWN_SOURCES and rec != "candidate":
            findings.append(Finding(
                "R012", "WARN", sid, "WARN",
                f"Known non-periodic source should be candidate, got {rec!r}",
                "Set status.recommended_status: candidate",
            ))

        # R018 registry
        if sid in D_CLASS_SOURCE_IDS:
            findings.append(Finding(
                "R018", "FAIL", sid, "FAIL",
                f"D-class source_id must not appear in B registry: {sid}",
                "Remove or rename source_id",
            ))

    # R003 global walk
    for path, msg in _walk_verified_issues(registry):
        if "verified is true" in msg or "verified" in msg:
            findings.append(Finding(
                "R003", "FAIL", path, "FAIL", msg,
                "Set verified: false everywhere",
            ))

    # R008 route_to
    for cat_key, route_sid in _collect_route_source_ids(categories):
        if route_sid not in registry_ids:
            findings.append(Finding(
                "R008", "FAIL", cat_key, "FAIL",
                f"route_to.source_id {route_sid!r} not in B registry",
                "Add source to registry or fix route_to",
            ))
        if route_sid in D_CLASS_SOURCE_IDS:
            findings.append(Finding(
                "R018", "FAIL", cat_key, "FAIL",
                f"route_to references D-class source_id: {route_sid}",
                "Use B-class document_corpus source_id",
            ))

    # R009
    if categories.get("verified") is True:
        findings.append(Finding(
            "R009", "FAIL", "categories_yaml", "FAIL",
            "Top-level verified must be false",
            "Set verified: false",
        ))

    # R010 category_code
    cats = categories.get("categories") or {}
    for cat_key, cat in cats.items():
        if not isinstance(cat, dict):
            continue
        code = cat.get("category_code")
        if code is not None:
            findings.append(Finding(
                "R010", "INFO", cat_key, "PASS",
                f"category_code is set: {code!r} (probe result)",
                "",
            ))

    # R011 periodic exclusion
    periodic = cats.get("periodic_report") or {}
    exclusions = periodic.get("exclusion_patterns") or []
    if isinstance(exclusions, list):
        for pattern in REQUIRED_PERIODIC_EXCLUSIONS:
            if pattern not in exclusions:
                findings.append(Finding(
                    "R011", "FAIL", "periodic_report", "FAIL",
                    f"Missing exclusion pattern: {pattern!r}",
                    "Add to categories.periodic_report.exclusion_patterns",
                ))

    # R013 schemas
    for fname in REQUIRED_SCHEMA_FILES:
        fpath = os.path.join(schemas_dir, fname)
        if not os.path.isfile(fpath):
            findings.append(Finding(
                "R013", "FAIL", fname, "FAIL",
                f"Missing schema file: {fpath}",
                f"Create schemas/b_class/{fname}",
            ))

    # Fixtures
    doc_pattern = os.path.join(fixtures_dir, "document", "*.jsonl")
    raw_pattern = os.path.join(fixtures_dir, "raw_file", "*.jsonl")
    parse_pattern = os.path.join(fixtures_dir, "parse_run", "*.jsonl")

    documents = _load_jsonl_glob(doc_pattern)
    raw_files = _load_jsonl_glob(raw_pattern)
    parse_runs = _load_jsonl_glob(parse_pattern)

    doc_by_id: Dict[str, Dict[str, Any]] = {}
    for i, doc in enumerate(documents):
        target = doc.get("document_id") or f"document[{i}]"
        doc_by_id[str(doc.get("document_id", ""))] = doc

        # R014
        sid = doc.get("source_id")
        if sid and sid not in registry_ids:
            findings.append(Finding(
                "R014", "FAIL", target, "FAIL",
                f"document source_id {sid!r} not in registry",
                "Fix source_id or add to registry",
            ))
        if sid in D_CLASS_SOURCE_IDS:
            findings.append(Finding(
                "R018", "FAIL", target, "FAIL",
                f"document fixture uses D-class source_id: {sid}",
                "Use B-class source_id",
            ))

        # R015
        sc = doc.get("source_confidence")
        group = _document_group(doc)
        if group == "non_periodic" and sc != "candidate":
            findings.append(Finding(
                "R015", "FAIL", target, "FAIL",
                f"non-periodic fixture must have source_confidence=candidate, got {sc!r}",
                "Set source_confidence: candidate",
            ))
        if group == "periodic" and sc not in ("testing_stable_sample", "testing", "candidate"):
            findings.append(Finding(
                "R015", "FAIL", target, "FAIL",
                f"Invalid source_confidence for periodic fixture: {sc!r}",
                "Use testing_stable_sample for Phase 1 derived fixtures",
            ))

        # R019-R021
        dt = doc.get("document_type")
        if dt and dt not in doc_type_enum:
            findings.append(Finding(
                "R019", "FAIL", target, "FAIL",
                f"Invalid document_type: {dt!r}",
                f"Use b_document enum: {sorted(doc_type_enum)}",
            ))
        rs = doc.get("retrieval_status")
        if rs and rs not in retrieval_enum:
            findings.append(Finding(
                "R020", "FAIL", target, "FAIL",
                f"Invalid retrieval_status: {rs!r}",
                f"Use b_document enum: {sorted(retrieval_enum)}",
            ))
        cs = doc.get("classification_status")
        if cs and cs not in classification_enum:
            findings.append(Finding(
                "R021", "FAIL", target, "FAIL",
                f"Invalid classification_status: {cs!r}",
                f"Use b_document enum: {sorted(classification_enum)}",
            ))

    # R016 raw_file
    for i, rf in enumerate(raw_files):
        target = rf.get("raw_file_id") or f"raw_file[{i}]"
        url = rf.get("source_url")
        if not url:
            findings.append(Finding(
                "R016", "FAIL", target, "FAIL",
                "raw_file source_url must be non-empty when row exists",
                "Add source_url from document pdf_url",
            ))
        ds = rf.get("download_status")
        if ds and ds not in download_enum:
            findings.append(Finding(
                "R022", "FAIL", target, "FAIL",
                f"Invalid download_status: {ds!r}",
                f"Use b_raw_file enum: {sorted(download_enum)}",
            ))

    # R017 parse_run
    parse_by_doc = {str(pr.get("document_id", "")): pr for pr in parse_runs}
    for doc_id, doc in doc_by_id.items():
        pr = parse_by_doc.get(doc_id)
        if not pr:
            findings.append(Finding(
                "R017", "FAIL", doc_id or "?", "FAIL",
                "Missing parse_run dry-run for document",
                "Run seed_cninfo_b_class_parse_run_dry_run_fixtures.py",
            ))
            continue
        group = _document_group(doc)
        ps = pr.get("parse_status")
        if ps and ps not in parse_status_enum:
            findings.append(Finding(
                "R023", "FAIL", pr.get("parse_run_id", doc_id), "FAIL",
                f"Invalid parse_status: {ps!r}",
                f"Use b_document_parse_run enum: {sorted(parse_status_enum)}",
            ))
        if group == "periodic" and ps != "not_started":
            findings.append(Finding(
                "R017", "FAIL", doc_id, "FAIL",
                f"periodic parse_run must be not_started, got {ps!r}",
                "Set parse_status: not_started",
            ))
        if group == "non_periodic" and ps != "skipped":
            findings.append(Finding(
                "R017", "FAIL", doc_id, "FAIL",
                f"non-periodic parse_run must be skipped, got {ps!r}",
                "Set parse_status: skipped",
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
    categories_path: str,
    schemas_dir: str,
    fixtures_dir: str,
    result: str,
) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fail_n = sum(1 for f in findings if f.severity == "FAIL")
    warn_n = sum(1 for f in findings if f.severity == "WARN")
    info_n = sum(1 for f in findings if f.severity == "INFO")

    fail_warn = [f for f in findings if f.severity in ("FAIL", "WARN")]

    lines = [
        "# CNINFO B 类 Registry Lint Summary",
        "",
        "## 1. 目的",
        "",
        "本地 **registry / category routing / JSON Schema / fixture** 一致性检查。",
        "**不请求 CNINFO**；不下载/解析 PDF；不写 verified。",
        "",
        "## 2. 输入",
        "",
        "| 来源 | 路径 |",
        "|------|------|",
        f"| B 类 registry | `{os.path.relpath(registry_path, BASE_DIR)}` |",
        f"| Category routing | `{os.path.relpath(categories_path, BASE_DIR)}` |",
        f"| Schemas | `{os.path.relpath(schemas_dir, BASE_DIR)}/` |",
        f"| Fixtures | `{os.path.relpath(fixtures_dir, BASE_DIR)}/` |",
        f"| 脚本 | `lab/lint_cninfo_b_class_registry.py` |",
        "",
        "## 3. 总体结果",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| total_rules | **{TOTAL_RULES}** |",
        f"| fail | **{fail_n}** |",
        f"| warn | **{warn_n}** |",
        f"| info | **{info_n}** |",
        f"| result | **{result}** |",
        "",
        "## 4. 重点检查结果",
        "",
        "- **source_layer**：全部须为 `document_corpus`（R002）",
        "- **verified**：全部须为 `false`；禁止 `verified` enum（R003/R009）",
        "- **route_to**：category YAML 中 `source_id` 须匹配 registry（R008）",
        "- **fixture source_id**：document fixture 须在 registry 内（R014）",
        "- **non-periodic source**：inquiry/meeting/general 保持 `candidate`（R007/R012）",
        "- **periodic source**：`cninfo_periodic_report_pdf` = `testing_stable_sample`（R007）",
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
        "- Lint **PASS** 不代表 CNINFO coverage%。",
        "- 不代表 PDF 已下载或已解析。",
        "- 不代表 source **verified**。",
        "- offline title fixture 的 `found` 仅表示 benchmark 路由。",
        "",
        "## 7. 下一步",
        "",
        "1. Corpus retrieval validation 小样本设计。",
        "2. Known-document benchmark 替换为真实样本。",
        "3. Probe 官方 `category_code`。",
        "4. 允许请求后补 `pdf_url` 与 raw_file。",
        "",
        "## 附录",
        "",
        "详见 [cninfo_b_class_registry_lint_report.csv](cninfo_b_class_registry_lint_report.csv)。",
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
    parser = argparse.ArgumentParser(description="Lint B-class document corpus registry")
    parser.add_argument("--registry", default=DEFAULT_REGISTRY)
    parser.add_argument("--categories", default=DEFAULT_CATEGORIES)
    parser.add_argument("--schemas-dir", default=DEFAULT_SCHEMAS_DIR)
    parser.add_argument("--fixtures-dir", default=DEFAULT_FIXTURES_DIR)
    parser.add_argument("--output-csv", default=DEFAULT_CSV)
    parser.add_argument("--output-md", default=DEFAULT_MD)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    registry = _load_yaml(args.registry)
    source_count = len(registry.get("sources") or [])

    findings = run_lint(
        args.registry,
        args.categories,
        args.schemas_dir,
        args.fixtures_dir,
    )

    write_csv(args.output_csv, findings)
    fail_n = sum(1 for f in findings if f.severity == "FAIL")
    result = "FAIL" if fail_n else "PASS"
    write_summary_md(
        args.output_md,
        findings,
        args.registry,
        args.categories,
        args.schemas_dir,
        args.fixtures_dir,
        result,
    )

    exit_code = print_report(findings, source_count, args.strict)
    print(f"CSV   {args.output_csv}")
    print(f"MD    {args.output_md}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
