# CNINFO P1 Report Retrieval Quality Audit Round 2 Results

- 生成时间：2026-07-05（离线整理）
- 二轮抽样清单：[cninfo_report_p1_quality_audit_round2.md](cninfo_report_p1_quality_audit_round2.md)
- 二轮人工批注样本：[cninfo_report_p1_quality_audit_round2_sample.csv](cninfo_report_p1_quality_audit_round2_sample.csv)（含 `manual_*` / `manual_evidence_*` 字段）
- 一轮审计结论：[cninfo_report_p1_quality_audit_results.md](cninfo_report_p1_quality_audit_results.md)
- title-filter 修正后跑次：[cninfo_report_p1_coverage_validation_summary.md](cninfo_report_p1_coverage_validation_summary.md)
- P1 阶段总结：[cninfo_report_p1_coverage_final_summary.md](cninfo_report_p1_coverage_final_summary.md)

---

## 1. 二轮审计目的

**一轮 quality audit**（基于 title-filter **修正前** CSV，750 found）发现：

- found 样本标题级 pass rate 仅 **78%**（100 条中 pass 78、fail 22）；
- 主因是 **「披露提示性公告」** 等假阳性，集中在 SZSE 创业板 Q1/Q3；
- 粗算有效 coverage 约 **73.5%**，与自动 retrieval **94.22%** 差距大。

脚本已加入 **official report title filter**（全 `report_type` exclusion）。修正后自动跑次为 **749/796 = 94.10%**（`excluded_title_count = 0`）。

**二轮 audit 要验证：**

> title-filter 修正后的 **94.10% effective coverage**，在人工标题 / 联网证据复核下是否可信？一轮主因假阳性是否已消除？

**边界**：本文档仅整理二轮人工审计结果；**不写 verified**；**不写 full-market stable**。

---

## 2. 二轮样本设计

| 项 | 数值 |
|----|------|
| **总样本** | **50** |
| Q1 found | 15 |
| Q3 found | 15 |
| annual / semi found | 10 |
| not_found | 10 |
| **random seed** | **43** |

### 交易所 / 板块覆盖

| exchange | board | 条数 |
|----------|-------|------|
| SSE | 主板 | 13 |
| SSE | 科创板 | 11 |
| SZSE | 主板 | 11 |
| SZSE | 创业板 | 10 |
| BSE | 北交所 | 5 |

| exchange | 条数 |
|----------|------|
| SSE | 24 |
| SZSE | 21 |
| BSE | 5 |

覆盖 **SSE / SZSE / BSE** 及 **主板 / 创业板 / 科创板 / 北交所** 五层。Q1/Q3 样本内 `matched_strategy` 在 `keyword_recent` 与 `keyword_with_year` 间均衡抽取。

---

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| **total sample** | **50** |
| found sample | 40 |
| **found pass** | **39** |
| **found fail** | **1** |
| **found pass rate** | **39/40 = 97.5%** |
| not_found sample | 10 |
| **not_found pass**（脚本 not_found 合理） | **10** |
| uncertain | **0** |

审计员对 found 样本结合 **公告标题 + CNINFO `pdf_url` + 联网检索证据**（`manual_evidence_url`）完成复核；not_found 样本通过联网检索判断「对应期间正式报告是否存在」。

---

## 4. 与一轮 audit 对比

| 维度 | 一轮（seed=42，修正前 CSV） | 二轮（seed=43，修正后 CSV） |
|------|------------------------------|------------------------------|
| found 样本量 | 100 | 40 |
| **found pass rate** | **78%** | **97.5%** |
| found fail | 22 | **1** |
| 主要假阳性类型 | **披露提示性公告**（18/22 fail） | **延期披露公告**（1/1 fail） |
| 粗算有效 coverage | ~**73.5%** | ~**91.7%**（见 §7） |

**解释：**

- **title filter 对「披露提示性公告」类假阳性修正效果显著**；一轮中大量 fail 的创业板 Q1/Q3（如披露提示性公告）在二轮同类型正式标题下多为 pass；
- 二轮表明修正后的 **94.10% effective coverage 比旧口径（~73.5% 外推）可信得多**；
- 仍存 **1 类未覆盖假阳性**（延期披露），需在脚本中补 exclusion 后可选重跑。

---

## 5. 按 sample_group 结果

| sample_group | pass | fail | pass rate |
|--------------|------|------|-----------|
| quarterly_report_q1 found | 14 | 1 | 93.3% |
| quarterly_report_q3 found | **15** | **0** | **100%** |
| annual / semi found | **10** | **0** | **100%** |
| not_found | **10** | **0** | 100%（脚本判定合理） |

Q3、annual/semi、not_found 在本轮样本中 **无 fail**。Q1 唯一 fail 见 §6。

---

## 6. 唯一 fail 分析

| 字段 | 内容 |
|------|------|
| **audit_id** | P1-AUD2-006 |
| **company_code** | 300241 |
| **company_name** | 瑞丰光电 |
| **exchange / board** | SZSE / 创业板 |
| **report_type** | quarterly_report_q1 |
| **expected_period** | 2024Q1 |
| **announcement_title** | 2024-017 关于延期披露2023年年度报告及2024年第一季度报告的公告 |
| **manual_issue_type** | announcement_preview |
| **manual_audit_result** | fail |

**原因：** 该 PDF 为 **延期披露说明类公告**，告知年报/Q1 披露时间调整，**不是**正式 2024 年第一季度报告正文。

**脚本 gap：** 当前 `OFFICIAL_REPORT_TITLE_EXCLUSIONS` **未覆盖**「延期披露」类标题；title pattern 因含「第一季度报告」字样仍可能命中。

**修复建议（供下一轮脚本迭代）：**

- 在 official title exclusion 中新增：
  - `延期披露`
  - `关于延期披露`
- 可选：将 `延期披露…公告` 与 `披露提示性公告` 统一归为 `announcement_preview` 统计口径。

**证据（审计员记录）：** `manual_evidence_url` = `http://static.cninfo.com.cn/finalpage/2024-04-24/1219798014.PDF`

---

## 7. 对 effective coverage 的重新估计

| 口径 | 数值 | 说明 |
|------|------|------|
| 自动 **effective coverage** | **749/796 = 94.10%** | title-filter 修正后跑次 |
| 二轮 found **pass rate** | **97.5%** | 40 条 found 样本 |
| **粗算有效命中** | **749 × 97.5% ≈ 730** | 抽样外推 |
| **粗算有效 coverage** | **730/796 ≈ 91.7%** | 风险估算，非全量人工 accuracy |

**说明：**

- 以上为 **抽样外推**，不是对 796 行全量逐条人工核验；
- 相比一轮外推 **~73.5%**，**可信度明显提升**；
- 若补上「延期披露」exclusion 并重跑，粗算有效 coverage 有望接近或略高于 **91.7%**，仍须以重跑后 audit 或更大样本确认。

---

## 8. not_found 结论

二轮 **not_found 10 条全部判为 pass**（`manual_audit_result=pass`），即 **脚本 not_found 在本样本内合理**；**uncertain = 0**。

| failure_reason | 样本数 | 主要情形（审计员归纳） |
|----------------|--------|------------------------|
| period_mismatch | 8 | 新上市（如 688411、688449、688605）、2024 年 10 月后上市（301556）、历史/退市代码（600840、000522）— 对应 **2024H1 / 2024 年报本不存在** |
| empty_response | 2 | 历史样本（600840 新湖创业 Q3）、BSE 检索仍空（920106 林泰新材 Q3） |

**结论：**

- 暂未发现 **大面积 false negative**（`not_found_but_exists`）；
- not_found 更多反映 **样本状态 / 上市时点 / BSE residual**，而非 title filter 问题；
- BSE `empty_response` 与 920/430 码映射仍建议单独做 [P1 residual diagnostics](cninfo_report_p1_coverage_final_summary.md)（见 §10）。

---

## 9. recommended_status 建议

| 维度 | 建议 |
|------|------|
| 自动 effective coverage | **94.10%**（749/796，P1 样本） |
| 二轮审计后粗算有效 coverage | **~91.7%**（抽样外推） |
| 相对一轮 | 从「pending title-filter fix / ~73.5% 外推」**显著改善** |
| **P1 样本内状态** | 可调整为 **testing / usable candidate** |
| **verified** | **不写** |
| **full-market stable** | **不写** |
| 保留事项 | 补「延期披露」exclusion；BSE residual / 920-430 code diagnostics |

自动跑次摘要中的 **94.10%** 在二轮 audit 支持下，可作为 **retrieval mechanism 在 P1 分层样本上基本可用** 的依据；但 **不等于全市场 accuracy**，扩面前仍需 residual 与可选三轮 spot-check。

---

## 10. 下一步

1. **脚本**：在 `validate_cninfo_report_coverage.py` 的 official title exclusion 中加入 **`延期披露` / `关于延期披露`**；
2. **可选**：重跑 P1 coverage，确认 `found_after_title_filter` 与 fail 行是否归零；
3. **文档**：更新 [cninfo_report_p1_coverage_final_summary.md](cninfo_report_p1_coverage_final_summary.md)（有效 coverage ~91.7%、recommended_status）；
4. **Residual**：处理 BSE `empty_response`、920/430 old-new code、period_mismatch 新上市样本（见 coverage summary §14 remaining gaps）；
5. **暂缓**全市场扩展；可先完成 P1 residual diagnostics，必要时 **三轮 spot-check**（~30 条）。

---

## 11. 边界

- 本文档**仅整理**二轮人工审计结果；
- **未修改** coverage CSV、audit sample CSV、脚本；
- **未联网**（整理时）；审计证据来自审计员已填写的 `manual_evidence_*` 字段；
- **未重跑** coverage 脚本；
- **不写 verified**；结论仅代表 **P1 二轮 50 条抽样**，不代表全市场。

---

## 附录：二轮 fail 与 not_found 索引

### fail（1 条）

| audit_id | company_code | report_type | title（摘要） | issue_type |
|----------|--------------|-------------|---------------|------------|
| P1-AUD2-006 | 300241 | quarterly_report_q1 | 关于延期披露…第一季度报告的公告 | announcement_preview |

### not_found（10 条，均 pass）

| audit_id | company_code | report_type | failure_reason |
|----------|--------------|-------------|----------------|
| P1-AUD2-041 | 000522 | annual_report | period_mismatch |
| P1-AUD2-042 | 603194 | semi_annual_report | period_mismatch |
| P1-AUD2-043 | 688605 | semi_annual_report | period_mismatch |
| P1-AUD2-044 | 301556 | semi_annual_report | period_mismatch |
| P1-AUD2-045 | 600840 | semi_annual_report | period_mismatch |
| P1-AUD2-046 | 600840 | annual_report | period_mismatch |
| P1-AUD2-047 | 688449 | semi_annual_report | period_mismatch |
| P1-AUD2-048 | 688411 | semi_annual_report | period_mismatch |
| P1-AUD2-049 | 920106 | quarterly_report_q3 | empty_response |
| P1-AUD2-050 | 600840 | quarterly_report_q3 | empty_response |
