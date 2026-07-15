# B-FM-34 Live Metrics — asset_valuation_explanation_known_001 / audit_report_known_001

| 项 | 值 |
|----|-----|
| task_id | B-FM-34 |
| result | **LIVE_PASS** |
| pass / fail / ambiguous | **2** / 0 / 0 |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| wall | **~43.3 s** |
| allow-list | `asset_valuation_explanation_known_001`, `audit_report_known_001` |

## 备注

- harvest 锚点 BD2E430（舍得酒业 600702 / ann=1223999581）、BD2E798（迎驾贡酒 603198 / ann=1223955004）。
- predicted_document_type=`announcement`（非 `other`；独立审计报告非 `annual_report`）。
- 窄 pattern：勿裸「说明」；含「年度报告」/「年报」的审计报告仍 periodic。
- 无 orgId fallback；无 PDF；首轮即 LIVE_PASS（无消歧重试）。
