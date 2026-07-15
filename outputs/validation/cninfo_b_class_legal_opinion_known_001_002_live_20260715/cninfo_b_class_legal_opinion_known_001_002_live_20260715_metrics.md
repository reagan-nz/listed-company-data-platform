# B-FM-25 Live Metrics — legal_opinion_known_001 / known_002

_生成时间：2026-07-15_

| 项 | 值 |
|----|-----|
| task_id | B-FM-25 |
| result | **LIVE_PASS** |
| allow-list | `legal_opinion_known_001`, `legal_opinion_known_002` |
| CNINFO | **4**（2 case × topSearch=1 + query=1；PDF=0；无试跑/重试） |
| wall | **~23.1 s** |
| pass / fail / ambiguous | **2** / 0 / 0 |

## Case

| case_id | kind | matched title | date | classification | result |
|---------|------|---------------|------|----------------|--------|
| `legal_opinion_known_001` | known | 2025年第一次临时股东大会的法律意见书 | 2025-06-02 | classified_correctly / announcement | **pass** |
| `legal_opinion_known_002` | known | 北京市星河律师事务所关于北京金自天正智能控制股份有限公司2024年年度股东会的法律意见书 | 2025-06-26 | classified_correctly / announcement | **pass** |

## 边界

- 首跑即 LIVE_PASS；无 ambiguous；无 orgId fallback。
- 未重开 supervisory_board_known_001–002 / shareholder_meeting_known_001–007 / board_resolution_known_001。
- harvest 锚点 BD2E544（永兴材料 002756 / ann=1223733432）、BD2E416（金自天正 600560 / ann=1223998801）。
- predicted_document_type=`announcement`（非 `shareholder_meeting_material`）。
