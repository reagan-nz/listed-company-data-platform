# CNINFO 公告类栏目小样本验证（Sub Issue 3，使用 retrieval strategy）

## 数据来源
- 公司映射：outputs/validation/cninfo_company_identity_mapping.csv
- 类别配置：config/cninfo_announcement_retrieval_strategies.yaml（retrieval strategy）
- 样本公司：outputs/validation/cninfo_p0_sample_companies.csv

## 样本与类别
- 样本公司数：40
- mapped 样本：30
- skipped（needs_orgid_mapping）：10
- 公告类别数：14
- 组合总数（含 skipped）：470

## 验证结果分布
- success：106
- partial：0
- failed：364
- skipped：0

### 按 rule_confidence
- high：23 / medium：83 / low：0 / none：364

### 按 category_key
- board_meeting: success 4 / partial 0 / failed 28 / skipped 0
- dividend_distribution: success 20 / partial 0 / failed 17 / skipped 0
- equity_incentive: success 5 / partial 0 / failed 27 / skipped 0
- major_asset_restructuring: success 1 / partial 0 / failed 29 / skipped 0
- penalty_litigation: success 1 / partial 0 / failed 29 / skipped 0
- performance_forecast: success 1 / partial 0 / failed 29 / skipped 0
- private_placement: success 1 / partial 0 / failed 29 / skipped 0
- quarterly_report: success 12 / partial 0 / failed 18 / skipped 0
- regulatory_inquiry: success 4 / partial 0 / failed 28 / skipped 0
- semi_annual_report: success 0 / partial 0 / failed 30 / skipped 0
- share_repurchase: success 6 / partial 0 / failed 27 / skipped 0
- share_unlock: success 0 / partial 0 / failed 30 / skipped 0
- shareholder_meeting: success 51 / partial 0 / failed 13 / skipped 0
- supervisory_board: success 0 / partial 0 / failed 30 / skipped 0

### 按 data_type
- capital_event_candidate: success 8 / partial 0 / failed 85 / skipped 0
- document: success 12 / partial 0 / failed 48 / skipped 0
- event_candidate: success 21 / partial 0 / failed 46 / skipped 0
- governance_event_candidate: success 60 / partial 0 / failed 98 / skipped 0
- market_event_candidate: success 0 / partial 0 / failed 30 / skipped 0
- risk_event_candidate: success 5 / partial 0 / failed 57 / skipped 0

### 按 board
- 主板: success 54 / partial 0 / failed 111 / skipped 0
- 创业板: success 0 / partial 0 / failed 98 / skipped 0
- 北交所: success 0 / partial 0 / failed 84 / skipped 0
- 科创板: success 52 / partial 0 / failed 71 / skipped 0

## 字段可得性（行计数）
- announcement_title：106/470
- publish_time：106/470
- source_url：0/470
- pdf_url：106/470
- matched_keyword：106/470

## 说明与当前结论
- 本轮使用 retrieval strategy（must/optional/exclude）实际运行；与旧关键词相比，success 106 / failed 364，整体未提升。
- 高命中类别：shareholder_meeting、dividend_distribution、quarterly_report。零命中：semi_annual_report、supervisory_board、share_unlock。
- 失败主要可能来源：查询范围/时间窗口、报告类别参数缺失、事件低频、orgId 覆盖不足，非仅关键词问题。
- recommended_status：testing / partial，不写 verified。

## 边界确认
- 未下载 PDF 正文；未解析 PDF；未做 OCR。
- 未做数据库 / MinIO 接入；未使用 BrowserUser。
- 未修改 docs/data_sources.md 与存储 schema。
