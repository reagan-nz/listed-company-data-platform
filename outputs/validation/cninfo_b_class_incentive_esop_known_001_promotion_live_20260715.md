# CNINFO B 类 B-FM-35 — 激励买卖自查报告 / 员工持股计划 Known-001 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-35  
> **性质：** routing harden + harvest 晋升 + allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 continuous_supervision / bond_trustee / tracking_rating / listing_sponsor / equity_change / verification_opinion / legal_opinion_known_001–006 / supervisory_board / shareholder_meeting / nonstandard_audit / raised_funds / independent_director / asset_valuation / audit_report known LIVE_PASS  
> **不**触碰 A/C/D · **不** commit / push · **不** PDF / OCR / DB / RAG  
> standing_scope 允许 CNINFO live；本包闭合 B-FM-34 之后最高价值 remaining-other：激励对象买卖自查报告（BD2E087）+ 员工持股计划草案（BD2E062）

## 1. 候选决策

| # | 类型 | 候选 | 决策 |
|---|------|------|------|
| 1 | routing harden + promotion | BD2E087 → incentive_trading_self_inspection_known_001 | **执行** — B-FM-34 明确可选下一边角；窄 pattern「买卖公司股票的自查报告」 |
| 2 | routing harden + promotion | BD2E062 → employee_stock_ownership_plan_known_001 | **执行** — 同包治理披露第二边角；路由用「员工持股计划」，live title_pattern 消歧至全文 |
| 3 | remaining other | 章程/制度/薪酬/激励名单/简报/工作细则/ESG 等 | **推迟** — 低价值边角，不硬推 routing |
| 4 | alternate | periodic_guard_001 / regulatory_known_003 | **拒绝** — harvest 仍缺 |

**价值判断：** remaining other ~16 中，BD2E087（激励对象买卖公司股票的自查报告）为 B-FM-34 已标出的最高价值可选边角；BD2E062（员工持股计划草案）为清晰可窄 pattern 的对称治理披露。裸「自查报告」会泛化过宽；章程/制度/薪酬/名单/简报继续推迟。

## 2. Routing 变更

| 层 | 变更 |
|----|------|
| `config/cninfo_announcement_categories.yaml` | general positive_patterns +`买卖公司股票的自查报告` / `员工持股计划` |
| `lab/validate_cninfo_b_class_category_routing.py` | `_general_document_type` 早退：含上述两串 → `announcement` |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表增自查报告 / 员工持股计划行 |

不扩 schema；不新造 document_type；不扩裸「自查报告」进 unrelated。

## 3. 晋升内容

| case_id | 状态 | harvest | title_pattern | 窗 |
|---------|------|---------|---------------|-----|
| `incentive_trading_self_inspection_known_001` | （新增）→ **ready** | BD2E087 北新建材 000786 · ann=1224017800 · 2025-06-27 | `买卖公司股票的自查报告` · 2025-06-26~29 | 激励买卖自查报告 |
| `employee_stock_ownership_plan_known_001` | （新增）→ **ready** | BD2E062 东方盛虹 000301 · ann=1224016542 · 2025-06-27 | `第二期员工持股计划（草案）(修订稿）` · 2025-06-26~29 | ESOP 草案（全文消歧） |

路由：含「买卖公司股票的自查报告」或「员工持股计划」→ `announcement` / `cninfo_general_announcement_pdf`（**非** `other`）。

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
| `asset_valuation_explanation_known_001` / `audit_report_known_001` | LIVE_PASS（B-FM-34；勿重开） |

## 5. Allow-list

仅 `incentive_trading_self_inspection_known_001` + `employee_stock_ownership_plan_known_001`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。  
ready_for_commit 文件清单不含 console / terminal 日志。

## 6. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_category_routing_incentive_esop_edge.py` | **5 OK** |
| `python lab/test_cninfo_b_class_incentive_esop_known_001_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_incentive_esop_known_001_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_category_routing_asset_valuation_audit_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_ind_director_governance_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_nonstandard_audit_raised_funds_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_continuous_supervision_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_legal_opinion_non_meeting_edge.py` | **10 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_bond_trustee_rating_edge.py` | **5 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py` | ready=**54** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=54 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

## 7. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计） | **12**（2 次 ESOP 消歧重试） |
| wall（成功 live） | **~27.4 s** |
| allow-list | `incentive_trading_self_inspection_known_001`, `employee_stock_ownership_plan_known_001` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `incentive_trading_self_inspection_known_001` | 关于2024年限制性股票激励计划内幕信息知情人及激励对象买卖公司股票的自查报告 | 2025-06-27 | classified_correctly / announcement | **pass** |
| `employee_stock_ownership_plan_known_001` | 第二期员工持股计划（草案）(修订稿） | 2025-06-27 | classified_correctly / announcement | **pass** |

执行要点：

1. 首轮自查案 **pass**；ESOP 案因窗内多条「员工持股计划」**ambiguous**（5→2）。
2. 收窄 live title_pattern 至「第二期员工持股计划（草案）(修订稿）」后 **LIVE_PASS**。
3. 无 orgId fallback；无 PDF。
4. predicted_type=`announcement`；与章程/制度/薪酬/名单/简报 other 可区分。
5. 裸「自查报告」仍落 other（锁测覆盖）。

## 8. 能力增益

- 激励买卖自查报告 / 员工持股计划进入 **known-document ready** 并经公司窗 live metadata 确认
- 闭合 B-FM-34 推迟的 BD2E087 边角；remaining other 16→**14**（章程/制度/薪酬/名单/简报/工作细则/ESG 等低价值边角）
- ready 计数 52 → **54**

## 9. Gate 摘要

```text
b_class_incentive_esop_known_001_promotion_live_gate = LIVE_PASS
task_id = B-FM-35
cninfo_calls_success_live = 4
cninfo_calls_task_total = 12
pdf_downloads = 0
ready_for_commit = true
commit = not_done
push = not_done
```

## 10. 受保护 / 隔离

- 未触碰 A/C/D 线文件（本包修改仅 B 线；工作区另有他线脏文件与本包无关）
- 未 mutate 既有 LIVE_PASS live 根（含 B-FM-34 asset_valuation / audit_report）
- 未 PDF / OCR / DB / MinIO / RAG
- 未 commit / push

## 11. 文件清单（ready_for_commit；不含 console 日志）

| 路径 | 角色 |
|------|------|
| `config/cninfo_announcement_categories.yaml` | +买卖公司股票的自查报告 / 员工持股计划 |
| `lab/validate_cninfo_b_class_category_routing.py` | `_general_document_type` 早退 |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表更新 |
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +self_inspection / esop known_001 |
| `lab/test_cninfo_b_class_category_routing_incentive_esop_edge.py` | routing 边角锁测 |
| `lab/test_cninfo_b_class_incentive_esop_known_001_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_incentive_esop_known_001_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_*` | ready 刷新（54） |
| `outputs/validation/cninfo_b_class_incentive_esop_known_001_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_incentive_esop_known_001_live_20260715/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_incentive_esop_known_001_promotion_live_20260715.md` | 本报告 |

## 12. 返回包

| 项 | 值 |
|----|-----|
| task | B-FM-35 激励买卖自查报告/员工持股计划 known_001 晋升 + bounded live（BD2E087/062） |
| files | routing harden + fixture + 3 tests + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | routing **5 OK** · promotion **7 OK** · live mock **3 OK** · asset_valuation/ind_director/nonstandard/continuous/legal/bond 不回退 · ready **54** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | 成功 live **4**；本任务合计 **12**（PDF=0） |
| allow-list | `incentive_trading_self_inspection_known_001`, `employee_stock_ownership_plan_known_001` |
| wall | 成功 live **~27.4 s** |
| ready_for_commit | **true** |

## 13. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 剩余 other ~14 多为章程/制度/薪酬方案/激励名单/简报/工作细则/ESG 等低价值边角，可按需抽样而非硬推。
3. `periodic_guard_001`（延期披露）仍缺 harvest，不宜硬推。
4. 真·监管问询函原文仍缺 harvest，不宜硬推 `regulatory_known_003`。
