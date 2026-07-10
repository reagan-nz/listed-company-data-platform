# CNINFO B 类 Phase 3 EP002/orgId Reachability Precheck — Planning Summary

_生成时间：2026-07-09_

> **性质：** 离线规划摘要 · **无 CNINFO** · **无 live** · **NOT APPROVED**

---

## Why Precheck Exists

Phase 3 effective result = **9/100** accepted · **91/100** unresolved at **EP002_topSearch_orgId**。8 例 retry 恢复证明 metadata pipeline 可用，但基础设施可达性未验证。Precheck 在 retry_v2 之前以最小 CNINFO 预算探测 orgId 路径。

---

## Candidate Selection

| 项 | 值 |
|----|-----|
| candidate count | **8** |
| source | persistent **91** only |
| markets | SSE主板（2）· SZSE主板（2）· 创业板（1）· 科创板（2） |
| announcement types | `periodic_report` EP004（3）· `general_announcement` EP005（5） |
| universe position | early（B3E001）· mid · late（B3E100） |

| precheck_id | case_id | company | market | type |
|-------------|---------|---------|--------|------|
| B3EP001 | B3E001 | 包钢股份 | SSE主板 | periodic_report |
| B3EP002 | B3E018 | 保利发展 | SSE主板 | periodic_report |
| B3EP003 | B3E035 | 特变电工 | SSE主板 | periodic_report |
| B3EP004 | B3E051 | 中国宝安 | SZSE主板 | general_announcement |
| B3EP005 | B3E074 | 长安汽车 | SZSE主板 | general_announcement |
| B3EP006 | B3E091 | 网宿科技 | 创业板 | general_announcement |
| B3EP007 | B3E096 | 华兴源创 | 科创板 | general_announcement |
| B3EP008 | B3E100 | 南微医学 | 科创板 | general_announcement |

---

## Request Cap

| 项 | 值 |
|----|-----|
| planned requests（dry-run） | **8** |
| max future live cap | **≤ 16** |
| check type | `ep002_orgid_reachability` only |

---

## Output Root

```text
outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck/
```

---

## Approval Status

```text
approval_status = NOT_APPROVED
approved_for_live = false
```

---

## Runner Support Status

| 项 | 状态 |
|----|------|
| runner path | `lab/run_cninfo_b_class_phase3_100_ep002_reachability_precheck.py` |
| implementation | **design only** |
| approval flag | `--approve-b-class-phase3-100-ep002-reachability-precheck` |
| dry-run / live | **not implemented** |

---

## Safety Confirmations

| 项 | 值 |
|----|-----|
| CNINFO calls（planning round） | **0** |
| live / precheck executed | **0** |
| retry_v2 created | **no** |
| B3E087 excluded | **yes** |
| 8 recovered excluded | **yes** |
| prior phases excluded | **yes** |
| persistent ledger mutated | **no** |
| PDF / OCR / DB / MinIO / RAG | **0** |
| verified / production_ready | **no** |

---

## Gate

```text
b_class_phase3_100_ep002_reachability_precheck_planning_gate = READY_FOR_APPROVAL
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

---

## Artifacts

| 项 | 路径 |
|----|------|
| plan | [cninfo_b_class_phase3_100_ep002_reachability_precheck_plan.md](../../plans/cninfo_b_class_phase3_100_ep002_reachability_precheck_plan.md) |
| candidates | [cninfo_b_class_phase3_100_ep002_reachability_precheck_candidates.csv](cninfo_b_class_phase3_100_ep002_reachability_precheck_candidates.csv) |
| approval checklist | [cninfo_b_class_phase3_100_ep002_reachability_precheck_approval_checklist.md](cninfo_b_class_phase3_100_ep002_reachability_precheck_approval_checklist.md) |
| command draft | [cninfo_b_class_phase3_100_ep002_reachability_precheck_command_draft.md](../../plans/cninfo_b_class_phase3_100_ep002_reachability_precheck_command_draft.md) |
| runner design | [cninfo_b_class_phase3_100_ep002_reachability_precheck_runner_design.md](../../plans/cninfo_b_class_phase3_100_ep002_reachability_precheck_runner_design.md) |

---

## Next Recommended Task

**B-class Phase 3 EP002 reachability precheck runner extension + dry-run**（offline · NOT APPROVED live）
