# CNINFO 公告检索规则回放摘要

## 输入
- 公告结果：outputs/validation/cninfo_announcement_category_validation.csv
- 策略配置：config/cninfo_announcement_retrieval_strategies.yaml

## 数量概览
- 输入公告标题数：106
- 输出匹配行数：106
- 规则置信度：high 23 / medium 83 / low 0 / none 0
- 需要 LLM 复核：1
- 实际调用 LLM：0（provider=not_used）
- LLM skipped：1
- multi-label 公告：0

## 按最终分类计数
- shareholder_meeting: 51
- dividend_distribution: 20
- quarterly_report: 12
- share_repurchase: 6
- equity_incentive: 5
- board_meeting: 4
- regulatory_inquiry: 4
- major_asset_restructuring: 1
- performance_forecast: 1
- penalty_litigation: 1
- private_placement: 1

## 当前结论
- 规则优先，LLM 仅在低置信/多标签/semantic_later 时使用（需显式 --use-llm）。
- 本摘要已由规则回放脚本生成，结果基于当前 106 条公告标题。

## 边界确认
- 未联网抓取 CNINFO；未修改原始验证 CSV；未修改原配置。
- 未下载/解析 PDF，未做 OCR；未做数据库/MinIO 接入；未使用 BrowserUser。
- LLM 仅在提供参数和 API Key 时调用；否则标记为 skipped/not_available。
