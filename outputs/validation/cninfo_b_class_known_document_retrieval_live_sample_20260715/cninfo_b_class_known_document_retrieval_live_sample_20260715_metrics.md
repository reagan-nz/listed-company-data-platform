# B-R16-02 Known-Document Retrieval Live Sample Metrics

_生成时间：2026-07-15 16:02:36 +0800_

## Cap & CNINFO

| 指标 | 数值 |
|------|------|
| CNINFO cap | **20** |
| CNINFO total HTTP | **8** |
| topSearch | **4** |
| hisAnnouncement/query | **4** |
| query_executed (script) | **4** |
| wall_time_s | **34.216** |
| result | **LIVE_PASS** |
| cap_ok | **true** |

计数依据：4 个不同 `company_code` 各 1× topSearch；4 条均 `query_status=executed` 且
首轮 keyword 命中（notes=`live metadata match`），无第二轮 shorter keyword。
wall_time 取自首次 live runner 实测（CSV 已写出后 summary 签名失败，未二次请求 CNINFO）。

## Per-case outcomes

| case_id | company | case_result | retrieval_status | classification_status | matched_date | matched_title |
|---------|---------|-------------|------------------|-----------------------|--------------|---------------|
| `inquiry_known_002` | 601901 方正证券 | **pass** | found | classified_correctly | 2025-06-13 | 关于2024年年度报告的信息披露监管问询函的回复公告 |
| `meeting_known_002` | 688041 海光信息 | **pass** | found | classified_correctly | 2025-06-10 | 海光信息技术股份有限公司关于召开重大资产重组事项投资者说明会的公告 |
| `ir_activity_known_001` | 000559 万向钱潮 | **pass** | found | classified_correctly | 2025-06-25 | 万向钱潮投资者关系活动记录表（2025年6月24日） |
| `shareholder_meeting_known_001` | 300446 航天智造 | **pass** | found | classified_correctly | 2025-06-24 | 关于召开2025年度第二次临时股东大会通知的公告 |

## Allow-list

见 [allow_list.md](allow_list.md)。
