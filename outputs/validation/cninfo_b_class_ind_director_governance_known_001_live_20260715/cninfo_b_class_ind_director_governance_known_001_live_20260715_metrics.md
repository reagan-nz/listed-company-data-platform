# B-FM-33 Live Metrics — independent_director_meeting_review_known_001 / nominee_declaration_known_001

| 项 | 值 |
|----|-----|
| task_id | B-FM-33 |
| executor | b-class-executor |
| result | **LIVE_PASS** |
| ready / pass / fail / ambiguous | **2** / **2** / **0** / **0** |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计，含首轮 PARTIAL 消歧重试） | **8** |
| wall（成功 live） | **~27.8 s** |
| allow-list | `independent_director_meeting_review_known_001`, `independent_director_nominee_declaration_known_001` |

## 证据锚点

- harvest 锚点 BD2E426（金枫酒业 600616 / ann=1223951163）、BD2E264（伟星股份 002003 / ann=1223973877）。
- 路由：含「独立董事专门会议的审核意见」或「独立董事提名人声明与承诺」→ `announcement` / `cninfo_general_announcement_pdf`（非 `other`）。
- 窄 pattern：勿裸「审核意见」（BD2E501 年报审核意见仍 periodic）；提名人案 title_pattern 含「（张永炬）」消歧。
- 无 orgId fallback；无 PDF / OCR / DB / RAG。

## 首轮 / 重试

1. 首轮 live：meeting_review **pass**；nominee **ambiguous**（同窗 3 条提名人声明）。
2. 收窄 nominee `title_pattern` → `独立董事提名人声明与承诺（张永炬）` 后重试 → **2/2 LIVE_PASS**。
