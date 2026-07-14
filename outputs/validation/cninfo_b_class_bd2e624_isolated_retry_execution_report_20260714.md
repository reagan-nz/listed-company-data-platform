# CNINFO B 类 BD2E624 — Isolated Retry Execution Report

_生成时间：2026-07-14 · task **B-GEN-20260714-07** · human approval **AQ-B-BD2E624** · **CNINFO = 0** · **live NOT executed**_

> **性质：** isolated retry 执行验收包 · dry-run **BLOCKED** · live **未执行** · slice2 主根 **未 mutate**

**前置：** [command draft](cninfo_b_class_bd2e624_isolated_retry_command_draft_20260714.md) · [validation rules](cninfo_b_class_bd2e624_offline_validation_rules_20260714.md) · [precheck post-execution](cninfo_b_class_bd2e624_isolated_retry_precheck_post_execution_20260714.csv)

---

## 1. Scope

| 项 | 值 |
|----|-----|
| task_id | **B-GEN-20260714-07** |
| case_id | **BD2E624** only（300778 · 新城市） |
| cohort | `fuller_next_slice2` |
| baseline retrieval_status | `network_error`（EP002 orgId resolution failed） |
| approval | AQ-B-BD2E624 · bounded · isolated 1/1 · CNINFO cap ≤2 |
| CNINFO calls（本包） | **0** |
| live 状态 | **NOT executed** |

---

## 2. Draft Command Dry-Run（按 command draft 原样）

**命令：**

```bash
cd /Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector

python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --erad-b-fuller-slice2 \
  --universe-csv outputs/validation/cninfo_b_class_bd2e624_isolated_retry_universe_20260714.csv \
  --output-root outputs/validation/cninfo_b_class_erad_fuller_next_slice2_bd2e624_retry/ \
  --case-range BD2E624:BD2E624 \
  --dry-run
```

| 指标 | 值 |
|------|-----|
| exit code | **2** |
| planned_ok | **0/1**（未进入 dry-run 流程） |
| CNINFO calls | **0** |
| blocker | `erad_b_fuller_slice2_universe_csv_required` |

**stderr（关键行）：**

```text
ERROR: erad_b_fuller_slice2_universe_csv_required
```

**根因：** `--erad-b-fuller-slice2` 模式要求 universe CSV 路径 **必须等于** canonical 300-case 文件（`cninfo_b_class_erad_fuller_next_slice_candidate_universe_draft.csv`）；isolated 1-case universe 被拒绝。

---

## 3. 补充探测（诊断 only · 非 draft 原样）

为确认 `case-range` 与 planned request 估算，在 **mock test 子目录** 下做补充探测（**非** isolated retry 官方输出根）：

**命令：**

```bash
python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --erad-b-fuller-slice2 \
  --universe-csv outputs/validation/cninfo_b_class_erad_fuller_next_slice_candidate_universe_draft.csv \
  --output-root outputs/validation/cninfo_b_class_erad_fuller_next_slice2/_mock_test/bd2e624_isolated_probe \
  --case-range BD2E624:BD2E624 \
  --dry-run
```

| 指标 | 值 |
|------|-----|
| exit code | **0** |
| planned_ok | **1/1** |
| planned_request_count_total | **2** |
| CNINFO calls | **0** |
| gate | `b_class_erad_fuller_next_slice_runner_extension_gate=READY_FOR_APPROVAL` |

**第二 blocker（isolated output root）：** 当使用 canonical universe 但 `--output-root` 指向 `cninfo_b_class_erad_fuller_next_slice2_bd2e624_retry/` 时：

```text
ERROR: output_root_must_be_under_cninfo_b_class_erad_fuller_next_slice2
```

**结论：** 当前 runner **不支持** command draft 所要求的 isolated universe + isolated output root 组合；须 separate runner extension（见 [runner extension note](cninfo_b_class_bd2e624_isolated_retry_runner_extension_note_20260714.md)）。

---

## 4. Live（NOT executed）

| 项 | 值 |
|----|-----|
| live 执行 | **否** |
| 原因 | draft dry-run **未通过**（PC-BD2E-013 blocked）；runner 缺 isolated-retry 扩展 |
| CNINFO calls | **0** |
| retrieval_status（本包） | **未变更** · baseline 保持 `network_error` |

**红线遵守：**

- slice2 主 report/quality/merge closure：**未写入**
- isolated 官方输出根 `cninfo_b_class_erad_fuller_next_slice2_bd2e624_retry/`：**未创建**
- PDF / OCR / DB / MinIO / RAG：**未触发**
- push：**未执行**

---

## 5. Baseline 保留

| 工件 | 状态 |
|------|------|
| slice2 主 live report row BD2E624 | **只读保留** · `network_error` |
| quality/BD2E624.json | **只读保留** · `needs_review` |
| merge closure gate | **PASS_WITH_CAVEAT** · 299/300 acceptable · **未变更** |
| unresolved ledger | BD2E624 **deferred** · **未 offline force-resolve** |

---

## 6. Gate Verdict

```text
task_id = B-GEN-20260714-07
bd2e624_isolated_retry_dryrun_gate = FAIL_BLOCKER
bd2e624_isolated_retry_live_gate = NOT_EXECUTED
bd2e624_isolated_retry_execution_gate = DEFERRED_RUNNER_EXTENSION
slice2_main_gate = PASS_WITH_CAVEAT（保持）
cninfo_calls_this_package = 0
retrieval_status = network_error（baseline 保持）
```

**分类：** dry-run blocker → **DEFERRED_RUNNER_EXTENSION**；**非** live 后 `FAIL_REVIEW_REQUIRED`（因 live 未执行）。

**下一步：** separate runner extension task → 允许 isolated universe CSV + isolated output root + per-case CNINFO cap ≤2 → 重跑 draft dry-run → human live phrase → bounded live。

---

## 7. 工件清单

| 工件 | 路径 |
|------|------|
| execution report（本文件） | `cninfo_b_class_bd2e624_isolated_retry_execution_report_20260714.md` |
| runner extension note | `cninfo_b_class_bd2e624_isolated_retry_runner_extension_note_20260714.md` |
| precheck post-execution | `cninfo_b_class_bd2e624_isolated_retry_precheck_post_execution_20260714.csv` |
| diagnostic probe（非官方 isolated 根） | `cninfo_b_class_erad_fuller_next_slice2/_mock_test/bd2e624_isolated_probe/` |

**NOT committed** · **NOT pushed**
