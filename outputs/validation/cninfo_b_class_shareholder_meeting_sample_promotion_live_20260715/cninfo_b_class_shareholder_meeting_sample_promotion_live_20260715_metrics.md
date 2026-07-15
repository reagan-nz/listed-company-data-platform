# CNINFO B 类 Shareholder Meeting Sample Promotion Live Metrics — B-FM-15

_生成时间：2026-07-15_

| 字段 | 值 |
|------|-----|
| task_id | B-FM-15 |
| result | **LIVE_PASS** |
| ready_cases | 1 |
| pass / fail / ambiguous | **1 / 0 / 0** |
| query_executed | **2**（category sse+szse） |
| topSearch | **0**（本包无 known） |
| CNINFO 本包合计 | **2** |
| wall_time_s | **~5.3**（REQUEST_TIMEOUT=45） |
| PDF download | **0** |

## Per-case

| case_id | type | matched_title（节选） | matched_date | classification | result |
|---------|------|----------------------|--------------|----------------|--------|
| `meeting_sample_002` | category | 关于召开2024年度股东大会通知的提示性公告（窗内 2 hits / scanned=60） | 2025-06-26 | classified_correctly / announcement | **pass** |

## 运行备注

- dry-run：`DRY_RUN_PASS` · ready=1 · invalid_ready=0 · query=0
- live：一次性 wrapper 将 `REQUEST_TIMEOUT` 提至 45s（**不**改共享 validator）；首跑即 LIVE_PASS，无失败试跑。
- predicted_document_type=`announcement` 落在 `expected_document_types`（含 shareholder_meeting_material / meeting_notice / announcement）；route=`cninfo_general_announcement_pdf`。
