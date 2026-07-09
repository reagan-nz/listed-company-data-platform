# CNINFO D 类 Tiny Live V2 Bounded Probe — Closure Review

_生成时间：2026-07-09_

> **性质：** 离线收口评审 only · **无 CNINFO** · **无 rerun** · **不修改 execution report**

**关联输入：** [v2 bounded probe report](../outputs/validation/cninfo_d_class_tiny_live_validation_v2/reports/d_class_tiny_live_v2_bounded_probe_report.csv) · [v2 comparison report](../outputs/validation/cninfo_d_class_tiny_live_validation_v2/reports/d_class_tiny_live_v2_comparison_report.csv) · [calibration review](cninfo_d_class_dlc003_dlc006_calibration_review.md)

---

## 1. Objective

收口 D-class v2 bounded probe 执行结果，为 DLC003/DLC006 **最终校准决策** 提供证据链：

- 记录 v1 mismatch → v2 bounded probe 完整路径
- 确认 caps · 隔离 · 安全红线
- 强化 empty_but_valid 证据
- 明确仍待人工 signoff 的 universe 变更

**本回合不修改** v1/v2 execution report · **不自动变更** universe。

---

## 2. V1 Mismatch Recap

| case | component | company | v1 expected | v1 observed | v1 requests |
|------|-----------|---------|-------------|-------------|-------------|
| DLC003 | restricted_shares_unlock | 300009 安科生物 | captured_normal | empty_but_valid | **8** |
| DLC006 | shareholder_change | 000550 江铃汽车 | captured_normal | empty_but_valid | **5** |

v1 tiny live：**5/7 acceptable** · 2 expectation mismatches · **非 schema failure**（Phase 1 closure 已确认）。

---

## 3. V2 Bounded Probe Design Recap

| 项 | 值 |
|----|-----|
| 模式 | Option B — bounded probe extension |
| 范围 | **仅 DLC003 · DLC006** |
| DLC003 cap | **24**（v1 baseline ∪ 12m monthly ∪ 24m quarterly dedup） |
| DLC006 cap | **20**（v1 baseline ∪ expanded mode/date union dedup） |
| total cap | **≤44** |
| early stop | 公司级 `>=1` 行即停 |
| 输出根 | `cninfo_d_class_tiny_live_validation_v2/` |
| 批准 flag | `--approve-d-class-tiny-live-v2-bounded-probe` |

---

## 4. V2 Execution Result

| 指标 | 值 |
|------|-----|
| CNINFO requests | **40** |
| DLC003 requests | **21** / cap 24 |
| DLC006 requests | **19** / cap 20 |
| early stop | **0** |
| execution gate | `d_class_tiny_live_v2_bounded_probe_execution_gate = PASS_WITH_CAVEAT` |
| DB / MinIO / RAG | **0** |

---

## 5. DLC003 Result

| 项 | 值 |
|----|-----|
| company | 300009 安科生物 |
| component | restricted_shares_unlock |
| v1 | empty_but_valid · 0 rows · **8** requests |
| v2 | empty_but_valid · 0 rows · **21** requests |
| combined | **29** total probes · 0 company rows |
| quality_status | pass |
| acceptable (vs captured_normal) | **no** |

---

## 6. DLC006 Result

| 项 | 值 |
|----|-----|
| company | 000550 江铃汽车 |
| component | shareholder_change |
| v1 | empty_but_valid · 0 rows · **5** requests |
| v2 | empty_but_valid · 0 rows · **19** requests |
| combined | **24** total probes · 0 company rows |
| quality_status | pass |
| acceptable (vs captured_normal) | **no** |

---

## 7. Request Cap Compliance

| check | status |
|-------|--------|
| DLC003 ≤ 24 | **yes**（21） |
| DLC006 ≤ 20 | **yes**（19） |
| total ≤ 44 | **yes**（40） |
| baseline cases CNINFO | **0** |

---

## 8. V1 Output Isolation

| 项 | 状态 |
|----|------|
| v1 report | **未修改**（只读引用） |
| v1 snapshots | **未修改** |
| v2 写入根 | 隔离至 `_v2/` |
| 本 closure 回合 CNINFO | **0** |

---

## 9. DB / MinIO / RAG Confirmation

| 项 | v2 execution | closure 回合 |
|----|--------------|--------------|
| DB write | 0 | 0 |
| MinIO write | 0 | 0 |
| RAG run | 0 | 0 |
| harvest | no | no |

---

## 10. Why This Is Still Not Schema Failure

| 维度 | 证据 |
|------|------|
| API | HTTP 200 · JSON 可解析 |
| endpoint | `liftBan/detail` · `shareholeder/detail` 与 registry 一致 |
| 全市场 | 各探测日/模式全市场有行（非空壳 API） |
| retrieval | `empty_but_valid` 符合 quality policy §4 |
| quality | `pass` — 合法空态 |
| freeze v1 | contract **无需修订** |
| 其他组件 | DLC001/004/007 等 captured 路径已验证 |

**结论：** v2 扩窗后仍空 → **expectation / company-selection mismatch**，不是 schema · registry · mapper 缺陷。

---

## 11. Stronger empty_but_valid Evidence

| case | v1 probes | v2 probes | combined |
|------|-----------|-----------|----------|
| DLC003 | 8 tdate | 21 tdate（dedup union） | **29** · 0 rows |
| DLC006 | 5 mode/date | 19 mode/date | **24** · 0 rows |

- 系统性日历窗口（月尾/季尾）· **无事件日猜测**
- caps 内穷尽 · early stop **未触发**（无隐藏命中）
- 两轮回合一致观测 → **stable_empty_but_valid_after_bounded_probe**

**不证明**组件全局无数据；仅证明 **这两家公司在 bounded 窗口内稳定空态**。

---

## 12. Remaining Human Decision

| 待决项 | 状态 |
|--------|------|
| Option A：reclassify DLC003/DLC006 → empty_but_valid | **推荐**（tiny-live universe closure）· **需人工 signoff** |
| Option C：replacement captured_normal cases | **推荐为下一验证任务** · placeholders 仍空 |
| universe 自动变更 | **禁止**（`apply_now=false`） |
| `d_class_dlc003_dlc006_calibration_gate` | 升级至 **`READY_FOR_HUMAN_SIGNOFF`** |
| verified / production_ready | **不标记** |

---

## 13. Closure Gate

```text
d_class_tiny_live_v2_bounded_probe_closure_gate = PASS_WITH_CAVEAT
d_class_dlc003_dlc006_final_calibration_gate = READY_FOR_HUMAN_SIGNOFF
```

**不是 PASS** · **不是 verified** · **不是 production_ready**

**CNINFO calls（本回合）：0**
