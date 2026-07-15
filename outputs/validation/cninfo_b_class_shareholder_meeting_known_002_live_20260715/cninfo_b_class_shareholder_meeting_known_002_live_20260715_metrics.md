# CNINFO B 类 Shareholder Meeting Known-002 Live Metrics — B-FM-17

_生成时间：2026-07-15_

| 字段 | 值 |
|------|-----|
| task_id | B-FM-17 |
| result | **LIVE_PASS** |
| ready_cases | 1 |
| pass / fail / ambiguous | **1 / 0 / 0** |
| query_executed | **1**（hisAnnouncement/query） |
| topSearch | **1** |
| CNINFO 本包合计 | **2** |
| wall_time_s | **~4.3**（REQUEST_TIMEOUT=45） |
| PDF download | **0** |

## Per-case

| case_id | type | matched_title | matched_date | classification | result |
|---------|------|---------------|--------------|----------------|--------|
| `shareholder_meeting_known_002` | known | 关于召开2025年第三次临时股东大会的通知 | 2025-06-27 | classified_correctly / shareholder_meeting_material | **pass** |

## 运行备注

- dry-run：`DRY_RUN_PASS` · ready=1 · invalid_ready=0 · query=0
- live：一次性 wrapper 将 `REQUEST_TIMEOUT` 提至 45s（**不**改共享 validator）；首跑即 LIVE_PASS，无失败试跑。
- predicted_document_type=`shareholder_meeting_material`；route=`cninfo_general_announcement_pdf`。
