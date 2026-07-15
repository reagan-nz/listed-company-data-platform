# B-R16-02 Live Sample Allow-List

| 字段 | 值 |
|------|-----|
| task_id | B-R16-02 |
| track | B |
| mode | `--live-metadata`（仅公告 metadata） |
| CNINFO cap | ≤20 total HTTP requests（topSearch + hisAnnouncement/query） |
| PDF download | 禁止 |
| FP lineage | 禁止新造 |

## Allowed case_id

1. `inquiry_known_002`
2. `meeting_known_002`
3. `ir_activity_known_001`
4. `shareholder_meeting_known_001`

## Explicitly excluded

- 其他 ready known-document（`inquiry_known_003`, `regulatory_known_002`, `meeting_known_001`, `board_resolution_known_001`）— 非本次晋升样本
- `periodic_guard_002` — 非本任务目标
- 全部 placeholder / A/C/D 文件

## Scoped inputs

- known: `known_document_retrieval_cases_live_sample_allowlist.yaml`
- category: `category_sample_cases_live_sample_empty.yaml`
