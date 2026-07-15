# B-FM-23 Live Metrics — supervisory_board_known_001

_生成时间：2026-07-15_

| 项 | 值 |
|----|-----|
| task_id | B-FM-23 |
| result | **LIVE_PASS** |
| allow-list | `supervisory_board_known_001` |
| category | 空 |
| CNINFO | **2**（1 topSearch + 1 query；无 PDF） |
| wall | **~7.6 s** |
| PDF download | **0** |
| PDF parse | **0** |
| pass / fail / ambiguous | **1** / 0 / 0 |

| case_id | kind | matched | date | classification | result |
|---------|------|---------|------|----------------|--------|
| `supervisory_board_known_001` | known | 第六届监事会第二十四次会议决议公告 | 2025-06-27 | classified_correctly / announcement | **pass** |

## 边界

- live：首跑即 LIVE_PASS；无网络失败试跑；无 orgId fallback；**未**修改共享 validator。
- 未重开 shareholder_meeting_known_001–007 / board_resolution_known_001 等已闭合案例。
- harvest 锚点 BD2E091（网宿科技 300017 / ann=1224016408）。
- **不** commit / push；**不**触碰 A/C/D。
