# CNINFO B 类 CPA Inquiry-Reply Promotion Live Metrics — B-FM-03

_生成时间：2026-07-15_

| 字段 | 值 |
|------|-----|
| task_id | B-FM-03 |
| result | **LIVE_PASS**（最终 allow-list 重跑） |
| ready_cases | 2 |
| pass / fail / ambiguous | **2 / 0 / 0** |
| query_executed（脚本计数） | **3**（known query×1 + category sse+szse×2） |
| topSearch | **1**（华钰矿业 orgId） |
| CNINFO 本轮最终 live | **4**（1 topSearch + 3 query） |
| CNINFO 本包合计 | **8**（含首次 pattern 过宽 → ambiguous 的试跑 4 次） |
| wall_time_s（最终 live） | **~12.6** |
| PDF download | **0** |

## Per-case（最终）

| case_id | type | matched_title（节选） | matched_date | classification | result |
|---------|------|----------------------|--------------|----------------|--------|
| `inquiry_known_001` | known | 立信…信息披露监管问询函的回复 | 2025-06-24 | classified_correctly | **pass** |
| `inquiry_sample_002` | category | …事后审核问询函的回复公告 | 2025-06-27 | classified_correctly | **pass** |

## 首次试跑（已废弃证据）

| 项 | 值 |
|----|-----|
| known title_pattern | `信息披露监管问询函的回复`（过宽） |
| outcome | known **ambiguous**（3 matches）；category **pass** |
| 处置 | 收紧为 harvest 全文 title_pattern 后重跑；以最终 LIVE_PASS 为准 |
