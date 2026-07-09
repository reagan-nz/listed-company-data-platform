"""
从 success-subset design 生成 Phase 3 batch 500 snapshot universe YAML（491 家）。

运行：
    python lab/generate_cninfo_c_class_phase3_batch_500_success_snapshot_universe_yaml.py

红线：无 CNINFO · 无 harvest · 无 snapshot build
"""

from __future__ import annotations

import csv
import os
import sys
from collections import Counter
from datetime import date

import yaml

_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(_LAB_DIR)
if _LAB_DIR not in sys.path:
    sys.path.insert(0, _LAB_DIR)

SUBSET_DESIGN = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_subset_design.csv",
)
CAVEAT_LEDGER = os.path.join(
    BASE_DIR,
    "outputs/validation/cninfo_c_class_phase3_batch_500_failure_identity_caveat_ledger.csv",
)
PARENT_YAML = os.path.join(
    BASE_DIR, "lab/eval_companies_c_class_phase3_batch_500_001.yaml"
)
OUTPUT_YAML = os.path.join(
    BASE_DIR, "lab/eval_companies_c_class_phase3_batch_500_success_snapshot_491.yaml"
)

EXCLUDED_CODES = {
    "600102", "600270", "600317", "600625", "600627",
    "600705", "600840", "601028", "601989",
}


def main() -> None:
    included_codes: list[str] = []
    with open(SUBSET_DESIGN, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["include_for_snapshot"] == "true":
                included_codes.append(row["company_code"])

    if len(included_codes) != 491:
        print(f"WARNING: expected 491 included, got {len(included_codes)}", file=sys.stderr)

    overlap = set(included_codes) & EXCLUDED_CODES
    if overlap:
        raise SystemExit(f"excluded codes found in included set: {sorted(overlap)}")

    with open(PARENT_YAML, encoding="utf-8") as fh:
        parent = yaml.safe_load(fh)

    parent_by_code = {str(c["company_code"]): c for c in parent["companies"]}
    companies = []
    for code in sorted(included_codes):
        if code not in parent_by_code:
            raise SystemExit(f"missing parent YAML entry: {code}")
        entry = dict(parent_by_code[code])
        board = entry.get("board", "")
        if board == "bse" or str(entry.get("exchange", "")).upper() == "BSE":
            raise SystemExit(f"BSE company in included set: {code}")
        entry["harvest_status"] = "phase3_batch_500_snapshot_candidate"
        entry["snapshot_subset_reason"] = "identity_clean_success_subset"
        companies.append(entry)

    board_counts = dict(Counter(c.get("board", "unknown") for c in companies))
    doc = {
        "version": "c-class-phase3-batch-500-success-snapshot-v1",
        "generated_at": date.today().isoformat(),
        "parent_universe": "lab/eval_companies_c_class_phase3_batch_500_001.yaml",
        "subset_design": (
            "outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_subset_design.csv"
        ),
        "universe_id": "phase3_batch_500_001_success_snapshot_491",
        "batch_id": "phase3_batch_500_001",
        "description": (
            "Phase 3 batch 500 success subset · 491 identity-clean companies for snapshot"
        ),
        "company_count": len(companies),
        "excluded_identity_caveat_count": 9,
        "harvest_root": "outputs/harvest/cninfo_c_class/phase3_batch_500_001",
        "snapshot_output_root": "outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success",
        "board_counts": board_counts,
        "companies": companies,
    }

    with open(OUTPUT_YAML, "w", encoding="utf-8") as fh:
        yaml.dump(
            doc,
            fh,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )

    print(f"YAML    {OUTPUT_YAML}")
    print(f"count   {len(companies)}")


if __name__ == "__main__":
    main()
