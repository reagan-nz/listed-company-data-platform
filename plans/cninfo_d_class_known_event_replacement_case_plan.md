# CNINFO D 类 Known Event Replacement Case Plan (Option C)

_生成时间：2026-07-09_

> **性质：** Option C 离线规划 only · **无 CNINFO** · **无 live** · **NOT APPROVED**

**关联状态：** `d_class_dlc003_dlc006_final_calibration_gate = HUMAN_SIGNED_OFF_WITH_CAVEAT` · [calibrated universe](../outputs/validation/cninfo_d_class_phase1_tiny_live_universe_calibrated.csv)

---

## 1. Objective

为 **restricted_shares_unlock** 与 **shareholder_change** 两个组件准备 **人工选定 known captured_normal** replacement case 规划包，补全组件级 live 验证缺口。

**本计划不执行验证** — 仅定义需求、模板、universe draft、批准流程。

---

## 2. Why Option C Is Needed

| 事实 | 含义 |
|------|------|
| Option A 已完成 | DLC003/DLC006 当前公司（300009 · 000550）校准为 `empty_but_valid` |
| tiny-live 7/7 | 校准后 universe mismatch 可收口 |
| 组件缺口 | `restricted_shares_unlock` · `shareholder_change` **均无** tiny-live `captured_normal` 命中 |
| mapper 回归 | captured 路径 live 证据 **仍缺** |
| v1+v2 证据 | 仅证明 **特定公司** 稳定空态，非组件全局无数据 |

**Option C 目标：** 在 **人工提供** known event 证据的前提下，用 replacement case 验证组件 captured 路径。

---

## 3. Why Current DLC003/DLC006 Calibration Is Valid

| case | company | 校准后行为 | 依据 |
|------|---------|------------|------|
| DLC003 | 300009 安科生物 | `empty_but_valid` | v1 **8** + v2 **21** probes · 0 rows · `human_signed_off` |
| DLC006 | 000550 江铃汽车 | `empty_but_valid` | v1 **5** + v2 **19** probes · 0 rows · `human_signed_off` |

- `schema_failure = false`
- quality policy 口径正确
- **不撤销** Option A signoff
- replacement **不替代** 已校准行 — 为 **并行补证轨道**

---

## 4. Why Component-Level captured_normal Coverage Is Still Outstanding

| 组件 | tiny-live captured_normal | 状态 |
|------|-------------------------|------|
| restricted_shares_unlock | **无** | outstanding |
| shareholder_change | **无** | outstanding |
| 其他 5 组件 | 有（captured / empty / needs_review） | covered |

**缺口性质：** 组件级 captured 路径未 live 验证 · **不是** schema freeze 缺陷。

---

## 5. Replacement Case Requirements

| 项 | DLC003R | DLC006R |
|----|---------|---------|
| replacement_case_id | DLC003R | DLC006R |
| replaces_case_id | DLC003 | DLC006 |
| component | restricted_shares_unlock | shareholder_change |
| required_behavior | `captured_normal` | `captured_normal` |
| company_code | **人工填写** | **人工填写** |
| company_name | **人工填写** | **人工填写** |
| event evidence | **人工填写** | **人工填写** |
| endpoint | `liftBan/detail` | `shareholeder/detail` |

**禁止：** 自动发明 company_code · web lookup · 猜测事件日

---

## 6. Human Evidence Requirements

人工须提供（填入 [candidate template](../outputs/validation/cninfo_d_class_known_event_replacement_candidate_template.csv)）：

| 字段 | 要求 |
|------|------|
| event_evidence_type | 如：公告解禁 / 股东增减持公告 / 监管披露 |
| event_evidence_description | 人工描述 known event（**非 agent 猜测**） |
| event_date_or_period | 人工记录日期或区间 |
| source_reference | 人工记录来源（文档名/内部记录 ID — **非 web 抓取**） |
| human_provided | `true` 后才可进入批准包 |

---

## 7. Validation Scope

| 包含 | 不包含 |
|------|--------|
| DLC003R · DLC006R（人工填码后） | DLC001/002/004/005/007 live 重探 |
| isolated metadata/event probe | harvest |
| 输出根 `cninfo_d_class_known_event_replacement_validation/` | DB / MinIO / RAG |
| bounded request cap（未来定义） | verified / production_ready |

**仅** `human_provided=true` 且 `candidate_status=approved` 的行可执行。

---

## 8. Approval Process

1. 人工填写 [candidate template](../outputs/validation/cninfo_d_class_known_event_replacement_candidate_template.csv)
2. 人工审核 [replacement universe draft](../outputs/validation/cninfo_d_class_tiny_live_replacement_universe_draft.csv)
3. 完成 [approval checklist](../outputs/validation/cninfo_d_class_known_event_replacement_approval_checklist.md)
4. 评审 [command draft](cninfo_d_class_known_event_replacement_validation_command_draft.md)
5. 显式 `--approve-d-class-known-event-replacement-validation`
6. **未来回合** runner 实现 + isolated live（**非本计划**）

**当前：** **NOT APPROVED** · gate **`READY_FOR_HUMAN_CANDIDATES`**

---

## 9. Red Lines

| 红线 | 状态 |
|------|------|
| No CNINFO | 本回合 **0** |
| No live / rerun / harvest | **yes** |
| No invented company codes | **yes** |
| No web lookup | **yes** |
| No original universe mutation | **yes** |
| No calibrated universe mutation | **yes** |
| No v1/v2 execution report mutation | **yes** |
| No DB / MinIO / RAG | **yes** |
| No verified / production_ready / testing_stable_sample | **yes** |

---

## 10. Artifacts

| 文档 | 路径 |
|------|------|
| candidate template | [cninfo_d_class_known_event_replacement_candidate_template.csv](../outputs/validation/cninfo_d_class_known_event_replacement_candidate_template.csv) |
| replacement universe draft | [cninfo_d_class_tiny_live_replacement_universe_draft.csv](../outputs/validation/cninfo_d_class_tiny_live_replacement_universe_draft.csv) |
| command draft | [cninfo_d_class_known_event_replacement_validation_command_draft.md](cninfo_d_class_known_event_replacement_validation_command_draft.md) |
| approval checklist | [cninfo_d_class_known_event_replacement_approval_checklist.md](../outputs/validation/cninfo_d_class_known_event_replacement_approval_checklist.md) |
| planning summary | [cninfo_d_class_known_event_replacement_planning_summary.md](../outputs/validation/cninfo_d_class_known_event_replacement_planning_summary.md) |

---

## 11. Gate

```text
d_class_known_event_replacement_case_planning_gate = READY_FOR_HUMAN_CANDIDATES
```

**不是 PASS** · **不是 approved** · **不是 live_ready** · **不是 verified**
