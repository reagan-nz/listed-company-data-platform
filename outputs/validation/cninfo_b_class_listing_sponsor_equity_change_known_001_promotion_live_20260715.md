# CNINFO B 类 B-FM-28 — 「保荐书」/「权益变动报告书」Routing Harden + Known-001 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-28  
> **性质：** routing harden + harvest 晋升 + allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 verification_opinion_known_001/002 / legal_opinion_known_001–004 / supervisory_board_known_001–002 / shareholder_meeting_known_001–007 / board_resolution_known_001  
> **不**触碰 A/C/D · **不** commit / push · **不** PDF / OCR / DB / RAG  
> standing_scope 允许 CNINFO live；本包闭合 B-FM-27 之后最高价值边角：上市保荐书 / 简式权益变动报告书落 `other`

## 1. 候选决策

| # | 类型 | 候选 | 决策 |
|---|------|------|------|
| 1 | routing harden | 「上市保荐书」落 `other` | **执行** — 最高价值：config + `_general_document_type` |
| 2 | harvest promotion | BD2E252 → listing_sponsor_known_001（可转债上市保荐书） | **执行** — 主路径 |
| 3 | routing harden + promotion | BD2E482 → equity_change_report_known_001（简式权益变动报告书） | **执行** — 同包第二 other 缺口 |
| 4 | harvest promotion | BD2E472 → legal_opinion_known_005（可转债法律意见书） | **拒绝** — 路由已通；低于新 other 缺口 |
| 5 | alternate | periodic_guard_001 / regulatory_known_003 | **拒绝** — harvest 仍缺 |

**价值判断：** B-FM-27 已闭合「核查意见」落 `other`。harvest 中「…上市保荐书」「…简式权益变动报告书」同样无 general positive_patterns，Priority 5 不进入，末尾 fallback 落 `other`。双缺口硬化 + known live 高于再 live 已通路由的可转债法律意见书。

## 2. Routing 变更

| 层 | 变更 |
|----|------|
| `config/cninfo_announcement_categories.yaml` | general `positive_patterns` +`保荐书` +`权益变动报告书` |
| `lab/validate_cninfo_b_class_category_routing.py` | `_general_document_type`：含「保荐书」/「权益变动报告书」早退 → `announcement` |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表增保荐书 / 权益变动报告书行 |

不扩 schema；不新造 document_type。

## 3. 晋升内容

| case_id | 状态 | harvest | title_pattern | 窗 |
|---------|------|---------|---------------|-----|
| `listing_sponsor_known_001` | （新增）→ **ready** | BD2E252 尚太科技 001301 · ann=1223824291 · 2025-06-09 | `可转换公司债券的上市保荐书` · 2025-06-08~11 | 可转债上市保荐书 |
| `equity_change_report_known_001` | （新增）→ **ready** | BD2E482 德林海 688069 · ann=1223980482 · 2025-06-25 | `权益变动报告书` · 2025-06-24~27 | 简式权益变动报告书 |

路由：含「保荐书」或「权益变动报告书」→ `announcement` / `cninfo_general_announcement_pdf`（**非** `other`）。

**searchkey 注记：** CNINFO 对「简式权益变动报告书」整串返回空（「简式」未有效索引）；pattern 取「权益变动报告书」可命中，且不误匹配同窗「权益变动提示性公告」。

## 4. 明确不重开

| case_id / 族 | 说明 |
|--------------|------|
| `verification_opinion_known_001`–`002` | LIVE_PASS（勿重开） |
| `legal_opinion_known_001`–`004` | LIVE_PASS（勿重开） |
| `supervisory_board_known_001`–`002` | LIVE_PASS（勿重开） |
| `shareholder_meeting_known_001`–`007` | LIVE_PASS（勿重开） |
| `board_resolution_known_001` | 已有 LIVE_PASS（勿重开） |

## 5. Allow-list

仅 `listing_sponsor_known_001` + `equity_change_report_known_001`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。  
ready_for_commit 文件清单不含 console / terminal 日志。

## 6. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_category_routing_listing_sponsor_equity_change_edge.py` | **7 OK** |
| `python lab/test_cninfo_b_class_listing_sponsor_equity_change_known_001_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_listing_sponsor_equity_change_known_001_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_category_routing_verification_opinion_edge.py` | **9 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_legal_opinion_non_meeting_edge.py` | **9 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py` | ready=**40** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=40 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live（复跑） | **LIVE_PASS** · pass=**2**/0/0 |

## 7. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO | **4**（成功复跑：2×(topSearch+query)；PDF=0） |
| wall | **~21.3 s** |
| allow-list | `listing_sponsor_known_001`, `equity_change_report_known_001` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `listing_sponsor_known_001` | …可转换公司债券的上市保荐书（修订稿） | 2025-06-09 | classified_correctly / announcement | **pass** |
| `equity_change_report_known_001` | 德林海简式权益变动报告书 | 2025-06-25 | classified_correctly / announcement | **pass** |

执行要点：

1. 首跑 PARTIAL（equity searchkey 整串空）；pattern 修正后复跑 LIVE_PASS；无 orgId fallback。
2. 共享 routing：config patterns + `_general_document_type` 早退（闭合 other）。
3. predicted_type=`announcement`；与 `other`、核查意见、法律意见书、股东会材料可区分。

## 8. 能力增益

- 上市保荐书 / 简式权益变动报告书进入 **known-document ready** 并经公司窗 live metadata 确认
- 闭合 B-FM-27 之后两处新的「落 other」routing 边角
- ready 计数 38 → **40**

## 9. Gate 摘要

```text
b_class_listing_sponsor_equity_change_known_001_promotion_live_gate = LIVE_PASS
task_id = B-FM-28
cninfo_calls = 4
pdf_downloads = 0
ready_for_commit = true
commit = not_done
push = not_done
```

## 10. 受保护 / 隔离

- 未触碰 A/C/D 线文件（本包修改仅 B 线）
- 未 mutate 既有 LIVE_PASS live 根（verification_opinion / legal_opinion / supervisory / shareholder）
- 未 PDF / OCR / DB / MinIO / RAG
- 未 commit / push

## 11. 文件清单（ready_for_commit；不含 console 日志）

| 路径 | 角色 |
|------|------|
| `config/cninfo_announcement_categories.yaml` | +保荐书 / 权益变动报告书 pattern |
| `lab/validate_cninfo_b_class_category_routing.py` | `_general_document_type` 早退 |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表 |
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +listing_sponsor / equity_change known_001 |
| `lab/test_cninfo_b_class_category_routing_listing_sponsor_equity_change_edge.py` | routing 锁测 |
| `lab/test_cninfo_b_class_listing_sponsor_equity_change_known_001_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_listing_sponsor_equity_change_known_001_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_*` | ready 刷新（40） |
| `outputs/validation/cninfo_b_class_listing_sponsor_equity_change_known_001_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_listing_sponsor_equity_change_known_001_live_20260715/` | live 包 |
| `outputs/validation/cninfo_b_class_listing_sponsor_equity_change_known_001_promotion_live_20260715.md` | 本报告 |

## 12. 返回包

| 项 | 值 |
|----|-----|
| task | B-FM-28 保荐书/权益变动报告书 routing harden + known_001 晋升 + bounded live（BD2E252/482） |
| files | config + routing + plan + fixture + 3 tests + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | routing **7 OK** · promotion **7 OK** · live mock **3 OK** · verification/legal 不回退 · ready **40** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | **4**（成功复跑；PDF=0） |
| allow-list | `listing_sponsor_known_001`, `equity_change_report_known_001` |
| wall | live **~21.3 s** |
| ready_for_commit | **true** |

## 13. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选下一边角：可转债法律意见书 known 扩展（BD2E472；路由已通）、或其他仍落 `other` 的中介文书。
3. `periodic_guard_001`（延期披露）仍缺 harvest，不宜硬推。
4. 真·监管问询函原文仍缺 harvest，不宜硬推 `regulatory_known_003`。
5. 已知旁路：含「半年报」子串的上市保荐书仍可能被 periodic 优先命中（非本包范围）。
