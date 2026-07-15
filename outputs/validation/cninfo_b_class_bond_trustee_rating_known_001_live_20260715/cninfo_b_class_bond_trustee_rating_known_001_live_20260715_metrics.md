# B-FM-29 Live Metrics — bond_trustee_report_known_001 / tracking_rating_report_known_001

| 项 | 值 |
|----|-----|
| task_id | B-FM-29 |
| result | **LIVE_PASS** |
| pass / fail / ambiguous | **2** / 0 / 0 |
| CNINFO（成功复跑） | **4**（2×(topSearch+query)；PDF=0） |
| wall | **~21.2 s** |
| allow-list | `bond_trustee_report_known_001`, `tracking_rating_report_known_001` |

| case_id | ann_id | date | predicted_type | result |
|---------|--------|------|----------------|--------|
| bond_trustee_report_known_001 | 1223979550 | 2025-06-25 | announcement | pass |
| tracking_rating_report_known_001 | 1224013532 | 2025-06-27 | announcement | pass |

注记：

- harvest 锚点 BD2E254（三羊马 001317 / ann=1223979550）、BD2E408（华海药业 600521 / ann=1224013532）。
- predicted_document_type=`announcement`（非 `other`）。
- 首跑 PARTIAL：短串「受托管理事务报告」同窗命中年度报告 + 第一次临时报告；pattern 收紧为「可转换公司债券受托管理事务报告（2024年度）」后复跑 LIVE_PASS。
