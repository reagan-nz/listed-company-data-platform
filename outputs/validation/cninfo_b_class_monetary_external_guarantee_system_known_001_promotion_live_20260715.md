# CNINFO B 类 B-FM-38 — 货币资金管理制度 / 对外担保管理制度 Known-001 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-38  
> **性质：** routing harden + harvest 晋升 + allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 continuous_supervision / bond_trustee / tracking_rating / listing_sponsor / equity_change / verification_opinion / legal_opinion_known_001–006 / supervisory_board / shareholder_meeting / nonstandard_audit / raised_funds_usage / independent_director / asset_valuation / audit_report / incentive_trading_self_inspection / employee_stock_ownership_plan / company_articles / raised_funds_management_system / independent_ned_work_system / general_manager_work_rules known LIVE_PASS  
> **不**触碰 A/C/D · **不** commit / push · **不** PDF / OCR / DB / RAG  
> standing_scope 允许 CNINFO live；本包闭合 B-FM-37 之后最高价值 remaining-other 抽样：货币资金管理制度（BD2E586）+ 对外担保管理制度（BD2E790）

## 1. 候选决策

| # | 类型 | 候选 | 决策 |
|---|------|------|------|
| 1 | routing harden + promotion | BD2E586 → monetary_funds_management_system_known_001 | **执行** — remaining other 中最高价值内控制度边角；窄 pattern「货币资金管理制度」 |
| 2 | routing harden + promotion | BD2E790 → external_guarantee_management_system_known_001 | **执行** — 对称担保内控制度边角；与「对外担保的情况简报」可区分 |
| 3 | remaining other | 分子公司管理制度/薪酬/激励名单/简报/ESG | **推迟** — 仍低价值；勿裸「管理制度」 |
| 4 | alternate | periodic_guard_001 / regulatory_known_003 | **拒绝** — harvest 仍缺 |

**价值判断：** remaining other ~8 中，货币资金管理制度（BD2E586）与对外担保管理制度（BD2E790）为最清晰可窄 pattern 的内控制度对（对称 B-FM-36 募集资金管理制度）；分子公司管理制度、薪酬/名单/简报/ESG 继续推迟。裸「管理制度」会泛化过宽；「对外担保的情况简报」不含「管理制度」子串，不误抬。

## 2. Routing 变更

| 层 | 变更 |
|----|------|
| `config/cninfo_announcement_categories.yaml` | general positive_patterns +`货币资金管理制度` / `对外担保管理制度` |
| `lab/validate_cninfo_b_class_category_routing.py` | `_general_document_type` 早退：含上述两串 → `announcement` |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表增货币资金管理制度 / 对外担保管理制度行 |

不扩 schema；不新造 document_type；不扩裸「管理制度」/「制度」进 unrelated。

## 3. 晋升内容

| case_id | 状态 | harvest | title_pattern | 窗 |
|---------|------|---------|---------------|-----|
| `monetary_funds_management_system_known_001` | （新增）→ **ready** | BD2E586 恒实科技 300513 · ann=1223719020 · 2025-05-29 | `货币资金管理制度` · 2025-05-28~31 | 货币资金管理制度 |
| `external_guarantee_management_system_known_001` | （新增）→ **ready** | BD2E790 海量数据 603138 · ann=1223999873 · 2025-06-26 | `对外担保管理制度` · 2025-06-25~28 | 对外担保管理制度 |

路由：含「货币资金管理制度」或「对外担保管理制度」→ `announcement` / `cninfo_general_announcement_pdf`（**非** `other`）。

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
| `incentive_trading_self_inspection_known_001` / `employee_stock_ownership_plan_known_001` | LIVE_PASS（B-FM-35；勿重开） |
| `company_articles_known_001` / `raised_funds_management_system_known_001` | LIVE_PASS（B-FM-36；勿重开） |
| `independent_ned_work_system_known_001` / `general_manager_work_rules_known_001` | LIVE_PASS（B-FM-37；勿重开） |

## 5. Allow-list

仅 `monetary_funds_management_system_known_001` + `external_guarantee_management_system_known_001`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。  
ready_for_commit 文件清单不含 console / terminal 日志。

## 6. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_category_routing_monetary_external_guarantee_system_edge.py` | **5 OK** |
| `python lab/test_cninfo_b_class_monetary_external_guarantee_system_known_001_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_monetary_external_guarantee_system_known_001_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_category_routing_ined_gm_work_rules_edge.py` | **5 OK**（不回退；仍 other 锚点改分子公司） |
| `python lab/test_cninfo_b_class_category_routing_articles_raised_funds_system_edge.py` | **5 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_incentive_esop_edge.py` | **5 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_asset_valuation_audit_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_ind_director_governance_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_nonstandard_audit_raised_funds_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_continuous_supervision_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_legal_opinion_non_meeting_edge.py` | **10 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_bond_trustee_rating_edge.py` | **5 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py` | ready=**60** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=60 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

## 7. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计） | **4** |
| wall（成功 live） | **~17.2 s** |
| allow-list | `monetary_funds_management_system_known_001`, `external_guarantee_management_system_known_001` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `monetary_funds_management_system_known_001` | 货币资金管理制度 | 2025-05-29 | classified_correctly / announcement | **pass** |
| `external_guarantee_management_system_known_001` | 海量数据对外担保管理制度 | 2025-06-26 | classified_correctly / announcement | **pass** |

执行要点：

1. 首轮两案均 **pass**（无 ambiguous / 无重试）。
2. 无 orgId fallback；无 PDF。
3. predicted_type=`announcement`；与分子公司/薪酬/名单/简报/ESG other 可区分。
4. 裸「管理制度」/「分、子公司管理制度」/「对外担保的情况简报」仍落 other（锁测覆盖）。

## 8. 能力增益

- 货币资金管理制度 / 对外担保管理制度进入 **known-document ready** 并经公司窗 live metadata 确认
- 闭合 B-FM-37 推迟的一般管理制度最高价值抽样；remaining other 8→**6**（分子公司/薪酬/名单/简报/ESG）
- ready 计数 58 → **60**

## 9. Gate 摘要

```text
b_class_monetary_external_guarantee_system_known_001_promotion_live_gate = LIVE_PASS
task_id = B-FM-38
cninfo_calls_success_live = 4
cninfo_calls_task_total = 4
pdf_downloads = 0
ready_for_commit = true
commit = not_done
push = not_done
```

## 10. 受保护 / 隔离

- 未触碰 A/C/D 线文件（本包修改仅 B 线；工作区另有他线脏文件与本包无关）
- 未 mutate 既有 LIVE_PASS live 根（含 B-FM-37 ined / gm_work_rules）
- 未 PDF / OCR / DB / MinIO / RAG
- 未 commit / push

## 11. 文件清单（ready_for_commit；不含 console 日志）

| 路径 | 角色 |
|------|------|
| `config/cninfo_announcement_categories.yaml` | +货币资金管理制度 / 对外担保管理制度 |
| `lab/validate_cninfo_b_class_category_routing.py` | `_general_document_type` 早退 |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表更新 |
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +monetary / external_guarantee known_001 |
| `lab/test_cninfo_b_class_category_routing_monetary_external_guarantee_system_edge.py` | routing 边角锁测 |
| `lab/test_cninfo_b_class_monetary_external_guarantee_system_known_001_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_monetary_external_guarantee_system_known_001_live.py` | live allow-list mock |
| `lab/test_cninfo_b_class_category_routing_ined_gm_work_rules_edge.py` | 仍 other 锚点改分子公司 |
| `lab/test_cninfo_b_class_category_routing_articles_raised_funds_system_edge.py` | 同上 |
| `lab/test_cninfo_b_class_category_routing_incentive_esop_edge.py` | 同上 |
| `lab/test_cninfo_b_class_category_routing_ind_director_governance_edge.py` | 同上 |
| `lab/test_cninfo_b_class_category_routing_asset_valuation_audit_edge.py` | 同上 |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_*` | ready 刷新（60） |
| `outputs/validation/cninfo_b_class_monetary_external_guarantee_system_known_001_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_monetary_external_guarantee_system_known_001_live_20260715/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_monetary_external_guarantee_system_known_001_promotion_live_20260715.md` | 本报告 |

## 12. 返回包

| 项 | 值 |
|----|-----|
| task | B-FM-38 货币资金管理制度/对外担保管理制度 known_001 晋升 + bounded live（BD2E586/790） |
| files | routing harden + fixture + 3 tests + prior edge 锚点调整 + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | routing **5 OK** · promotion **7 OK** · live mock **3 OK** · ined/articles/incentive/asset/ind/nonstandard/continuous/legal/bond 不回退 · ready **60** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | 成功 live **4**；本任务合计 **4**（PDF=0） |
| allow-list | `monetary_funds_management_system_known_001`, `external_guarantee_management_system_known_001` |
| wall | 成功 live **~17.2 s** |
| ready_for_commit | **true** |

## 13. 下一步（Controller）

1. 可选：commit B-FM-38 包（不含 console 日志；勿 `git add .`）。
2. 剩余 other ~6 多为分子公司管理制度/薪酬方案/激励名单/简报/ESG 等低价值边角，可按需抽样而非硬推。
3. 勿重开已 LIVE_PASS known（含本包两案与 B-FM-37 及更早）。
4. 不 push，除非 human 明确要求。
