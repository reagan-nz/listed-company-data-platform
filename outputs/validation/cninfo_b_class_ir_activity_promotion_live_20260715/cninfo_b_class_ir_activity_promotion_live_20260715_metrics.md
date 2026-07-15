# CNINFO B 类 IR Activity Promotion Live Metrics — B-FM-10

_生成时间：2026-07-15_

| 字段 | 值 |
|------|-----|
| task_id | B-FM-10 |
| result | **LIVE_PASS** |
| ready_cases | 4 |
| pass / fail / ambiguous | **4 / 0 / 0** |
| query_executed（脚本计数） | **6**（known query×2 + category sse+szse×4） |
| topSearch | **2**（吉林化纤 000420 + 新乡化纤 000949 orgId） |
| CNINFO 本包合计 | **8**（2 topSearch + 6 query） |
| wall_time_s | **26.14** |
| PDF download | **0** |

## Per-case

| case_id | type | matched_title（节选） | matched_date | classification | result |
|---------|------|----------------------|--------------|----------------|--------|
| `ir_activity_known_002` | known | 关于参加2025年吉林辖区上市公司投资者网上集体接待日活动的公告 | 2025-05-20 | classified_correctly | **pass** |
| `ir_activity_known_003` | known | 关于举办投资者开放日活动的公告 | 2025-06-03 | classified_correctly | **pass** |
| `ir_activity_sample_001` | category | …投资者网上集体接待日活动的公告（窗内 30 hits） | 2025-05-21 | classified_correctly | **pass** |
| `ir_activity_sample_002` | category | 关于举办投资者开放日活动的公告（窗内 1 hit） | 2025-06-03 | classified_correctly | **pass** |
