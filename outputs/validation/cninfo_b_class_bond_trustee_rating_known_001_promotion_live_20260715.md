# CNINFO B 类 B-FM-29 — 「受托管理事务报告」/「跟踪评级报告」Routing Harden + Known-001 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-29  
> **性质：** routing harden + harvest 晋升 + allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 listing_sponsor_known_001 / equity_change_report_known_001 / verification_opinion_known_001/002 / legal_opinion_known_001–004 / supervisory_board_known_001–002 / shareholder_meeting_known_001–007 / board_resolution_known_001  
> **不**触碰 A/C/D · **不** commit / push · **不** PDF / OCR / DB / RAG  
> standing_scope 允许 CNINFO live；本包闭合 B-FM-28 之后最高价值边角：债券受托管理事务报告 / 跟踪评级报告落 `other`

## 1. 候选决策

| # | 类型 | 候选 | 决策 |
|---|------|------|------|
| 1 | routing harden | 「受托管理事务报告」落 `other`（harvest ~20+） | **执行** — 最高价值：config + `_general_document_type` |
| 2 | harvest promotion | BD2E254 → bond_trustee_report_known_001 | **执行** — 主路径 |
| 3 | routing harden + promotion | BD2E408 → tracking_rating_report_known_001（跟踪评级报告） | **执行** — 同包第二 other 缺口 |
| 4 | harvest promotion | BD2E472 → legal_opinion_known_005（可转债法律意见书） | **拒绝** — 路由已通；低于新 other 缺口 |
| 5 | routing FP | 「持续督导年度报告书」误进 annual_report | **推迟** — 非 other；属 periodic 误抬，另开 |
| 6 | alternate | periodic_guard_001 / regulatory_known_003 | **拒绝** — harvest 仍缺 |

**价值判断：** B-FM-28 已闭合保荐书 / 权益变动报告书落 `other`。harvest 中「…受托管理事务报告」「…跟踪评级报告」同样无 general positive_patterns，Priority 5 不进入，末尾 fallback 落 `other`（扫描约 54 条 other 中债券受托/评级为最大中介文书簇）。双缺口硬化 + known live 高于再 live 已通路由的可转债法律意见书。

## 2. Routing 变更

| 层 | 变更 |
|----|------|
| `config/cninfo_announcement_categories.yaml` | general `positive_patterns` +`受托管理事务报告` +`跟踪评级报告` |
| `lab/validate_cninfo_b_class_category_routing.py` | `_general_document_type`：含「受托管理事务报告」/「跟踪评级报告」早退 → `announcement` |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表增受托管理事务报告 / 跟踪评级报告行 |

不扩 schema；不新造 document_type。

## 3. 晋升内容

| case_id | 状态 | harvest | title_pattern | 窗 |
|---------|------|---------|---------------|-----|
| `bond_trustee_report_known_001` | （新增）→ **ready** | BD2E254 三羊马 001317 · ann=1223979550 · 2025-06-25 | `可转换公司债券受托管理事务报告（2024年度）` · 2025-06-24~27 | 可转债受托管理年度事务报告 |
| `tracking_rating_report_known_001` | （新增）→ **ready** | BD2E408 华海药业 600521 · ann=1224013532 · 2025-06-27 | `跟踪评级报告` · 2025-06-26~29 | 定期跟踪评级报告 |

路由：含「受托管理事务报告」或「跟踪评级报告」→ `announcement` / `cninfo_general_announcement_pdf`（**非** `other`）。

**searchkey 注记：** 短串「受托管理事务报告」同窗命中年度报告 +「第一次临时…（2025年度）」→ ambiguous；pattern 取「可转换公司债券受托管理事务报告（2024年度）」唯一命中。

## 4. 明确不重开

| case_id / 族 | 说明 |
|--------------|------|
| `listing_sponsor_known_001` / `equity_change_report_known_001` | LIVE_PASS（勿重开） |
| `verification_opinion_known_001`–`002` | LIVE_PASS（勿重开） |
| `legal_opinion_known_001`–`004` | LIVE_PASS（勿重开） |
| `supervisory_board_known_001`–`002` | LIVE_PASS（勿重开） |
| `shareholder_meeting_known_001`–`007` | LIVE_PASS（勿重开） |
| `board_resolution_known_001` | 已有 LIVE_PASS（勿重开） |

## 5. Allow-list

仅 `bond_trustee_report_known_001` + `tracking_rating_report_known_001`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。  
ready_for_commit 文件清单不含 console / terminal 日志。

## 6. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_category_routing_bond_trustee_rating_edge.py` | **5 OK** |
| `python lab/test_cninfo_b_class_bond_trustee_rating_known_001_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_bond_trustee_rating_known_001_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_category_routing_listing_sponsor_equity_change_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_verification_opinion_edge.py` | **9 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_legal_opinion_non_meeting_edge.py` | **9 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py` | ready=**42** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=42 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live（复跑） | **LIVE_PASS** · pass=**2**/0/0 |

## 7. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO | **4**（成功复跑：2×(topSearch+query)；PDF=0） |
| wall | **~21.2 s** |
| allow-list | `bond_trustee_report_known_001`, `tracking_rating_report_known_001` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `bond_trustee_report_known_001` | …可转换公司债券受托管理事务报告（2024年度） | 2025-06-25 | classified_correctly / announcement | **pass** |
| `tracking_rating_report_known_001` | …可转换公司债券定期跟踪评级报告 | 2025-06-27 | classified_correctly / announcement | **pass** |

执行要点：

1. 首跑 PARTIAL（trustee 短串 ambiguous）；pattern 修正后复跑 LIVE_PASS；无 orgId fallback。
2. 共享 routing：config patterns + `_general_document_type` 早退（闭合 other）。
3. predicted_type=`announcement`；与 `other`、保荐书、权益变动、核查意见、法律意见书可区分。

## 8. 能力增益

- 债券受托管理事务报告 / 跟踪评级报告进入 **known-document ready** 并经公司窗 live metadata 确认
- 闭合 B-FM-28 之后两处新的「落 other」routing 边角（扫描 other 约 54→24，主要剩章程/制度/薪酬等低价值边角）
- ready 计数 40 → **42**

## 9. Gate 摘要

```text
b_class_bond_trustee_rating_known_001_promotion_live_gate = LIVE_PASS
task_id = B-FM-29
cninfo_calls = 4
pdf_downloads = 0
ready_for_commit = true
commit = not_done
push = not_done
```

## 10. 受保护 / 隔离

- 未触碰 A/C/D 线文件（本包修改仅 B 线）
- 未 mutate 既有 LIVE_PASS live 根（listing_sponsor / equity_change / verification_opinion / legal_opinion / supervisory / shareholder）
- 未 PDF / OCR / DB / MinIO / RAG
- 未 commit / push

## 11. 文件清单（ready_for_commit；不含 console 日志）

| 路径 | 角色 |
|------|------|
| `config/cninfo_announcement_categories.yaml` | +受托管理事务报告 / 跟踪评级报告 pattern |
| `lab/validate_cninfo_b_class_category_routing.py` | `_general_document_type` 早退 |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表 |
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +bond_trustee / tracking_rating known_001 |
| `lab/test_cninfo_b_class_category_routing_bond_trustee_rating_edge.py` | routing 锁测 |
| `lab/test_cninfo_b_class_bond_trustee_rating_known_001_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_bond_trustee_rating_known_001_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_*` | ready 刷新（42） |
| `outputs/validation/cninfo_b_class_bond_trustee_rating_known_001_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_bond_trustee_rating_known_001_live_20260715/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_bond_trustee_rating_known_001_promotion_live_20260715.md` | 本报告 |

## 12. 返回包

| 项 | 值 |
|----|-----|
| task | B-FM-29 受托管理事务报告/跟踪评级报告 routing harden + known_001 晋升 + bounded live（BD2E254/408） |
| files | config + routing + plan + fixture + 3 tests + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | routing **5 OK** · promotion **7 OK** · live mock **3 OK** · listing_sponsor/verification/legal 不回退 · ready **42** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | **4**（成功复跑；PDF=0） |
| allow-list | `bond_trustee_report_known_001`, `tracking_rating_report_known_001` |
| wall | live **~21.2 s** |
| ready_for_commit | **true** |

## 13. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选下一边角：可转债法律意见书 known 扩展（BD2E472；路由已通）、或「持续督导年度报告书」误进 periodic 硬化。
3. `periodic_guard_001`（延期披露）仍缺 harvest，不宜硬推。
4. 真·监管问询函原文仍缺 harvest，不宜硬推 `regulatory_known_003`。
5. 剩余 other 多为章程/制度/薪酬方案等低价值边角，可按需抽样而非硬推。
