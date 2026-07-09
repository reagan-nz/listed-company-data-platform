# CNINFO D 类 Tiny Live V2 Bounded Probe — Command Draft

_生成时间：2026-07-09_

> **状态：NOT APPROVED** — 未来命令草案 only；**本回合不执行**

---

## 1. Purpose

在未来用户显式批准后，对 **DLC003** · **DLC006** 执行有界 probe 扩展（Option B），输出隔离至 v2 根目录，并生成 v1 vs v2 对照报告。

---

## 2. Prerequisites

- [ ] `d_class_phase1_boundary_gate = PASS_WITH_CAVEAT` 已评审
- [ ] `d_class_dlc003_dlc006_calibration_gate = READY_FOR_HUMAN_DECISION` 已评审
- [ ] [bounded probe design](cninfo_d_class_dlc003_dlc006_bounded_probe_extension_design.md) 已批准
- [ ] [probe matrix](../outputs/validation/cninfo_d_class_dlc003_dlc006_bounded_probe_matrix.csv) 请求上限已批准
- [ ] [approval checklist](../outputs/validation/cninfo_d_class_tiny_live_v2_bounded_probe_approval_checklist.md) 全部勾选
- [ ] runner v2 修改已落地（见 [modification plan](cninfo_d_class_tiny_live_v2_runner_modification_plan.md)）
- [ ] universe v2 中 `*_CANDIDATE_REQUIRED` 行 **仍 skip**（不发明公司代码）

---

## 3. Output Root（隔离）

```text
outputs/validation/cninfo_d_class_tiny_live_validation_v2/
```

**禁止写入：**

```text
outputs/validation/cninfo_d_class_tiny_live_validation/   # v1 只读
```

---

## 4. Universe

```text
outputs/validation/cninfo_d_class_phase1_tiny_live_universe_v2_draft.csv
```

| 规则 | 说明 |
|------|------|
| DLC003 | 使用 v1 公司 **300009**（直至人工填入 replacement） |
| DLC006 | 使用 v1 公司 **000550**（直至人工填入 replacement） |
| `*_CANDIDATE_REQUIRED` | **skip** · 不请求 CNINFO |
| DLC001/002/004/005/007 | baseline 对照 · **v2 不新增 CNINFO** |

---

## 5. Approval Flag（占位）

```text
--approve-d-class-tiny-live-v2-bounded-probe
```

无此 flag → runner **拒绝 live**。

---

## 6. Proposed Command（NOT APPROVED）

```bash
cd listed_company_data_collector

python lab/run_cninfo_d_class_tiny_live_validation.py \
  --live \
  --bounded-probe-v2 \
  --universe outputs/validation/cninfo_d_class_phase1_tiny_live_universe_v2_draft.csv \
  --output-root outputs/validation/cninfo_d_class_tiny_live_validation_v2/ \
  --approve-d-class-tiny-live-v2-bounded-probe \
  --dlc003-max-requests 24 \
  --dlc006-max-requests 20 \
  --cases DLC003,DLC006
```

> **注：** `--bounded-probe-v2` · `--dlc003-max-requests` · `--dlc006-max-requests` · `--cases` 为 runner 修改计划中的 **未来参数**；当前 runner **尚未实现**。

---

## 7. Dry-run Command（未来 · NOT APPROVED）

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --bounded-probe-v2 \
  --universe outputs/validation/cninfo_d_class_phase1_tiny_live_universe_v2_draft.csv \
  --output-root outputs/validation/cninfo_d_class_tiny_live_validation_v2/ \
  --cases DLC003,DLC006
```

预期：`cninfo_calls=0` · 输出 planned probe matrix 至 v2 dry-run 报告。

---

## 8. Expected Outputs（v2）

| 文件 | 说明 |
|------|------|
| `reports/d_class_tiny_live_v2_report.csv` | v2 执行行 |
| `reports/d_class_tiny_live_v2_comparison_report.csv` | v1 vs v2 对照 |
| `reports/d_class_tiny_live_v2_summary.md` | 摘要 |
| `reports/d_class_tiny_live_v2_quality_report.csv` | 质量行 |
| `live_snapshots/DLC003_restricted_shares_unlock.json` | DLC003 快照 |
| `live_snapshots/DLC006_shareholder_change.json` | DLC006 快照 |

---

## 9. Request Budget（设计值）

| case | cap |
|------|-----|
| DLC003 | **24** |
| DLC006 | **20** |
| **合计** | **≤44** |

---

## 10. Explicit Exclusions

| 项 | 值 |
|----|-----|
| DB write | **no** |
| MinIO write | **no** |
| RAG run | **no** |
| verified | **no** |
| production_ready | **no** |
| testing_stable_sample upgrade | **no** |
| harvest | **no** |
| v1 report mutation | **no** |
| invented company codes | **no** |

---

## 11. Gate

```text
d_class_tiny_live_v2_bounded_probe_design_gate = READY_FOR_APPROVAL
```

**NOT APPROVED** · **NOT live_ready** · **NOT verified** · **NOT production_ready**
