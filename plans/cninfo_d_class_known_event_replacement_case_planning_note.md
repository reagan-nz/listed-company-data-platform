# CNINFO D 类 Known Event Replacement Case — Planning Note (Option C)

_生成时间：2026-07-09_

> **性质：** 未来任务规划 only · **NOT STARTED** · **无 CNINFO** · **无 live** · **无 web lookup**

**前置：** Option A human signoff 已完成 · [calibrated universe](../outputs/validation/cninfo_d_class_phase1_tiny_live_universe_calibrated.csv)

---

## 1. Goal

规划未来 **人工选定** 的 `captured_normal` replacement cases，补全组件级 live 验证：

| case | component | replacement target |
|------|-----------|-------------------|
| DLC003 replacement | `restricted_shares_unlock` | known captured_normal company with documented unlock event |
| DLC006 replacement | `shareholder_change` | known captured_normal company with documented inc/desc event |

**不替代** 已校准的 300009 / 000550 行 — replacement 为 **新增验证轨道**（universe v2 placeholders）。

---

## 2. DLC003 Replacement Target

| 项 | 要求 |
|----|------|
| component | `restricted_shares_unlock` |
| expected_behavior | `captured_normal` |
| company_code | **人工提供** — 禁止自动发明 |
| evidence | 人工记录的 known unlock event（日期/公告来源） |
| endpoint | `liftBan/detail` |
| 当前 placeholder | `DLC003_V2_CANDIDATE_REQUIRED` in universe v2 draft |

---

## 3. DLC006 Replacement Target

| 项 | 要求 |
|----|------|
| component | `shareholder_change` |
| expected_behavior | `captured_normal` |
| company_code | **人工提供** — 禁止自动发明 |
| evidence | 人工记录的 known shareholder inc/desc event |
| endpoint | `shareholeder/detail` |
| 当前 placeholder | `DLC006_V2_CANDIDATE_REQUIRED` in universe v2 draft |

---

## 4. Rules

| 规则 | 说明 |
|------|------|
| no invented company codes | runner / agent **不得**自动填码 |
| human event evidence | 人工须提供 known event 依据 |
| no web lookup | 本规划回合 **不**查询外部源 |
| no live execution | 执行需 **单独批准包** |
| no harvest | 仅 metadata/event validation |
| no DB / MinIO / RAG | **0** |
| no verified / production_ready | 禁止升级 |

---

## 5. Approval Package (Future)

未来执行前须准备：

1. replacement universe CSV（填入人工 company_code + event evidence 列）
2. approval checklist
3. command draft（isolated output root）
4. explicit approval flag（**新 flag · 未定义**）
5. request cap（tiny · bounded）

**当前状态：** **NOT APPROVED** · **NOT STARTED**

---

## 6. Relationship to Option A

| 层 | 状态 |
|----|------|
| Option A（300009 / 000550） | **已 signoff** → `empty_but_valid` |
| Option C（replacement） | **待启动** → 组件 captured_normal 补证 |
| 并行 | Option A 不消除 Option C 必要性 |

---

## 7. Gate

```text
d_class_known_event_replacement_case_planning_gate = READY_FOR_HUMAN_CANDIDATES
```

（已由完整规划包 supersede — 见 [replacement case plan](cninfo_d_class_known_event_replacement_case_plan.md)）

**不是 PASS** · **不是 live_ready** · **不是 verified**

---

## 8. Next Step (When Ready)

1. 人工提供 DLC003 / DLC006 replacement `company_code` + event evidence
2. 更新 `cninfo_d_class_phase1_tiny_live_universe_v2_draft.csv` placeholders
3. 准备单独 approval package
4. 未来回合执行 isolated tiny validation（**非本任务**）
