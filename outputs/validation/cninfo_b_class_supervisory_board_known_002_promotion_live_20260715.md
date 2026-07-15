# CNINFO B 类 B-FM-24 — 「监事会决议的公告」Known-002 晋升 + Bounded Live

_生成时间：2026-07-15_

> **性质：** harvest 晋升 + allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 supervisory_board_known_001 / shareholder_meeting_known_001–007 / board_resolution_known_001  
> **不**触碰 A/C/D  
> standing_scope 允许 CNINFO live；本包仅新晋 `supervisory_board_known_002`（闭合 B-FM-23 指出的「的」助词边角）

## 0. 任务选择

| # | 候选 | 说明 | 裁决 |
|---|------|------|------|
| 1 | harvest promotion | BD2E244 → supervisory_board_known_002（会议决议**的**公告） | **执行** — 主路径（B-FM-23 下一边角；镜像股东会 known_002「的」助词矩阵） |
| 2 | category-sample | 短标题「监事会决议公告」全市场窗 | **推迟** — 长标题通常无连续「监事会决议公告」子串；价值低于 known「的」边角 |
| 3 | harvest promotion | board_resolution_known_001 再 live | **拒绝** — 早期 corpus live 已 LIVE_PASS；非新能力 |
| 4 | alternate | periodic_guard_001（延期披露） | **拒绝** — harvest 仍缺 |
| 5 | alternate | 法律意见书新 document_type | **拒绝** — 保持 announcement；不扩 schema |

**价值判断：** known_001 锚定无「的」长标题届次片段；harvest BD2E244 提供「会议决议的公告」助词变体，与股东会 known_002 对称补齐监事会决议 pattern 矩阵。高于再 live 董事会 known / 硬推延期披露。

## 1. 晋升槽位

| case_id | 状态 | harvest | title_pattern | 窗 |
|---------|------|---------|---------------|-----|
| `supervisory_board_known_002` | （新增）→ **ready** | BD2E244 农心科技 001231 · ann=1223998915 · 2025-06-26 | `第二十二次会议决议的公告` · 2025-06-25~28 | 监事会会议决议（含「的」） |

路由（依赖既有 general_006 / 监事会分支）：标题含「监事会」→ `announcement` / `cninfo_general_announcement_pdf`（**非** `board_resolution`）。

说明：首跑试用 pattern `会议决议的公告` 同窗命中 3 条 → ambiguous；收紧为届次锚定 `第二十二次会议决议的公告`（仍含「的」），与 known_001 `第二十四次会议决议公告` 互斥。

## 2. 已闭合（本包不重开）

| case_id | pattern / 类型 | 状态 |
|---------|----------------|------|
| `supervisory_board_known_001` | 第二十四次会议决议公告 | LIVE_PASS（勿重开） |
| `shareholder_meeting_known_001`–`007` | 股东（大）会通知/决议族 | LIVE_PASS（勿重开） |
| `board_resolution_known_001` | 董事会决议公告 | 已有 LIVE_PASS（勿重开） |

## 3. Allow-list

仅 `supervisory_board_known_002`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。

## 4. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_supervisory_board_known_002_promotion.py` | **6 OK** |
| `python lab/test_cninfo_b_class_supervisory_board_known_002_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_supervisory_board_known_001_promotion.py` | **6 OK**（不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_007_promotion.py` | **6 OK**（不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_005_006_promotion.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_shareholder_meeting_short_form_edge.py` | **10 OK**（B-FM-20 不回退） |
| `python lab/test_cninfo_b_class_category_routing_shareholder_meeting_resolution_edge.py` | **9 OK**（B-FM-18 不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py` | ready **32** · invalid_ready **0** · PASS |

| 阶段 | 结果 |
|------|------|
| fixture dry-run | **DRY_RUN_PASS** · ready=32 · query=0 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=1 · would_query=true |
| live 试跑（宽 pattern） | **PARTIAL** · ambiguous=1（同窗×3） |
| bounded live（收紧 pattern） | **LIVE_PASS** · pass=**1**/0/0 |

## 5. Live 证据

| 项 | 值 |
|----|-----|
| CNINFO | **4**（试跑 2 + 成功跑 2；各 1 topSearch + 1 query；PDF=0） |
| wall（成功跑） | **~12.7 s** |
| allow-list | `supervisory_board_known_002` |
| matched | 农心作物科技股份有限公司第二届监事会第二十二次会议决议的公告 · 2025-06-26 |
| predicted_type | `announcement` |
| predicted_route | `cninfo_general_announcement_pdf` |
| classification | classified_correctly |

| case_id | matched title | date | classification | result |
|---------|---------------|------|----------------|--------|
| `supervisory_board_known_002` | …第二十二次会议决议的公告 | 2025-06-26 | classified_correctly / announcement | **pass** |

## 6. 观察

1. 宽 pattern 同窗歧义是预期风险；届次锚定保留「的」助词能力增益并消除 ambiguous。
2. 未修改共享 validator / routing 代码（监事会→announcement 已覆盖）。
3. predicted_type=`announcement`；与董事会 `board_resolution`、股东会 `shareholder_meeting_material`、known_001 均可区分。
4. 成功跑 query_executed=1；CNINFO 合计含试跑 = **4**。

## 7. 能力增益

- 「监事会会议决议的公告」（「的」助词）进入 **known-document ready** 并经公司窗 live metadata 确认（known_002）
- 与 known_001（无「的」届次片段）形成监事会决议 pattern 对；对称股东会 known_002
- 不扩 schema；诚实保留 document_type=`announcement`

## 8. 返回包

```text
b_class_supervisory_board_known_002_promotion_live_gate = LIVE_PASS
task_id = B-FM-24
CNINFO = 4
wall_s ~= 12.7
allow_list = supervisory_board_known_002
ready_for_commit = true
```

## 9. 修改 / 产物文件

| 路径 | 作用 |
|------|------|
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | 新晋 known_002 |
| `lab/test_cninfo_b_class_supervisory_board_known_002_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_supervisory_board_known_002_live.py` | allow-list + mock live 锁测 |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_{report.csv,summary.md}` | ready=32 刷新 |
| `outputs/validation/cninfo_b_class_supervisory_board_known_002_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_supervisory_board_known_002_live_20260715/` | allow-list + live 证据包 |
| `outputs/validation/cninfo_b_class_supervisory_board_known_002_promotion_live_20260715.md` | 本报告 |

## 10. Controller 返回摘要

| 项 | 值 |
|----|-----|
| task | B-FM-24 「监事会决议的公告」known_002 晋升 + bounded live（BD2E244） |
| files | fixture + 2 tests + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | promotion **6 OK** · live mock **3 OK** · known_001/007/005-006/short-form/resolution 不回退 · ready **32** · dry-run **PASS** · live **1/1 LIVE_PASS** |
| CNINFO | **4**（试跑 ambiguous 2 + 成功 2；PDF=0） |
| allow-list | `supervisory_board_known_002` |
| wall | live 成功跑 **~12.7 s** |
| ready_for_commit | **true** |

## 11. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选下一边角：监事会短标题 category-sample（需可匹配真实标题窗），或其它未覆盖 event（法律意见书保持 announcement）。
3. `periodic_guard_001`（延期披露）仍缺 harvest，不宜硬推。
4. 真·监管问询函原文仍缺 harvest，不宜硬推 `regulatory_known_003`。
5. 若需更细 document_type，须先扩 `b_document.schema.json` 枚举（跨 schema；本包明确未做）。
