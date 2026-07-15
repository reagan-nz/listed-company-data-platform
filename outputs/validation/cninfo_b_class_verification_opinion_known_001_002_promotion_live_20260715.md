# CNINFO B 类 B-FM-27 — 「核查意见」Routing Harden + Known-001/002 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-27  
> **性质：** routing harden + harvest 晋升 + allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 legal_opinion_known_001–004 / supervisory_board_known_001–002 / shareholder_meeting_known_001–007 / board_resolution_known_001  
> **不**触碰 A/C/D · **不** commit / push · **不** PDF / OCR / DB / RAG  
> standing_scope 允许 CNINFO live；本包闭合 B-FM-26 之后最高价值边角：保荐「核查意见」落 `other`

## 1. 候选决策

| # | 类型 | 候选 | 决策 |
|---|------|------|------|
| 1 | routing harden | 保荐「核查意见」落 `other` | **执行** — 最高价值：config + `_general_document_type` |
| 2 | harvest promotion | BD2E172 → verification_opinion_known_001（募资置换核查意见） | **执行** — 主路径 |
| 3 | harvest promotion | BD2E466 → verification_opinion_known_002（限售流通核查意见） | **执行** — 同包第二边角 |
| 4 | harvest promotion | BD2E472 → legal_opinion_known_005（可转债法律意见书） | **拒绝** — B-FM-26 路由已通；仅缺 live 锚点，低于新 other 缺口 |
| 5 | category-sample | 异常波动 / 业绩预告 | **拒绝** — 已正确 `announcement`；无 routing 缺口 |
| 6 | alternate | 保荐书 / 权益变动报告书 / periodic_guard_001 / regulatory_known_003 | **拒绝** — 保荐书可后续；延期披露与真·问询函仍缺 harvest |

**价值判断：** B-FM-26 已闭合非会议法律意见书落 `other`。harvest 中「…核查意见」标题同样无 general positive_patterns，Priority 5 不进入，末尾 fallback 落 `other`。硬化 + known_001/002 live 高于再 live 已通路由的可转债法律意见书 / 异常波动 category-sample。

## 2. Routing 变更

| 层 | 变更 |
|----|------|
| `config/cninfo_announcement_categories.yaml` | general `positive_patterns` +`核查意见` |
| `lab/validate_cninfo_b_class_category_routing.py` | `_general_document_type`：含「核查意见」早退 → `announcement` |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表增核查意见行 |

不扩 schema；不新造 document_type。

## 3. 晋升内容

| case_id | 状态 | harvest | title_pattern | 窗 |
|---------|------|---------|---------------|-----|
| `verification_opinion_known_001` | （新增）→ **ready** | BD2E172 三六零 601360 · ann=1224013030 · 2025-06-27 | `募集资金等额置换的核查意见` · 2025-06-26~29 | 募资置换核查意见 |
| `verification_opinion_known_002` | （新增）→ **ready** | BD2E466 福元医药 601089 · ann=1223974498 · 2025-06-24 | `限售股上市流通的核查意见` · 2025-06-23~26 | 限售流通核查意见 |

路由：含「核查意见」→ `announcement` / `cninfo_general_announcement_pdf`（**非** `other`）。

## 4. 明确不重开

| case_id / 族 | 说明 |
|--------------|------|
| `legal_opinion_known_001`–`004` | LIVE_PASS（勿重开） |
| `supervisory_board_known_001`–`002` | LIVE_PASS（勿重开） |
| `shareholder_meeting_known_001`–`007` | LIVE_PASS（勿重开） |
| `board_resolution_known_001` | 已有 LIVE_PASS（勿重开） |
| `meeting_sample_002` | LIVE_PASS（勿重开） |

## 5. Allow-list

仅 `verification_opinion_known_001` + `verification_opinion_known_002`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。

## 6. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_category_routing_verification_opinion_edge.py` | **9 OK** |
| `python lab/test_cninfo_b_class_verification_opinion_known_001_002_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_verification_opinion_known_001_002_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_legal_opinion_known_003_004_promotion.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_legal_opinion_non_meeting_edge.py` | **9 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_shareholder_meeting_short_form_edge.py` | **10 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_shareholder_meeting_resolution_edge.py` | **9 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py` | ready=**38** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=38 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

## 7. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO | **4**（2×(topSearch+query)；PDF=0） |
| wall | **~20.0 s** |
| allow-list | `verification_opinion_known_001`, `verification_opinion_known_002` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `verification_opinion_known_001` | …募集资金等额置换的核查意见 | 2025-06-27 | classified_correctly / announcement | **pass** |
| `verification_opinion_known_002` | …限售股上市流通的核查意见 | 2025-06-24 | classified_correctly / announcement | **pass** |

执行要点：

1. 首跑即 LIVE_PASS；无网络失败试跑；无 orgId fallback。
2. 共享 routing：config patterns + `_general_document_type` 早退（闭合 other）。
3. predicted_type=`announcement`；与 `other`、股东会材料、董事会决议、法律意见书可区分。

## 8. 能力增益

- 保荐机构「核查意见」（募资置换 / 限售流通等）进入 **known-document ready** 并经公司窗 live metadata 确认
- 闭合 B-FM-26 之后新的「落 other」routing 边角（非再 live 已通包）
- ready 计数 36 → **38**

## 9. Gate 摘要

```text
b_class_verification_opinion_known_001_002_promotion_live_gate = LIVE_PASS
task_id = B-FM-27
cninfo_calls = 4
pdf_downloads = 0
ready_for_commit = true
commit = not_done
push = not_done
```

## 10. 受保护 / 隔离

- 未触碰 A/C/D 线文件
- 未 mutate 既有 LIVE_PASS live 根（legal_opinion / supervisory / shareholder）
- 未 PDF / OCR / DB / MinIO / RAG
- 未 commit / push

## 11. 文件清单

| 路径 | 角色 |
|------|------|
| `config/cninfo_announcement_categories.yaml` | +核查意见 pattern |
| `lab/validate_cninfo_b_class_category_routing.py` | `_general_document_type` 早退 |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表 |
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +known_001/002 |
| `lab/test_cninfo_b_class_category_routing_verification_opinion_edge.py` | routing 锁测 |
| `lab/test_cninfo_b_class_verification_opinion_known_001_002_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_verification_opinion_known_001_002_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_*` | ready 刷新（38） |
| `outputs/validation/cninfo_b_class_verification_opinion_known_001_002_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_verification_opinion_known_001_002_live_20260715/` | live 包 |
| `outputs/validation/cninfo_b_class_verification_opinion_known_001_002_promotion_live_20260715.md` | 本报告 |

## 12. 返回包

| 项 | 值 |
|----|-----|
| task | B-FM-27 核查意见 routing harden + known_001/002 晋升 + bounded live（BD2E172/466） |
| files | config + routing + plan + fixture + 3 tests + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | routing **9 OK** · promotion **7 OK** · live mock **3 OK** · legal_opinion/short-form/resolution 不回退 · ready **38** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | **4**（PDF=0） |
| allow-list | `verification_opinion_known_001`, `verification_opinion_known_002` |
| wall | live **~20.0 s** |
| ready_for_commit | **true** |

## 13. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选下一边角：可转债法律意见书 known 扩展（BD2E472；路由已通）、或「上市保荐书」落 other 硬化。
3. `periodic_guard_001`（延期披露）仍缺 harvest，不宜硬推。
4. 真·监管问询函原文仍缺 harvest，不宜硬推 `regulatory_known_003`。
