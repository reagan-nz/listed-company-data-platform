# B-FM-27 Live Metrics — verification_opinion_known_001 / known_002

| 项 | 值 |
|----|-----|
| task_id | B-FM-27 |
| result | **LIVE_PASS** |
| pass / fail / ambiguous | **2** / 0 / 0 |
| CNINFO | **4**（2×(topSearch+hisAnnouncement/query)；PDF=0） |
| wall | **~20.0 s** |
| allow-list | `verification_opinion_known_001`, `verification_opinion_known_002` |

## Case

| case_id | ann | date | predicted_type | result |
|---------|-----|------|----------------|--------|
| verification_opinion_known_001 | 1224013030 | 2025-06-27 | announcement | pass |
| verification_opinion_known_002 | 1223974498 | 2025-06-24 | announcement | pass |

## Notes

- 首跑即 LIVE_PASS；无 ambiguous；无 orgId fallback。
- harvest 锚点 BD2E172（三六零 601360 / ann=1224013030）、BD2E466（福元医药 601089 / ann=1223974498）。
- predicted_document_type=`announcement`（非 `other`）。
