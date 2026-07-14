# CNINFO A 类 — Mission Coverage Gap Analysis

_生成时间：2026-07-14_

> **offline analysis** · **CNINFO = 0** · **NOT verified** · **NOT production_ready**

---

## Mission Goal

**全市场上市公司基础信息覆盖**（A 类 mission objective v2：full-market company information coverage）。

本分析仅基于已收口 lineage 与 unresolved ledger，不发起 live、不调用 CNINFO、不升级 gate。

---

## What Is Covered（已覆盖范围）

证据来源：`CURRENT_STATUS.md` · `PROJECT_CONTROL.md` · [cumulative lineage summary](cninfo_a_class_erad_next_scale_slice1_cumulative_lineage_summary.md)（commit `4118974` / merge `71a83c1`）。

| 维度 | 指标 | 说明 |
|------|------|------|
| **Cumulative effective company codes** | **486** | scale-200 effective **192** + slice1 effective **294**（零 code 重叠） |
| **Cumulative executed case slots** | **500** | scale-200 **200** + slice1 **300** case_ids |
| **Cumulative acceptable cases** | **486/500** | 阶段 staged ~500 目标内 **97.2%** |
| **Slice1 effective（本包）** | **294/300** | gate **`PASS_WITH_CAVEAT`** · post-integration **HOLD** |
| **Scale-200 effective（前序）** | **192/200** | 已 merge closed · unresolved **8** 保留于 side-track |
| **Attribute coverage** | **UNKNOWN** | catalog completeness 本 run 未评分 |
| **Full-market completion %** | **UNKNOWN** | 全市场 universe 分母尚未采用，**486** 为 lineage 信号而非全市场占比 |

### Prior Packages（已并入 cumulative lineage）

| Stage | Case range | Effective | Unresolved |
|-------|------------|-----------|------------|
| Era D scale-200 | AD2E001–200 | **192** | **8**（side-track） |
| Era D next-scale slice1 | AD2E201–500 | **294** | **6**（本包 focus） |
| **Cumulative** | AD2E001–500 | **486** | **14**（8 + 6） |

---

## Missing Scope / Gap

### 1. 全市场分母缺口

全市场上市公司总数尚未作为正式分母采纳，因此 **无法计算 A 类相对全市场的完成百分比**。当前 **486** effective codes 仅代表 staged expansion path（~500 case slots）内的覆盖信号。

### 2. Slice1 Unresolved 6（本包未纳入 effective）

来源：[unresolved final ledger](cninfo_a_class_erad_next_scale_slice1_unresolved_final_ledger.csv) · [unresolved triage summary](cninfo_a_class_erad_next_scale_slice1_unresolved_triage_summary.md)。

| case_id | company_code | status | failure_class | report_type | expected_period | disposition |
|---------|--------------|--------|---------------|-------------|-----------------|-------------|
| AD2E216 | 601206 | not_found | not_found_or_matching_miss | annual_report | 2024-12-31 | accept_unresolved_with_caveat |
| AD2E270 | 603262 | not_found | not_found_or_matching_miss | quarterly_report_q3 | 2024-09-30 | accept_unresolved_with_caveat |
| AD2E284 | 603400 | not_found | not_found_or_matching_miss | annual_report | 2024-12-31 | accept_unresolved_with_caveat |
| AD2E308 | 603698 | not_found | not_found_or_matching_miss | semi_annual_report | 2024-06-30 | accept_unresolved_with_caveat |
| AD2E323 | 000559 | network_error | network_or_empty_response | annual_report | 2024-12-31 | accept_unresolved_with_caveat |
| AD2E373 | 002710 | not_found | not_found_or_matching_miss | annual_report | 2024-12-31 | accept_unresolved_with_caveat |

**Pattern breakdown：** not_found **5** · network_error **1** · 全部 `live_needed=no` · `retry_again=no`。

### 3. Scale-200 Side-Track Unresolved 8（不在本包 focus，但计入 cumulative gap）

AD2E066 · AD2E088 · AD2E119 · AD2E121 · AD2E122 · AD2E146 · AD2E185 · AD2E190

Ledger：[scale-200 unresolved final](../cninfo_a_class_erad_scale_200_unresolved_final_ledger.csv)

### 4. Attribute / Catalog Gap

属性维度覆盖未评分（**UNKNOWN**）。即使 company-code lineage 达 **486**，全市场 mission 在 attribute completeness 上仍有未量化缺口。

---

## Safe Next Offline Steps（可执行 · 无需 live 授权）

| 步骤 | 说明 |
|------|------|
| **Unresolved-6 offline packaging** | 生成本 run 的 [offline packaging CSV](cninfo_a_class_unresolved6_offline_packaging_20260714.csv)，供 Controller / human review |
| **Offline raw_metadata review** | 对 6 案已有 slice1 live 产物做 orgId / records / matching 离线审计（不发起新 CNINFO） |
| **Attribute-gap ledger** | 在 offline 层建立属性缺口台账，与 company-code lineage 分离统计 |
| **Next-scale slice2 planning** | 在 ~500 staged 目标完成后，规划下一批 universe 选取与 overlap lint（planning only） |
| **Cumulative unresolved triage** | 可选将 scale-200 unresolved **8** 与 slice1 unresolved **6** 合并为单一 offline caveat registry |

---

## Blocked Live Steps（需显式授权 · 本 run 禁止）

| 动作 | 阻断原因 |
|------|----------|
| CNINFO 调用 / live retry | post-integration **HOLD** · slice1 closure 已判定 **no further live retry** |
| 对 unresolved 6 发起 isolated retry | `live_needed=no` · 需 human 单独批准新 retry package |
| Gate 升级至 verified / production_ready | Executor 无权限 · 当前 **NOT verified** · **NOT production_ready** |
| push / remote publication | PROJECT_CONTROL blocked · **无 push** |
| PDF / OCR / DB / MinIO / RAG | 不在 A 类本任务授权范围 |

---

## Governance State（explicit）

| 字段 | 值 |
|------|-----|
| verified | **NOT verified** |
| production_ready | **NOT production_ready** |
| current gate | **`PASS_WITH_CAVEAT`**（slice1 merge closure · post-integration **HOLD**） |
| CNINFO（本分析） | **0** |
| integrated commits | `4118974` · merge `71a83c1` |

---

## Evidence Paths

- [cumulative lineage summary](cninfo_a_class_erad_next_scale_slice1_cumulative_lineage_summary.md)
- [unresolved final ledger](cninfo_a_class_erad_next_scale_slice1_unresolved_final_ledger.csv)
- [unresolved triage summary](cninfo_a_class_erad_next_scale_slice1_unresolved_triage_summary.md)
- [merge closure summary](cninfo_a_class_erad_next_scale_slice1_merge_closure_summary.md)
- [offline packaging CSV](cninfo_a_class_unresolved6_offline_packaging_20260714.csv)
