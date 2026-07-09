# CNINFO D 类 DLC003 / DLC006 Calibration Application Summary

_生成时间：2026-07-09_

> **性质：** Option A 人工 signoff 应用摘要 · **无 CNINFO** · **不是 verified** · **不是 production_ready**

---

## 1. Changes Applied

| case | company | component | original | new |
|------|---------|-----------|----------|-----|
| DLC003 | 300009 安科生物 | restricted_shares_unlock | `captured_normal` | **`empty_but_valid`** |
| DLC006 | 000550 江铃汽车 | shareholder_change | `captured_normal` | **`empty_but_valid`** |

**输出文件：** [cninfo_d_class_phase1_tiny_live_universe_calibrated.csv](cninfo_d_class_phase1_tiny_live_universe_calibrated.csv)

**未修改：** [cninfo_d_class_phase1_tiny_live_universe.csv](cninfo_d_class_phase1_tiny_live_universe.csv)（v1 原始 universe 保持只读）

---

## 2. Why This Is Safe for Current Tiny-live Universe

| 理由 | 说明 |
|------|------|
| 证据一致 | v1 **与** v2 bounded probes 均观测 `empty_but_valid` · 0 company rows |
| 探测充分 | DLC003 **29** total probes · DLC006 **24** total · caps 内穷尽 |
| 非 schema 问题 | API 可用 · quality `pass` · `schema_failure=false` |
| 范围限定 | 仅调整 **这两家公司** 的预期 · 其他 5 case **不变** |
| 无生产声明 | 不构成 verified / production_ready |

校准后 tiny-live universe **7/7 acceptable** 口径可对齐（DLC003/DLC006 mismatch 消除）。

---

## 3. Why This Does Not Prove Component-Level captured_normal Coverage

| 局限 | 说明 |
|------|------|
| 组件样本 | `restricted_shares_unlock` · `shareholder_change` **仍无** tiny-live `captured_normal` 命中 |
| 公司特异性 | 仅证明 300009 / 000550 在 bounded 窗口内稳定空态 |
| 全局数据 | **不证明**组件无数据或 API 无 captured 路径 |
| mapper 回归 | captured 路径 live 证据 **仍缺** |

---

## 4. Why Future Replacement Cases Are Still Needed

**Option C** 仍为推荐下一任务：

- 人工选定 **已知解禁事件** 公司（DLC003 replacement）
- 人工选定 **已知增减持事件** 公司（DLC006 replacement）
- 保留 `captured_normal` 预期 · 单独批准包 · **不发明公司代码**

见 [known event replacement planning note](../plans/cninfo_d_class_known_event_replacement_case_planning_note.md)。

---

## 5. Safety

| 项 | 状态 |
|----|------|
| CNINFO calls（本回合） | **0** |
| live / rerun / harvest | **no** |
| v1/v2 execution reports | **untouched** |
| original universe | **untouched** |
| DB / MinIO / RAG | **0** |
| invented company codes | **no** |

---

## 6. Gate

```text
d_class_dlc003_dlc006_final_calibration_gate = HUMAN_SIGNED_OFF_WITH_CAVEAT
```

| 声明 | 值 |
|------|-----|
| PASS | **no** |
| verified | **false** |
| production_ready | **false** |
| testing_stable_sample upgrade | **no** |

---

## 7. Related Artifacts

| 文档 | 路径 |
|------|------|
| human signoff | [cninfo_d_class_dlc003_dlc006_calibration_human_signoff.md](cninfo_d_class_dlc003_dlc006_calibration_human_signoff.md) |
| calibrated universe | [cninfo_d_class_phase1_tiny_live_universe_calibrated.csv](cninfo_d_class_phase1_tiny_live_universe_calibrated.csv) |
