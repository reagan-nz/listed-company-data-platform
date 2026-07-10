# CNINFO D 类 Known Event Targeted Probe Plan

_生成时间：2026-07-09_

> **性质：** Option A 规划包 only · **无 CNINFO** · **无 live** · **无 runner 实现** · **NOT APPROVED**

**人工决策：** 仅推进 Option A planning package · 不实现 targeted probe · 不执行 targeted probe live

**关联 gate：** `d_class_known_event_replacement_validation_execution_gate = FAIL_REVIEW_REQUIRED` · `d_class_known_event_replacement_live_failure_review_gate = READY_FOR_HUMAN_DECISION`

---

## 1. Objective

在 replacement bounded live 双 case 失败后，为 DLC003R/DLC006R 准备 **event-date targeted probe** 隔离规划包，测试 anchor 日邻近 metadata 查询能否 surfacing 公司级结构化行。

**本计划不：** 将人工披露等同于 live `captured_normal` · 升级 replacement execution gate · 标记 verified。

---

## 2. Why Targeted Probe Is Needed

| 事实 | 含义 |
|------|------|
| replacement live CNINFO **40** | bounded replay 策略耗尽预算 |
| 双 case `empty_but_valid` | 端点可达 · company-level 零行 |
| human disclosure exists | 2024-02-19 unlock · 2024-07-16 shareholder change |
| reconciliation | `human_evidence_exists_but_component_probe_empty` |
| component captured_normal | **仍 outstanding** |

Bounded probe 未以 known event date 为中心；targeted probe 是 **假设检验**，非披露文本推断。

---

## 3. Replacement Live Failure Recap

| case | requests | retrieval | records | failure_type |
|------|----------|-----------|---------|--------------|
| DLC003R | 21 | empty_but_valid | 0 | empty_but_valid_after_budget |
| DLC006R | 19 | empty_but_valid | 0 | empty_but_valid_after_budget |

Execution gate：**`FAIL_REVIEW_REQUIRED`**（保持 · **不升级**）

---

## 4. Evidence Reconciliation Recap

见 [evidence reconciliation matrix](../outputs/validation/cninfo_d_class_known_event_replacement_evidence_reconciliation_matrix.csv)：

- `component_level_captured_normal = no`（双 case）
- `reconciliation_status = human_evidence_exists_but_component_probe_empty`

---

## 5. Scope

| targeted_probe_id | replacement | company | component | anchor_date | request_cap |
|-------------------|-------------|---------|-----------|-------------|-------------|
| DLC003R-T01 | DLC003R | 688671 碧兴物联 | restricted_shares_unlock | **2024-02-19** | **≤ 12** |
| DLC006R-T01 | DLC006R | 301259 艾布鲁 | shareholder_change | **2024-07-16** | **≤ 12** |

**合计 request cap：≤ 24**

Universe draft：[cninfo_d_class_known_event_targeted_probe_universe_draft.csv](../outputs/validation/cninfo_d_class_known_event_targeted_probe_universe_draft.csv)

---

## 6. Non-Goals

- 不 rerun 旧 DLC003 (300009) / DLC006 (000550)
- 不 rerun full D-class tiny-live
- 不 rerun v2 bounded probe
- 不 rerun replacement live
- 不修改 replacement live 报告
- 不 PDF/OCR/extraction
- 不 DB/MinIO/RAG
- 不 verified / production_ready / testing_stable_sample

---

## 7. Target Cases

仅 **DLC003R** · **DLC006R** — 各 1 行 · universe **exactly 2 rows**

不含：DLC001/002/004/005/007 baseline · 旧 DLC003/DLC006 · full tiny-live universe

---

## 8. Anchor Dates

| case | anchor_date | human evidence |
|------|-------------|----------------|
| DLC003R | 2024-02-19 | CNINFO 限售股上市流通公告 |
| DLC006R | 2024-07-16 | CNINFO 简式权益变动报告书 |

Anchor 用于 **probe 参数生成**，不等同于 live 已捕获证据。

---

## 9. Request Cap

| 层级 | cap |
|------|-----|
| DLC003R | ≤ **12** |
| DLC006R | ≤ **12** |
| total | ≤ **24** |
| early stop | 公司级命中 ≥1 行即停该 case |

---

## 10. Output Isolation

```text
outputs/validation/cninfo_d_class_known_event_targeted_probe/
```

**写保护：**

- `cninfo_d_class_known_event_replacement_validation/`（replacement live）
- `cninfo_d_class_tiny_live_validation/`（v1）
- `cninfo_d_class_tiny_live_validation_v2/`（v2）
- original / calibrated universe 文件

---

## 11. Approval Requirements

| 阶段 | 要求 |
|------|------|
| planning | 本规划包评审 → `READY_FOR_APPROVAL` |
| implementation | 显式人工批准 runner extension · `approved_for_implementation = true` |
| live | `--approve-d-class-known-event-targeted-probe` · `approved_for_live = true` |

**当前：** `approval_status = NOT_APPROVED` · `approved_for_implementation = false` · `approved_for_live = false`

---

## 12. Interpretation Rules

1. 人工披露证据 **≠** component-level `captured_normal`
2. targeted probe 命中前 **不得** 升级 replacement execution gate
3. execution gate 永不使用 `PASS` — 仅 `PASS_WITH_CAVEAT` 或 `FAIL_REVIEW_REQUIRED`
4. `empty_but_valid` after budget **不是** schema failure
5. targeted probe 仍可能失败 — 需接受 `FAIL_REVIEW_REQUIRED`

---

## 13. Red Lines

| 项 | 值 |
|----|-----|
| CNINFO（本回合） | **0** |
| live / rerun | **0** |
| runner implementation | **0** |
| invented company codes | **no** |
| web lookup | **no** |

---

## 14. Next Step After Planning

1. 评审 [approval checklist](../outputs/validation/cninfo_d_class_known_event_targeted_probe_approval_checklist.md)
2. 评审 [runner extension design](cninfo_d_class_known_event_targeted_probe_runner_extension_design.md)
3. 人工批准后 **离线实现** runner extension + dry-run（**非本回合**）
4. 显式 approval 后 isolated targeted live（**NOT APPROVED**）

---

## 15. Gate

```text
d_class_known_event_targeted_probe_planning_gate = READY_FOR_APPROVAL
d_class_known_event_replacement_validation_execution_gate = FAIL_REVIEW_REQUIRED
```

**NOT PASS** · **NOT live_ready** · **NOT verified**
