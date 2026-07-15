# B-FM-31 Live Metrics — legal_opinion_known_005 / legal_opinion_known_006

| 项 | 值 |
|----|-----|
| task_id | B-FM-31 |
| result | **LIVE_PASS** |
| pass / fail / ambiguous | **2** / 0 / 0 |
| CNINFO（成功跑） | **4**（2×(topSearch+query)；PDF=0） |
| CNINFO（含首跑 PARTIAL 消歧前） | **8** |
| wall（成功跑） | **~30.4 s** |
| allow-list | `legal_opinion_known_005`, `legal_opinion_known_006` |

| case_id | ann_id | date | predicted_type | result |
|---------|--------|------|----------------|--------|
| legal_opinion_known_005 | 1223956527 | 2025-06-23 | announcement | pass |
| legal_opinion_known_006 | 1223877213 | 2025-06-13 | announcement | pass |

注记：

- harvest 锚点 BD2E472（天准科技 688003 / ann=1223956527）、BD2E168（恒生电子 600570 / ann=1223877213）。
- predicted_document_type=`announcement`（非 `other`）。
- 首跑 known_006 因短 pattern 同窗 3 命中 → ambiguous；收紧为「调整2024年股票期权激励计划行权价格的法律意见书」后复跑 LIVE_PASS。
- 无 orgId fallback；无 PDF。
