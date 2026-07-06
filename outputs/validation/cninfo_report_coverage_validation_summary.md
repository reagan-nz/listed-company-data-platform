# CNINFO A 类报告 coverage 验证（Era C Phase 1）

## 1. 数据来源
- 公司映射：outputs/validation/cninfo_company_identity_mapping.csv
- 样本公司：outputs/validation/cninfo_p0_sample_companies.csv
- 分层口径：plans/cninfo_data_source_layered_inventory.md
- 脚本：lab/validate_cninfo_report_coverage.py

## 2. Coverage 口径说明
- **一行 = 一家公司 × 一个 report_type × 一个 expected_period**。
- 多种 query strategy（keyword_with_year → keyword_recent → longer_time_window → report_title_pattern；季报另增 quarterly_keyword_expanded / quarterly_seDate_fallback / quarterly_category_fallback）仅作**内部 fallback**，命中即停，**不拆成多行**。
- **分母（expected）**：`mapping_status=mapped` 的公司 × 各 report_type 的 expected_period 行数。
- **分子（found）**：`found=yes` 且标题匹配 report_type、`parsed_report_period == expected_period`、`pdf_url` 非空。
- **skipped**：`needs_orgid_mapping` 公司行计入 CSV 与 skipped 统计，**不计入 coverage 分母**。

## 3. 样本与覆盖
- 样本公司数：40
- mapped 公司数：30
- skipped（needs_orgid_mapping）公司数：10
- expected rows（coverage 分母）：120
- CSV 总行数（含 skipped 行）：160

## 4. 结果分布
- found：113
- not_found：7
- skipped rows（needs_orgid_mapping）：40

## 5. Overall coverage
- **coverage = found / expected = 113/120 = 94.17%**

## 6. 按 report_type
- annual_report: 30/30 (100.00%)
- quarterly_report_q1: 26/30 (86.67%)
- quarterly_report_q3: 27/30 (90.00%)
- semi_annual_report: 30/30 (100.00%)

## 7. 按 board
- 主板: 40/40 (100.00%)
- 创业板: 21/28 (75.00%)
- 北交所: 24/24 (100.00%)
- 科创板: 28/28 (100.00%)

## 8. 按 exchange
- BSE: 24/24 (100.00%)
- SSE: 68/68 (100.00%)
- SZSE: 21/28 (75.00%)

## 9. 字段可得性（mapped expected 行）
- pdf_url 可得（found 行）：113/120
- parsed_report_period 与 expected_period 一致（found 行）：113/113

## 10. 主要 failure_reason（not_found 行）
- empty_response：7

## 11. 与旧口径的区别
- 旧 [cninfo_report_announcement_validation_summary.md](cninfo_report_announcement_validation_summary.md)：`success 368/780` 按 **company × report_type × query_strategy** 计行，同一报告可能多行 success/failed。
- 本摘要：**company × expected_period** 一行；strategy 仅记录 `matched_strategy`。

## 12. recommended_status
- overall coverage 94.17% → **testing / usable candidate**
- 阈值：<80% partial/not acceptable；80–90% partial；90–95% testing/usable candidate；95%+ stable pipeline candidate。
- **不写 verified**；仅代表当前 40 家 P0 样本小样本结论。

## 13. 边界确认
- 未下载 PDF 正文；未解析 PDF；未计算 hash。
- 未做数据库 / MinIO 接入；未使用 BrowserUser。
- 请求间 sleep；不绕过登录/验证码/付费/权限。
- 本摘要基于当前脚本运行结果生成。
- 参数诊断详见 [cninfo_report_coverage_parameter_diagnostics.md](cninfo_report_coverage_parameter_diagnostics.md)。
- 季报失败诊断详见 [cninfo_report_quarterly_failure_diagnostics.md](cninfo_report_quarterly_failure_diagnostics.md)。

## 14. Q1/Q3 季报策略优化对比（本轮仅改季报）

- **本轮变更范围**：仅 `quarterly_report_q1` / `quarterly_report_q3` 关键词、title_patterns、seDate/category fallback；**annual_report / semi_annual_report 逻辑未改**。

### 优化前（baseline）
- overall：101/120 = 84.17%
- Q1：20/30 = 66.67%
- Q3：21/30 = 70.00%

### 优化后（本次运行）
- overall：**113/120 = 94.17%**（Δ +12）
- Q1：**26/30 = 86.67%**（Δ +6）
- Q3：**27/30 = 90.00%**（Δ +6）

### 季报命中策略分布（found 行）
- keyword_with_year：41
- quarterly_category_fallback：12

- 其中新增季报 fallback 策略命中：**12** 行（quarterly_keyword_expanded / quarterly_seDate_fallback / quarterly_category_fallback）

### 仍 not_found 的季报样本
| company_code | company_name | exchange | board | report_type | failure_reason |
|--------------|--------------|----------|-------|-------------|----------------|
| 300001 | 特锐德 | SZSE | 创业板 | quarterly_report_q1 | empty_response |
| 300001 | 特锐德 | SZSE | 创业板 | quarterly_report_q3 | empty_response |
| 300002 | 神州泰岳 | SZSE | 创业板 | quarterly_report_q1 | empty_response |
| 300002 | 神州泰岳 | SZSE | 创业板 | quarterly_report_q3 | empty_response |
| 300003 | 乐普医疗 | SZSE | 创业板 | quarterly_report_q1 | empty_response |
| 300006 | 莱美药业 | SZSE | 创业板 | quarterly_report_q1 | empty_response |
| 300006 | 莱美药业 | SZSE | 创业板 | quarterly_report_q3 | empty_response |

