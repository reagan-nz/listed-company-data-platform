# B-FM-26 Live Metrics — legal_opinion_known_003 / known_004

_生成时间：2026-07-15_

| 项 | 值 |
|----|-----|
| task_id | B-FM-26 |
| result | **LIVE_PASS** |
| allow-list | `legal_opinion_known_003`, `legal_opinion_known_004` |
| CNINFO | **4**（2 case × topSearch=1 + query=1；PDF=0；无试跑/重试） |
| wall | **~30.9 s** |
| pass / fail / ambiguous | **2** / 0 / 0 |

## Case

| case_id | kind | matched title | date | classification | result |
|---------|------|---------------|------|----------------|--------|
| `legal_opinion_known_003` | known | 浙江天册律师事务所关于恒逸石化股份有限公司控股股东增持公司股份之法律意见书 | 2025-06-24 | classified_correctly / announcement | **pass** |
| `legal_opinion_known_004` | known | 北京市通商律师事务所上海分所关于东浩兰生会展集团股份有限公司差异化分红的法律意见书 | 2025-06-17 | classified_correctly / announcement | **pass** |

## 边界

- 首跑即 LIVE_PASS；无 ambiguous；无 orgId fallback。
- 未重开 legal_opinion_known_001–002 / supervisory_board_known_001–002 / shareholder_meeting_known_001–007 / board_resolution_known_001。
- harvest 锚点 BD2E079（恒逸石化 000703 / ann=1223973353）、BD2E442（兰生股份 600826 / ann=1223900931）。
- predicted_document_type=`announcement`（非 `other`；非 `shareholder_meeting_material`）。
- routing harden：`法律意见` positive_patterns + `_general_document_type` 早退。
