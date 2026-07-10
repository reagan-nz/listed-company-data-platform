# CNINFO D 类 DLC006R — Human Decision Record

_决策日期：2026-07-10_

> **性质：** 离线人工决策记录 only · **无 CNINFO** · **无 live** · **无 rerun** · **不是 verified**

---

## 1. Decision Context

| 项 | 值 |
|----|-----|
| closure gate（决策前） | `d_class_known_event_targeted_probe_closure_gate = READY_FOR_HUMAN_DECISION` |
| targeted probe execution gate | `FAIL_REVIEW_REQUIRED` |
| replacement execution gate | `FAIL_REVIEW_REQUIRED` |
| DLC003R-T01 | **captured_normal_structured_evidence**（targeted probe live · 1 record） |
| DLC006R-T01 | **unresolved_empty_but_valid_after_budget**（replacement 19 + targeted 12 · 0 records） |

关联：[human decision package](cninfo_d_class_dlc006r_human_decision_package.md) · [closure review](cninfo_d_class_known_event_targeted_probe_closure_review.md)

---

## 2. Selected Options

**Option A + Option C**（组合采纳）

| Option | 内容 |
|--------|------|
| **A** | Accept DLC006R `shareholder_change` component gap with caveat |
| **C** | Reconcile human disclosure evidence offline as separate evidence lineage — **不** promote 至 `captured_normal` |

---

## 3. Decision Statement

DLC006R `shareholder_change` structured component remains **unresolved** after replacement live and targeted probe. The component gap is **accepted with caveat**. Human disclosure evidence may be retained and reconciled as **separate lineage evidence**, but it **must not** be promoted to `captured_normal` or treated as structured component capture.

---

## 4. Why Immediate Rerun Is Rejected

- DLC006R-T01 已耗尽 targeted cap（12/12）
- replacement live 已耗尽 bounded cap（19/19）
- 合计 **31** metadata 探针无公司级行
- `schema_impact = none` — 无证据支持 schema 修复即可命中
- 人工决策为 **接受缺口** · **非** 追加 live

---

## 5. Why captured_normal Is Not Allowed for DLC006R

- metadata 探针路径未返回 `found` + `record_count >= 1`
- `captured_normal_allowed = no`
- 人工披露 **≠** 结构化组件捕获
- final_effective_status → `accepted_component_gap_with_separate_disclosure_evidence`

---

## 6. Why Disclosure Evidence Remains Separate

- 披露证据来源：human intake · CNINFO finalpage PDF 引用（离线记录）
- 性质：**separate_disclosure_lineage_only**
- Option C 仅允许谱系文档化 · **禁止** merge 入 structured component result
- 见 [disclosure evidence reconciliation note](cninfo_d_class_dlc006r_disclosure_evidence_reconciliation_note.md)

---

## 7. Schema and Quality Impact

| 项 | 值 | 理由 |
|----|-----|------|
| schema_impact | **none** | 无 http_error / invalid_json 直接证据 |
| quality_impact | **component_gap_unresolved** | endpoint 合法 empty · 组件级零行持续 |

---

## 8. Implications for D-Class Replacement Closure

| case | 处置 |
|------|------|
| DLC003R | **accept_structured_capture_with_caveat** — targeted probe 正向证据保留 |
| DLC006R | **accept_gap_with_caveat_and_reconcile_disclosure_offline** |

**Final closure gate：** `d_class_known_event_replacement_final_closure_gate = PASS_WITH_CAVEAT`

- **不是 PASS** · **不是 verified** · **不是 production_ready**
- execution gates（replacement / targeted probe）**保持** `FAIL_REVIEW_REQUIRED`（历史 live 事实不变）

---

## 9. Red-Line Confirmations

| 项 | 状态 |
|----|------|
| CNINFO calls（本回合） | **0** |
| live / rerun | **0** |
| disclosure → captured_normal | **禁止** |
| verified / production_ready | **未标记** |
| live / dry-run / replacement reports mutation | **未修改** |

---

## 10. Artifacts Produced

| 项 | 路径 |
|----|------|
| final effective ledger | [cninfo_d_class_known_event_replacement_final_effective_status_ledger.csv](../outputs/validation/cninfo_d_class_known_event_replacement_final_effective_status_ledger.csv) |
| disclosure reconcile note | [cninfo_d_class_dlc006r_disclosure_evidence_reconciliation_note.md](cninfo_d_class_dlc006r_disclosure_evidence_reconciliation_note.md) |
| final closure summary | [cninfo_d_class_known_event_replacement_final_closure_summary.md](../outputs/validation/cninfo_d_class_known_event_replacement_final_closure_summary.md) |
