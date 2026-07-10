# CNINFO A 类 Phase 3 50-Company Runner Extension 设计

_生成时间：2026-07-10_

> **性质：** 设计 only · **本回合不实现** · **无 CNINFO** · **无 live**

**目标文件：** `lab/run_cninfo_a_class_phase2_metadata_expansion.py`（扩展现有 runner · 新 Phase 3 模式）

---

## 1. 当前 Runner 缺口

| 能力 | 现状 | Phase 3 需要 |
|------|------|-------------|
| expansion mode | Phase 2 default（20 case） | `--phase3-50` |
| approval flag | Phase 2 / retry flags only | `--approve-a-class-phase3-50-company-expansion` |
| output root | expansion / retry / retry_v2 / retry_v3 / precheck | `cninfo_a_class_phase3_50_company_expansion/` |
| universe CSV | `phase2_include` · 20 rows | `phase3_include` · **50** rows |
| overlap guard | Phase 1 only | Phase 1 + Phase 2 effective 20 |

---

## 2. Required CLI Flags

```python
parser.add_argument(
    "--phase3-50",
    action="store_true",
    help="Phase 3 50-company metadata expansion 模式",
)
parser.add_argument(
    "--approve-a-class-phase3-50-company-expansion",
    action="store_true",
    help="显式批准 A-class Phase 3 50-company live expansion",
)
```

**常量：**

```python
PHASE3_APPROVAL_REQUIRED = "approve_a_class_phase3_50_company_expansion_required"
PHASE3_WRONG_APPROVAL = "approve_a_class_phase3_50_company_expansion_wrong_flag"
DEFAULT_PHASE3_OUTPUT_ROOT = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_phase3_50_company_expansion"
)
DEFAULT_PHASE3_UNIVERSE_CSV = os.path.join(
    BASE_DIR, "outputs", "validation", "cninfo_a_class_phase3_50_company_universe_draft.csv"
)
PHASE3_REQUIRED_UNIVERSE_SIZE = 50
PHASE3_ACCEPTABLE_THRESHOLD = 40  # 规划：≥40/50 → PASS_WITH_CAVEAT；<40 → FAIL_REVIEW_REQUIRED
PHASE1_EXCLUDED_CODES = {"600000", "300001", "688001", "000858", "600519"}
PHASE2_EXCLUDED_CODES = {
    "600036", "601318", "000333", "002415", "601012", "600276", "000002", "601888",
    "300014", "300750", "600887", "601166", "688599", "688036", "000725", "601899",
    "300059", "688111", "600309", "002594",
}
```

---

## 3. Phase 3 Universe Loader

**必需列：** `case_id` · `company_code` · `company_name` · `market` · `report_type` · `expected_period` · `expected_title_keywords` · `excluded_title_keywords` · `phase3_include` · `risk_level`

**可选列：** `phase1_overlap` · `phase2_overlap` · `reason`

**校验：**

1. universe size = **50**
2. `phase3_include=yes` 行数 = **50**
3. case_ids = A3M001–A3M050（连续无缺口）
4. case_ids ∩ Phase2 case_ids（A2M*）= ∅
5. company_codes ∩ PHASE1_EXCLUDED_CODES = ∅
6. company_codes ∩ PHASE2_EXCLUDED_CODES = ∅
7. company_codes 无重复
8. `report_type` / `expected_period` 与 bucket 设计一致
9. `validate_universe_code_name()` code↔name 一致性

---

## 4. Write-block Guards

Phase 3 模式须 **禁止写入** 以下根：

```python
PHASE3_WRITE_BLOCKED_ROOTS = [
    "cninfo_a_class_tiny_live_metadata",
    "cninfo_a_class_phase2_metadata_expansion",
    "cninfo_a_class_phase2_metadata_retry",
    "cninfo_a_class_phase2_metadata_retry_v2",
    "cninfo_a_class_phase2_metadata_retry_v3",
    "cninfo_a_class_phase2_cninfo_reachability_precheck",
    "outputs/harvest",
]
```

Dry-run 与 live 均须校验 output_root 不在 blocked list。

---

## 5. Mode Detection Priority

建议 mode 检测顺序（高优先级覆盖低优先级）：

1. `--retry-v3` → retry v3 isolated
2. `--retry-v2` → retry v2 isolated
3. `--retry-failed-only` → retry v1
4. `--phase3-50` → Phase 3 expansion
5. default → Phase 2 expansion

**Phase 3 与 retry 模式互斥。**

---

## 6. Dry-run Path

| 步骤 | 行为 |
|------|------|
| load universe | 50 rows · phase3_include=yes |
| overlap check | Phase 1 + Phase 2 codes = ∅ |
| code/name validate | registry 一致性 |
| report-type mix | 20/10/10/10 |
| output root check | isolated |
| write-blocks | PDF/OCR/DB/MinIO/RAG = blocked |
| CNINFO calls | **0** |
| output | dryrun_report.csv · dryrun_summary.md |

---

## 7. Live Path（未来实现 · NOT APPROVED）

| 步骤 | 行为 |
|------|------|
| approval guard | `--phase3-50` + `--live` 须 `--approve-a-class-phase3-50-company-expansion` |
| per-case | orgId resolve → announcement query → title/period match → lineage record |
| PDF | **never download** |
| rate limit | sleep 0.6s · concurrency 1 |
| output | report.csv · summary.md · quality_report.csv · raw_metadata/*.json |

**execution gate 规划：**

```text
≥40/50 acceptable → a_class_phase3_50_company_execution_gate = PASS_WITH_CAVEAT
<40/50 acceptable → a_class_phase3_50_company_execution_gate = FAIL_REVIEW_REQUIRED
```

**永不使用 bare PASS。**

---

## 8. Test Plan（未来回合）

新增 `lab/test_cninfo_a_class_phase3_50_company_runner.py`：

| 测试类 | 覆盖 |
|--------|------|
| dry_run_calls_cninfo_zero_times | CNINFO=0 |
| universe_size_must_equal_50 | 50 rows |
| phase1_overlap_rejected | Phase 1 codes blocked |
| phase2_overlap_rejected | Phase 2 codes blocked |
| output_root_isolation_enforced | write-block |
| pdf_download_blocked | PDF=0 |
| db_minio_rag_blocked | 0 |
| verified_production_ready_blocked | false |
| wrong_approval_flag_rejected | guard |
| live_requires_approval_flag | guard |

**本回合不创建测试文件。**

---

## 9. Gate（本回合）

```text
a_class_phase3_50_company_planning_gate = READY_FOR_APPROVAL
a_class_phase3_50_company_runner_extension_gate = NOT_STARTED
```

**不是 PASS。** **不是 live_ready。** **不是 verified。**
