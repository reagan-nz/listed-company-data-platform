# B-FM-43 Live Metrics — continuous_supervision_annual_known_002 / company_articles_known_002

| 字段 | 值 |
|------|-----|
| task_id | B-FM-43 |
| result | **LIVE_PASS** |
| ready | **2** |
| query_executed | **2** |
| pass / fail / ambiguous | **2** / 0 / 0 |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| allow-list | `continuous_supervision_annual_known_002`, `company_articles_known_002` |
| wall（成功 live） | **~6.7 s** |
| routing_changes | **none** |

## 边界

- 未下载 PDF；未写 verified / production_ready
- 未重开 known_001 LIVE_PASS（含 B-FM-30 / B-FM-36）与 B-FM-42
- remaining other harvest 仍为 ~0
- console 日志不纳入 allow-list / 提交清单
