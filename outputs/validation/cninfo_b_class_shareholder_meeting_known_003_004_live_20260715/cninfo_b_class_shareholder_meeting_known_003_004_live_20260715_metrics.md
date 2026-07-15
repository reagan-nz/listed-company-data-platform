# CNINFO B 类 Shareholder Meeting Known-003/004 Live Metrics — B-FM-19

_生成时间：2026-07-15_

| 字段 | 值 |
|------|-----|
| task_id | B-FM-19 |
| result | **LIVE_PASS** |
| ready_cases | 2 |
| pass / fail / ambiguous | **2 / 0 / 0** |
| query_executed | **2**（hisAnnouncement/query） |
| topSearch | **2** |
| CNINFO 本包合计 | **4** |
| wall_time_s | **~17.0**（REQUEST_TIMEOUT=45） |
| PDF download | **0** |

## Per-case

| case_id | type | matched_title | matched_date | classification | result |
|---------|------|---------------|--------------|----------------|--------|
| `shareholder_meeting_known_003` | known | 2025年第二次临时股东大会决议公告 | 2025-06-27 | classified_correctly / shareholder_meeting_material | **pass** |
| `shareholder_meeting_known_004` | known | 关于召开2025年第二次临时股东大会的公告 | 2025-06-26 | classified_correctly / shareholder_meeting_material | **pass** |

## 运行备注

- dry-run（allow-list）：`DRY_RUN_PASS` · ready=2 · invalid_ready=0 · query=0
- live：一次性 wrapper 将 `REQUEST_TIMEOUT` 提至 45s（**不**改共享 validator）；首跑即 LIVE_PASS，无失败试跑。
- predicted_document_type=`shareholder_meeting_material`；route=`cninfo_general_announcement_pdf`。
- 未重开 known_001 / known_002 / meeting_sample_002 等已 LIVE_PASS 案例。
