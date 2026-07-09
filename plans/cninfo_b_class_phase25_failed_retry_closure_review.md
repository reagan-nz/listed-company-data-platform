# CNINFO B 类 Phase 2.5 Failed Retry — Closure Review

_生成时间：2026-07-09_

> **性质：** 离线收口评审；**无 CNINFO** · **无 live** · **无 rerun** · **不是 verified** · **不是 production_ready**

---

## 1. Objective

在 Phase 2.5 主 batch（50 家）产生 **45/50 acceptable** 后，对 **5** 例 `network_error` / orgId 失败 case 执行 isolated retry，并将 **original + retry** 合并为 **50/50 effective metadata coverage** 收口文档。

**不**宣称 production readiness 或 verified。

---

## 2. Original Phase 2.5 Result

| 指标 | 值 |
|------|-----|
| cases | **50** |
| acceptable | **45** |
| failed | **5** |
| CNINFO requests | **93** |
| execution gate | `b_class_phase25_expansion_execution_gate = PASS_WITH_CAVEAT` |
| closure gate | `b_class_phase25_expansion_closure_gate = PASS_WITH_CAVEAT` |

---

## 3. Failed Case Triage Recap

| case_id | company | failure_type | schema_impact | quality_impact |
|---------|---------|--------------|---------------|----------------|
| B25E003 | 工商银行 | network_timeout | none | retry_needed |
| B25E008 | 中兴通讯 | proxy_503 | none | retry_needed |
| B25E032 | 传音控股 | network_timeout | none | retry_needed |
| B25E039 | 比亚迪 | ep002_orgid_resolution_failed | none | retry_needed |
| B25E040 | 牧原股份 | ep002_orgid_resolution_failed | none | retry_needed |

**分类结论：** 全部为 network/proxy/orgId 瞬态问题 — **非 schema failure**

详见 [failed-case triage](../outputs/validation/cninfo_b_class_phase25_failed_case_triage.csv)

---

## 4. Isolated Retry Scope

| 项 | 值 |
|----|-----|
| retry cases | **5** only |
| successful cases excluded | **45** |
| output root | `outputs/validation/cninfo_b_class_phase25_failed_retry/` |
| Phase 2.5 expansion baseline | **write-blocked / untouched** |
| metadata + URL lineage only | **yes** |
| PDF download / parse | **0** |

---

## 5. Retry Result

| 指标 | 值 |
|------|-----|
| retry cases | **5** |
| retry acceptable | **5** |
| retry failed | **0** |
| CNINFO requests | **10** |
| execution gate | `b_class_phase25_failed_retry_execution_gate = PASS_WITH_CAVEAT` |

全 **5** 例 retry 均为 `found/pass/discovered`。

---

## 6. Recovered Case List

| case_id | company | original | retry result |
|---------|---------|----------|--------------|
| B25E003 | 工商银行 | network_timeout | **found/pass/discovered** |
| B25E008 | 中兴通讯 | proxy_503 | **found/pass/discovered** |
| B25E032 | 传音控股 | network_timeout | **found/pass/discovered** |
| B25E039 | 比亚迪 | ep002_orgid_resolution_failed | **found/pass/discovered** |
| B25E040 | 牧原股份 | ep002_orgid_resolution_failed | **found/pass/discovered** |

---

## 7. Combined 50/50 Effective Coverage

| 来源 | 数量 | final_effective_status |
|------|------|------------------------|
| original_phase25_live | **45** | `accepted_original_success` |
| phase25_failed_retry | **5** | `accepted_retry_recovered` |
| **合计** | **50** | **0 unresolved** |

详见 [effective merged result](../outputs/validation/cninfo_b_class_phase25_effective_merged_result.csv)

---

## 8. URL Lineage Status

| 指标 | 值 |
|------|-----|
| pdf_url_present（effective 50） | **50/50** |
| adjunct_url_present（effective 50） | **50/50** |
| pdf_downloaded | **0** |
| pdf_parsed | **0** |

所有 effective case 均登记 URL lineage；**无文件落盘**。

---

## 9. PDF Boundary Confirmation

| 项 | 值 |
|----|-----|
| PDF download | **0** |
| PDF parse | **0** |
| OCR | **0** |
| section extraction | **0** |
| `.pdf` files in output trees | **0** |

---

## 10. Output Isolation Confirmation

| 根 | 状态 |
|----|------|
| `cninfo_b_class_phase25_expansion/` | 主 batch 产物（**45 found 行未修改**） |
| `cninfo_b_class_phase25_failed_retry/` | retry 产物（**5 case**） |
| Phase 1 / TLC002 / Phase 2 / C-class | **unchanged** |

---

## 11. Why Failures Were Not Schema Issues

1. **network_timeout / proxy_503** — 请求未返回或代理中断；retry 同 endpoint 成功
2. **ep002_orgid_resolution_failed** — orgId 查找瞬态失败；retry 后 EP002 + EP001 正常
3. 失败 case 无 schema 字段违规 · 无 required field 系统性缺失
4. retry 恢复后 quality_status **pass** · lineage_status **discovered** — 与成功 case 一致
5. Phase 1 TLC002 先例：同类 orgId 失败经 isolated retry 恢复

---

## 12. Non-Production Claim

```text
NOT verified
NOT production_ready
NOT testing_stable_sample upgrade
NOT PASS (use PASS_WITH_CAVEAT only)
```

Phase 2.5 + retry 为 **limited expansion**（50 家）；不足以支撑全市场 production readiness。

---

## 13. Next Options

| Option | 内容 | 推荐 |
|--------|------|------|
| A | B-class Phase 2.5 commit boundary | **推荐优先** |
| B | Phase 3 100-company planning only | 不立即 live |
| C | A/B lineage integration design | 可并行 |
| D | title/date matching hardening | 可并行 |

详见 [post-retry next-step recommendation](cninfo_b_class_phase25_post_retry_next_step_recommendation.md)

---

## Related Artifacts

| 文档 | 路径 |
|------|------|
| expansion closure summary | [cninfo_b_class_phase25_expansion_closure_summary.md](../outputs/validation/cninfo_b_class_phase25_expansion_closure_summary.md) |
| retry report | [b_class_phase25_failed_retry_report.csv](../outputs/validation/cninfo_b_class_phase25_failed_retry/reports/b_class_phase25_failed_retry_report.csv) |
| merged effective result | [cninfo_b_class_phase25_effective_merged_result.csv](../outputs/validation/cninfo_b_class_phase25_effective_merged_result.csv) |
| retry closure metrics | [cninfo_b_class_phase25_failed_retry_closure_metrics.csv](../outputs/validation/cninfo_b_class_phase25_failed_retry_closure_metrics.csv) |
| final closure summary | [cninfo_b_class_phase25_failed_retry_closure_summary.md](../outputs/validation/cninfo_b_class_phase25_failed_retry_closure_summary.md) |
