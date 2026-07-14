# CNINFO B 类 BD2E624 — Isolated Retry Command Draft

_生成时间：2026-07-14 · task **B-GEN-20260714-06** · **DO NOT RUN** · **CNINFO = 0** · **NOT APPROVED for live**

> **性质：** 未来 BD2E624 isolated retry 命令草案。**本回合不执行** · dry-run / live 均 **未运行**

**前置：** [retry plan](cninfo_b_class_bd2e624_isolated_retry_plan_20260714.md) · [validation rules](cninfo_b_class_bd2e624_offline_validation_rules_20260714.md) · [precheck checklist](cninfo_b_class_bd2e624_offline_precheck_checklist_20260714.csv)

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`（无变更）

---

## 1. Scope

| 项 | 值 |
|----|-----|
| task_id | **B-GEN-20260714-06** |
| case_id | **BD2E624** only |
| company_code | **300778**（新城市） |
| cohort | `fuller_next_slice2` |
| universe | [cninfo_b_class_bd2e624_isolated_retry_universe_20260714.csv](cninfo_b_class_bd2e624_isolated_retry_universe_20260714.csv)（**1/1**） |
| endpoint chain | **EP002 → EP001**（orgId 解析 → EP004/EP005） |
| baseline failure | `network_error` · EP002 orgId resolution failed |
| CNINFO calls（本回合） | **0** |
| CNINFO cap（live） | **≤ 2** |

---

## 2. Output Isolation

```text
outputs/validation/cninfo_b_class_erad_fuller_next_slice2_bd2e624_retry/
├── raw_metadata/
├── quality/
│   └── BD2E624.json
└── reports/
    ├── b_class_erad_fuller_next_slice2_bd2e624_retry_report.csv
    ├── b_class_erad_fuller_next_slice2_bd2e624_retry_quality_report.csv
    └── b_class_erad_fuller_next_slice2_bd2e624_retry_summary.md
```

**禁止写入（write-block）：**

- `outputs/validation/cninfo_b_class_erad_fuller_next_slice2/`（slice2 主根 · 失败证据只读保留）
- `outputs/validation/cninfo_b_class_erad_scale_200/`
- `outputs/validation/cninfo_b_class_erad_next_scale_slice1/`
- `outputs/validation/cninfo_b_class_phase3_100_*`
- A/C/D validation / harvest / snapshot production roots

---

## 3. Flags（复用 fuller slice2 runner）

| Flag | 说明 |
|------|------|
| `--erad-b-fuller-slice2` | fuller next-slice2 模式 |
| `--approve-b-class-erad-fuller-slice2` | live 人批 gate（dry-run 不需要） |
| `--universe-csv` | 指向 isolated 1-case universe CSV |
| `--output-root` | 隔离 retry 根（见上） |
| `--case-range BD2E624:BD2E624` | 单 case 范围 |
| `--live` | live 模式（**须 separate approval**） |

> **注：** 若 runner 需专用 isolated-retry flag，须 separate runner extension task；当前草案复用 `--erad-b-fuller-slice2` + isolated universe + case-range。

---

## 4. Dry-Run Shape（CNINFO = 0 · NOT EXECUTED）

**前置：** PC-BD2E-013 全绿前不得 live。

```bash
cd /Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector

python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --erad-b-fuller-slice2 \
  --universe-csv outputs/validation/cninfo_b_class_bd2e624_isolated_retry_universe_20260714.csv \
  --output-root outputs/validation/cninfo_b_class_erad_fuller_next_slice2_bd2e624_retry/ \
  --case-range BD2E624:BD2E624 \
  --dry-run
```

**期望：** 1/1 `planned_ok` · planned requests **≤ 2** · CNINFO **0**

**测试（若 runner 扩展）：**

```bash
python lab/test_cninfo_b_class_erad_fuller_next_slice2_runner.py
python lab/test_cninfo_b_class_erad_fuller_next_slice2_live_path.py
```

---

## 5. Live Shape（DO NOT RUN · Separate Approval）

**须同时满足：**

- post-integration HOLD 解除（PC-BD2E-005）
- human live 执行短语（PC-BD2E-006）
- controller approval queue 含 retry 条目（PC-BD2E-007）
- dry-run 1/1 planned_ok（PC-BD2E-013）
- precheck status 全 `ready`（required_before_retry=yes）

**批准短语（示意）：**

```text
I approve B-class BD2E624 isolated retry live metadata validation.
```

```bash
cd /Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector

python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --erad-b-fuller-slice2 \
  --approve-b-class-erad-fuller-slice2 \
  --universe-csv outputs/validation/cninfo_b_class_bd2e624_isolated_retry_universe_20260714.csv \
  --output-root outputs/validation/cninfo_b_class_erad_fuller_next_slice2_bd2e624_retry/ \
  --case-range BD2E624:BD2E624 \
  --live
```

---

## 6. Rate Limit & Cap

| 项 | 值 |
|----|-----|
| universe | 1/1 |
| endpoint chain | EP002 + EP001 |
| max CNINFO requests | **≤ 2** |
| burst retry | **禁止** |
| 不同 session 连打 | **禁止** |

---

## 7. Expected Outcomes（live 后验收）

引用 [validation rules §3](cninfo_b_class_bd2e624_offline_validation_rules_20260714.md)：

| 结果 | retry execution gate | slice2 主 gate |
|------|---------------------|----------------|
| `found` | **PASS_WITH_CAVEAT** | 保持 PASS_WITH_CAVEAT（至 separate merge closure） |
| `empty_response` | **PASS_WITH_CAVEAT**（ER-VAL 子类） | 同上 |
| `network_error` | **FAIL_REVIEW_REQUIRED** | **保持** PASS_WITH_CAVEAT · BD2E624 仍 deferred |

**Misclassification guard：** 验收时核对 VR-MIS-01..05 · 不得将 network_error 标为 empty_response。

**永不：** `verified` · PDF 落盘 · slice2 主根 mutate

---

## 8. Gate

```text
task_id = B-GEN-20260714-06
b_class_bd2e624_isolated_retry_command_draft_gate = READY_FOR_DRYRUN
b_class_bd2e624_isolated_retry_live_gate = NOT_APPROVED
cninfo_calls_this_package = 0
```

**NOT EXECUTED** · **NOT committed** · **NOT pushed**

---

## 9. Red Lines

- No CNINFO in this planning round
- No retry execution in this planning round
- No slice2 main harvest root mutation
- No retroactive merge closure edit
- No PDF · No OCR · No DB · No MinIO · No RAG · No verified
- No mixing with 16-case ER-VAL requery batch
