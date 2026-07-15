# B-FM-22 Live Metrics — shareholder_meeting_known_007

_生成时间：2026-07-15_

| 项 | 值 |
|----|-----|
| task_id | B-FM-22 |
| result | **LIVE_PASS** |
| allow-list | `shareholder_meeting_known_007` |
| category | 空 |
| CNINFO | **2**（1 topSearch + 1 query；无 PDF） |
| wall | **~19.2 s** |
| PDF download | **0** |
| PDF parse | **0** |
| pass / fail / ambiguous | **1** / 0 / 0 |

| case_id | kind | matched | date | classification | result |
|---------|------|---------|------|----------------|--------|
| `shareholder_meeting_known_007` | known | 2024年年度股东会决议公告 | 2025-06-25 | classified_correctly / shareholder_meeting_material | **pass** |

## 边界

- live：首跑即 LIVE_PASS；无网络失败试跑；无 orgId fallback；**未**修改共享 validator。
- 未重开 known_001–006 / meeting_sample_002 等已 LIVE_PASS 案例。
- harvest 锚点 BD2E258（信凯科技 001335 / ann=1223981729）。
- **不** commit / push；**不**触碰 A/C/D。
