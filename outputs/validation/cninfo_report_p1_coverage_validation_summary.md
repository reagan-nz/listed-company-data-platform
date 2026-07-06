# CNINFO A 类报告 coverage 验证 — P1 扩展样本

## 1. 数据来源
- 跑次标签：**P1**
- 公司映射：outputs/validation/cninfo_report_p1_identity_mapping.csv
- 样本公司：outputs/validation/cninfo_report_p1_sample_companies.csv
- 分层口径：plans/cninfo_data_source_layered_inventory.md
- 脚本：lab/validate_cninfo_report_coverage.py

## 2. Coverage 口径说明
- **一行 = 一家公司 × 一个 report_type × 一个 expected_period**。
- 多种 query strategy（keyword_with_year → keyword_recent → longer_time_window → report_title_pattern；季报另增 quarterly_keyword_expanded / quarterly_seDate_fallback / quarterly_category_fallback）仅作**内部 fallback**，命中即停，**不拆成多行**。
- **分母（expected）**：`mapping_status=mapped` 的公司 × 各 report_type 的 expected_period 行数。
- **分子（found / effective found）**：`found=yes` 且 `pdf_url` 非空、`parsed_report_period == expected_period`、标题匹配 `report_type`，且**未命中** official title exclusion（说明会/预告/披露提示/问询函回复/摘要/交叉披露提示等；`title_excluded` 不计入）。
- **found_before_title_filter**：若策略曾命中 excluded 标题后仍继续 fallback，最终在 `_RUN_STATS` 中单独统计。
- **skipped**：`needs_orgid_mapping` 公司行计入 CSV 与 skipped 统计，**不计入 coverage 分母**。

## 3. 样本与覆盖
- 样本公司数：200
- mapped 公司数：199
- skipped（needs_orgid_mapping）公司数：1
- expected rows（coverage 分母）：796
- CSV 总行数（含 skipped 行）：800

## 4. 结果分布
- found：749
- not_found：47
- skipped rows（needs_orgid_mapping）：4

## 5. Overall coverage
- **coverage = found / expected = 749/796 = 94.10%**
- （title filter 后口径；修正前 found = 749，排除 0 条假阳性）

## 5a. 质量口径（audit-aware title filter / SZSE category fallback）

- **found_before_title_filter**：749
- **found_after_title_filter**（coverage 分子）：749
- **excluded_title_count** / **title_excluded_count**：0

**excluded_by_report_type：**

| report_type | 被排除行数 |
|-------------|------------|
| annual_report | 0 |
| quarterly_report_q1 | 0 |
| quarterly_report_q3 | 0 |
| semi_annual_report | 0 |

**excluded_by_reason（归类）：**

- （本次无 title_excluded 行）

- **摘要类命中（单独统计，不计正式全文 found）**：0
- **Q1/Q3 通过 SZSE quarterly_category_fallback 新增命中**：0

- P1 title-filter 修正前 retrieval：**750/796 = 94.22%**（含假阳性；quality audit 标题级 pass rate **78%**，粗算有效 **~73.5%**）
- 本次重跑（official title filter 后）effective coverage = **94.10%**
- 参考：[cninfo_report_p1_quality_audit_results.md](cninfo_report_p1_quality_audit_results.md)

## 6. 按 report_type
- annual_report: 193/199 (96.98%)
- quarterly_report_q1: 184/199 (92.46%)
- quarterly_report_q3: 187/199 (93.97%)
- semi_annual_report: 185/199 (92.96%)

## 7. 按 board
- 主板: 301/316 (95.25%)
- 创业板: 157/160 (98.12%)
- 北交所: 140/160 (87.50%)
- 科创板: 151/160 (94.38%)

## 8. 按 exchange
- BSE: 140/160 (87.50%)
- SSE: 304/320 (95.00%)
- SZSE: 305/316 (96.52%)

## 9. 字段可得性（mapped expected 行）
- pdf_url 可得（found 行）：749/796
- parsed_report_period 与 expected_period 一致（found 行）：749/749

## 10. 主要 failure_reason（not_found 行）
- empty_response：39
- period_mismatch：8

## 11. 与旧口径的区别
- 旧 [cninfo_report_announcement_validation_summary.md](cninfo_report_announcement_validation_summary.md)：`success 368/780` 按 **company × report_type × query_strategy** 计行，同一报告可能多行 success/failed。
- 本摘要：**company × expected_period** 一行；strategy 仅记录 `matched_strategy`。

## 12. recommended_status
- overall **effective** coverage（title filter 后）94.10% → **testing / usable candidate**
- 阈值：<80% partial/not acceptable；80–90% partial；90–95% testing/usable candidate；95%+ stable pipeline candidate。
- P1 quality audit 已显示修正前 **750/796 = 94.22%** retrieval 含约 **22%** found 样本标题级假阳性；**勿将旧 94.22% 视为 accuracy**。
- 本次跑次使用 **official report title filter**（全 report_type exclusion）；coverage 以 **found_after_title_filter** 为准。
- **不写 verified**；**不写 full-market stable**；仅代表当前 P1 扩展样本。

## 13. 边界确认
- 未下载 PDF 正文；未解析 PDF；未计算 hash。
- 未做数据库 / MinIO 接入；未使用 BrowserUser。
- 请求间 sleep；不绕过登录/验证码/付费/权限。
- 本摘要基于当前脚本运行结果生成。
- 参数诊断详见 [cninfo_report_p1_coverage_parameter_diagnostics.md](cninfo_report_p1_coverage_parameter_diagnostics.md)。
- 季报失败诊断详见 [cninfo_report_quarterly_failure_diagnostics.md](cninfo_report_quarterly_failure_diagnostics.md)。
- P1 计划详见 [cninfo_report_p1_expansion_plan.md](cninfo_report_p1_expansion_plan.md)。

## 14. 与 P0 baseline 对比

- P0 小样本（30 mapped）：**113/120 = 94.17%** — mechanism passed，非全市场结论
- P1 本次（199 mapped）：**749/796 = 94.10%**（Δ overall +636）

| 维度 | P0 | P1（本次） |
|------|-----|----------|
| overall | 113/120 (94.17%) | 749/796 (94.10%) |
| annual_report | 30/30 | 193/199 |
| semi_annual_report | 30/30 | 185/199 |
| quarterly_report_q1 | 26/30 | 184/199 |
| quarterly_report_q3 | 27/30 | 187/199 |
| SSE | 68/68 | 304/320 |
| SZSE | 21/28 | 305/316 |
| BSE | 24/24 | 140/160 |

### P1 remaining gaps（not_found 行）

| company_code | company_name | exchange | board | report_type | failure_reason |
|--------------|--------------|----------|-------|-------------|----------------|
| 920008 | 成电光信 | BSE | 北交所 | quarterly_report_q1 | empty_response |
| 920008 | 成电光信 | BSE | 北交所 | semi_annual_report | empty_response |
| 920056 | 能之光 | BSE | 北交所 | annual_report | empty_response |
| 920056 | 能之光 | BSE | 北交所 | quarterly_report_q1 | empty_response |
| 920056 | 能之光 | BSE | 北交所 | quarterly_report_q3 | empty_response |
| 920056 | 能之光 | BSE | 北交所 | semi_annual_report | empty_response |
| 920080 | 奥美森 | BSE | 北交所 | annual_report | empty_response |
| 920080 | 奥美森 | BSE | 北交所 | quarterly_report_q1 | empty_response |
| 920080 | 奥美森 | BSE | 北交所 | quarterly_report_q3 | empty_response |
| 920080 | 奥美森 | BSE | 北交所 | semi_annual_report | empty_response |
| 920106 | 林泰新材 | BSE | 北交所 | quarterly_report_q1 | empty_response |
| 920106 | 林泰新材 | BSE | 北交所 | quarterly_report_q3 | empty_response |
| 920106 | 林泰新材 | BSE | 北交所 | semi_annual_report | empty_response |
| 920128 | 胜业电气 | BSE | 北交所 | quarterly_report_q1 | empty_response |
| 920128 | 胜业电气 | BSE | 北交所 | quarterly_report_q3 | empty_response |
| 920128 | 胜业电气 | BSE | 北交所 | semi_annual_report | empty_response |
| 920166 | 海圣医疗 | BSE | 北交所 | annual_report | empty_response |
| 920166 | 海圣医疗 | BSE | 北交所 | quarterly_report_q1 | empty_response |
| 920166 | 海圣医疗 | BSE | 北交所 | quarterly_report_q3 | empty_response |
| 920166 | 海圣医疗 | BSE | 北交所 | semi_annual_report | empty_response |
| 600840 | 新湖创业 | SSE | 主板 | annual_report | period_mismatch |
| 600840 | 新湖创业 | SSE | 主板 | quarterly_report_q1 | empty_response |
| 600840 | 新湖创业 | SSE | 主板 | quarterly_report_q3 | empty_response |
| 600840 | 新湖创业 | SSE | 主板 | semi_annual_report | period_mismatch |
| 603194 | 中力股份 | SSE | 主板 | quarterly_report_q1 | empty_response |
| 603194 | 中力股份 | SSE | 主板 | quarterly_report_q3 | empty_response |
| 603194 | 中力股份 | SSE | 主板 | semi_annual_report | period_mismatch |
| 688411 | 海博思创 | SSE | 科创板 | quarterly_report_q1 | empty_response |
| 688411 | 海博思创 | SSE | 科创板 | quarterly_report_q3 | empty_response |
| 688411 | 海博思创 | SSE | 科创板 | semi_annual_report | period_mismatch |
| 688449 | 联芸科技 | SSE | 科创板 | quarterly_report_q1 | empty_response |
| 688449 | 联芸科技 | SSE | 科创板 | quarterly_report_q3 | empty_response |
| 688449 | 联芸科技 | SSE | 科创板 | semi_annual_report | period_mismatch |
| 688605 | 先锋精科 | SSE | 科创板 | quarterly_report_q1 | empty_response |
| 688605 | 先锋精科 | SSE | 科创板 | quarterly_report_q3 | empty_response |
| 688605 | 先锋精科 | SSE | 科创板 | semi_annual_report | period_mismatch |
| 000522 | 白云山A | SZSE | 主板 | annual_report | period_mismatch |
| 000522 | 白云山A | SZSE | 主板 | quarterly_report_q1 | empty_response |
| 000522 | 白云山A | SZSE | 主板 | quarterly_report_q3 | empty_response |
| 000522 | 白云山A | SZSE | 主板 | semi_annual_report | empty_response |
| 001365 | 天海电子 | SZSE | 主板 | annual_report | empty_response |
| 001365 | 天海电子 | SZSE | 主板 | quarterly_report_q1 | empty_response |
| 001365 | 天海电子 | SZSE | 主板 | quarterly_report_q3 | empty_response |
| 001365 | 天海电子 | SZSE | 主板 | semi_annual_report | empty_response |
| 301556 | 托普云农 | SZSE | 创业板 | quarterly_report_q1 | empty_response |
| 301556 | 托普云农 | SZSE | 创业板 | semi_annual_report | period_mismatch |
| 301606 | 绿联科技 | SZSE | 创业板 | quarterly_report_q1 | empty_response |

