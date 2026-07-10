# CNINFO A 类 Phase 3 50-Company Merge Closure Review

_生成时间：2026-07-10_

> **性质：** Phase 3 merge closure 离线审阅；**无 CNINFO** · **无 live** · **无 rerun** · **不是 verified** · **不是 production_ready**

---

## 1. Objective

将 Phase 3 50-company live 结果合并进 A-class Phase 3 effective ledger，确认 **49/50 effective accepted metadata results**，显式登记 **1** 条 unresolved network caveat（A3M017），更新 closure metrics 与 summary。

**Closure gate：**

```text
a_class_phase3_50_company_closure_gate = PASS_WITH_CAVEAT
```

**Preserved execution gate：**

```text
a_class_phase3_50_company_execution_gate = PASS_WITH_CAVEAT
```

---

## 2. Phase 3 Live Recap

| 项 | 值 |
|----|-----|
| universe | **50**（A3M001–A3M050） |
| acceptable | **49/50** |
| failed | **1** |
| needs_review | **1** |
| CNINFO requests | **104** |
| PDF downloaded / parsed | **0 / 0** |
| matching_logic | **v2** |
| Phase 1 overlap | **0/50** |
| Phase 2 overlap | **0/50** |
| execution gate | `PASS_WITH_CAVEAT` |

**Live inputs（read-only）：**

- [expansion report](../outputs/validation/cninfo_a_class_phase3_50_company_expansion/reports/a_class_phase3_50_company_expansion_report.csv)
- [expansion summary](../outputs/validation/cninfo_a_class_phase3_50_company_expansion/reports/a_class_phase3_50_company_expansion_summary.md)
- [expansion quality report](../outputs/validation/cninfo_a_class_phase3_50_company_expansion/reports/a_class_phase3_50_company_expansion_quality_report.csv)
- [universe draft](../outputs/validation/cninfo_a_class_phase3_50_company_universe_draft.csv)
- raw_metadata × **50** under `cninfo_a_class_phase3_50_company_expansion/raw_metadata/`

**Live 报告未修改**（closure 仅读取）。

---

## 3. Effective Merge Composition

| 类别 | 数量 | final_effective_status |
|------|------|------------------------|
| Phase 3 live accepted | **49** | `accepted_phase3_live` |
| Unresolved / needs_review | **1** | `unresolved_network_orgid_failure` |
| **Total universe** | **50** | — |

**Effective accepted final：** **49/50**（98% metadata coverage）

---

## 4. Forty-Nine Accepted Case Summary

49 case 在 Phase 3 live 中 `found` · quality `pass` · lineage `discovered` · title/period pass · wrong_report_type=0 · pdf_url_present=yes · adjunct_url_present=yes。

**Preserved without rerun：** A3M001–A3M016 · A3M018–A3M050（**不重跑** successful 49）

Report-type mix preserved from universe：

- annual_report：**20/20** accepted（A3M017 excluded）
- semi_annual_report：**10/10** accepted
- quarterly_report_q1：**10/10** accepted
- quarterly_report_q3：**10/10** accepted（A3M050 included）

---

## 5. A3M017 Explicit Handling（不静默丢弃）

| 项 | 值 |
|----|-----|
| case_id | **A3M017** |
| company_code | **002352** |
| company_name | **顺丰控股** |
| market | SZSE |
| report_type | annual_report |
| expected_period | 2024-12-31 |
| phase3_live_status | `network_error` |
| failure_stage | **orgId_resolution** |
| failure_type | **network_error** |
| quality_status | `needs_review` |
| lineage_status | `needs_review` |
| cninfo_request_count（case） | **0**（orgId 阶段失败，未进入公告查询） |
| final_resolution_status | `unresolved_network_orgid_failure` |
| isolated_retry_recommended_later | **yes**（offline planning only · **NOT in this task**） |

**Notes：**

- 失败模式与 Phase 2 历史 orgId network_error 一致（Phase 2 retry_v3 曾恢复同类 case）
- **非** schema failure · **非** matching_logic failure · **非** wrong_report_type
- raw_metadata 已保留失败记录：[A3M017.json](../outputs/validation/cninfo_a_class_phase3_50_company_expansion/raw_metadata/A3M017.json)
- **不在 closure 任务中 live retry A3M017**

---

## 6. Phase 1 / Phase 2 Boundary

| 项 | 值 |
|----|-----|
| Phase 1 overlap | **0/50** |
| Phase 2 overlap | **0/50** |
| Phase 1 rerun | **no** |
| Phase 2 effective 20 rerun | **no** |
| Phase 2 reports mutated | **no** |
| retry / precheck reports mutated | **no** |

Phase 3 effective ledger **独立**于 Phase 2 effective ledger（`cninfo_a_class_phase2_metadata_merged_result_v3.csv` 未修改）。

---

## 7. Safety Red Lines（Closure Task）

| 项 | 值 |
|----|-----|
| CNINFO during closure | **0** |
| live rerun | **no** |
| Phase 3 49 successful rerun | **no** |
| A3M017 live retry | **no** |
| PDF download / parse | **0** |
| OCR / extraction | **0** |
| DB / MinIO / RAG | **0** |
| verified | **no** |
| production_ready | **no** |
| testing_stable_sample | **no** |
| commit | **no** |
| push | **no** |

---

## 8. Closure Outputs

| 产物 | 路径 |
|------|------|
| effective merged result | [cninfo_a_class_phase3_50_company_effective_merged_result.csv](../outputs/validation/cninfo_a_class_phase3_50_company_effective_merged_result.csv) |
| unresolved case ledger | [cninfo_a_class_phase3_50_company_unresolved_case_ledger.csv](../outputs/validation/cninfo_a_class_phase3_50_company_unresolved_case_ledger.csv) |
| closure metrics | [cninfo_a_class_phase3_50_company_closure_metrics.csv](../outputs/validation/cninfo_a_class_phase3_50_company_closure_metrics.csv) |
| closure summary | [cninfo_a_class_phase3_50_company_closure_summary.md](../outputs/validation/cninfo_a_class_phase3_50_company_closure_summary.md) |
| next-step recommendation | [cninfo_a_class_phase3_50_company_post_closure_next_step_recommendation.md](../outputs/validation/cninfo_a_class_phase3_50_company_post_closure_next_step_recommendation.md) |

---

## 9. Gate Decision

**49/50 accepted** with only documented **A3M017** network orgId caveat →

```text
a_class_phase3_50_company_closure_gate = PASS_WITH_CAVEAT
```

**不是 bare PASS** · **不是 verified** · **不是 production_ready**

---

## 10. Next Step

见 [post-closure next-step recommendation](../outputs/validation/cninfo_a_class_phase3_50_company_post_closure_next_step_recommendation.md)。

**不在此任务启动 commit boundary execution。**
