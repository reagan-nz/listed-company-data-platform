#!/usr/bin/env python3
"""
CNINFO C-class — 隔离 snapshot dry-run 可复现性检查（无 CNINFO · 无 EXECUTE）。

连续两次对同一隔离根跑 dry-run，比对 content/fingerprint SHA256。

Usage:
    python3 lab/run_cninfo_c_class_isolated_snapshot_dryrun_repro_check.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

from build_cninfo_c_class_snapshot_batch import (  # noqa: E402
    BASE_DIR,
    HOLD_YAML,
    UNIVERSE_YAML,
    reset_snapshot_batch_paths,
    run_dry_run,
)
from cninfo_c_class_erad_cleanup_guard import (  # noqa: E402
    DEFAULT_ISOLATED_SNAPSHOT_DRYRUN_ROOT_REL,
)

REPORT_JSON = os.path.join(
    BASE_DIR,
    "outputs/validation/"
    "cninfo_c_class_isolated_snapshot_dryrun_repro_check_20260715.json",
)
REPORT_MD = os.path.join(
    BASE_DIR,
    "outputs/validation/"
    "cninfo_c_class_isolated_snapshot_dryrun_repro_check_20260715.md",
)


def main() -> int:
    reset_snapshot_batch_paths()
    out_dir = os.path.join(BASE_DIR, DEFAULT_ISOLATED_SNAPSHOT_DRYRUN_ROOT_REL)
    report_path = os.path.join(out_dir, "dryrun_report.csv")
    summary_path = os.path.join(out_dir, "dryrun_summary.md")

    runs = []
    for i in range(2):
        result = run_dry_run(
            universe_path=UNIVERSE_YAML,
            hold_path=HOLD_YAML,
            out_dir=out_dir,
            report_path=report_path,
            summary_path=summary_path,
        )
        fp = result["dryrun_fingerprint"]
        runs.append(
            {
                "run_index": i + 1,
                "gate": result["gate"],
                "company_count": result["validation"]["company_count"],
                "universe_ok": result["universe_ok"],
                "content_sha256": fp["content_sha256"],
                "fingerprint_sha256": fp["fingerprint_sha256"],
            }
        )

    match = (
        runs[0]["content_sha256"] == runs[1]["content_sha256"]
        and runs[0]["fingerprint_sha256"] == runs[1]["fingerprint_sha256"]
        and runs[0]["gate"] == runs[1]["gate"]
    )
    gate = "PASS_OFFLINE" if match and runs[0]["universe_ok"] else "FAIL_REVIEW_REQUIRED"
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "output_root": DEFAULT_ISOLATED_SNAPSHOT_DRYRUN_ROOT_REL,
        "runs": runs,
        "reproducible": match,
        "gate": gate,
        "cninfo_calls": 0,
        "execute_production_snapshot_rebuild": False,
        "capability_gain": True,
    }

    os.makedirs(os.path.dirname(REPORT_JSON), exist_ok=True)
    with open(REPORT_JSON, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    lines = [
        "# CNINFO C 类 — 隔离 Snapshot Dry-run 可复现性检查",
        "",
        f"_生成时间：{payload['generated_at']}_",
        "",
        f"- output_root: `{DEFAULT_ISOLATED_SNAPSHOT_DRYRUN_ROOT_REL}`",
        f"- reproducible: **{match}**",
        f"- gate: `{gate}`",
        f"- company_count: **{runs[0]['company_count']}**",
        f"- content_sha256: `{runs[0]['content_sha256']}`",
        f"- fingerprint_sha256: `{runs[0]['fingerprint_sha256']}`",
        "- cninfo_calls: **0**",
        "- execute_production_snapshot_rebuild: **false**",
        "",
        "详见 JSON 报告。",
        "",
    ]
    with open(REPORT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    print(f"reproducible: {match}")
    print(f"gate: {gate}")
    print(f"content_sha256: {runs[0]['content_sha256']}")
    print(f"fingerprint_sha256: {runs[0]['fingerprint_sha256']}")
    print(f"report_json: {REPORT_JSON}")
    print("cninfo_calls=0")
    print("execute_production_snapshot_rebuild: false")
    return 0 if match and runs[0]["universe_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
