# B-FM-28 Live Metrics — listing_sponsor_known_001 / equity_change_report_known_001

| 项 | 值 |
|----|-----|
| task_id | B-FM-28 |
| result | **LIVE_PASS** |
| pass / fail / ambiguous | **2** / 0 / 0 |
| CNINFO | **4**（2×(topSearch+hisAnnouncement/query)；PDF=0） |
| wall | **~21.3 s** |
| allow-list | `listing_sponsor_known_001`, `equity_change_report_known_001` |

## Case

| case_id | ann | date | predicted_type | result |
|---------|-----|------|----------------|--------|
| listing_sponsor_known_001 | 1223824291 | 2025-06-09 | announcement | pass |
| equity_change_report_known_001 | 1223980482 | 2025-06-25 | announcement | pass |

## Notes

- 首跑 equity 因 searchkey「简式权益变动报告书」整串 CNINFO 返回 0 → PARTIAL；pattern 改为「权益变动报告书」后复跑 LIVE_PASS。
- harvest 锚点 BD2E252（尚太科技 001301 / ann=1223824291）、BD2E482（德林海 688069 / ann=1223980482）。
- predicted_document_type=`announcement`（非 `other`）。
