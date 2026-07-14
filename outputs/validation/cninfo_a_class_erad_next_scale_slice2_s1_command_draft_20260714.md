# CNINFO A 类 Next-Scale Slice2 S1 +100 — Command Draft

_生成时间：2026-07-14 · task **A-GEN-20260714-10** · **DO NOT RUN** · **CNINFO = 0** · **NOT APPROVED for live**

> **性质：** 未来 slice2 S1 +100 dry-run / live 命令草案。**本回合不执行** · dry-run / live 均 **未运行**

**前置：** [live prep package](cninfo_a_class_erad_next_scale_slice2_s1_live_prep_package_20260714.md) · [cohort freeze note](cninfo_a_class_erad_next_scale_slice2_s1_cohort_freeze_note_20260714.md) · [lint check](cninfo_a_class_erad_next_scale_slice2_s1_plus100_lint_check_20260714.md) · [precheck checklist](cninfo_a_class_erad_next_scale_slice2_s1_live_precheck_20260714.csv)

---

## 1. Scope

| 项 | 值 |
|----|-----|
| task_id | **A-GEN-20260714-10**（prep）· cohort freeze **A-GEN-20260714-09** |
| cohort | `next_scale_slice2` · **S1 +100 non-ST** |
| case_id | **AD2E501** – **AD2E600**（**100**） |
| universe | [cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv](cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv) |
| ST 策略 | **S1 ST-EXCLUDE** · L-D4 **0**/100 |
| mode | **fresh_metadata only** · matching_logic **v2** |
| CNINFO calls（本回合） | **0** |
| CNINFO cap（future live） | **≤240** |

---

## 2. Runner Status

| 项 | 状态 |
|----|------|
| runner 文件 | `lab/run_cninfo_a_class_phase2_metadata_expansion.py` |
| slice1 flag（已实现） | `--erad-a-scale-500-slice1` |
| **slice2 flag（规划 · 未实现）** | `--erad-a-scale-500-slice2` |
| **slice2 approval flag（规划 · 未实现）** | `--approve-a-class-erad-scale-500-slice2` |
| slice1 参照 | [slice1 runner extension summary](cninfo_a_class_erad_next_scale_slice1_runner_extension_summary.md) |
| 命名备选 | [offline prep §P4](cninfo_a_class_next_scale_slice2_offline_prep_20260714.md) 曾记 `--erad-a-next-scale-slice2`（待定） |

> **阻塞：** slice2 runner extension **须 separate task** 完成后方可执行下列 dry-run。本草案按 slice1 同型 runner 规划命令形状。

---

## 3. Output Isolation

```text
outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1/
├── raw_metadata/
├── reports/
│   ├── session1/                    # AD2E501–550（若分 session）
│   ├── session2/                    # AD2E551–600
│   ├── a_class_erad_next_scale_slice2_s1_dryrun_report.csv
│   ├── a_class_erad_next_scale_slice2_s1_dryrun_summary.md
│   ├── a_class_erad_next_scale_slice2_s1_live_report.csv
│   ├── a_class_erad_next_scale_slice2_s1_live_quality_report.csv
│   └── a_class_erad_next_scale_slice2_s1_live_summary.md
└── ledgers/
```

**禁止写入（write-block）：**

- `outputs/validation/cninfo_a_class_erad_scale_200/`
- `outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/`
- `outputs/validation/cninfo_a_class_erad_next_scale_slice1/`（slice1 主根 · 294/300 effective）
- Phase 3 / A3M017 production roots
- [182 台账](cninfo_a_class_slice2_ab_overlap_182_ledger_20260714.csv) · [remainder draft](cninfo_a_class_slice2_pool_remainder_draft_20260714.csv) · 旧 S4/+50 draft
- B / C / D validation / harvest / snapshot production roots

---

## 4. Flags（规划 · 复用 slice1 runner 同型）

| Flag | 说明 |
|------|------|
| `--erad-a-scale-500-slice2` | slice2 S1 +100 模式（**未实现**） |
| `--approve-a-class-erad-scale-500-slice2` | live 人批 gate（**未实现** · dry-run 不需要） |
| `--universe-csv` | 指向 S1 +100 candidate universe CSV |
| `--output-root` | 隔离 slice2 S1 根（见上） |
| `--case-range AD2E501:AD2E600` | 全 cohort 范围 |
| `--dry-run` | 规划模式 · CNINFO **0** |
| `--live` | live 模式（**须 separate approval**） |

---

## 5. Dry-Run Shape（CNINFO = 0 · NOT EXECUTED）

**前置：** runner extension 完成 · precheck PC-S2S1-009 全绿前不得 live。

```bash
cd /Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector

python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --erad-a-scale-500-slice2 \
  --universe-csv outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv \
  --output-root outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1/ \
  --dry-run
```

**期望：** **100/100** `planned_ok` · planned_request_count_total **~210** · cap **≤240** · CNINFO **0**

**测试（runner extension 完成后）：**

```bash
python lab/test_cninfo_a_class_erad_next_scale_slice2_runner.py
python lab/test_cninfo_a_class_erad_next_scale_slice2_live_path.py
```

> **注：** 测试文件名按 slice1 同型规划；实际文件名以 runner extension task 交付为准。

---

## 6. Live Shape（DO NOT RUN · Separate Approval）

**须同时满足：**

- post-integration HOLD 解除（PC-S2S1-005）
- runner extension 实现 + tests PASS（PC-S2S1-008）
- dry-run **100/100** planned_ok（PC-S2S1-009）
- [precheck checklist](cninfo_a_class_erad_next_scale_slice2_s1_live_precheck_20260714.csv) 全 `ready`（required_before_live=yes）
- human slice2 live 批准短语（PC-S2S1-006）
- controller approval queue 含 slice2 live 条目（PC-S2S1-007）

**批准短语（示意 · 未消费）：**

```text
I approve A-class Era D next-scale slice2 S1 +100 live metadata validation.
```

### 6.1 Full Cohort（100 cases）

```bash
cd /Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector

python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --erad-a-scale-500-slice2 \
  --approve-a-class-erad-scale-500-slice2 \
  --universe-csv outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv \
  --output-root outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1/ \
  --live
```

### 6.2 Session Split（推荐 · 2×50）

```bash
# Session 1 — cases AD2E501–550（50）
python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --erad-a-scale-500-slice2 \
  --approve-a-class-erad-scale-500-slice2 \
  --universe-csv outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv \
  --output-root outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1/ \
  --live \
  --case-range AD2E501:AD2E550

# Session 2 — cases AD2E551–600（50）
python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --erad-a-scale-500-slice2 \
  --approve-a-class-erad-scale-500-slice2 \
  --universe-csv outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_plus100_candidate_universe_20260714.csv \
  --output-root outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1/ \
  --live \
  --case-range AD2E551:AD2E600
```

---

## 7. Rate Limit & Cap

| 项 | 值 |
|----|-----|
| universe | 100/100 |
| est. CNINFO / case | ~2.1 |
| max CNINFO requests | **≤240** |
| 单日 cases | **≤100** |
| inter-request sleep | **≥1.0s** |
| burst retry | **禁止** |
| 跨 session 连打 | 建议 **≥4h** 间隔 |

---

## 8. Expected Outcomes（live 后验收）

引用 [live prep package §7](cninfo_a_class_erad_next_scale_slice2_s1_live_prep_package_20260714.md)：

| 结果 | execution gate |
|------|----------------|
| **≥90/100** acceptable | **`PASS_WITH_CAVEAT`** |
| **<90/100** acceptable | **`FAIL_REVIEW_REQUIRED`** |
| bare PASS | **永不宣称** |

**Unresolved 政策：** 新 unresolved 记入 slice2 ledger · 不重跑 scale-200 **8** · slice1 **6** · **不 offline force-resolve**。

**永不：** `verified` · PDF 落盘 · 182/remainder/旧 draft mutate · slice1 主根 overwrite

---

## 9. Red Lines

- **不得** rerun AD2E001–500（lineage-reference only）
- **不得**写入 scale-200 · slice1 · failed_retry · Phase 3 / A3M017 生产根
- **不得** mutate [182 台账](cninfo_a_class_slice2_ab_overlap_182_ledger_20260714.csv) · [remainder](cninfo_a_class_slice2_pool_remainder_draft_20260714.csv) · superseded draft
- **无** PDF / DB / MinIO / RAG / verified
- mock 输出仅 `_mock_*` 子目录

---

## 10. Gates（当前）

```text
a_class_erad_next_scale_slice2_s1_runner_extension_gate = NOT_IMPLEMENTED
a_class_erad_next_scale_slice2_s1_dryrun_gate = NOT_APPLICABLE
a_class_erad_next_scale_slice2_s1_live_gate = NOT_APPROVED
a_class_erad_next_scale_slice2_s1_execution_gate = NOT_APPLICABLE
```

**CNINFO = 0**（本规划任务 · 命令未执行）
