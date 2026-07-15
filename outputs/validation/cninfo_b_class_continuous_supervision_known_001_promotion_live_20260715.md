# CNINFO B 类 B-FM-30 — 「持续督导」Routing Harden + Known-001 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-30  
> **性质：** routing harden + harvest 晋升 + allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 bond_trustee_report / tracking_rating_report / listing_sponsor / equity_change / verification_opinion / legal_opinion_known_001–004 / supervisory_board / shareholder_meeting known LIVE_PASS  
> **不**触碰 A/C/D · **不** commit / push · **不** PDF / OCR / DB / RAG  
> standing_scope 允许 CNINFO live；本包闭合 B-FM-29 之后最高价值边角：持续督导年度报告书误进 periodic + 培训情况报告落 `other`

## 1. 候选决策

| # | 类型 | 候选 | 决策 |
|---|------|------|------|
| 1 | routing harden | 「持续督导年度报告书」误进 `annual_report`（harvest ~6+） | **执行** — 最高价值：periodic FP |
| 2 | harvest promotion | BD2E131 → continuous_supervision_annual_known_001 | **执行** — 主路径 |
| 3 | routing harden + promotion | BD2E248 → continuous_supervision_training_known_001（培训情况报告） | **执行** — 同包剩余 other 中最高价值中介文书 |
| 4 | harvest promotion | BD2E472 → legal_opinion_known_005（可转债法律意见书） | **拒绝** — 路由已通；低于持续督导 periodic FP |
| 5 | alternate | periodic_guard_001 / regulatory_known_003 | **拒绝** — harvest 仍缺 |
| 6 | remaining other | 章程/制度/薪酬/激励等 | **推迟** — 低价值边角，可按需抽样 |

**价值判断：** B-FM-29 已闭合受托管理事务报告 / 跟踪评级报告落 `other`。剩余 other ~24 中仅「持续督导培训情况的报告」为清晰中介文书；同时「持续督导年度报告书」因含「年度报告」子串误进 periodic（污染年报检索）。双缺口硬化 + known live 高于再 live 已通路由的可转债法律意见书。

## 2. Routing 变更

| 层 | 变更 |
|----|------|
| `config/cninfo_announcement_categories.yaml` | general `positive_patterns` +`持续督导` |
| `lab/validate_cninfo_b_class_category_routing.py` | `_periodic_document_type`：含「持续督导年度报告」早退 `None`；`_general_document_type`：含「持续督导」早退 → `announcement` |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表增持续督导行 |

不扩 schema；不新造 document_type。

## 3. 晋升内容

| case_id | 状态 | harvest | title_pattern | 窗 |
|---------|------|---------|---------------|-----|
| `continuous_supervision_annual_known_001` | （新增）→ **ready** | BD2E131 恒立液压 601100 · ann=1223493907 · 2025-05-08 | `持续督导年度报告书` · 2025-05-07~10 | 保荐机构持续督导年度报告书 |
| `continuous_supervision_training_known_001` | （新增）→ **ready** | BD2E248 三联锻造 001282 · ann=1223955243 · 2025-06-23 | `持续督导培训情况的报告` · 2025-06-22~25 | 持续督导培训情况报告 |

路由：含「持续督导」→ `announcement` / `cninfo_general_announcement_pdf`（**非** `annual_report` / `other`）。

## 4. 明确不重开

| case_id / 族 | 说明 |
|--------------|------|
| `bond_trustee_report_known_001` / `tracking_rating_report_known_001` | LIVE_PASS（勿重开） |
| `listing_sponsor_known_001` / `equity_change_report_known_001` | LIVE_PASS（勿重开） |
| `verification_opinion_known_001`–`002` | LIVE_PASS（勿重开） |
| `legal_opinion_known_001`–`004` | LIVE_PASS（勿重开） |
| `supervisory_board_known_001`–`002` | LIVE_PASS（勿重开） |
| `shareholder_meeting_known_001`–`007` | LIVE_PASS（勿重开） |
| `board_resolution_known_001` | 已有 LIVE_PASS（勿重开） |

## 5. Allow-list

仅 `continuous_supervision_annual_known_001` + `continuous_supervision_training_known_001`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。  
ready_for_commit 文件清单不含 console / terminal 日志。

## 6. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_category_routing_continuous_supervision_edge.py` | **7 OK** |
| `python lab/test_cninfo_b_class_continuous_supervision_known_001_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_continuous_supervision_known_001_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_category_routing_bond_trustee_rating_edge.py` | **5 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_listing_sponsor_equity_change_edge.py` | **7 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py` | ready=**44** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=44 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

## 7. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO | **4**（2×(topSearch+query)；PDF=0） |
| wall | **~24.4 s** |
| allow-list | `continuous_supervision_annual_known_001`, `continuous_supervision_training_known_001` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `continuous_supervision_annual_known_001` | …2024年度持续督导年度报告书 | 2025-05-08 | classified_correctly / announcement | **pass** |
| `continuous_supervision_training_known_001` | …2025年度持续督导培训情况的报告 | 2025-06-23 | classified_correctly / announcement | **pass** |

执行要点：

1. 首跑 LIVE_PASS；无 orgId fallback；无 pattern 复跑。
2. 共享 routing：`_periodic_document_type` 对「持续督导年度报告」早退 + config pattern「持续督导」+ `_general_document_type` 早退。
3. predicted_type=`announcement`；与真·年度报告、other、受托管理、跟踪评级可区分。

## 8. 能力增益

- 持续督导年度报告书 / 培训情况报告进入 **known-document ready** 并经公司窗 live metadata 确认
- 闭合 B-FM-29 之后最高价值边角：periodic 误抬 + remaining other 中介文书（扫描 other 约 24→23，主要剩章程/制度/薪酬等低价值边角）
- ready 计数 42 → **44**

## 9. Gate 摘要

```text
b_class_continuous_supervision_known_001_promotion_live_gate = LIVE_PASS
task_id = B-FM-30
cninfo_calls = 4
pdf_downloads = 0
ready_for_commit = true
commit = not_done
push = not_done
```

## 10. 受保护 / 隔离

- 未触碰 A/C/D 线文件（本包修改仅 B 线）
- 未 mutate 既有 LIVE_PASS live 根（bond_trustee / tracking_rating / listing_sponsor / equity_change / verification / legal / supervisory / shareholder）
- 未 PDF / OCR / DB / MinIO / RAG
- 未 commit / push

## 11. 文件清单（ready_for_commit；不含 console 日志）

| 路径 | 角色 |
|------|------|
| `config/cninfo_announcement_categories.yaml` | +持续督导 pattern |
| `lab/validate_cninfo_b_class_category_routing.py` | periodic / general 早退 |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表 |
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +continuous_supervision annual / training known_001 |
| `lab/test_cninfo_b_class_category_routing_continuous_supervision_edge.py` | routing 锁测 |
| `lab/test_cninfo_b_class_continuous_supervision_known_001_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_continuous_supervision_known_001_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_*` | ready 刷新（44） |
| `outputs/validation/cninfo_b_class_continuous_supervision_known_001_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_continuous_supervision_known_001_live_20260715/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_continuous_supervision_known_001_promotion_live_20260715.md` | 本报告 |

## 12. 返回包

| 项 | 值 |
|----|-----|
| task | B-FM-30 持续督导年度报告书/培训情况报告 routing harden + known_001 晋升 + bounded live（BD2E131/248） |
| files | config + routing + plan + fixture + 3 tests + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | routing **7 OK** · promotion **7 OK** · live mock **3 OK** · bond_trustee/listing_sponsor 不回退 · ready **44** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | **4**（PDF=0） |
| allow-list | `continuous_supervision_annual_known_001`, `continuous_supervision_training_known_001` |
| wall | live **~24.4 s** |
| ready_for_commit | **true** |

## 13. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选下一边角：可转债法律意见书 known 扩展（BD2E472；路由已通）。
3. `periodic_guard_001`（延期披露）仍缺 harvest，不宜硬推。
4. 真·监管问询函原文仍缺 harvest，不宜硬推 `regulatory_known_003`。
5. 剩余 other 多为章程/制度/薪酬方案等低价值边角，可按需抽样而非硬推。
