# CNINFO B 类 Phase 3 Failed Retry — Closure Review

_生成时间：2026-07-09_

> **性质：** 离线收口评审 + EP002 orgId failure triage；**无 CNINFO** · **无 live** · **无 rerun** · **不是 verified** · **不是 production_ready**

---

## 1. Objective

在 Phase 3 100-company expansion live（**1/100 acceptable**）与 failed-case isolated retry live（**8/99 recovered**）完成后，合并 original + retry 有效结果为 **9/100 effective accepted**，对 **91** 例 persistent EP002 orgId/network failure 做收口分类，并决定 Phase 3 expansion 在当前网络条件下的 closure posture。

**不**宣称 production readiness、verified 或 schema change。

---

## 2. Original Phase 3 Live Recap

| 指标 | 值 |
|------|-----|
| cases | **100**（B3E001–B3E100） |
| acceptable | **1**（B3E087 北新建材） |
| failed | **99** |
| CNINFO requests | **3** |
| dominant failure | `network_error` at **EP002_topSearch_orgId** |
| execution gate | `b_class_phase3_100_execution_gate = FAIL_REVIEW_REQUIRED` |
| PDF download / parse | **0** |

详见 [b_class_phase3_100_report.csv](../outputs/validation/cninfo_b_class_phase3_100_expansion/reports/b_class_phase3_100_report.csv)

---

## 3. Failed Retry Live Recap

| 指标 | 值 |
|------|-----|
| retry universe | **99**（B3E087 excluded） |
| retry acceptable | **8** |
| retry failed | **91** |
| CNINFO requests | **18** |
| dominant failure | `network_error` at **EP002_topSearch_orgId** |
| execution gate | `b_class_phase3_100_failed_retry_execution_gate = FAIL_REVIEW_REQUIRED` |
| PDF download / parse | **0** |

详见 [b_class_phase3_100_failed_retry_report.csv](../outputs/validation/cninfo_b_class_phase3_100_failed_retry/reports/b_class_phase3_100_failed_retry_report.csv)

---

## 4. B3E087 Hold Recap

| 项 | 值 |
|----|-----|
| case_id | **B3E087** |
| company | 北新建材（000786） |
| original result | found / pass / discovered |
| rerun_allowed | **no** |
| final_effective_status | `accepted_original_success` |
| source | `original_phase3_live` |

详见 [success hold ledger](../outputs/validation/cninfo_b_class_phase3_100_success_hold_ledger.csv)

---

## 5. Eight Recovered Retry Cases Recap

| case_id | company | original failure | retry result |
|---------|---------|------------------|--------------|
| B3E003 | 华夏银行 | ep002_orgid_resolution_failed | **found/pass/discovered** |
| B3E004 | 民生银行 | ep002_orgid_resolution_failed | **found/pass/discovered** |
| B3E005 | 日照港 | ep002_orgid_resolution_failed | **found/pass/discovered** |
| B3E006 | 上港集团 | ep002_orgid_resolution_failed | **found/pass/discovered** |
| B3E007 | 宝钢股份 | ep002_orgid_resolution_failed | **found/pass/discovered** |
| B3E008 | 浙能电力 | ep002_orgid_resolution_failed | **found/pass/discovered** |
| B3E009 | 华能水电 | ep002_orgid_resolution_failed | **found/pass/discovered** |
| B3E011 | 华电国际 | ep002_orgid_resolution_failed | **found/pass/discovered** |

全部 8 例均有 `pdf_url_present=1` · `pdf_downloaded=0`。

详见 [retry recovered case ledger](../outputs/validation/cninfo_b_class_phase3_100_retry_recovered_case_ledger.csv)

---

## 6. Ninety-One Persistent Failure Recap

| 指标 | 值 |
|------|-----|
| count | **91** |
| original status | network_error |
| retry status | network_error |
| failure stage | **EP002_topSearch_orgId** |
| schema_impact | **none** |
| quality_impact | **unresolved_network_caveat** |
| retry_again_candidate | **no**（默认，不自动批准 retry_v2） |

详见 [persistent failure ledger](../outputs/validation/cninfo_b_class_phase3_100_persistent_failure_ledger.csv)

---

## 7. EP002 OrgId Failure Pattern Analysis

| 观察 | 说明 |
|------|------|
| 失败阶段集中 | **EP002_topSearch_orgId** — orgId 解析步骤 |
| original CNINFO | **3** requests — 大规模早期 EP002 失败 |
| retry CNINFO | **18** requests — 部分 case 到达 EP001/EP004/EP005 |
| 8 例恢复 | 同一 orgId failure 类型在 retry 时 transient 恢复 |
| 91 例持续 | 同一基础设施条件下仍无法稳定解析 orgId |
| schema 证据 | **none** — 无字段缺失、无 parse shape break、无 endpoint model mismatch |

详见 [EP002 orgId failure analysis](../outputs/validation/cninfo_b_class_phase3_100_ep002_orgid_failure_analysis.csv)

---

## 8. Why This Remains Infrastructure/Network Caveat

1. 失败发生在 **EP002 orgId resolution**，早于 EP001 公告检索与 metadata 字段填充。
2. original 与 retry 均出现 **瞬态恢复**（1 + 8 例 found），说明非确定性网络/代理/可达性问题。
3. CNINFO 请求数远低于 planned cap（3 + 18 vs 200 + 198），符合 early-exit network failure 模式。
4. 恢复 case 的 `quality_status=pass` · `lineage_status=discovered` 表明 **一旦 orgId 可用，下游 metadata pipeline 正常**。

---

## 9. Why This Is Not Currently Schema Failure

| 检查 | 结果 |
|------|------|
| phase1_freeze_v1 字段 | 恢复 case 正常填充 |
| announcement_id / title / time | 8 例恢复 case 均有值 |
| pdf_url lineage | 8 例恢复 + 1 例 hold 均有 URL |
| parser / OCR / extraction 错误 | **0** |
| endpoint model change 需求 | **无** |

**结论：** 当前证据不支持 schema change 或 endpoint model change。

---

## 10. Why Immediate Rerun Is Not Recommended

1. **91/100** 仍 unresolved — 立即 full retry 预期重复 EP002 失败模式。
2. 已执行 isolated retry — 仅恢复 **8/99**，未达 **90/99** threshold。
3. 无 EP002 reachability precheck — 在 orgId 可达性未验证前 rerun 浪费 CNINFO quota。
4. B3E087 hold — 不得纳入任何 rerun batch。
5. Phase 3 scope 固定 **100** — 不得扩展 universe。

**推荐：** Option A — EP002/orgId reachability precheck package（见 [next-step recommendation](cninfo_b_class_phase3_100_post_failed_retry_next_step_recommendation.md)）

---

## 11. Red-Line Confirmations

| 项 | 状态 |
|----|------|
| CNINFO calls（本回合 closure） | **0** |
| live / retry execution（本回合） | **0** |
| B3E087 rerun | **no** |
| prior-phase rerun | **no** |
| original Phase 3 reports mutated | **no** |
| failed-retry reports mutated | **no** |
| Phase 2.5 reports mutated | **no** |
| PDF / OCR / extraction / DB / MinIO / RAG | **0** |
| verified / production_ready | **no** |
| schema change | **no** |
| endpoint model change | **no** |

---

## 12. Combined Effective Result

| 来源 | 数量 | final_effective_status |
|------|------|------------------------|
| original_phase3_live（B3E087 hold） | **1** | `accepted_original_success` |
| phase3_failed_retry recovered | **8** | `accepted_retry_recovered` |
| original + retry persistent | **91** | `unresolved_ep002_orgid_network_failure` |
| **合计 accepted** | **9** | |
| **合计 unresolved** | **91** | |

详见 [effective merged result](../outputs/validation/cninfo_b_class_phase3_100_effective_merged_result.csv)

---

## 13. Closure Decision Options

| Option | 描述 | 推荐 |
|--------|------|------|
| **A** | EP002/orgId reachability precheck before retry_v2 | **Recommended** |
| **B** | Hold Phase 3 with network caveat; no retry until infra stabilizes | Acceptable |
| **C** | Offline orgId resolution fallback design investigation | Secondary |
| **D** | Commit Phase 3 attempt + caveat after closure review | After A/B decision |

**Closure gate（本回合）：**

```text
b_class_phase3_100_failed_retry_closure_gate = PASS_WITH_CAVEAT_NETWORK_UNRESOLVED
```

**不是 PASS** · **不是 verified** · **不是 production_ready**
