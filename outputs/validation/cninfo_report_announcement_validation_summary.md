# CNINFO 报告类公告查询机制验证（Sub Issue 5）

## 数据来源
- 公司映射：outputs/validation/cninfo_company_identity_mapping.csv
- 样本公司：outputs/validation/cninfo_p0_sample_companies.csv
- 策略配置：config/cninfo_announcement_retrieval_strategies.yaml

## 样本与覆盖
- 样本公司数：40
- mapped：30
- skipped（needs_orgid_mapping）：10
- report_type 数量：4
- query_strategy 数量：4
- 输出行数：780

## 结果分布
- success：368
- failed：412
- skipped：0

### 按 report_type
- annual_report: success 98 / failed 82 / skipped 0
- quarterly_report_q1: success 113 / failed 97 / skipped 0
- quarterly_report_q3: success 102 / failed 108 / skipped 0
- semi_annual_report: success 55 / failed 125 / skipped 0

### 按 query_strategy
- keyword_recent: success 121 / failed 119 / skipped 0
- keyword_with_year: success 102 / failed 78 / skipped 0
- longer_time_window: success 121 / failed 119 / skipped 0
- report_title_pattern: success 24 / failed 96 / skipped 0

### 字段可得性（行计数，非空且非 unknown）
- announcement_title：368/780
- publish_time：368/780
- report_period：332/780
- report_period_unknown：448
- pdf_url：368/780
- source_url：0/780
- 说明：failed 行 CSV 中 report_period 保留为 unknown，不计入 report_period 可得性。

## 观察与结论
- 报告类专项查询明显有效。
- 半年报已从前一轮公告类别验证的 0 命中提升到 55 success。
- Q1/Q3 季报比普通 category 验证更稳定，分别达到 113 / 102 success。
- 年报、半年报、季报应从普通事件公告分类中拆出，作为 document/report retrieval 机制单独处理。
- keyword_recent 和 longer_time_window 当前效果最好；keyword_with_year 也有效。
- report_title_pattern 单独使用效果较弱。
- report_period 已从标题解析 332/780；另有 448 行为 unknown（含 failed 行占位，不代表解析成功）。
- source_url 当前仍为 0，但 pdf_url 可得。
- recommended_status：testing / partial（不写 verified）。

## 边界确认
- 未下载 PDF 正文；未解析 PDF；未做 hash。
- 未做数据库 / MinIO 接入；未使用 BrowserUser。
- 不修改 docs / plans / storage schema；不修改原始 CSV。
- 本摘要已基于当前运行结果生成。
