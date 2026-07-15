# CNINFO B 类 Regulatory Work Letter Promotion Live Metrics — B-FM-13

_生成时间：2026-07-15_

| 字段 | 值 |
|------|-----|
| task_id | B-FM-13 |
| result | **LIVE_PASS** |
| ready_cases | 2 |
| pass / fail / ambiguous | **2 / 0 / 0** |
| query_executed（最终成功跑） | **3**（known query×1 + category sse+szse×2） |
| topSearch（最终成功跑） | **1**（600715；SSL/空响应后改用 registry orgId=`gssh0600715`） |
| CNINFO 最终成功跑 | **4**（1 topSearch + 3 query） |
| CNINFO 本包合计（含 2 次网络失败试跑） | **~8** |
| wall_time_s（最终成功跑） | **~90**（REQUEST_TIMEOUT=45；含 topSearch 失败等待） |
| PDF download | **0** |

## Per-case

| case_id | type | matched_title（节选） | matched_date | classification | result |
|---------|------|----------------------|--------------|----------------|--------|
| `inquiry_known_004` | known | 中兴财光华…信息披露监管工作函的专项说明 | 2025-04-28 | classified_correctly / inquiry_reply | **pass** |
| `inquiry_sample_003` | category | 鹏博士…终止上市相关事项的监管工作函…（窗内 11 hits / scanned=22） | 2025-04-29 | classified_correctly / regulatory_inquiry | **pass** |

## 运行备注

- 前两轮直跑 `validate_cninfo_b_class_corpus_retrieval.py --live-metadata`：`orgId resolution failed via topSearch` + `network_timeout`（wall 22.32s / 21.59s）。
- 最终成功跑：一次性 wrapper 将 `REQUEST_TIMEOUT` 提至 45s；topSearch 失败时显式使用 C-class/harvest 已验证 `gssh0600715`（**不**改共享 validator；**非**静默 fallback）。
