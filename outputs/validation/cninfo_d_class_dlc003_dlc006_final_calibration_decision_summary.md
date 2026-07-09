# CNINFO D 类 DLC003 / DLC006 Final Calibration Decision Summary

_生成时间：2026-07-09_

> **性质：** 离线决策摘要 · **无 CNINFO** · **无 universe 自动变更** · **不是 verified**

**关联证据：** [v1-v2 evidence matrix](cninfo_d_class_dlc003_dlc006_v1_v2_evidence_matrix.csv) · [v2 closure review](../plans/cninfo_d_class_tiny_live_v2_bounded_probe_closure_review.md) · [universe calibration proposal](cninfo_d_class_phase1_tiny_live_universe_calibration_proposal.csv)

---

## 1. Evidence Summary

| case | v1 probes | v2 probes | total | records | combined interpretation |
|------|-----------|-----------|-------|---------|----------------------|
| DLC003 | 8 | 21 | **29** | 0 | stable_empty_but_valid_after_bounded_probe |
| DLC006 | 5 | 19 | **24** | 0 | stable_empty_but_valid_after_bounded_probe |

- CNINFO v2 execution：**40** requests · caps respected · early stop **0**
- schema_failure：**false**
- v1 outputs：**untouched**

---

## 2. Decision Options

### Option A — Reclassify expected_behavior to empty_but_valid

对 **当前 tiny-live universe 中这两家公司**（300009 · 000550），将 `expected_behavior` 从 `captured_normal` 改为 `empty_but_valid`。

| 优点 | 风险 |
|------|------|
| 与 v1+v2 观测一致 | 组件级仍缺 captured_normal live 样本 |
| 消除 expectation mismatch | 不证明全局组件无数据 |
| tiny-live closure 可推进 | 需人工 signoff |

### Option C — Human-selected replacement cases

人工选定 **已知解禁/增减持事件** 公司填入 universe v2 placeholders，保留 `captured_normal` 预期，执行 focused validation。

| 优点 | 风险 |
|------|------|
| 保留 captured 路径验证 | 需人工提供 company_code |
| 组件级覆盖更完整 | 额外 CNINFO 回合（需单独批准） |

---

## 3. Recommended Decision

**对 DLC003 与 DLC006 均采用：**

| 层级 | 推荐 |
|------|------|
| **Tiny-live universe closure** | **Option A** — reclassify `expected_behavior` → `empty_but_valid` for 300009 / 000550 |
| **Next validation task** | **Option C** — human-selected known `captured_normal` replacement cases |

### Reason

1. v1 **与** v2 bounded probes **均无公司级行** — 证据一致且加强
2. request caps 遵守 · empty_but_valid 语义经 **29 / 24** 次探测强化
3. **不证明**整个组件缺乏数据 — 仅证明当前选股在 bounded 窗口内稳定空态
4. 组件级 captured_normal 验证 **仍需要** Option C 补充
5. universe 变更 **`apply_now=false`** — 待人工 signoff

---

## 4. Per-Case Recommendation

| case | Option A (closure) | Option C (next) |
|------|-------------------|-----------------|
| **DLC003** | **推荐** — reclassify to empty_but_valid | **推荐** — 下一任务：已知解禁事件 replacement |
| **DLC006** | **推荐** — reclassify to empty_but_valid | **推荐** — 下一任务：已知增减持事件 replacement |

**不推荐立即单独执行 Option C 而不处理 Option A** — mismatch 应先通过 signoff 收口。

---

## 5. What Is Not Done

| 项 | 状态 |
|----|------|
| universe CSV 自动修改 | **未执行** |
| invented company codes | **无** |
| v1/v2 execution report 修改 | **未执行** |
| verified / production_ready | **未标记** |
| testing_stable_sample upgrade | **未执行** |
| harvest / DB / MinIO / RAG | **0** |

---

## 6. Gates

```text
d_class_tiny_live_v2_bounded_probe_closure_gate = PASS_WITH_CAVEAT
d_class_dlc003_dlc006_final_calibration_gate = READY_FOR_HUMAN_SIGNOFF
```

Prior gates preserved:
- `d_class_phase1_boundary_gate = PASS_WITH_CAVEAT`
- `d_class_tiny_live_v2_bounded_probe_execution_gate = PASS_WITH_CAVEAT`
- `d_class_dlc003_dlc006_calibration_gate = READY_FOR_HUMAN_DECISION` → superseded by **final_calibration** signoff track

**不是 PASS** · **不是 verified** · **不是 production_ready**

**CNINFO calls（本回合）：0**

---

## 7. Next Step After Human Signoff

1. 批准 [universe calibration proposal](cninfo_d_class_phase1_tiny_live_universe_calibration_proposal.csv)
2. 人工填入 Option C replacement candidates（universe v2 placeholders）
3. 规划 focused captured_normal validation（**单独批准包**）
