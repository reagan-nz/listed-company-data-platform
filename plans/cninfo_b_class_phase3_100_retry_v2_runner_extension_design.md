# CNINFO B 类 Phase 3 Retry v2 Runner Extension 设计

_生成时间：2026-07-10_

> **性质：** 设计 only · **本回合不实现** · **无 CNINFO** · **无 live**

**目标文件：** `lab/run_cninfo_b_class_phase25_expansion_validation.py`

---

## 1. 当前 Runner 缺口

| 能力 | 现状 | retry_v2 需要 |
|------|------|---------------|
| mode flag | `--phase3-100-failed-retry`（v1 retry） | `--phase3-100-retry-v2` |
| approval flag | `--approve-b-class-phase3-100-failed-retry` | `--approve-b-class-phase3-100-retry-v2` |
| universe CSV | `cninfo_b_class_phase3_100_failed_retry_universe.csv`（99 行） | `cninfo_b_class_phase3_100_retry_v2_universe.csv`（**91** 行） |
| output root | `cninfo_b_class_phase3_100_failed_retry/` | `cninfo_b_class_phase3_100_retry_v2/` |
| case ID namespace | B3E* only | B3R2_* mapping → B3E* original |

当前 runner **无** `--phase3-100-retry-v2` 或 `--approve-b-class-phase3-100-retry-v2`。

---

## 2. Required CLI Flags

```python
parser.add_argument(
    "--phase3-100-retry-v2",
    action="store_true",
    help="B-class Phase 3 isolated retry v2 mode",
)
parser.add_argument(
    "--approve-b-class-phase3-100-retry-v2",
    action="store_true",
    help="显式批准 B-class Phase 3 retry v2 live",
)
```

**常量：**

```python
RETRY_V2_APPROVAL_REQUIRED = "approve_b_class_phase3_100_retry_v2_required"
DEFAULT_RETRY_V2_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_b_class_phase3_100_retry_v2"
)
DEFAULT_RETRY_V2_UNIVERSE_CSV = os.path.join(
    BASE_DIR, "outputs", "validation",
    "cninfo_b_class_phase3_100_retry_v2_universe.csv",
)
REQUIRED_RETRY_V2_UNIVERSE_SIZE = 91
PHASE3_SUCCESS_HOLD_CASE_ID = "B3E087"
RECOVERED_CASE_IDS = frozenset({
    "B3E003", "B3E004", "B3E005", "B3E006",
    "B3E007", "B3E008", "B3E009", "B3E011",
})
RETRY_V2_SUCCESS_THRESHOLD = 82  # 82/91 ≈ 90%
```

---

## 3. Retry v2 Universe Loader

**必需列：** `retry_v2_case_id` · `original_case_id` · `company_code` · `company_name` · `market` · `announcement_type` · `target_endpoint` · `retry_v2_include` · `persistent_failure_stage`

**校验：**

1. `retry_v2_include=yes` 行数 = **91**
2. `retry_v2_case_id` = B3R2_001–B3R2_091（无缺口）
3. `original_case_id` ⊆ persistent **91** ledger
4. `original_case_id` ≠ B3E087
5. `original_case_id` ∩ recovered **8** = ∅
6. `original_case_id` 不得为 B1E*/B2E*/B25E*
7. `final_effective_status_before_retry_v2 = unresolved_ep002_orgid_network_failure`

**错误码：**

- `RETRY_V2_UNIVERSE_SIZE_VIOLATION`
- `HOLD_CASE_IN_RETRY_V2_FORBIDDEN`
- `RECOVERED_CASE_IN_RETRY_V2_FORBIDDEN`
- `PRIOR_PHASE_CASE_IN_RETRY_V2_FORBIDDEN`
- `RETRY_V2_INCLUDE_REQUIRED`

---

## 4. Accepted Retry v2 Case IDs

- `retry_v2_case_id`: B3R2_001 … B3R2_091
- `original_case_id`: persistent **91** B3E* subset only

---

## 5. Blocked Cases

| 类别 | 规则 |
|------|------|
| hold | B3E087 |
| recovered | B3E003–B3E011 |
| prior B-class | B1E* · B2E* · B25E* |
| non-persistent | 不在 persistent ledger 的 case |
| replacement | 禁止新增 case |

---

## 6. Output-Root Isolation

新增 `validate_retry_v2_output_root()`：

| 路径 | retry_v2 模式 |
|------|---------------|
| `cninfo_b_class_phase3_100_retry_v2/` | **允许** |
| `cninfo_b_class_phase3_100_expansion/` | **write-blocked** |
| `cninfo_b_class_phase3_100_failed_retry/` | **write-blocked** |
| `cninfo_b_class_phase3_100_ep002_reachability_precheck/` | **write-blocked** |
| `cninfo_b_class_phase25_expansion/` | **write-blocked** |
| `cninfo_b_class_phase25_failed_retry/` | **write-blocked** |

---

## 7. Write-Block Protections

retry_v2 模式禁止写入：

- `b_class_phase3_100_report.csv` / `_summary.md` / `_quality_report.csv`
- `b_class_phase3_100_failed_retry_*` live/dryrun reports
- `b_class_phase3_100_ep002_reachability_precheck_*` reports
- Phase 2.5 expansion / failed-retry reports

---

## 8. Report Paths

| 报告 | 路径 |
|------|------|
| dry-run report | `{output_root}/reports/b_class_phase3_100_retry_v2_dryrun_report.csv` |
| dry-run summary | `{output_root}/reports/b_class_phase3_100_retry_v2_dryrun_summary.md` |
| live report | `{output_root}/reports/b_class_phase3_100_retry_v2_report.csv` |
| live summary | `{output_root}/reports/b_class_phase3_100_retry_v2_summary.md` |
| quality report | `{output_root}/reports/b_class_phase3_100_retry_v2_quality_report.csv` |

---

## 9. Dry-Run Behavior

- 加载 91-case universe
- 校验全部 preflight 规则
- 计算 planned CNINFO request count（每 case EP002 + EP001/EP004/EP005 依 target_endpoint）
- 生成 dry-run report + summary
- **CNINFO calls = 0**

---

## 10. Future Live Behavior After Approval

1. `enforce_retry_v2_approval_gate()` — 须 `--approve-b-class-phase3-100-retry-v2`
2. 拒绝 wrong approval flags（phase3 expansion / failed-retry v1 / EP002 precheck / phase25）
3. validate universe + output root
4. 对每 included case 执行 metadata retry（EP002 orgId → EP001/EP004/EP005）
5. 写入隔离 live reports
6. 计算 execution gate（≥82/91 → PASS_WITH_CAVEAT）
7. **不**自动 merge effective result · **不** mark verified

---

## 11. Execution Gate Logic

```python
def compute_retry_v2_execution_gate(acceptable_count: int, total: int = 91) -> str:
    if acceptable_count >= RETRY_V2_SUCCESS_THRESHOLD:
        return "PASS_WITH_CAVEAT"
    return "FAIL_REVIEW_REQUIRED"
```

**Never：** `PASS` · `verified` · `production_ready`

---

## 12. No PDF/OCR/Extraction/DB/MinIO/RAG Boundary

与 Phase 3 expansion / failed-retry 一致：

- `--download-pdf` · `--parse-pdf` · `--enable-ocr` · `--enable-extraction`
- `--write-db` · `--write-minio` · `--run-rag`
- `--mark-verified` · `--mark-production-ready`

retry_v2 live：**metadata + URL lineage only** · PDF **0**

---

## 13. Tests（未来回合）

独立或扩展测试文件：`lab/test_cninfo_b_class_phase3_100_retry_v2_runner.py`

最低覆盖：universe validation · B3E087 block · recovered block · output isolation · approval guard · dry-run CNINFO=0
