# CNINFO P1 Report Retrieval Quality Audit Results

- 生成时间：2026-07-05（离线整理）
- 审计样本：[cninfo_report_p1_quality_audit_sample.csv](cninfo_report_p1_quality_audit_sample.csv)
- 抽样设计：[cninfo_report_p1_quality_audit.md](cninfo_report_p1_quality_audit.md)
- P1 自动跑次：[cninfo_report_p1_coverage_validation_summary.md](cninfo_report_p1_coverage_validation_summary.md)
- P1 最终总结：[cninfo_report_p1_coverage_final_summary.md](cninfo_report_p1_coverage_final_summary.md)

---

## 1. 审计目的

P1 A 类 report retrieval 自动跑次结果为 **750/796 = 94.22%**。该数字是 **retrieval hit rate**（脚本在 CNINFO `hisAnnouncement/query` 上检索到一行 `found=yes` 的比例），**不等于**人工打开 PDF、核对标题与报告期后的 **accuracy（准确率）**。

本次审计的目的：

- 对 P1 **found** 样本做随机抽样，检查是否存在**假阳性**（脚本标 found，但标题并非正式报告）；
- 重点关注 **Q1/Q3** 是否误命中说明会、预告、**披露提示性公告**等非正式报告类标题；
- 对 **not_found** 样本仅做边界标注，**不**在本轮直接判定 false negative；
- 为后续 **title filter** 修复与 P1 coverage 重跑提供依据。

**边界**：本轮为**标题/元数据级**审计；审计员注明未逐页阅读 PDF 正文。本文档**不写 verified**。

---

## 2. 审计样本

| 项 | 数值 |
|----|------|
| **总样本** | **120** |
| found 样本 | 100 |
| not_found 样本 | 20 |
| annual_report found | 20 |
| semi_annual_report found | 20 |
| quarterly_report_q1 found | 30 |
| quarterly_report_q3 found | 30 |
| not_found | 20 |
| **random seed** | **42**（可复现） |

### 交易所 / 板块覆盖（120 条合计）

| exchange | board | 条数 |
|----------|-------|------|
| SSE | 主板 | 21 |
| SSE | 科创板 | 29 |
| SZSE | 主板 | 19 |
| SZSE | 创业板 | 32 |
| BSE | 北交所 | 19 |

| exchange | 条数 |
|----------|------|
| SSE | 50 |
| SZSE | 51 |
| BSE | 19 |

抽样覆盖 **SSE / SZSE / BSE** 及 **主板 / 创业板 / 科创板 / 北交所** 五层。Q1/Q3 found 样本中优先混入了含「披露提示 / 说明会 / 预告」等风险词的记录（池内风险标题已尽量纳入）。

---

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| found 样本 | 100 |
| **pass** | **78** |
| **fail** | **22** |
| **title-level pass rate** | **78/100 = 78%** |
| not_found → **uncertain** | **20** |

**强调：**

- **78%** 是 **标题/元数据级**审计 pass rate，不是 PDF 正文级 accuracy；
- 审计员在 `manual_auditor_notes` 中注明：**未逐页阅读 PDF 全文**；若后续打开 PDF 封面复核，个别 pass/fail 可能调整；
- **not_found 20 条**均标为 `uncertain`，**未**在本轮直接判定 false negative（无 `pdf_url` 可打开，需 CNINFO 页面二次检索）。

---

## 4. 按 report_type 结果

| report_type | 样本数 | pass | fail | fail rate |
|-------------|--------|------|------|-----------|
| annual_report | 20 | 18 | 2 | **10%** |
| semi_annual_report | 20 | 18 | 2 | **10%** |
| quarterly_report_q1 | 30 | 21 | 9 | **30%** |
| quarterly_report_q3 | 30 | 21 | 9 | **30%** |

**解释：**

- **Q1/Q3 假阳性明显更严重**（fail rate 30% vs annual/semi 10%）；
- 季报 fail 的 **绝大多数**为 **`announcement_preview`**（披露提示性公告），与脚本 `title_patterns` 中**主动包含**「一季度/三季度报告披露提示性公告」高度一致；
- annual/semi 的 10% fail 主要来自**监管问询函回复**、**披露提示性公告**、**交叉公司提示标题**（见 §5）。

---

## 5. 假阳性类型

| manual_issue_type | 数量 | 说明 |
|-------------------|------|------|
| **announcement_preview** | **18** | 披露提示性公告（季报为主） |
| **title_false_positive** | **2** | 监管问询函回复类（非正式年报正文） |
| **wrong_company** | **1** | 标题主体/报告对象与目标公司不匹配 |
| **investor_meeting_notice** | **1** | 业绩说明会预告 |
| **合计 fail** | **22** | — |

### 典型问题标题

| 类型 | 示例（audit_id） |
|------|------------------|
| 季报披露提示 | `2024年第一季度报告披露提示性公告`（P1-AUD-041 等） |
| 季报披露提示 | `2024年第三季度报告披露提示性公告`（P1-AUD-071 等） |
| 半年报披露提示 | `2024年半年度报告披露提示性公告`（P1-AUD-039） |
| 问询函回复 | `丽尚国潮关于对公司2024年年度报告信息披露监管问询函的回复公告`（P1-AUD-002） |
| 问询函回复 | `关于2024年年度报告的信息披露监管问询函的回复公告`（P1-AUD-018） |
| 交叉公司提示 | `北京金隅集团股份有限公司关于披露冀东水泥2024年半年度报告的提示性公告`（P1-AUD-022） |
| 业绩说明会预告 | `2024年年度报告暨2025年一季度报告业绩说明会预告公告`（P1-AUD-044） |

**分布特征：** 18 条 `announcement_preview` 中，**17 条**集中在 **SZSE 创业板** Q1/Q3；说明当前季报检索对创业板「披露提示性公告」过滤不足。

---

## 6. 对 94.22% 的重新解释

| 口径 | 数值 | 含义 |
|------|------|------|
| **自动 retrieval coverage** | **750/796 = 94.22%** | 脚本 `found=yes` 比例 |
| **found 样本标题级 pass rate** | **78/100 = 78%** | 人工审计 found 样本 |
| **粗算有效命中（外推）** | **750 × 78% ≈ 585** | 仅按 found 样本同比例估算 |
| **粗算有效 coverage（外推）** | **585/796 ≈ 73.5%** | 风险估算，**非**最终全量 accuracy |

**写清楚：**

- **94.22%** 仍然是**自动 retrieval coverage**，不因本次审计而改写自动跑次 CSV；
- 人工抽样显示 **found 样本存在约 22% 标题级假阳性**；
- **73.5%** 仅为标题级抽样外推的风险估算，**不是**对 796 行全量人工核验后的 accuracy；
- 在修复 title filter 并重跑 P1 coverage 之前，**不应**将 P1 维持为乐观的 **testing / usable candidate** 读法；
- 更稳妥的当前状态：**partial / testing，pending title-filter fix**。

---

## 7. 对脚本的直接启示

以下三类修复建议针对 `lab/validate_cninfo_report_coverage.py`（**本文档不修改脚本**；供下一轮迭代参考）。

### 7.1 季报 title filter

- **移除或排除**作为正向匹配的：
  - `一季度报告披露提示性公告` / `第一季度报告披露提示性公告`
  - `三季度报告披露提示性公告` / `第三季度报告披露提示性公告`
  - `关于披露…季度报告的提示性公告`
- 将以下加入 **Q1/Q3 exclusion**（与 annual/semi 对齐或加强）：
  - `披露提示性公告` / `提示性公告`
  - `预告公告` / `说明会` / `业绩说明会` / `投资者说明会`

### 7.2 annual / semi title filter

在现有 annual/semi exclusion 基础上补充：

- `问询函` / `回复公告`（监管问询函回复）
- `披露提示性公告` / `提示性公告`
- `关于披露…公司…报告` 类**交叉公司**提示标题（如披露参股/控股子公司报告）

### 7.3 found 判定原则

- **found** 不应仅依赖 `parsed_report_period == expected_period` + `pdf_url` 非空；
- 必须经 **official report title filter** 排除非正式报告类标题；
- title filter 应成为 **所有 report_type** 的共同逻辑（Q1/Q3 当前明显弱于 annual/semi）。

---

## 8. not_found 样本边界

| 项 | 说明 |
|----|------|
| 样本数 | 20 |
| manual_audit_result | 全部为 **uncertain** |
| failure_reason | `period_mismatch` 8；`empty_response` 12 |
| 交易所 | SSE 10；SZSE 6；BSE 4 |

**原因：**

- not_found 行通常**无 `pdf_url`**，无法像 found 样本一样打开 PDF 核对；
- `period_mismatch` 可能为新上市/退市/更名/标题年份解析问题；
- `empty_response` 可能为 BSE 代码映射、样本状态或报告确实未按预期标题披露；
- 若要判断 **false negative**（`not_found_but_exists`），需在 **CNINFO 官网**按 `company_code` + `expected_period` + 报告类型关键词人工检索。

本轮**未**对 not_found 做 false negative 计数。

---

## 9. 当前 recommended_status 建议

| 维度 | 建议 |
|------|------|
| 自动 P1 coverage | **94.22%**（retrieval hit rate，见跑次 CSV） |
| 审计后风险 | found 样本标题级 pass rate **78%**；粗算有效 coverage **~73.5%** |
| **verified** | **不写** |
| **full-market stable** | **不写** |
| 当前推荐读法 | **partial / testing，pending title-filter fix** |
| 修复后 | 修改 title filter → 重跑 P1 coverage → 更新 summary → 必要时第二轮 audit |

自动跑次摘要中的 **testing / usable candidate**（基于 94.22%）**未考虑**本次审计发现的 **~22% found 假阳性**；在 title filter 修复前，应以本审计结论为准做保守判断。

---

## 10. 下一步

1. **修改** `validate_cninfo_report_coverage.py` 的 title filter（§7 三类修复）；
2. **对 Q1/Q3 加强 exclusion**（披露提示性公告、说明会、预告等）；
3. **重跑** P1 coverage（同一 identity mapping / sample，不扩面）；
4. **生成** updated `cninfo_report_p1_coverage_validation_summary.md` 与 final summary；
5. **必要时**做第二轮 quality audit（可对修后 found 样本再抽 ~50–80 条，或全量核对 fail 类型是否归零）。

---

## 11. 边界

- 本文档**仅汇总**人工审计结果，不修改 [cninfo_report_p1_quality_audit_sample.csv](cninfo_report_p1_quality_audit_sample.csv) 与 [cninfo_report_p1_coverage_validation.csv](cninfo_report_p1_coverage_validation.csv)；
- **未联网**；**未重跑** coverage 脚本；
- **不写 verified**；结论仅代表 **120 条抽样** + 标题级审计口径，不代表全市场最终 accuracy。

---

## 附录：fail 样本索引（22 条）

| audit_id | company_code | report_type | manual_issue_type | announcement_title（摘要） |
|----------|--------------|-------------|-------------------|---------------------------|
| P1-AUD-002 | 600738 | annual_report | title_false_positive | 监管问询函的回复公告 |
| P1-AUD-018 | 688651 | annual_report | title_false_positive | 监管问询函的回复公告 |
| P1-AUD-022 | 601992 | semi_annual_report | wrong_company | 关于披露冀东水泥半年报的提示性公告 |
| P1-AUD-039 | 300320 | semi_annual_report | announcement_preview | 半年度报告披露提示性公告 |
| P1-AUD-041 | 300080 | quarterly_report_q1 | announcement_preview | 第一季度报告披露提示性公告 |
| P1-AUD-042 | 300661 | quarterly_report_q1 | announcement_preview | 第一季度报告披露提示性公告 |
| P1-AUD-043 | 301058 | quarterly_report_q1 | announcement_preview | 第一季度报告披露提示性公告 |
| P1-AUD-044 | 920106 | quarterly_report_q1 | investor_meeting_notice | 业绩说明会预告公告 |
| P1-AUD-045 | 300695 | quarterly_report_q1 | announcement_preview | 第一季度报告披露提示性公告 |
| P1-AUD-046 | 300625 | quarterly_report_q1 | announcement_preview | 第一季度报告披露提示性公告 |
| P1-AUD-047 | 300732 | quarterly_report_q1 | announcement_preview | 第一季度报告披露提示性公告 |
| P1-AUD-048 | 300320 | quarterly_report_q1 | announcement_preview | 第一季度报告披露提示性公告 |
| P1-AUD-053 | 300200 | quarterly_report_q1 | announcement_preview | 关于披露第一季度报告的提示性公告 |
| P1-AUD-071 | 300320 | quarterly_report_q3 | announcement_preview | 第三季度报告披露提示性公告 |
| P1-AUD-072 | 300554 | quarterly_report_q3 | announcement_preview | 第三季度报告披露提示性公告 |
| P1-AUD-073 | 300732 | quarterly_report_q3 | announcement_preview | 第三季度报告披露提示性公告 |
| P1-AUD-074 | 301058 | quarterly_report_q3 | announcement_preview | 第三季度报告披露提示性公告 |
| P1-AUD-075 | 300661 | quarterly_report_q3 | announcement_preview | 第三季度报告披露提示性公告 |
| P1-AUD-076 | 300695 | quarterly_report_q3 | announcement_preview | 第三季度报告披露提示性公告 |
| P1-AUD-077 | 300625 | quarterly_report_q3 | announcement_preview | 第三季度报告披露提示性公告 |
| P1-AUD-078 | 300278 | quarterly_report_q3 | announcement_preview | 第三季度报告披露提示性公告 |
| P1-AUD-093 | 300877 | quarterly_report_q3 | announcement_preview | 第三季度报告披露的提示性公告 |
