# CNINFO A 类 Phase 2 Retry v3 Runner Extension 设计

_生成时间：2026-07-09_

> **性质：** 设计 only · **本回合不实现** · **无 CNINFO** · **无 live**

**目标文件：** `lab/run_cninfo_a_class_phase2_metadata_expansion.py`

---

## 1. 当前 Runner 缺口

| 能力 | 现状 | v3 需要 |
|------|------|---------|
| retry mode flag | `--retry-failed-only` + v2 detection | `--retry-v3` |
| approval flag | v1 / v2 flags only | `--approve-a-class-phase2-retry-v3` |
| output root | expansion / retry / retry_v2 | `cninfo_a_class_phase2_metadata_retry_v3/` |
| universe CSV | `retry_v2_include` · `report_period` | `retry_v3_include` · `report_period` |
| precheck root | N/A | **只读** · 禁止写入 |

---

## 2. Required CLI Flags

```python
parser.add_argument(
    "--retry-v3",
    action="store_true",
    help="isolated retry v3 模式：仅 8 unresolved case",
)
parser.add_argument(
    "--approve-a-class-phase2-retry-v3",
    action="store_true",
    help="显式批准 A-class Phase 2 retry v3 live",
)
```

**常量：**

```python
RETRY_V3_APPROVAL_REQUIRED = "approve_a_class_phase2_retry_v3_required"
RETRY_V3_WRONG_APPROVAL = "approve_a_class_phase2_retry_v3_wrong_flag"
DEFAULT_RETRY_V3_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_phase2_metadata_retry_v3"
)
DEFAULT_RETRY_V3_UNIVERSE_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_phase2_retry_v3_universe.csv"
)
RETRY_V3_REQUIRED_UNIVERSE_SIZE = 8
RETRY_V3_ACCEPTABLE_THRESHOLD = 6
PRECHECK_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_phase2_cninfo_reachability_precheck"
)
```

---

## 3. Retry v3 Universe Loader

**必需列：** `case_id` · `company_code` · `company_name` · `market` · `report_type` · `report_period` · `retry_v3_include` · `precheck_signal` · `precheck_orgid_status`

**列别名：**

- `retry_v3_include` → internal `retry_include`
- `report_period` → internal `expected_period`

**校验：**

1. universe size = **8**
2. `retry_v3_include=yes` 行数 = **8**
3. case_ids = `RETRY_ALLOWED_CASE_IDS`（unresolved 8）
4. case_ids ∩ `SUCCESSFUL_CASE_IDS` = ∅
5. `report_type` / `report_period` 与 ledger v2 一致
6. 无 replacement case

---

## 4. Accepted / Rejected Case IDs

**允许（8）：**

```text
A2M005 A2M010 A2M011 A2M012 A2M013 A2M018 A2M019 A2M020
```

**拒绝（12）：**

```text
A2M001 A2M002 A2M003 A2M004 A2M006 A2M007 A2M008 A2M009
A2M014 A2M015 A2M016 A2M017
```

错误码：`SUCCESSFUL_CASE_IN_RETRY_FORBIDDEN` · `NON_RETRY_CASE_REJECTED`

---

## 5. Approval Guard

Live retry v3 须同时满足：

1. `--retry-v3` 已设置
2. `--live` 已设置
3. `--approve-a-class-phase2-retry-v3` 已设置
4. **不得** 同时设置 v1 / v2 / expansion / precheck approval flags
5. output root = `retry_v3/` 子树
6. precheck execution gate = `PASS_WITH_CAVEAT`（文档化门禁，非自动 live）

否则返回 `RETRY_V3_APPROVAL_REQUIRED` 或 `RETRY_V3_WRONG_APPROVAL`。

---

## 6. Output-Root Isolation

`validate_retry_v3_output_root()`：

| 路径 | v3 模式 |
|------|---------|
| `cninfo_a_class_phase2_metadata_expansion/` | **禁止写入** |
| `cninfo_a_class_phase2_metadata_retry/` | **禁止写入** |
| `cninfo_a_class_phase2_metadata_retry_v2/` | **禁止写入** |
| `cninfo_a_class_phase2_cninfo_reachability_precheck/` | **禁止写入** |
| `cninfo_a_class_phase2_metadata_retry_v3/` | **允许** |
| Phase 1 baseline | **禁止** |

---

## 7. Report Paths

| 报告 | 路径 |
|------|------|
| dry-run report | `{output_root}/reports/a_class_phase2_retry_v3_dryrun_report.csv` |
| dry-run summary | `{output_root}/reports/a_class_phase2_retry_v3_dryrun_summary.md` |
| live report | `{output_root}/reports/a_class_phase2_retry_v3_report.csv` |
| live summary | `{output_root}/reports/a_class_phase2_retry_v3_summary.md` |
| quality report | `{output_root}/reports/a_class_phase2_retry_v3_quality_report.csv` |

**live report 列（设计）：** 复用 v2 live 列 + `precheck_signal` · `precheck_orgid_status` · `retry_v3_retrieval_status`

---

## 8. Dry-run Behavior

- 加载 universe · 校验 8 case · 校验 output root
- **CNINFO = 0**
- 写入 dryrun report + summary
- gate = `a_class_phase2_retry_v3_runner_extension_gate = READY_FOR_APPROVAL`

---

## 9. Future Live Behavior After Approval

1. Preflight：universe · cap · write-block · forbidden flags
2. 对每 case 执行 metadata retrieval（orgId → announcement query → title/period match）
3. **无 PDF 下载/解析**
4. 写入 live report + quality report + summary
5. 计算 execution gate：

| 条件 | gate |
|------|------|
| acceptable ≥ **6/8** · wrong_report_type=0 · 无红线 | `PASS_WITH_CAVEAT` |
| acceptable < **6/8** | `FAIL_REVIEW_REQUIRED` |

**Never PASS** · **not verified** · **not production_ready**

---

## 10. Boundary（无 PDF/OCR/DB/MinIO/RAG）

与 v1/v2 相同：`enforce_forbidden_options()` 拒绝 PDF/OCR/extraction/DB/MinIO/RAG/verified/production_ready flags。

---

## 11. 本回合状态

| 项 | 状态 |
|----|------|
| runner 实现 | **未开始** |
| dry-run | **未执行** |
| tests | **未创建** |
| CNINFO calls | **0** |

**下一步（未执行）：** runner extension + dry-run + tests → 人工批准 live retry_v3
