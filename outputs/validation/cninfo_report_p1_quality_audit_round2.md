# CNINFO P1 Report Retrieval 二轮 Quality Audit

- 生成时间：2026-07-05T03:21:34Z
- 来源 CSV：[cninfo_report_p1_coverage_validation.csv](cninfo_report_p1_coverage_validation.csv)（**title-filter 修正后**跑次）
- 跑次摘要：[cninfo_report_p1_coverage_validation_summary.md](cninfo_report_p1_coverage_validation_summary.md)
- 一轮审计结论：[cninfo_report_p1_quality_audit_results.md](cninfo_report_p1_quality_audit_results.md)
- 抽样清单：[cninfo_report_p1_quality_audit_round2_sample.csv](cninfo_report_p1_quality_audit_round2_sample.csv)
- 一轮样本（对照）：[cninfo_report_p1_quality_audit_sample.csv](cninfo_report_p1_quality_audit_sample.csv)

---

## 1. 本轮目的

title-filter 修正后，P1 **effective coverage** 为 **749/796 = 94.10%**，`excluded_title_count = 0`。

但 **一轮 quality audit**（基于修正前 CSV）显示：

- found 样本标题级 pass rate 仅 **78%**（100 条中 fail 22）；
- 主因是「披露提示性公告」等假阳性，集中在 SZSE 创业板 Q1/Q3。

脚本已加入 **official report title filter**（全 report_type exclusion）。本轮二轮审计要回答：

> **修正后的 94.10% retrieval coverage，在人工标题/PDF 复核下是否可信？假阳性是否已显著下降？**

**边界**：本文档与 CSV **仅生成抽样清单**；未联网、未打开 PDF、**不写 verified**。

---

## 2. 与一轮审计的区别

| 维度 | 一轮（seed=42） | 二轮（seed=43） |
|------|----------------|----------------|
| 依据 CSV | title-filter **修正前**（750 found） | title-filter **修正后**（749 found） |
| 样本量 | 120 | **50** |
| 重点 | 发现假阳性类型 | **验证修正后 found 是否仍含假阳性** |
| Q1/Q3 权重 | 各 30 found | 各 **15** found（仍为重点） |

---

## 3. 抽样设计

| sample_group | 目标 | 实际 | 池内可用 |
|--------------|------|------|----------|
| quarterly_report_q1 found | 15 | 15 | 184 |
| quarterly_report_q3 found | 15 | 15 | 187 |
| annual / semi found | 10 | 10 | 193 + 185（annual 5 + semi 5） |
| not_found | 10 | 10 | 47 |

- **random seed**：`43`
- **实际抽样总数**：**50**

### 交易所覆盖

| exchange | 条数 |
|----------|------|
| BSE | 5 |
| SSE | 24 |
| SZSE | 21 |

### exchange × board 覆盖

| exchange | board | 条数 |
|----------|-------|------|
| BSE | 北交所 | 5 |
| SSE | 主板 | 13 |
| SSE | 科创板 | 11 |
| SZSE | 主板 | 11 |
| SZSE | 创业板 | 10 |

### Q1/Q3 matched_strategy 分布（样本内）

| sample_group | matched_strategy | 条数 |
|--------------|------------------|------|
| quarterly_report_q1_found | keyword_recent | 8 |
| quarterly_report_q1_found | keyword_with_year | 7 |
| quarterly_report_q3_found | keyword_recent | 8 |
| quarterly_report_q3_found | keyword_with_year | 7 |

### not_found failure_reason（样本内）

| failure_reason | 条数 |
|----------------|------|
| empty_response | 2 |
| period_mismatch | 8 |

各 sample_group 均达到目标条数。

---

## 4. 怎么人工检查

与一轮相同，对 [cninfo_report_p1_quality_audit_round2_sample.csv](cninfo_report_p1_quality_audit_round2_sample.csv) 每一行：

1. 打开 `pdf_url`（found 样本）；
2. 核对标题是否为**正式报告**（非披露提示/说明会/问询函回复/摘要）；
3. 确认公司、report_type、report_period 正确；
4. not_found 样本在 CNINFO 页面二次检索，判断是否 `not_found_but_exists`。

**本轮特别关注：**

- Q1/Q3 是否仍出现「披露提示性公告」类假阳性（一轮 fail 主因）；
- annual/semi 是否仍有问询函回复被误标 found；
- 修正后 `excluded_title_count=0` 是否与人感一致。

---

## 5. 人工字段填写说明

填写 CSV 中 `manual_*` 列（默认 `pending`）：

| 字段 | 说明 |
|------|------|
| `manual_pdf_opens` | PDF 是否可打开 |
| `manual_is_official_report` | 是否为正式报告全文 |
| `manual_company_correct` | 公司是否正确 |
| `manual_report_type_correct` | 报告类型是否正确 |
| `manual_period_correct` | 报告期是否正确 |
| `manual_title_problem` | 标题问题简述 |
| `manual_issue_type` | `ok` / `announcement_preview` / `title_false_positive` / … |
| `manual_audit_result` | `pass` / `fail` / `uncertain` / `pending` |
| `manual_auditor_notes` | 补充说明 |

---

## 6. 审计完成后如何解读

建议统计并与一轮对比：

| 指标 | 一轮（修正前 CSV） | 二轮（目标） |
|------|-------------------|--------------|
| found 样本 pass rate | **78%** | 应 **显著高于 78%** |
| `announcement_preview` fail | 18/22 | 应 **接近 0** |
| 粗算 effective coverage | ~73.5% | 若 pass rate ≥90%，94.10% 较可信 |

若二轮 pass rate 仍 <85%，需继续收紧 title filter 或增加 PDF 级校验，**不宜**扩全市场。

---

## 7. 边界

- 仅生成二轮抽样清单；
- 未修改 coverage CSV / 脚本；
- 未联网；未打开 PDF；
- **不写 verified**。

---

## 附录：audit_id 索引

| audit_id | sample_group | company_code | company_name | report_type | found | matched_strategy |
|----------|--------------|--------------|--------------|-------------|-------|------------------|
| P1-AUD2-001 | quarterly_report_q1_found | 839167 | 同享科技 | quarterly_report_q1 | yes | keyword_recent |
| P1-AUD2-002 | quarterly_report_q1_found | 605277 | 新亚电子 | quarterly_report_q1 | yes | keyword_with_year |
| P1-AUD2-003 | quarterly_report_q1_found | 003006 | 百亚股份 | quarterly_report_q1 | yes | keyword_recent |
| P1-AUD2-004 | quarterly_report_q1_found | 601019 | 山东出版 | quarterly_report_q1 | yes | keyword_with_year |
| P1-AUD2-005 | quarterly_report_q1_found | 300625 | 三雄极光 | quarterly_report_q1 | yes | keyword_recent |
| P1-AUD2-006 | quarterly_report_q1_found | 300241 | 瑞丰光电 | quarterly_report_q1 | yes | keyword_with_year |
| P1-AUD2-007 | quarterly_report_q1_found | 300443 | 金雷股份 | quarterly_report_q1 | yes | keyword_recent |
| P1-AUD2-008 | quarterly_report_q1_found | 688777 | 中控技术 | quarterly_report_q1 | yes | keyword_with_year |
| P1-AUD2-009 | quarterly_report_q1_found | 002801 | 微光股份 | quarterly_report_q1 | yes | keyword_recent |
| P1-AUD2-010 | quarterly_report_q1_found | 688357 | 建龙微纳 | quarterly_report_q1 | yes | keyword_with_year |
| P1-AUD2-011 | quarterly_report_q1_found | 920208 | 青矩技术 | quarterly_report_q1 | yes | keyword_recent |
| P1-AUD2-012 | quarterly_report_q1_found | 688621 | 阳光诺和 | quarterly_report_q1 | yes | keyword_with_year |
| P1-AUD2-013 | quarterly_report_q1_found | 002376 | 新北洋 | quarterly_report_q1 | yes | keyword_recent |
| P1-AUD2-014 | quarterly_report_q1_found | 688196 | 卓越新能 | quarterly_report_q1 | yes | keyword_with_year |
| P1-AUD2-015 | quarterly_report_q1_found | 002337 | 赛象科技 | quarterly_report_q1 | yes | keyword_recent |
| P1-AUD2-016 | quarterly_report_q3_found | 001226 | 拓山重工 | quarterly_report_q3 | yes | keyword_recent |
| P1-AUD2-017 | quarterly_report_q3_found | 603303 | 得邦照明 | quarterly_report_q3 | yes | keyword_with_year |
| P1-AUD2-018 | quarterly_report_q3_found | 300732 | 设研院 | quarterly_report_q3 | yes | keyword_recent |
| P1-AUD2-019 | quarterly_report_q3_found | 688485 | 九州一轨 | quarterly_report_q3 | yes | keyword_with_year |
| P1-AUD2-020 | quarterly_report_q3_found | 000408 | 藏格矿业 | quarterly_report_q3 | yes | keyword_recent |
| P1-AUD2-021 | quarterly_report_q3_found | 600117 | 西宁特钢 | quarterly_report_q3 | yes | keyword_with_year |
| P1-AUD2-022 | quarterly_report_q3_found | 002337 | 赛象科技 | quarterly_report_q3 | yes | keyword_recent |
| P1-AUD2-023 | quarterly_report_q3_found | 603657 | 春光科技 | quarterly_report_q3 | yes | keyword_with_year |
| P1-AUD2-024 | quarterly_report_q3_found | 002801 | 微光股份 | quarterly_report_q3 | yes | keyword_recent |
| P1-AUD2-025 | quarterly_report_q3_found | 600738 | 丽尚国潮 | quarterly_report_q3 | yes | keyword_with_year |
| P1-AUD2-026 | quarterly_report_q3_found | 300695 | 兆丰股份 | quarterly_report_q3 | yes | keyword_recent |
| P1-AUD2-027 | quarterly_report_q3_found | 600530 | 交大昂立 | quarterly_report_q3 | yes | keyword_with_year |
| P1-AUD2-028 | quarterly_report_q3_found | 300771 | 智莱科技 | quarterly_report_q3 | yes | keyword_recent |
| P1-AUD2-029 | quarterly_report_q3_found | 688091 | 上海谊众 | quarterly_report_q3 | yes | keyword_with_year |
| P1-AUD2-030 | quarterly_report_q3_found | 300911 | 亿田智能 | quarterly_report_q3 | yes | keyword_recent |
| P1-AUD2-031 | annual_semi_found | 920475 | 三友科技 | annual_report | yes | keyword_with_year |
| P1-AUD2-032 | annual_semi_found | 603657 | 春光科技 | annual_report | yes | keyword_with_year |
| P1-AUD2-033 | annual_semi_found | 688320 | 禾川科技 | annual_report | yes | keyword_with_year |
| P1-AUD2-034 | annual_semi_found | 002091 | 江苏国泰 | annual_report | yes | keyword_with_year |
| P1-AUD2-035 | annual_semi_found | 301020 | 密封科技 | annual_report | yes | keyword_with_year |
| P1-AUD2-036 | annual_semi_found | 920580 | 科创新材 | semi_annual_report | yes | keyword_with_year |
| P1-AUD2-037 | annual_semi_found | 603815 | 交建股份 | semi_annual_report | yes | keyword_with_year |
| P1-AUD2-038 | annual_semi_found | 688357 | 建龙微纳 | semi_annual_report | yes | keyword_with_year |
| P1-AUD2-039 | annual_semi_found | 002668 | TCL智家 | semi_annual_report | yes | keyword_with_year |
| P1-AUD2-040 | annual_semi_found | 300080 | 易成新能 | semi_annual_report | yes | keyword_with_year |
| P1-AUD2-041 | not_found | 000522 | 白云山A | annual_report | no | - |
| P1-AUD2-042 | not_found | 603194 | 中力股份 | semi_annual_report | no | - |
| P1-AUD2-043 | not_found | 688605 | 先锋精科 | semi_annual_report | no | - |
| P1-AUD2-044 | not_found | 301556 | 托普云农 | semi_annual_report | no | - |
| P1-AUD2-045 | not_found | 600840 | 新湖创业 | semi_annual_report | no | - |
| P1-AUD2-046 | not_found | 600840 | 新湖创业 | annual_report | no | - |
| P1-AUD2-047 | not_found | 688449 | 联芸科技 | semi_annual_report | no | - |
| P1-AUD2-048 | not_found | 688411 | 海博思创 | semi_annual_report | no | - |
| P1-AUD2-049 | not_found | 920106 | 林泰新材 | quarterly_report_q3 | no | - |
| P1-AUD2-050 | not_found | 600840 | 新湖创业 | quarterly_report_q3 | no | - |
