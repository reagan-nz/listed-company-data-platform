# CNINFO A 类 Phase 2 Retry v3 Isolated 规划

_生成时间：2026-07-09_

> **性质：** 离线规划 only · **无 CNINFO** · **无 live** · **无 retry_v3 执行** · **不是 verified** · **不是 production_ready**

---

## 1. Objective

在 CNINFO/orgId reachability precheck 显示 **partial recovery** 后，为 Phase 2 中 **8 个 unresolved network failure** case 准备 **isolated retry v3** 规划包，验证 metadata 可检索性，不改变 schema / matching / universe。

**前置 gate：**

```text
a_class_phase2_cninfo_reachability_precheck_execution_gate = PASS_WITH_CAVEAT
a_class_phase2_retry_v2_closure_gate = PASS_WITH_CAVEAT_NETWORK_UNRESOLVED
```

**本规划 gate：**

```text
a_class_phase2_retry_v3_planning_gate = READY_FOR_APPROVAL
```

**Live 仍未批准：** `approval_status = NOT_APPROVED` · `approved_for_live = false`

---

## 2. Why Retry v3 Is Justified After Reachability Precheck

| 轮次 | 结果 |
|------|------|
| Precheck live | **2/3** orgId resolved · CNINFO **2** · gate **`PASS_WITH_CAVEAT`** |

Precheck 证明 CNINFO topSearch / orgId 路径 **部分恢复**（SSE · STAR 可达），不再是 v1/v2 的零 CNINFO 空跑窗口。

Retry v3 目的：

- 对 **全部 8 unresolved** 执行 metadata-only isolated retry
- 使用 **新隔离输出根** `cninfo_a_class_phase2_metadata_retry_v3/`
- 与 original / v1 / v2 / precheck 报告并存，便于审计 partial recovery 后的 metadata 结果

**重要：** precheck **不是** metadata retry · precheck `PASS_WITH_CAVEAT` **不解决** 8 case 的 metadata 状态。

---

## 3. Why Retry v3 Is Still NOT APPROVED for Live

| 项 | 原因 |
|----|------|
| runner gap | `--retry-v3` · `--approve-a-class-phase2-retry-v3` **尚未实现** |
| ChiNext risk | A2M010 precheck **unreachable** · `network_error` 残留 |
| partial precheck | 5/8 case **not_directly_prechecked** |
| human approval | 须显式批准 flag + dry-run + tests 后再 live |
| no auto-run | precheck 通过 **不等于** retry_v3 live 自动执行 |

---

## 4. Original Phase 2 Recap

| 项 | 值 |
|----|-----|
| total | **20** |
| accepted | **12** |
| unresolved | **8** |
| wrong_report_type | **0** |
| execution gate | `FAIL_REVIEW_REQUIRED` |

---

## 5. Retry v1 Recap

| 项 | 值 |
|----|-----|
| retry cases | **8** |
| acceptable | **0** |
| CNINFO | **0** |
| failure | orgId network_error（outage 窗口） |
| execution gate | `FAIL_REVIEW_REQUIRED` |

---

## 6. Retry v2 Recap

| 项 | 值 |
|----|-----|
| retry cases | **8** |
| acceptable | **0** |
| CNINFO | **0** |
| failure | orgId network_error |
| execution gate | `FAIL_REVIEW_REQUIRED` |
| closure gate | `PASS_WITH_CAVEAT_NETWORK_UNRESOLVED` |

---

## 7. Reachability Precheck Recap

| precheck_id | case_id | market | orgId | result |
|-------------|---------|--------|-------|--------|
| APC001 | A2M005 | SSE | resolved | 9900022338 |
| APC002 | A2M010 | ChiNext | failed | network_error |
| APC003 | A2M018 | STAR | resolved | 9900035303 |

| 项 | 值 |
|----|-----|
| CNINFO requests | **2** |
| execution gate | **`PASS_WITH_CAVEAT`** |

---

## 8. Unresolved 8 Case List

A2M005 · A2M010 · A2M011 · A2M012 · A2M013 · A2M018 · A2M019 · A2M020

---

## 9. Successful 12 Exclusion Rule

**禁止进入 retry_v3 universe：**

A2M001 · A2M002 · A2M003 · A2M004 · A2M006 · A2M007 · A2M008 · A2M009 · A2M014 · A2M015 · A2M016 · A2M017

- 已 `accepted_original_success` · title/period pass · wrong_report_type=0
- 重跑将污染 closure baseline 与 CNINFO 审计轨迹

---

## 10. ChiNext / Network Residual Risk

- **A2M010**（宁德时代 · ChiNext）在 precheck 中 **unreachable** · `network_error`
- 同一市场/路由可能在 retry_v3 live 中再次失败
- 5 case 未经直接 precheck（`not_directly_prechecked`）
- retry_v3 结果须按 case 审阅，不可因 precheck 2/3 而整体标记 verified

---

## 11. Output Isolation Plan

| 输出根 | retry v3 写入 |
|--------|---------------|
| `cninfo_a_class_phase2_metadata_expansion/` | **禁止** |
| `cninfo_a_class_phase2_metadata_retry/` | **禁止** |
| `cninfo_a_class_phase2_metadata_retry_v2/` | **禁止** |
| `cninfo_a_class_phase2_cninfo_reachability_precheck/` | **禁止** |
| `cninfo_a_class_phase2_metadata_retry_v3/` | **允许** |

---

## 12. Approval Requirements

| 项 | 要求 |
|----|------|
| 人工批准 | **必须** |
| 批准 flag | `--approve-a-class-phase2-retry-v3` |
| runner extension | dry-run + tests **待实现** |
| universe | **8** case · `retry_v3_include=yes` |
| scope | metadata only · **无 PDF** |

**当前：NOT_APPROVED**

---

## 13. Expected Result Interpretation

| retry_v3 结果 | execution gate（未来 live 后） |
|---------------|-------------------------------|
| acceptable ≥ **6/8** · 无红线违规 | `PASS_WITH_CAVEAT` |
| acceptable < **6/8** | `FAIL_REVIEW_REQUIRED` |

- **Never PASS** · **not verified** · **not production_ready**
- wrong_report_type=0 仍为必要质量约束
- 50-company expansion **阻塞** 直至 retry_v3 结果审阅

---

## 14. Red Lines

- 无 successful 12 rerun
- 无 50-company expansion
- 无 schema / matching logic change
- 无 PDF / OCR / DB / MinIO / RAG
- 无 verified / production_ready / testing_stable_sample
- 不修改 original / v1 / v2 / precheck 报告

---

## 15. Next Step After Planning

1. Runner extension + dry-run + tests（**无 CNINFO**）
2. 人工批准 live retry_v3
3. 审阅 live 结果 → 可能 merge closure update v3
4. **不推荐** 50-company expansion 直至 v3 审阅完成

---

## Artifacts

| 项 | 路径 |
|----|------|
| universe | [cninfo_a_class_phase2_retry_v3_universe.csv](../outputs/validation/cninfo_a_class_phase2_retry_v3_universe.csv) |
| approval checklist | [cninfo_a_class_phase2_retry_v3_approval_checklist.md](../outputs/validation/cninfo_a_class_phase2_retry_v3_approval_checklist.md) |
| command draft | [cninfo_a_class_phase2_retry_v3_command_draft.md](cninfo_a_class_phase2_retry_v3_command_draft.md) |
| runner design | [cninfo_a_class_phase2_retry_v3_runner_extension_design.md](cninfo_a_class_phase2_retry_v3_runner_extension_design.md) |
| planning summary | [cninfo_a_class_phase2_retry_v3_planning_summary.md](../outputs/validation/cninfo_a_class_phase2_retry_v3_planning_summary.md) |
