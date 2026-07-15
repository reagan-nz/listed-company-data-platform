# CNINFO B 类 B-FM-23 — 「监事会决议」Known-001 晋升 + Bounded Live

_生成时间：2026-07-15_

> **性质：** harvest 晋升 + allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 shareholder_meeting_known_001–007 / board_resolution_known_001  
> **不**触碰 A/C/D  
> standing_scope 允许 CNINFO live；本包仅新晋 `supervisory_board_known_001`（闭合 B-FM-22 推迟的监事会边角）

## 0. 任务选择

| # | 候选 | 说明 | 裁决 |
|---|------|------|------|
| 1 | harvest promotion | BD2E091 → supervisory_board_known_001（监事会会议决议） | **执行** — 主路径（B-FM-22 明确下一边角；路由已有 general_006） |
| 2 | routing edges | 新 document_type（如 supervisory_board_resolution） | **拒绝** — schema 无该枚举；general_006 已锁 announcement；本包不扩 schema |
| 3 | harvest promotion | board_resolution_known_001 再 live | **拒绝** — 非新能力；本包不重开 |
| 4 | alternate | periodic_guard_001（延期披露） | **拒绝** — harvest 仍缺 |
| 5 | alternate | regulatory_known_003（真·问询函原文） | **拒绝** — harvest 仍缺 |

**价值判断：** 股东会 known_001–007 与 B-FM-20 简称 trio 已闭合；监事会决议是下一未覆盖 event 族。路由已通（announcement → general），缺独立 known-document pattern 矩阵与 live 锚点。高于硬推延期披露 / 真·问询函原文。

## 1. 晋升槽位

| case_id | 状态 | harvest | title_pattern | 窗 |
|---------|------|---------|---------------|-----|
| `supervisory_board_known_001` | （新增）→ **ready** | BD2E091 网宿科技 300017 · ann=1224016408 · 2025-06-27 | `第二十四次会议决议公告` · 2025-06-26~29 | 监事会会议决议 |

路由（依赖既有 general_006）：标题含「监事会」→ `announcement` / `cninfo_general_announcement_pdf`（**非** `board_resolution`）。

说明：长标题「第六届监事会第二十四次会议决议公告」不含连续子串「监事会决议公告」；pattern 取长标题可匹配届次片段，避免与董事会 / 股东会决议互撞。

## 2. 已闭合（本包不重开）

| case_id | pattern / 类型 | 状态 |
|---------|----------------|------|
| `shareholder_meeting_known_001`–`007` | 股东（大）会通知/决议族 | LIVE_PASS（勿重开） |
| `board_resolution_known_001` | 董事会决议公告 | ready（本包不 live） |
| B-FM-20 short-form trio | 股东会同义路由 | 已闭合 |

## 3. Allow-list

仅 `supervisory_board_known_001`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard / board_resolution_known_001。

## 4. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_supervisory_board_known_001_promotion.py` | **6 OK** |
| `python lab/test_cninfo_b_class_supervisory_board_known_001_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_007_promotion.py` | **6 OK**（不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_005_006_promotion.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_shareholder_meeting_short_form_edge.py` | **10 OK**（B-FM-20 不回退） |
| `python lab/test_cninfo_b_class_category_routing_shareholder_meeting_resolution_edge.py` | **9 OK**（B-FM-18 不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py` | ready **31** · invalid_ready **0** · PASS |

| 阶段 | 结果 |
|------|------|
| fixture dry-run | **DRY_RUN_PASS** · ready=31 · query=0 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=1 · would_query=true |
| bounded live | **LIVE_PASS** · pass=**1**/0/0 |

## 5. Live 证据

| 项 | 值 |
|----|-----|
| CNINFO | **2**（1 topSearch + 1 query；PDF=0） |
| wall | **~7.6 s** |
| allow-list | `supervisory_board_known_001` |
| matched | 第六届监事会第二十四次会议决议公告 · 2025-06-27 |
| predicted_type | `announcement` |
| predicted_route | `cninfo_general_announcement_pdf` |
| classification | classified_correctly |

| case_id | matched title | date | classification | result |
|---------|---------------|------|----------------|--------|
| `supervisory_board_known_001` | 第六届监事会第二十四次会议决议公告 | 2025-06-27 | classified_correctly / announcement | **pass** |

## 6. 观察

1. 首跑即 LIVE_PASS；无网络失败试跑；无 orgId fallback。
2. 未修改共享 validator / routing 代码（general_006 已覆盖）。
3. predicted_type=`announcement`；与董事会 `board_resolution`、股东会 `shareholder_meeting_material` 可区分。
4. query_executed 计数=1（仅 hisAnnouncement）；CNINFO 合计含 topSearch = **2**。

## 7. 能力增益

- 「监事会会议决议」进入 **known-document ready** 并经公司窗 live metadata 确认（known_001）
- 闭合 B-FM-22 推迟的监事会边角；与 board_resolution / 股东会决议族形成三分叉
- 不扩 schema；诚实保留 document_type=`announcement`

## 8. 返回包

```text
b_class_supervisory_board_known_001_promotion_live_gate = LIVE_PASS
task_id = B-FM-23
CNINFO = 2
wall_s ~= 7.6
allow_list = supervisory_board_known_001
ready_for_commit = true
```

## 9. 修改 / 产物文件

| 路径 | 作用 |
|------|------|
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | 新晋 known_001 |
| `lab/test_cninfo_b_class_supervisory_board_known_001_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_supervisory_board_known_001_live.py` | allow-list + mock live 锁测 |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_{report.csv,summary.md}` | ready=31 刷新 |
| `outputs/validation/cninfo_b_class_supervisory_board_known_001_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_supervisory_board_known_001_live_20260715/` | allow-list + live 证据包 |
| `outputs/validation/cninfo_b_class_supervisory_board_known_001_promotion_live_20260715.md` | 本报告 |

## 10. Controller 返回摘要

| 项 | 值 |
|----|-----|
| task | B-FM-23 「监事会决议」known_001 晋升 + bounded live（BD2E091） |
| files | fixture + 2 tests + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | promotion **6 OK** · live mock **3 OK** · known_005/006/007/short-form/resolution 不回退 · ready **31** · dry-run **PASS** · live **1/1 LIVE_PASS** |
| CNINFO | **2**（topSearch=1 + query=1；PDF=0） |
| allow-list | `supervisory_board_known_001` |
| wall | live **~7.6 s** |
| ready_for_commit | **true** |

---

## 11. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选下一边角：监事会短标题「监事会决议公告」category-sample，或其它未覆盖 event category（法律意见书保持 announcement 排除）。
3. `periodic_guard_001`（延期披露）仍缺 harvest，不宜硬推。
4. 真·监管问询函原文仍缺 harvest，不宜硬推 `regulatory_known_003`。
5. 若需更细 document_type，须先扩 `b_document.schema.json` 枚举（跨 schema；本包明确未做）。
