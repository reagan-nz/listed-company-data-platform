# CNINFO B 类 B-FM-26 — 非会议类「法律意见书」Routing Harden + Known-003/004 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-26  
> **性质：** routing harden + harvest 晋升 + allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 legal_opinion_known_001–002 / supervisory_board_known_001–002 / shareholder_meeting_known_001–007 / board_resolution_known_001  
> **不**触碰 A/C/D · **不** commit / push · **不** PDF / OCR / DB / RAG  
> standing_scope 允许 CNINFO live；本包闭合 B-FM-25 指出的「非会议类法律意见书落 other」边角

## 1. 候选决策

| # | 类型 | 候选 | 决策 |
|---|------|------|------|
| 1 | routing harden | 非会议法律意见书（增持/分红/可转债）落 `other` | **执行** — 最高价值：config + `_general_document_type` |
| 2 | harvest promotion | BD2E079 → legal_opinion_known_003（增持法律意见书） | **执行** — 主路径 |
| 3 | harvest promotion | BD2E442 → legal_opinion_known_004（差异化分红法律意见书） | **执行** — 同包第二非会议边角 |
| 4 | category-sample | 异常波动（BD2E712） | **拒绝** — 已正确 `announcement`；无 routing 缺口 |
| 5 | category-sample | 业绩预告 | **拒绝** — 已有 general_005 + pattern；无新缺口 |
| 6 | alternate | periodic_guard_001 / regulatory_known_003 | **拒绝** — harvest 仍缺 |

**价值判断：** B-FM-25 已锚会议类法律意见书（含股东（大）会 → announcement）。非会议标题无 general positive_patterns 时 Priority 5 不进入，末尾 fallback 落 `other`；含「决议」的会议法律意见亦会被抬成 `shareholder_meeting_material`。硬化 + known_003/004 live 高于再 live 已闭合包 / 硬推异常波动 category-sample。

## 2. Routing 变更

| 层 | 变更 |
|----|------|
| `config/cninfo_announcement_categories.yaml` | general `positive_patterns` +`法律意见书` +`法律意见` |
| `lab/validate_cninfo_b_class_category_routing.py` | `_general_document_type`：含「法律意见」早退 → `announcement`（先于股东会决议抬升） |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表增法律意见行 |

不扩 schema；不新造 document_type。

## 3. 晋升内容

| case_id | 状态 | harvest | title_pattern | 窗 |
|---------|------|---------|---------------|-----|
| `legal_opinion_known_003` | （新增）→ **ready** | BD2E079 恒逸石化 000703 · ann=1223973353 · 2025-06-24 | `增持公司股份之法律意见书` · 2025-06-23~26 | 增持法律意见书 |
| `legal_opinion_known_004` | （新增）→ **ready** | BD2E442 兰生股份 600826 · ann=1223900931 · 2025-06-17 | `差异化分红的法律意见书` · 2025-06-16~19 | 差异化分红法律意见书 |

路由：含「法律意见」→ `announcement` / `cninfo_general_announcement_pdf`（**非** `other`；**非** `shareholder_meeting_material`）。

## 4. 明确不重开

| case_id / 族 | 说明 |
|--------------|------|
| `legal_opinion_known_001`–`002` | LIVE_PASS（勿重开） |
| `supervisory_board_known_001`–`002` | LIVE_PASS（勿重开） |
| `shareholder_meeting_known_001`–`007` | LIVE_PASS（勿重开） |
| `board_resolution_known_001` | 已有 LIVE_PASS（勿重开） |
| `meeting_sample_002` | LIVE_PASS（勿重开） |

## 5. Allow-list

仅 `legal_opinion_known_003` + `legal_opinion_known_004`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。

## 6. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_category_routing_legal_opinion_non_meeting_edge.py` | **9 OK** |
| `python lab/test_cninfo_b_class_legal_opinion_known_003_004_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_legal_opinion_known_003_004_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_legal_opinion_known_001_002_promotion.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_legal_opinion_known_001_002_live.py` | **3 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_shareholder_meeting_short_form_edge.py` | **10 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_shareholder_meeting_resolution_edge.py` | **9 OK**（不回退） |
| `python lab/test_cninfo_b_class_supervisory_board_known_002_promotion.py` | **6 OK**（不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_007_promotion.py` | **6 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py` | ready=**36** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=36 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

## 7. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO | **4**（2×(topSearch+query)；PDF=0） |
| wall | **~30.9 s** |
| allow-list | `legal_opinion_known_003`, `legal_opinion_known_004` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `legal_opinion_known_003` | …控股股东增持公司股份之法律意见书 | 2025-06-24 | classified_correctly / announcement | **pass** |
| `legal_opinion_known_004` | …差异化分红的法律意见书 | 2025-06-17 | classified_correctly / announcement | **pass** |

执行要点：

1. 首跑即 LIVE_PASS；无网络失败试跑；无 orgId fallback。
2. 共享 routing：config patterns + `_general_document_type` 早退（闭合 other / 误抬会议材料）。
3. predicted_type=`announcement`；与 `other`、股东会材料、董事会决议可区分。

## 8. 能力增益

- 非会议类法律意见书（增持 / 差异化分红等）进入 **known-document ready** 并经公司窗 live metadata 确认
- 闭合 B-FM-25 推迟的「落 other」routing 边角；会议法律意见含「决议」亦不再误抬
- ready 计数 34 → **36**

## 9. Gate 摘要

```text
b_class_legal_opinion_known_003_004_promotion_live_gate = LIVE_PASS
task_id = B-FM-26
cninfo_calls = 4
pdf_downloads = 0
allow_list = legal_opinion_known_003,legal_opinion_known_004
ready_for_commit = true
commit = not_done
push = not_done
```

## 10. 文件

| 路径 | 说明 |
|------|------|
| `config/cninfo_announcement_categories.yaml` | +法律意见书/法律意见 patterns + notes |
| `lab/validate_cninfo_b_class_category_routing.py` | `_general_document_type` 法律意见早退 |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 法律意见行 |
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +legal_opinion_known_003/004 |
| `lab/test_cninfo_b_class_category_routing_legal_opinion_non_meeting_edge.py` | routing 边角锁测 |
| `lab/test_cninfo_b_class_legal_opinion_known_003_004_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_legal_opinion_known_003_004_live.py` | allow-list + mock live 锁测 |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_*` | selector 刷新 ready=36 |
| `outputs/validation/cninfo_b_class_legal_opinion_known_003_004_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_legal_opinion_known_003_004_live_20260715/` | allow-list + live 证据包 |
| `outputs/validation/cninfo_b_class_legal_opinion_known_003_004_promotion_live_20260715.md` | 本报告 |

## 11. 回报卡

| 项 | 值 |
|----|-----|
| task | B-FM-26 非会议法律意见书 routing harden + known_003/004 晋升 + bounded live（BD2E079/442） |
| files | config + routing + plan + fixture + 3 tests + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | routing **9 OK** · promotion **7 OK** · live mock **3 OK** · known_001/002/short-form/resolution/supervisory/shareholder 不回退 · ready **36** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | **4**（PDF=0） |
| allow-list | `legal_opinion_known_003`, `legal_opinion_known_004` |
| wall | live **~30.9 s** |
| ready_for_commit | **true** |

## 12. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选下一边角：异常波动 / 业绩预告 category-sample（routing 已通；仅缺独立 live 锚点时再开），或可转债法律意见书 known 扩展。
3. `periodic_guard_001`（延期披露）仍缺 harvest，不宜硬推。
4. 真·监管问询函原文仍缺 harvest，不宜硬推 `regulatory_known_003`。
