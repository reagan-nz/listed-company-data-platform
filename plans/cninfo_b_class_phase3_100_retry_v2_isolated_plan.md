# CNINFO B 类 Phase 3 Retry v2 Isolated 规划

_生成时间：2026-07-10_

> **性质：** 离线规划 only · **无 CNINFO** · **无 live** · **无 retry_v2 执行** · **不是 verified** · **不是 production_ready**

---

## 1. Objective

在 EP002/orgId reachability precheck **8/8 resolved** 之后，为 Phase 3 **91** 例 persistent unresolved case 准备 **isolated retry_v2** 规划包，用于未来（经独立批准后）验证 metadata 可检索性是否因基础设施恢复而补全。

**前置 execution gate：** `b_class_phase3_100_ep002_reachability_precheck_execution_gate = PASS_WITH_CAVEAT`

**本规划 gate（规划完成后）：** `b_class_phase3_100_retry_v2_planning_gate = READY_FOR_APPROVAL`

---

## 2. Why Retry v2 Is Justified After EP002 Precheck 8/8

| 轮次 | 结果 | 问题 |
|------|------|------|
| Phase 3 original live | **1/100** acceptable · B3E087 hold | 99 failed · 主导 EP002 orgId/network |
| Failed retry v1 (isolated) | **8/99** recovered · **91/99** network_error at EP002 | 证明 pipeline 在 orgId 可用时正常 |
| EP002 precheck (8 representatives) | **8/8** orgId resolved · CNINFO **8** | 代表性市场（SSE/SZSE/创业板/科创板）EP002 可达 |

EP002 precheck 表明 **EP002_topSearch_orgId 基础设施在采样窗口内已恢复**，retry_v1 的 91 例失败更可能归因 **transient network outage**，而非 schema / endpoint 模型缺陷。

Retry v2 需要：

- **新隔离输出根** `cninfo_b_class_phase3_100_retry_v2/`
- **新批准 flag** `--approve-b-class-phase3-100-retry-v2`
- **新 universe** `cninfo_b_class_phase3_100_retry_v2_universe.csv`（**91** 行 · B3R2_001–B3R2_091）
- **与 original / failed-retry / EP002 precheck 报告并存**，便于审计

---

## 3. Why Retry v2 Is Still NOT APPROVED for Live

| 项 | 说明 |
|----|------|
| precheck 范围 | 仅 **8** 例代表性候选 · **非** 91 例全量验证 |
| effective acceptance | 仍为 **9/100** · retry_v2 **不自动升级** |
| runner | `run_cninfo_b_class_phase25_expansion_validation.py` **尚未实现** `--phase3-100-retry-v2` |
| approval | `approval_status = NOT_APPROVED` · `approved_for_live = false` |
| CNINFO budget | 91-case live 将产生显著 CNINFO 调用 · 须人工批准 |

**EP002 precheck 证明可达性，不本身恢复 91 例。** retry_v2 须 **单独批准** 后方可 live。

---

## 4. Original Phase 3 Recap

| 项 | 值 |
|----|-----|
| universe | B3E001–B3E100（**100** 家） |
| acceptable | **1**（B3E087 北新建材 · hold） |
| execution gate | `FAIL_REVIEW_REQUIRED` |
| 主导失败 | EP002_topSearch_orgId network/orgId |
| schema_impact | **none** |

---

## 5. Failed Retry Recap

| 项 | 值 |
|----|-----|
| universe | **99** 家（B3E087 excluded） |
| recovered | **8**（B3E003–B3E011 subset） |
| persistent | **91** network_error at EP002 |
| execution gate | `FAIL_REVIEW_REQUIRED` |
| CNINFO | **18** · PDF **0** |

---

## 6. Failed Retry Closure Recap

| 项 | 值 |
|----|-----|
| effective accepted | **9/100**（1 hold + 8 recovered） |
| persistent unresolved | **91/100** |
| closure gate | `PASS_WITH_CAVEAT_NETWORK_UNRESOLVED` |
| dominant failure | infrastructure / reachability caveat · **非 schema** |

---

## 7. EP002 Precheck Recap

| 项 | 值 |
|----|-----|
| candidates | **8**（B3EP001–B3EP008） |
| orgId resolved | **8/8** |
| CNINFO requests | **8** |
| execution gate | `PASS_WITH_CAVEAT` |
| check type | `ep002_orgid_reachability` only · 无 metadata retry |

---

## 8. Effective Accepted 9/100 Recap

| 类别 | case_ids | 处理 |
|------|----------|------|
| accepted original hold | B3E087 | **不重跑** · `rerun_allowed=no` |
| retry recovered | B3E003, B3E004, B3E005, B3E006, B3E007, B3E008, B3E009, B3E011 | **不重跑** · 已 found/pass |
| persistent unresolved | **91** 其余 | retry_v2 only |

---

## 9. Persistent 91 Case Recap

- `final_effective_status = unresolved_ep002_orgid_network_failure`
- `failure_stage = EP002_topSearch_orgId`
- `schema_impact = none`
- `quality_impact = unresolved_network_caveat`
- 来源：[persistent failure ledger](../outputs/validation/cninfo_b_class_phase3_100_persistent_failure_ledger.csv)

---

## 10. B3E087 Exclusion Rule

| 项 | 值 |
|----|-----|
| case_id | B3E087 |
| company | 北新建材（000786） |
| status | `accepted_original_success` |
| rerun_allowed | **no** |

Runner 须拒绝 B3E087 进入 retry_v2 universe。

---

## 11. 8 Recovered Case Exclusion Rule

以下 case **不得** 进入 retry_v2：

`B3E003` · `B3E004` · `B3E005` · `B3E006` · `B3E007` · `B3E008` · `B3E009` · `B3E011`

均已 `accepted_retry_recovered` · URL lineage discovered · **不重跑**。

---

## 12. Output Isolation Plan

| 输出根 | retry_v2 写入 |
|--------|---------------|
| `cninfo_b_class_phase3_100_expansion/` | **禁止** |
| `cninfo_b_class_phase3_100_failed_retry/` | **禁止** |
| `cninfo_b_class_phase3_100_ep002_reachability_precheck/` | **禁止** |
| `cninfo_b_class_phase25_expansion/` | **禁止** |
| `cninfo_b_class_phase25_failed_retry/` | **禁止** |
| `cninfo_b_class_phase3_100_retry_v2/` | **允许**（未来 live） |

---

## 13. Approval Requirements

| 项 | 要求 |
|----|------|
| 人工批准 | **必须** |
| approval flag | `--approve-b-class-phase3-100-retry-v2` |
| runner mode | `--phase3-100-retry-v2`（**待实现**） |
| 当前状态 | **NOT_APPROVED** |
| dry-run | 未来回合 · CNINFO=0 |
| live | 须显式批准 + runner extension |

批准检查清单：[cninfo_b_class_phase3_100_retry_v2_approval_checklist.md](../outputs/validation/cninfo_b_class_phase3_100_retry_v2_approval_checklist.md)

---

## 14. Expected Result Interpretation

| retry_v2 结果 | execution gate | 解释 |
|---------------|----------------|------|
| acceptable ≥ **82/91**（≥90%）且无 red-line | `PASS_WITH_CAVEAT` | 网络恢复有效 · metadata 大幅补全 |
| acceptable < **82/91** | `FAIL_REVIEW_REQUIRED` | 基础设施或匹配问题仍存 |
| red-line（PDF downloaded 等） | `FAIL_REVIEW_REQUIRED` | 违反边界 |

**Never：** `PASS` · `verified` · `production_ready` · `testing_stable_sample`

retry_v2 成功 **不自动** 将 effective accepted 升级为 verified；须独立 closure review。

---

## 15. Red Lines

- 无 CNINFO（本回合）
- 无 live retry_v2 执行
- 无 B3E087 rerun
- 无 8 recovered rerun
- 无 prior B1E/B2E/B25E rerun
- 无 original 100-case 全量 rerun
- 无 replacement cases
- 无 schema / endpoint model change
- 无 PDF / OCR / extraction / DB / MinIO / RAG
- 无 verified / production_ready
- 不突变 original / failed-retry / EP002 precheck / Phase 2.5 报告

---

## 16. Next Step After Planning

1. **Runner extension + dry-run**（`--phase3-100-retry-v2` · 91-case validation · CNINFO=0）
2. **Human approval review**
3. **Future live retry_v2**（仅批准后 · 隔离输出根）
4. **Post-retry_v2 closure review**（merge effective result · 不自动 verified）
