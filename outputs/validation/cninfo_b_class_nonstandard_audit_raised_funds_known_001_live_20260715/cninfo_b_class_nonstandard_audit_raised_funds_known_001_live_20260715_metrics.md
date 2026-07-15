# B-FM-32 Live Metrics — nonstandard_audit_opinion_known_001 / raised_funds_usage_report_known_001

| 项 | 值 |
|----|-----|
| task_id | B-FM-32 |
| executor | b-class-executor |
| result | **LIVE_PASS** |
| ready / pass / fail / ambiguous | **2** / **2** / **0** / **0** |
| CNINFO | **4**（2×(topSearch+query)；PDF=0） |
| wall | **~21.4 s** |
| allow-list | `nonstandard_audit_opinion_known_001`, `raised_funds_usage_report_known_001` |

## 证据锚点

- harvest 锚点 BD2E366（永鼎股份 600105 / ann=1223956135）、BD2E234（东方钽业 000962 / ann=1223958745）。
- 路由：含「非标准审计意见」或「募集资金使用情况报告」→ `announcement` / `cninfo_general_announcement_pdf`（非 `other`）。
- 窄 pattern：不泛化裸「专项说明」；不扩「审核意见」。
- 无 orgId fallback；无 PDF / OCR / DB / RAG。
