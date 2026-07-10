# CNINFO A 类 Phase 2 CNINFO Reachability Precheck Runner 设计

_生成时间：2026-07-09_

> **性质：** 设计 only · **本回合不实现 live** · **无 CNINFO** · **无 dry-run 执行**

**目标文件（未来）：** `lab/run_cninfo_a_class_phase2_cninfo_reachability_precheck.py`

---

## 1. 设计目标

提供 **独立** precheck runner，与 metadata expansion / retry v1 / retry v2 runner **解耦**，仅执行轻量级 CNINFO/orgId 可达性探测。

**不做：** metadata retry · report matching · PDF · OCR · extraction · DB · MinIO · RAG

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
    default=6,
    help="live CNINFO 请求硬上限",
)
parser.add_argument(
    "--approve-a-class-phase2-cninfo-reachability-precheck",
    action="store_true",
    help="显式批准 live precheck",
)
```

**常量：**

```python
PRECHECK_APPROVAL_REQUIRED = "approve_a_class_phase2_cninfo_reachability_precheck_required"
DEFAULT_PRECHECK_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation",
    "cninfo_a_class_phase2_cninfo_reachability_precheck",
)
DEFAULT_PRECHECK_CANDIDATES_CSV = os.path.join(
    BASE_DIR, "outputs", "validation",
    "cninfo_a_class_phase2_cninfo_reachability_precheck_candidates.csv",
)
SUCCESSFUL_CASE_IDS = frozenset({
    "A2M001", "A2M002", "A2M003", "A2M004",
    "A2M006", "A2M007", "A2M008", "A2M009",
    "A2M014", "A2M015", "A2M016", "A2M017",
})
MAX_PRECHECK_REQUEST_CAP = 6
```

---

## 3. Candidates CSV Loader

**必需列：** `precheck_id` · `case_id` · `company_code` · `company_name` · `market` · `report_type` · `report_period` · `precheck_include` · `planned_check_type`

**校验：**

1. `precheck_include=yes` 行数 ≥ 1
2. `case_id` ⊆ unresolved 8（A2M005 · A2M010–A2M013 · A2M018–A2M020）
3. `case_id` ∩ `SUCCESSFUL_CASE_IDS` = ∅
4. `planned_check_type` ∈ `{orgid_resolution_reachability}`（v1 仅接受此类型）
5. `report_type` / `report_period` 与 ledger v2 一致（只读校验，不用于 matching）

**错误码：**

- `SUCCESSFUL_CASE_IN_PRECHECK_FORBIDDEN`
- `PRECHECK_CANDIDATE_OUT_OF_UNIVERSE`
- `PRECHECK_CHECK_TYPE_UNSUPPORTED`
- `PRECHECK_CANDIDATES_CSV_INVALID`

---

## 4. Request Cap Enforcement

| 模式 | CNINFO |
|------|--------|
| dry-run | **0** |
| live | **≤ min(--request-cap, 6)** |

Live 执行前估算计划请求数：

- 可选 1 次 `topsearch_reachability` probe
- 每候选 1 次 `orgid_resolution_reachability`

若 `planned_requests > cap` → 拒绝 live，返回 `PRECHECK_REQUEST_CAP_EXCEEDED`。

执行中维护 `cninfo_request_count`；达到 cap 后 **停止** 后续候选。

---

## 5. Accepted Check Types

| check_type | live 行为 | 计入 cap |
|------------|-----------|----------|
| `orgid_resolution_reachability` | 对 `company_code` 调用 orgId 解析路径 | yes |
| `topsearch_reachability`（可选全局） | 单次 topSearch HTTP probe | yes |

**明确拒绝：** `announcement_query` · `metadata_match` · `pdf_url_fetch`

---

## 6. Approval Guard

Live 须同时满足：

1. `--live` 已设置
2. `--approve-a-class-phase2-cninfo-reachability-precheck` 已设置
3. **不得** 设置 metadata expansion / retry v1 / retry v2 approval flags
4. output root = `cninfo_a_class_phase2_cninfo_reachability_precheck/` 子树
5. dry-run 已通过（可选门禁：检查 dryrun report 存在）

否则返回 `PRECHECK_APPROVAL_REQUIRED`。

---

## 7. Output-Root Isolation

`validate_precheck_output_root()`：

| 路径 | precheck 模式 |
|------|---------------|
| `cninfo_a_class_phase2_metadata_expansion/` | **禁止写入** |
| `cninfo_a_class_phase2_metadata_retry/` | **禁止写入** |
| `cninfo_a_class_phase2_metadata_retry_v2/` | **禁止写入** |
| `cninfo_a_class_phase2_cninfo_reachability_precheck/` | **允许** |

---

## 8. Report Paths

| 报告 | 路径 |
|------|------|
| dry-run report | `{output_root}/reports/a_class_phase2_cninfo_reachability_precheck_dryrun_report.csv` |
| dry-run summary | `{output_root}/reports/a_class_phase2_cninfo_reachability_precheck_dryrun_summary.md` |
| live report | `{output_root}/reports/a_class_phase2_cninfo_reachability_precheck_report.csv` |
| live summary | `{output_root}/reports/a_class_phase2_cninfo_reachability_precheck_summary.md` |

**live report 列（设计）：**

`precheck_id` · `case_id` · `company_code` · `market` · `planned_check_type` · `check_status` · `failure_stage` · `failure_category` · `org_id_resolved` · `http_status` · `cninfo_request_count` · `notes`

---

## 9. Failure Taxonomy

| failure_category | 含义 |
|------------------|------|
| `network_error` | TCP/HTTP 不可达 · timeout |
| `orgid_not_found` | 可达但无 orgId |
| `http_error` | 4xx/5xx（非 network_error） |
| `cap_exceeded` | 达到 request cap 后跳过 |
| `planned_ok` | dry-run 计划有效 |

**不产出：** `wrong_report_type` · `title_mismatch` · `period_mismatch`

---

## 10. Interpretation Rules

| 汇总 | execution_gate（未来） |
|------|------------------------|
| 全部候选 orgId 可达 | `READY_FOR_RETRY_V3_PLANNING`（非 PASS） |
| 部分可达 | `PASS_WITH_CAVEAT` |
| 全部 network_error | `FAIL_REVIEW_REQUIRED` |
| dry-run | `READY_FOR_APPROVAL` |

Precheck summary **不得** 标记 verified · production_ready · testing_stable_sample。

---

## 11. Boundary（无 PDF/OCR/DB/MinIO/RAG）

Runner 模块 **不 import** PDF parser · OCR · DB writer · MinIO client · RAG pipeline。

若检测到相关 flag 或输出路径 → `PRECHECK_BOUNDARY_VIOLATION`。

---

## 12. Future Live Behavior After Approval

1. 加载 candidates CSV · 校验 cap · 校验 output root
2. 可选 topSearch probe（1 request）
3. 按 `precheck_id` 顺序执行 `orgid_resolution_reachability`
4. 写入 live report + summary
5. 记录 `cninfo_request_count` · timestamp · gate
6. **不** 触发 retry_v3 · **不** 更新 merged result v2

---

## 13. 本回合状态

| 项 | 状态 |
|----|------|
| runner 实现 | **未开始** |
| dry-run | **未执行** |
| tests | **未创建** |
| CNINFO calls | **0** |

**下一步（未执行）：** runner implementation + dry-run + tests → 人工批准 live precheck
