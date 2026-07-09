# CNINFO B 类 Phase 2 Expansion — Closure Review

_生成时间：2026-07-09_

> **性质：** 离线收口评审；**无 CNINFO** · **无 live** · **无 rerun** · **不是 verified** · **不是 production_ready**

---

## 1. Objective

在 Phase 1 tiny live（5 家）收口后，将 B-class live metadata validation 扩大至 **Option A（20 家）**，验证：

- phase1_freeze_v1 schema **不变** 前提下，EP001/EP002/EP004/EP005 在更多板块与公司上的稳定性
- announcement metadata + pdf URL lineage（**不下载**）可重复执行
- 专用输出隔离根可承载更大批次产物
- **不**宣称 production readiness 或 verified

---

## 2. Phase 1 Baseline Recap

| 项 | 值 |
|----|-----|
| closure gate | `b_class_phase1_tiny_live_closure_gate = PASS_WITH_CAVEAT` |
| cases | **5** · resolved **5** · failed **0** |
| TLC002 | EP002 `network_error` → isolated retry → `found/pass/discovered` |
| validated endpoints | EP001 · EP002 · EP004 · EP005 |
| PDF / DB / MinIO / RAG | **0** |
| verified | **false** |

Phase 1 证明极小样本 metadata-only live 路径可行；Phase 2 在 **不修改 Phase 1 产物** 前提下扩大样本。

---

## 3. Phase 2 Scope

| 项 | 内容 |
|----|------|
| universe | B2E001–B2E020（**20** 家） |
| schema | phase1_freeze_v1 · **15** required fields（**unchanged**） |
| endpoints | EP001 · EP002 · EP004 · EP005 |
| announcement types | periodic_report（**12**）· general_announcement（**8**） |
| 允许 | metadata retrieval · announcement lineage · pdf URL lineage |
| 禁止 | PDF download/parse · OCR · section extraction · DB/MinIO/RAG · verified |

**输出隔离：** `outputs/validation/cninfo_b_class_phase2_expansion/`

**未触碰：** Phase 1 tiny live · TLC002 retry · A/C/D-class 输出

---

## 4. Universe Coverage

| 市场 | 公司数 | case 示例 |
|------|--------|-----------|
| SZSE主板 | **8** | 平安银行 · 万科A · 五粮液 · 格力电器 · 京东方A · 海康威视 · 美的集团 |
| SSE主板 | **8** | 贵州茅台 · 招商银行 · 中国平安 · 中国中免 · 恒瑞医药 · 中国石油 · 浦发银行 · 中国人寿 |
| 创业板 | **3** | 东方财富 · 宁德时代 · 汇川技术 |
| 科创板 | **2** | 金山办公 · 天合光能 |

**Bucket 覆盖：** mainboard annual report · financial · consumer · manufacturing · technology · growth board · STAR board · general announcements

**筛选规则：** 活跃上市 · 非 ST · 非退市 · 非 BSE legacy · 无 manual identity review

---

## 5. Endpoint Coverage

| Endpoint | Hits | Role |
|----------|------|------|
| EP001 | **20** | hisAnnouncement/query 主公告检索 |
| EP002 | **20** | topSearch/query orgId 辅助 |
| EP004 | **12** | cninfo_periodic_report_pdf metadata lineage |
| EP005 | **8** | cninfo_general_announcement_pdf metadata lineage |

**CNINFO requests（live batch）：** **40**（每 case 约 EP002 + EP001）  
**收口回合 CNINFO：** **0**

EP003 removed · EP006/EP007 deferred — **未使用**

---

## 6. Execution Result

| 指标 | 值 |
|------|-----|
| cases | **20** |
| acceptable | **20** |
| failed | **0** |
| needs_review | **0** |
| empty_but_valid | **0** |
| retrieval_status | **found**（全 20） |
| quality_status | **pass**（全 20） |
| lineage_status | **discovered**（全 20） |
| execution gate | `b_class_phase2_expansion_execution_gate = PASS_WITH_CAVEAT` |

全 case 无 `network_error` · 无 `http_429` · 无 inline retry 需求。

---

## 7. URL Lineage Result

| 指标 | 值 |
|------|-----|
| pdf_url_present | **20/20** |
| adjunct_url_present | **20/20** |
| pdf_downloaded | **0** |
| pdf_parsed | **0** |

所有 case 均登记 `adjunct_url` / `pdf_url`（CNINFO static URL 拼接）；**无文件落盘**。

---

## 8. PDF Boundary Confirmation

| 项 | 值 |
|----|-----|
| PDF download | **0** |
| PDF parse | **0** |
| OCR | **0** |
| section extraction | **0** |
| runner flags `--download-pdf` / `--parse-pdf` | **未使用** |

Phase 2 严格 metadata + URL lineage only。

---

## 9. Output Isolation

| 根目录 | 状态 |
|--------|------|
| `cninfo_b_class_phase2_expansion/` | **写入**（本批次唯一 live 产物） |
| `cninfo_b_class_tiny_live_validation/` | **未修改** |
| `cninfo_b_class_tlc002_retry/` | **未修改** |
| `outputs/harvest/cninfo_c_class/` | **未修改** |

---

## 10. Quality Policy Result

对齐 Phase 1 freeze v1 口径：

- 必填字段齐全 → `quality_status=pass` · `lineage_status=discovered`
- 无 `verified` 升级
- 无 `testing_stable_sample` 升级
- 无 forced category mapping
- 本批次无 `needs_review` / `caveat` case

---

## 11. Known Caveats

1. **样本量仍有限：** 20 家虽覆盖四板块，但非全市场代表性样本。
2. **无 PDF 内容验证：** URL lineage 存在不等于 PDF 可下载或可解析。
3. **标题匹配启发式：** periodic_report 依赖年度报告标题规则；general 取最新公告，未必为业务最优代表。
4. **无并发/长时间压测：** 单次顺序执行，未观测 rate limit 或长时间批次稳定性。
5. **Phase 1 TLC002 教训未在本批次复现：** EP002 transient error 频率仍未知。
6. **schema freeze v1 未因 Phase 2 扩展而变更。**

---

## 12. Non-Production Claim

```text
b_class_phase2_expansion_closure_gate = PASS_WITH_CAVEAT
```

**Explicitly NOT:**

- `PASS`（全量通过口径）
- `verified`
- `production_ready`
- `testing_stable_sample` upgrade
- `full_b_class_support`

Phase 2 Option A（20 家）metadata expansion **收口完成**；**不是** B-class 生产就绪声明。

---

## 13. Recommended Next Options

| Option | 说明 | 优先级 |
|--------|------|--------|
| **A** | Hold at 20 · **commit boundary** after closure | **推荐首先** |
| **B** | Prepare 50-company Phase 2.5 expansion planning（offline） | 次选 |
| **C** | B-class + A-class report/announcement lineage integration design | 次选 |
| **D** | Title/date matching hardening before further expansion | 可选 |

**不推荐：** 立即 100-company live expansion。

详见 [cninfo_b_class_phase2_next_step_recommendation.md](cninfo_b_class_phase2_next_step_recommendation.md)

---

## 14. Related Artifacts

| 文档 | 路径 |
|------|------|
| expansion plan | [cninfo_b_class_phase2_expansion_plan.md](cninfo_b_class_phase2_expansion_plan.md) |
| universe draft | [cninfo_b_class_phase2_expansion_universe_draft.csv](../outputs/validation/cninfo_b_class_phase2_expansion_universe_draft.csv) |
| approval summary | [cninfo_b_class_phase2_expansion_approval_summary.md](../outputs/validation/cninfo_b_class_phase2_expansion_approval_summary.md) |
| execution report | [b_class_phase2_expansion_report.csv](../outputs/validation/cninfo_b_class_phase2_expansion/reports/b_class_phase2_expansion_report.csv) |
| execution summary | [b_class_phase2_expansion_summary.md](../outputs/validation/cninfo_b_class_phase2_expansion/reports/b_class_phase2_expansion_summary.md) |
| closure metrics | [cninfo_b_class_phase2_expansion_closure_metrics.csv](../outputs/validation/cninfo_b_class_phase2_expansion_closure_metrics.csv) |
| closure summary | [cninfo_b_class_phase2_expansion_closure_summary.md](../outputs/validation/cninfo_b_class_phase2_expansion_closure_summary.md) |

---

## 15. Red Lines（收口回合）

- No CNINFO · No live · No rerun · No retry
- No expansion to 50/100 in this round
- No PDF · No DB · No MinIO · No RAG
- No verified · No production_ready · No commit in this round
