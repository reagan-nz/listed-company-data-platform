# CNINFO B 类 B-FM-34 — 资产评估说明 / 独立审计报告 Known-001 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-34  
> **性质：** routing harden + harvest 晋升 + allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 continuous_supervision / bond_trustee / tracking_rating / listing_sponsor / equity_change / verification_opinion / legal_opinion_known_001–006 / supervisory_board / shareholder_meeting / nonstandard_audit / raised_funds / independent_director known LIVE_PASS  
> **不**触碰 A/C/D · **不** commit / push · **不** PDF / OCR / DB / RAG  
> standing_scope 允许 CNINFO live；本包闭合 B-FM-33 之后最高价值 remaining-other：资产评估说明（BD2E430）+ 独立审计报告（BD2E798）

## 1. 候选决策

| # | 类型 | 候选 | 决策 |
|---|------|------|------|
| 1 | routing harden + promotion | BD2E430 → asset_valuation_explanation_known_001 | **执行** — B-FM-33 明确可选下一边角；窄 pattern「资产评估说明」 |
| 2 | routing harden + promotion | BD2E798 → audit_report_known_001 | **执行** — 同包中介文书第二边角；无「年度报告」/「年报」子串，旧逻辑落 other |
| 3 | remaining other | 章程/制度/薪酬/激励名单/简报/自查报告等 | **推迟** — 低价值边角，不硬推 routing |
| 4 | alternate | BD2E087 激励对象买卖自查报告 | **推迟** — 价值低于评估说明/独立审计报告 |
| 5 | alternate | periodic_guard_001 / regulatory_known_003 | **拒绝** — harvest 仍缺 |

**价值判断：** remaining other ~19 中，BD2E430（资产评估说明）为 B-FM-33 已标出的最高价值可选边角；BD2E798（独立审计报告，无年报字样）为清晰可窄 pattern 的对称中介文书。裸「说明」会泛化过宽；含「年度报告」/「年报」的审计报告仍由 periodic Priority 3 先命中，故 general 仅承接独立审计报告。

## 2. Routing 变更

| 层 | 变更 |
|----|------|
| `config/cninfo_announcement_categories.yaml` | general positive_patterns +`资产评估说明` / `审计报告` |
| `lab/validate_cninfo_b_class_category_routing.py` | `_general_document_type` 早退：含上述两串 → `announcement` |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表增资产评估说明 / 独立审计报告行 |

不扩 schema；不新造 document_type；不扩裸「说明」进 unrelated。

## 3. 晋升内容

| case_id | 状态 | harvest | title_pattern | 窗 |
|---------|------|---------|---------------|-----|
| `asset_valuation_explanation_known_001` | （新增）→ **ready** | BD2E430 舍得酒业 600702 · ann=1223999581 · 2025-06-26 | `资产评估说明` · 2025-06-25~28 | 资产评估说明 |
| `audit_report_known_001` | （新增）→ **ready** | BD2E798 迎驾贡酒 603198 · ann=1223955004 · 2025-06-22 | `迎驾贡酒2024年审计报告` · 2025-06-21~24 | 独立审计报告（公司消歧） |

路由：含「资产评估说明」或（periodic 未先命中时）「审计报告」→ `announcement` / `cninfo_general_announcement_pdf`（**非** `other` / `annual_report`）。

## 4. 明确不重开

| case_id / 族 | 说明 |
|--------------|------|
| `legal_opinion_known_001`–`006` | LIVE_PASS（勿重开） |
| `continuous_supervision_annual_known_001` / `training_known_001` | LIVE_PASS（勿重开） |
| `bond_trustee_report_known_001` / `tracking_rating_report_known_001` | LIVE_PASS（勿重开） |
| `listing_sponsor_known_001` / `equity_change_report_known_001` | LIVE_PASS（勿重开） |
| `verification_opinion_known_001`–`002` | LIVE_PASS（勿重开） |
| `supervisory_board_known_001`–`002` | LIVE_PASS（勿重开） |
| `shareholder_meeting_known_001`–`007` | LIVE_PASS（勿重开） |
| `board_resolution_known_001` | LIVE_PASS（勿重开） |
| `nonstandard_audit_opinion_known_001` / `raised_funds_usage_report_known_001` | LIVE_PASS（B-FM-32；勿重开） |
| `independent_director_meeting_review_known_001` / `nominee_declaration_known_001` | LIVE_PASS（B-FM-33；勿重开） |

## 5. Allow-list

仅 `asset_valuation_explanation_known_001` + `audit_report_known_001`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。  
ready_for_commit 文件清单不含 console / terminal 日志。

## 6. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_category_routing_asset_valuation_audit_edge.py` | **7 OK** |
| `python lab/test_cninfo_b_class_asset_valuation_audit_known_001_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_asset_valuation_audit_known_001_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_category_routing_ind_director_governance_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_nonstandard_audit_raised_funds_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_continuous_supervision_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_legal_opinion_non_meeting_edge.py` | **10 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_bond_trustee_rating_edge.py` | **5 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py` | ready=**52** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=52 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

## 7. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计） | **4**（无重试） |
| wall（成功 live） | **~43.3 s** |
| allow-list | `asset_valuation_explanation_known_001`, `audit_report_known_001` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `asset_valuation_explanation_known_001` | 舍得酒业拟进行资产收购所涉及的位于遂宁市射洪县沱牌镇四处住宅用、商业用房地产市场价值资产评估说明 | 2025-06-26 | classified_correctly / announcement | **pass** |
| `audit_report_known_001` | 迎驾贡酒2024年审计报告-容诚审字[2025]230Z0521号（修订版） | 2025-06-22 | classified_correctly / announcement | **pass** |

执行要点：

1. 首轮即 **LIVE_PASS**（无 ambiguous / 无消歧重试）。
2. 无 orgId fallback；无 PDF。
3. predicted_type=`announcement`；与章程/制度/薪酬 other、真·年报审计报告（periodic）可区分。
4. 裸「说明」仍落 other（锁测覆盖）。

## 8. 能力增益

- 资产评估说明 / 独立审计报告进入 **known-document ready** 并经公司窗 live metadata 确认
- 闭合 B-FM-33 推迟的 BD2E430 边角；remaining other 19→**17**（章程/制度/薪酬/名单/简报/自查报告等低价值边角）
- ready 计数 50 → **52**

## 9. Gate 摘要

```text
b_class_asset_valuation_audit_known_001_promotion_live_gate = LIVE_PASS
task_id = B-FM-34
cninfo_calls_success_live = 4
cninfo_calls_task_total = 4
pdf_downloads = 0
ready_for_commit = true
commit = not_done
push = not_done
```

## 10. 受保护 / 隔离

- 未触碰 A/C/D 线文件（本包修改仅 B 线；工作区另有他线脏文件与本包无关）
- 未 mutate 既有 LIVE_PASS live 根（含 B-FM-33 independent_director / B-FM-32 nonstandard_audit）
- 未 PDF / OCR / DB / MinIO / RAG
- 未 commit / push

## 11. 文件清单（ready_for_commit；不含 console 日志）

| 路径 | 角色 |
|------|------|
| `config/cninfo_announcement_categories.yaml` | +资产评估说明 / 审计报告 |
| `lab/validate_cninfo_b_class_category_routing.py` | `_general_document_type` 早退 |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表更新 |
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +asset_valuation / audit_report known_001 |
| `lab/test_cninfo_b_class_category_routing_asset_valuation_audit_edge.py` | routing 边角锁测 |
| `lab/test_cninfo_b_class_asset_valuation_audit_known_001_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_asset_valuation_audit_known_001_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_*` | ready 刷新（52） |
| `outputs/validation/cninfo_b_class_asset_valuation_audit_known_001_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_asset_valuation_audit_known_001_live_20260715/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_asset_valuation_audit_known_001_promotion_live_20260715.md` | 本报告 |

## 12. 返回包

| 项 | 值 |
|----|-----|
| task | B-FM-34 资产评估说明/独立审计报告 known_001 晋升 + bounded live（BD2E430/798） |
| files | routing harden + fixture + 3 tests + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | routing **7 OK** · promotion **7 OK** · live mock **3 OK** · ind_director/nonstandard/continuous/legal/bond 不回退 · ready **52** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | 成功 live **4**；本任务合计 **4**（PDF=0） |
| allow-list | `asset_valuation_explanation_known_001`, `audit_report_known_001` |
| wall | 成功 live **~43.3 s** |
| ready_for_commit | **true** |

## 13. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 剩余 other ~17 多为章程/制度/薪酬方案/激励名单/简报/自查报告等低价值边角，可按需抽样而非硬推。
3. 可选：BD2E087「激励对象买卖…自查报告」若要硬化，需窄 pattern（避免泛化「自查报告」）。
4. `periodic_guard_001`（延期披露）仍缺 harvest，不宜硬推。
5. 真·监管问询函原文仍缺 harvest，不宜硬推 `regulatory_known_003`。
