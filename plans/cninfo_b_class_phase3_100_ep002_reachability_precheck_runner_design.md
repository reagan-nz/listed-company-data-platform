# CNINFO B 类 Phase 3 EP002/orgId Reachability Precheck Runner 设计

_生成时间：2026-07-09_

> **性质：** 设计 only · **本回合不实现 live** · **无 CNINFO** · **无 dry-run 执行**

**目标文件（未来）：** `lab/run_cninfo_b_class_phase3_100_ep002_reachability_precheck.py`

---

## 1. 设计目标

提供 **独立** precheck runner，与 Phase 3 expansion / failed retry runner **解耦**，仅执行轻量级 **EP002 orgId 可达性**探测。

**不做：** metadata retry · EP001/EP004/EP005 · PDF · OCR · extraction · DB · MinIO · RAG

---

## 2. CLI Flags

```python
parser.add_argument("--dry-run", action="store_true", help="离线计划模式，CNINFO=0")
parser.add_argument("--live", action="store_true", help="live precheck（须批准 flag）")
parser.add_argument(
    "--candidates-csv",
    default=DEFAULT_PRECHECK_CANDIDATES_CSV,
    help="precheck 候选 CSV",
)
parser.add_argument(
    "--output-root",
    default=DEFAULT_PRECHECK_OUTPUT_ROOT,
    help="隔离输出根",
)
parser.add_argument(
    "--request-cap",
    type=int,
    default=16,
    help="live CNINFO 请求硬上限",
)
parser.add_argument(
    "--approve-b-class-phase3-100-ep002-reachability-precheck",
    action="store_true",
    help="显式批准 live precheck",
)
```

**常量：**

```python
PRECHECK_APPROVAL_REQUIRED = "approve_b_class_phase3_100_ep002_reachability_precheck_required"
DEFAULT_PRECHECK_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation",
    "cninfo_b_class_phase3_100_ep002_reachability_precheck",
)
DEFAULT_PRECHECK_CANDIDATES_CSV = os.path.join(
    BASE_DIR, "outputs", "validation",
    "cninfo_b_class_phase3_100_ep002_reachability_precheck_candidates.csv",
)
HOLD_CASE_ID = "B3E087"
RECOVERED_CASE_IDS = frozenset({
    "B3E003", "B3E004", "B3E005", "B3E006",
    "B3E007", "B3E008", "B3E009", "B3E011",
})
ALLOWED_PRECHECK_CASE_IDS = frozenset({...})  # 8 candidates from persistent 91
MAX_PRECHECK_REQUEST_CAP = 16
PRECHECK_RESOLVE_THRESHOLD = 0.60  # >= 60% -> PASS_WITH_CAVEAT
```

---

## 3. Candidates CSV Loader

**必需列：** `precheck_id` · `case_id` · `company_code` · `company_name` · `market` · `announcement_type` · `target_endpoint` · `precheck_include` · `planned_check_type`

**校验：**

1. `precheck_include=yes` 行数 ∈ **[5, 8]**
2. `case_id` ⊆ persistent **91** ledger
3. `case_id` ≠ `B3E087`
4. `case_id` ∩ `RECOVERED_CASE_IDS` = ∅
5. `case_id` 不得为 prior B-class Phase 1/2/2.5 case
6. `planned_check_type` = `ep002_orgid_reachability`
7. candidates CSV 路径固定为 `cninfo_b_class_phase3_100_ep002_reachability_precheck_candidates.csv`

**错误码：**

- `HOLD_CASE_IN_PRECHECK_FORBIDDEN`
- `RECOVERED_CASE_IN_PRECHECK_FORBIDDEN`
- `PRECHECK_CANDIDATE_OUT_OF_PERSISTENT_UNIVERSE`
- `PRECHECK_CHECK_TYPE_UNSUPPORTED`
- `PRECHECK_CANDIDATES_CSV_INVALID`
- `PRECHECK_CANDIDATE_COUNT_VIOLATION`

---

## 4. Blocked Cases

| 类别 | case_id / 规则 |
|------|----------------|
| hold | B3E087 |
| recovered retry | B3E003–B3E011（8 例） |
| prior B-class | B1E* · B2E* · B25E* |
| non-persistent | 不在 persistent failure ledger 的 case |

---

## 5. Request Cap Enforcement

| 模式 | CNINFO |
|------|--------|
| dry-run | **0** |
| live | **≤ min(--request-cap, 16)** |

Live 执行前估算：

- 可选 1 次全局 `topsearch_reachability` probe（计入 cap）
- 每候选 1 次 `ep002_orgid_reachability`
- 超过 cap 时 **中止** 并返回 error

---

## 6. Approval Guard

```python
def enforce_precheck_approval_gate(args):
    if args.mode == "live" and not args.approve_b_class_phase3_100_ep002_reachability_precheck:
        sys.exit(PRECHECK_APPROVAL_REQUIRED)
    # reject wrong approval flags from phase3 expansion / failed retry / phase25
```

Live 无批准 flag → **拒绝** · **不调用 CNINFO** · **不创建 live report**

---

## 7. Output Root Isolation

| 根 | 策略 |
|----|------|
| `cninfo_b_class_phase3_100_ep002_reachability_precheck/` | **允许** |
| `cninfo_b_class_phase3_100_expansion/` | **write-blocked** |
| `cninfo_b_class_phase3_100_failed_retry/` | **write-blocked** |
| `cninfo_b_class_phase25_expansion/` | **write-blocked** |
| `cninfo_b_class_phase25_failed_retry/` | **write-blocked** |

---

## 8. Report Paths

| 报告 | 路径 |
|------|------|
| dry-run report | `{output_root}/reports/b_class_phase3_100_ep002_reachability_precheck_dryrun_report.csv` |
| dry-run summary | `{output_root}/reports/b_class_phase3_100_ep002_reachability_precheck_dryrun_summary.md` |
| live report | `{output_root}/reports/b_class_phase3_100_ep002_reachability_precheck_report.csv` |
| live summary | `{output_root}/reports/b_class_phase3_100_ep002_reachability_precheck_summary.md` |
| quality report | `{output_root}/reports/b_class_phase3_100_ep002_reachability_precheck_quality_report.csv` |

**Live report 列（设计）：**

`precheck_id` · `case_id` · `company_code` · `company_name` · `market` · `announcement_type` · `planned_check_type` · `orgid_resolution_status` · `orgid_value_present` · `http_status` · `failure_type` · `cninfo_request_count` · `pdf_downloaded` · `pdf_parsed` · `notes`

---

## 9. Failure Taxonomy

| failure_type | 含义 |
|--------------|------|
| `orgid_resolved` | EP002 返回有效 orgId |
| `network_error` | HTTP/timeout at EP002 |
| `orgid_not_found` | HTTP OK but no orgId |
| `proxy_error` | 503/502 proxy |
| `request_cap_exceeded` | 超过 cap 中止 |

---

## 10. Interpretation Rules

| 结果 | execution gate |
|------|----------------|
| resolve count / total ≥ **60%** | `PASS_WITH_CAVEAT` |
| resolve count / total < **60%** | `FAIL_REVIEW_REQUIRED` |
| red-line（PDF downloaded 等） | `FAIL_REVIEW_REQUIRED` |

**Never：** `PASS` · `verified` · `production_ready`

---

## 11. No PDF/OCR/Extraction/DB/MinIO/RAG Boundary

```python
PDF_DOWNLOAD_ENABLED = False
PDF_PARSE_ENABLED = False
# enforce_forbidden_options blocks --download-pdf --parse-pdf --run-ocr etc.
```

---

## 12. Future Live Behavior After Approval

1. validate candidates + output root + approval
2. for each included candidate: call EP002 topSearch orgId only
3. record resolution status per candidate
4. write live reports under isolated output root
5. compute execution gate
6. **不** proceed to metadata retry automatically

---

## 13. Forbidden Options（shared pattern）

与 Phase 3 expansion runner 一致：

- `--download-pdf` · `--parse-pdf` · `--run-ocr` · `--extract-sections`
- `--write-db` · `--write-minio` · `--run-rag`
- `--mark-verified` · `--mark-production-ready`

---

## 14. Tests（未来回合）

独立测试文件：`lab/test_cninfo_b_class_phase3_100_ep002_reachability_precheck_runner.py`

最低覆盖：approval guard · candidate validation · cap enforcement · output isolation · dry-run CNINFO=0
