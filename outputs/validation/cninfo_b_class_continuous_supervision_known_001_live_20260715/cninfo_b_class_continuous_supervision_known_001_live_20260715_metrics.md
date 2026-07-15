# B-FM-30 Live Metrics — continuous_supervision_annual_known_001 / continuous_supervision_training_known_001

| 项 | 值 |
|----|-----|
| task_id | B-FM-30 |
| result | **LIVE_PASS** |
| pass / fail / ambiguous | **2** / 0 / 0 |
| CNINFO | **4**（2×(topSearch+query)；PDF=0） |
| wall | **~24.4 s** |
| allow-list | `continuous_supervision_annual_known_001`, `continuous_supervision_training_known_001` |

| case_id | ann_id | date | predicted_type | result |
|---------|--------|------|----------------|--------|
| continuous_supervision_annual_known_001 | 1223493907 | 2025-05-08 | announcement | pass |
| continuous_supervision_training_known_001 | 1223955243 | 2025-06-23 | announcement | pass |

注记：

- harvest 锚点 BD2E131（恒立液压 601100 / ann=1223493907）、BD2E248（三联锻造 001282 / ann=1223955243）。
- predicted_document_type=`announcement`（非 `annual_report` / `other`）。
- 首跑即 LIVE_PASS；无 orgId fallback；无 pattern 复跑。
