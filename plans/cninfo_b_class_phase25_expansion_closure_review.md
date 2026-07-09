# CNINFO B 类 Phase 2.5 Expansion — Closure Review

_生成时间：2026-07-09_

> **性质：** 离线收口评审；**无 CNINFO** · **无 live** · **无 rerun** · **不是 verified** · **不是 production_ready**

---

## 1. Objective

在 Phase 2（20 家）收口后，将 B-class live metadata validation 扩大至 **50 家（Phase 2.5）**，验证：

- phase1_freeze_v1 schema **不变** 前提下，EP001/EP002/EP004/EP005 在更大样本、更多板块与公司上的稳定性
- announcement metadata + pdf URL lineage（**不下载**）可在 50-case 批次下达到 **45/50 acceptable** 阈值
- 专用输出隔离根可承载 Phase 2.5 产物
- 对 **5** 例 `network_error` 进行失败分类与 isolated retry 规划（**本回合不执行 retry**）
- **不**宣称 production readiness 或 verified

---

## 2. Phase 2 Baseline Recap

| 项 | 值 |
|----|-----|
| closure gate | `b_class_phase2_expansion_closure_gate = PASS_WITH_CAVEAT` |
| cases | **20** · acceptable **20** · failed **0** |
| CNINFO requests | **40** |
| endpoint hits | EP001 **20** · EP002 **20** · EP004 **12** · EP005 **8** |
| URL lineage | pdf_url_present **20/20** · adjunct_url_present **20/20** |
| PDF / DB / MinIO / RAG | **0** |
| verified | **false** |

Phase 2 Option A 证明 20 家批次可全量 `found/pass/discovered`；为 Phase 2.5 扩大提供基线，但不足以推断 50 家批次的 transient failure 率。

---

## 3. Phase 2.5 Scope

| 项 | 内容 |
|----|------|
| universe | B25E001–B25E050（**50** 家） |
| schema | phase1_freeze_v1 · **15** required fields（**unchanged**） |
| endpoints | EP001 · EP002 · EP004 · EP005 |
| announcement types | periodic_report（**25**）· general_announcement（**25**） |
| phase1_overlap | **0** |
| phase2_overlap | **0** |
| 允许 | metadata retrieval · announcement lineage · pdf URL lineage |
| 禁止 | PDF download/parse · OCR · section extraction · DB/MinIO/RAG · verified |

**输出隔离：** `outputs/validation/cninfo_b_class_phase25_expansion/`

**未触碰：** Phase 1 tiny live · TLC002 retry · Phase 2 expansion · A/C/D-class 输出

---

## 4. Universe Coverage

| 市场 | 公司数 |
|------|--------|
| SSE主板 | **27** |
| SZSE主板 | **13** |
| 创业板 | **5** |
| 科创板 | **5** |

| 公告类型 | 公司数 |
|----------|--------|
| periodic_report（EP004） | **25** |
| general_announcement（EP005） | **25** |

**EP002 financial cases：** **7**（B25E002–B25E006 · B25E019–B25E020）

**Bucket 覆盖：** 大型银行/保险 · 能源/制造 · 消费 · 科技 · 创业板一般公告 · 科创板一般公告 · SSE/SZSE 一般公告分流

**筛选规则：** 活跃上市 · 非 ST · 非退市 · 刻意零重叠 Phase 1/2

---

## 5. Endpoint Coverage

| Endpoint | Hits | Role |
|----------|------|------|
| EP001 | **45** | hisAnnouncement/query 主公告检索（成功 case） |
| EP002 | **48** | topSearch/query orgId 辅助（含失败 case 部分请求） |
| EP004 | **25** | cninfo_periodic_report_pdf metadata lineage |
| EP005 | **25** | cninfo_general_announcement_pdf metadata lineage |

**CNINFO requests（live batch）：** **93**（计划 **100**；5 例失败提前终止部分请求）  
**收口回合 CNINFO：** **0**

EP003 removed · EP006/EP007 deferred — **未使用**

---

## 6. Execution Result

| 指标 | 值 |
|------|-----|
| cases | **50** |
| acceptable | **45** |
| failed | **5** |
| needs_review | **5** |
| empty_but_valid | **0** |
| retrieval_status found | **45** |
| retrieval_status network_error | **5** |
| execution gate | `b_class_phase25_expansion_execution_gate = PASS_WITH_CAVEAT` |

**阈值：** acceptable ≥ **45/50** — **达标**

---

## 7. 45 Acceptable Case Result

| 指标 | 值 |
|------|-----|
| retrieval_status | **found**（全 45） |
| quality_status | **pass**（全 45） |
| lineage_status | **discovered**（全 45） |
| pdf_url_present | **45/45** |
| adjunct_url_present | **45/45** |
| pdf_downloaded | **0** |
| pdf_parsed | **0** |

45 例成功 case 均完成 metadata 检索与 URL lineage 登记；质量检查通过；**无 PDF 落盘**。

---

## 8. 5 network_error Case Triage

| case_id | company | failure | failure_stage | retry |
|---------|---------|---------|---------------|-------|
| B25E003 | 工商银行 | network_timeout | EP001/EP004 fetch | yes |
| B25E008 | 中兴通讯 | proxy_503 | EP001 hisAnnouncement | yes |
| B25E032 | 传音控股 | network_timeout | EP001/EP005 fetch | yes |
| B25E039 | 比亚迪 | ep002_orgid_resolution_failed | EP002 topSearch | yes |
| B25E040 | 牧原股份 | ep002_orgid_resolution_failed | EP002 topSearch | yes |

**分类结论：**

- **schema_impact = none** — 无字段缺失、无 schema 违规；失败发生在网络/代理/orgId 解析阶段
- **quality_impact = retry_needed** — 需 isolated retry，**非** schema failure
- 3 例 transient network（timeout/proxy）· 2 例 EP002 orgId（与 Phase 1 TLC002 模式类似）

详见 [failed-case triage CSV](../outputs/validation/cninfo_b_class_phase25_failed_case_triage.csv)

---

## 9. URL Lineage Result

| 指标 | 值 |
|------|-----|
| pdf_url_present（acceptable） | **45/45** |
| adjunct_url_present（acceptable） | **45/45** |
| pdf_url_present（failed） | **0/5**（未检索到公告） |
| pdf_downloaded | **0** |
| pdf_parsed | **0** |

成功 case 均登记 `adjunct_url` / `pdf_url`（CNINFO static URL 拼接）；失败 case 无 URL lineage（符合预期）。

---

## 10. PDF Boundary Confirmation

| 项 | 值 |
|----|-----|
| PDF download | **0** |
| PDF parse | **0** |
| OCR | **0** |
| section extraction | **0** |
| `.pdf` files in output tree | **0** |

metadata + URL lineage only — **边界保持**

---

## 11. Output Isolation

| 根 | 状态 |
|----|------|
| `cninfo_b_class_phase25_expansion/` | Phase 2.5 live 产物 |
| Phase 1 tiny live | **unchanged** |
| TLC002 retry | **unchanged** |
| Phase 2 expansion | **unchanged** |
| C-class | **`SNAPSHOT_GENERATED_QA_REVIEW`** |

---

## 12. Quality Policy Result

| 策略 | 结果 |
|------|------|
| acceptable threshold | **45/50** met |
| needs_review 处理 | 5 例 network_error → triage · retry_candidate |
| verified 禁止 | **enforced** |
| production_ready 禁止 | **enforced** |
| empty_but_valid | **0** |

---

## 13. Known Caveats

1. **5/50 network_error** — 非 schema 问题；建议 isolated retry（5 case only）
2. **CNINFO 93 vs 计划 100** — 失败 case 提前终止部分请求
3. **EP002 orgId** — B25E039/B25E040 在 general_announcement 路径仍触发 EP002；与 TLC002 模式一致
4. **proxy 503** — B25E008 为环境/代理 transient；非 CNINFO schema 变更
5. **title 选取** — 部分 periodic case 命中英文年报或制度类公告（如 B25E012）；quality pass 但需后续 title matching hardening（Option D）
6. **50 家仍非全市场** — 不足以支撑 production readiness 或 verified 声明

---

## 14. Non-Production Claim

```text
NOT verified
NOT production_ready
NOT testing_stable_sample upgrade
NOT PASS (use PASS_WITH_CAVEAT only)
```

Phase 2.5 为 **limited expansion**（50 家）；5 例失败待 isolated retry 决策。

---

## 15. Recommended Next Options

| Option | 内容 | 推荐 |
|--------|------|------|
| A | Commit Phase 2.5 closure boundary | 收口后版本节点 |
| B | Prepare isolated retry for 5 failed cases | **推荐优先** |
| C | 100-company planning only（after retry decision） | 不立即 live |
| D | B/A lineage integration design | 可并行 |

**明确不推荐：** 立即 100-company live expansion · 在未 retry 决策前扩大样本 · verified / production_ready

详见 [next-step recommendation](cninfo_b_class_phase25_next_step_recommendation.md)

---

## Related Artifacts

| 文档 | 路径 |
|------|------|
| expansion plan | [cninfo_b_class_phase25_expansion_plan.md](cninfo_b_class_phase25_expansion_plan.md) |
| execution report | [b_class_phase25_expansion_report.csv](../outputs/validation/cninfo_b_class_phase25_expansion/reports/b_class_phase25_expansion_report.csv) |
| execution summary | [b_class_phase25_expansion_summary.md](../outputs/validation/cninfo_b_class_phase25_expansion/reports/b_class_phase25_expansion_summary.md) |
| failed-case triage | [cninfo_b_class_phase25_failed_case_triage.csv](../outputs/validation/cninfo_b_class_phase25_failed_case_triage.csv) |
| retry planning note | [cninfo_b_class_phase25_failed_retry_planning_note.md](cninfo_b_class_phase25_failed_retry_planning_note.md) |
| closure metrics | [cninfo_b_class_phase25_expansion_closure_metrics.csv](../outputs/validation/cninfo_b_class_phase25_expansion_closure_metrics.csv) |
| closure summary | [cninfo_b_class_phase25_expansion_closure_summary.md](../outputs/validation/cninfo_b_class_phase25_expansion_closure_summary.md) |
