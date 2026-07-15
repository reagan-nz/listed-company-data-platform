# CNINFO B 类 Shareholder Meeting Known-005/006 Live Metrics — B-FM-21

_生成时间：2026-07-15_

| 字段 | 值 |
|------|-----|
| task_id | B-FM-21 |
| result | **LIVE_PASS** |
| ready_cases | 2 |
| pass / fail / ambiguous | **2 / 0 / 0** |
| query_executed | **2**（hisAnnouncement/query） |
| topSearch | **2** |
| CNINFO 本包合计 | **4** |
| wall_time_s | **~23.2**（默认 REQUEST_TIMEOUT；无 wrapper） |
| PDF download | **0** |

## Per-case

| case_id | type | matched_title | matched_date | classification | result |
|---------|------|---------------|--------------|----------------|--------|
| `shareholder_meeting_known_005` | known | 2025年第五次临时股东会决议公告 | 2025-06-30 | classified_correctly / shareholder_meeting_material | **pass** |
| `shareholder_meeting_known_006` | known | 关于召开2025年第二次临时股东会的通知 | 2025-06-26 | classified_correctly / shareholder_meeting_material | **pass** |

## 运行备注

- dry-run（allow-list）：`DRY_RUN_PASS` · ready=2 · invalid_ready=0 · query=0
- live：首跑即 LIVE_PASS；无网络失败试跑；无 orgId fallback；**未**修改共享 validator。
- predicted_document_type=`shareholder_meeting_material`；route=`cninfo_general_announcement_pdf`（与 B-FM-20 对齐）。
- 未重开 known_001–004 / meeting_sample_002 等已 LIVE_PASS 案例。
- BD2E258（年度股东会决议）本包不晋升、不 live。
