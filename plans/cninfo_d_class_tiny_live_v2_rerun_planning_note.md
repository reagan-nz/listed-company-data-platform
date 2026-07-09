# CNINFO D 类 Tiny Live v2 Rerun — Planning Note

_生成时间：2026-07-09_

> **性质：** 未来 rerun 规划 only · **NOT APPROVED** · **无 CNINFO** · **无 rerun 执行**

---

## 1. Status

| 项 | 值 |
|----|-----|
| v1 execution gate | `d_class_tiny_live_execution_gate = PASS_WITH_CAVEAT` |
| v1 closure gate | `d_class_phase1_tiny_live_closure_gate = PASS_WITH_CAVEAT` |
| calibration gate | `d_class_dlc003_dlc006_calibration_gate = READY_FOR_HUMAN_DECISION` |
| v2 rerun | **NOT APPROVED** |

---

## 2. Prerequisites（人工决策后方可申请 v2 rerun）

v2 rerun **不得**在以下任一未完成时启动：

1. 人工对 DLC003 选择 **Option B 和/或 C**（见 [decision matrix](../outputs/validation/cninfo_d_class_dlc003_dlc006_calibration_decision_matrix.csv)）
2. 人工对 DLC006 选择 **Option B 和/或 C**
3. 若选 **C**：在 [universe v2 draft](../outputs/validation/cninfo_d_class_phase1_tiny_live_universe_v2_draft.csv) 中填入 **人工确认** 的公司代码（**禁止**自动发明）
4. 若选 **B**：批准 bounded probe 扩展上限（最大 tdate 数 · 最大 mode 组合数）
5. 显式批准 v2 rerun flag（见 §5）

**不推荐立即 Option A**（reclassify to empty_but_valid）作为 v2 前置——组件需先获得 captured_normal 证据。

---

## 3. Output Isolation

### v1（冻结 · 不覆盖）

```text
outputs/validation/cninfo_d_class_tiny_live_validation/
```

- v1 `d_class_tiny_live_report.csv` · snapshots · summaries **只读保留**
- v2 rerun **不得** overwrite v1 产物

### v2（提议）

```text
outputs/validation/cninfo_d_class_tiny_live_validation_v2/
  reports/
    d_class_tiny_live_v2_report.csv
    d_class_tiny_live_v2_summary.md
    d_class_tiny_live_v2_quality_report.csv
  live_snapshots/
  run_status.csv
```

---

## 4. Scope（v2 草案）

| 项 | 内容 |
|----|------|
| universe | [cninfo_d_class_phase1_tiny_live_universe_v2_draft.csv](../outputs/validation/cninfo_d_class_phase1_tiny_live_universe_v2_draft.csv) |
| size | **7** cases |
| unchanged | DLC001 · DLC002 · DLC004 · DLC005 · DLC007 |
| pending | DLC003_V2_CANDIDATE_REQUIRED · DLC006_V2_CANDIDATE_REQUIRED |
| 允许 | metadata/event probe only |
| 禁止 | harvest · DB · MinIO · RAG · verified · production_ready |

---

## 5. Approval Flag（未来 · NOT APPROVED）

```bash
# NOT APPROVED — 示例草案 only

python lab/run_cninfo_d_class_tiny_live_validation.py \
  --live \
  --universe-csv outputs/validation/cninfo_d_class_phase1_tiny_live_universe_v2_draft.csv \
  --output-root outputs/validation/cninfo_d_class_tiny_live_validation_v2/ \
  --approve-d-class-tiny-live-v2-validation
```

| 项 | 值 |
|----|-----|
| approval flag | `--approve-d-class-tiny-live-v2-validation` |
| runner 扩展 | **未实现**（规划名；须与 v1 flag 区分） |
| 状态 | **NOT APPROVED** |

---

## 6. Option B — Bounded Probe Extension（规划）

### DLC003（restricted_shares_unlock）

- 在 v1 **8** tdate 基础上，批准包可定义额外 tdate 上限（例如 +12，总 cap 20）
- 仍须 `sleep_seconds >= 0.6` · 并发 = 1
- 若仍空 → 不自动降为 empty_but_valid；转 Option C

### DLC006（shareholder_change）

- 扩展 inc/desc × tdate 组合，设 **max_probe_combinations**（例如 10）
- 优先 inc 近期窗口，再 desc 无 tdate
- 若仍空 → 转 Option C

---

## 7. Option C — Replacement Case（规划）

- 人工提供 company_code · company_name · 事件依据（公告日期/解禁日等 **离线文档**）
- 更新 universe v2 draft 中 placeholder 行
- `expected_behavior` 保持 `captured_normal`
- v2 rerun 仅替换 DLC003/DLC006 探针，其余 5 case 可 skip（run_status 标记 completed_from_v1）

---

## 8. Gate（v2 rerun · 未来）

```text
d_class_tiny_live_v2_validation_gate = NOT_APPROVED
```

执行完成后目标 gate（规划）：

```text
d_class_tiny_live_v2_execution_gate = PASS_WITH_CAVEAT  # 仍不是 PASS
```

---

## 9. Red Lines

- No CNINFO in this planning round
- No live · No rerun · No harvest
- No invented company codes · No web lookup
- No overwrite of v1 outputs
- No verified · No production_ready · No testing_stable_sample upgrade
