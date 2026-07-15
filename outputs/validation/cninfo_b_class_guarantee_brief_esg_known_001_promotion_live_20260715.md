# CNINFO B 类 B-FM-40 — 对外担保情况简报 / 英文 ESG Known-001 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-40  
> **性质：** routing harden + harvest 晋升 + allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 continuous_supervision / bond_trustee / tracking_rating / listing_sponsor / equity_change / verification_opinion / legal_opinion_known_001–006 / supervisory_board / shareholder_meeting / nonstandard_audit / raised_funds_usage / independent_director / asset_valuation / audit_report / incentive_trading_self_inspection / employee_stock_ownership_plan / company_articles / raised_funds_management_system / independent_ned_work_system / general_manager_work_rules / monetary_funds_management_system / external_guarantee_management_system / subsidiary_management_system / compensation_assessment_plan known LIVE_PASS  
> **不**触碰 A/C/D · **不** commit / push · **不** PDF / OCR / DB / RAG  
> standing_scope 允许 CNINFO live；本包闭合 B-FM-39 之后最高价值 remaining-other 抽样：对外担保的情况简报（BD2E432）+ 英文 ESG（BD2E166）

## 1. 候选决策

| # | 类型 | 候选 | 决策 |
|---|------|------|------|
| 1 | routing harden + promotion | BD2E432 → external_guarantee_situation_brief_known_001 | **执行** — remaining other 中最高价值担保披露边角；窄 pattern「对外担保的情况简报」 |
| 2 | routing harden + promotion | BD2E166 → esg_report_known_001 | **执行** — 次高价值可持续披露边角；窄检索键「Corporate Governance Report」 |
| 3 | remaining other | 激励名单/销售简报 | **推迟** — 仍低价值；勿裸「简报」/「名单」 |
| 4 | alternate | periodic_guard_001 / regulatory_known_003 | **拒绝** — harvest 仍缺 |

**价值判断：** remaining other ~4 中，对外担保的情况简报（BD2E432）为担保族对称披露边角（≠管理制度）；英文 ESG（BD2E166）为次高价值可持续披露。激励名单/销售简报继续推迟。长逗号英文 searchKey 会被 CNINFO 拒返 0，故 ESG 用「Corporate Governance Report」。

## 2. Routing 变更

| 层 | 变更 |
|----|------|
| `config/cninfo_announcement_categories.yaml` | general positive_patterns +`对外担保的情况简报` / `Corporate Governance Report` |
| `lab/validate_cninfo_b_class_category_routing.py` | `_general_document_type` 早退：含上述两串 → `announcement` |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表增对外担保情况简报 / 英文 ESG 行 |

不扩 schema；不新造 document_type；不扩裸「简报」/「ESG」/「Report」进 unrelated。

## 3. 晋升内容

| case_id | 状态 | harvest | title_pattern | 窗 |
|---------|------|---------|---------------|-----|
| `external_guarantee_situation_brief_known_001` | （新增）→ **ready** | BD2E432 光明地产 600708 · ann=1223951749 · 2025-06-20 | `对外担保的情况简报` · 2025-06-19~22 | 对外担保的情况简报 |
| `esg_report_known_001` | （新增）→ **ready** | BD2E166 圣邦股份 300661 · ann=1224040090 · 2025-06-30 | `Corporate Governance Report` · 2025-06-29~07-02 | 英文 ESG 报告 |

路由：含「对外担保的情况简报」或「Corporate Governance Report」→ `announcement` / `cninfo_general_announcement_pdf`（**非** `other`）。

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
| `monetary_funds_management_system_known_001` / `external_guarantee_management_system_known_001` | LIVE_PASS（B-FM-38；勿重开） |
| `subsidiary_management_system_known_001` / `compensation_assessment_plan_known_001` | LIVE_PASS（B-FM-39；勿重开） |

## 5. Allow-list

仅 `external_guarantee_situation_brief_known_001` + `esg_report_known_001`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。  
ready_for_commit 文件清单不含 console / terminal 日志。

## 6. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_category_routing_guarantee_brief_esg_edge.py` | **5 OK** |
| `python lab/test_cninfo_b_class_guarantee_brief_esg_known_001_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_guarantee_brief_esg_known_001_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_category_routing_subsidiary_compensation_edge.py` | **5 OK**（不回退；仍 other 锚点改名单/销售简报） |
| `python lab/test_cninfo_b_class_category_routing_monetary_external_guarantee_system_edge.py` | **5 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_ined_gm_work_rules_edge.py` | **5 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_articles_raised_funds_system_edge.py` | **5 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_incentive_esop_edge.py` | **5 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py` | ready=**64** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=64 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live（成功轮） | **LIVE_PASS** · pass=**2**/0/0 |

## 7. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计） | **14**（首轮 PARTIAL 4 + 检索键诊断 6 + 成功 live 4） |
| wall（成功 live） | **~16.9 s** |
| allow-list | `external_guarantee_situation_brief_known_001`, `esg_report_known_001` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `external_guarantee_situation_brief_known_001` | 光明地产关于对外担保的情况简报 | 2025-06-20 | classified_correctly / announcement | **pass** |
| `esg_report_known_001` | 2024 Environmental, Social and Corporate Governance Report | 2025-06-30 | classified_correctly / announcement | **pass** |

执行要点：

1. 首轮 ESG 因长逗号英文 searchKey 返 0 → PARTIAL；改「Corporate Governance Report」后两案均 **pass**。
2. 无 orgId fallback；无 PDF。
3. predicted_type=`announcement`；与激励名单/销售简报 other 可区分。
4. 「对外担保管理制度」仍 announcement 且 pattern 可区分；裸「简报」/「ESG」仍 other。

## 8. 能力增益

- 对外担保情况简报 / 英文 ESG 进入 **known-document ready** 并经公司窗 live metadata 确认
- 闭合 B-FM-39 推迟的 remaining-other 最高价值抽样；remaining other 4→**2**（激励名单/销售简报）
- ready 计数 62 → **64**

## 9. Gate 摘要

```text
b_class_guarantee_brief_esg_known_001_promotion_live_gate = LIVE_PASS
task_id = B-FM-40
cninfo_calls_success_live = 4
cninfo_calls_task_total = 14
pdf_downloads = 0
ready_for_commit = true
commit = not_done
push = not_done
```

## 10. 受保护 / 隔离

- 未触碰 A/C/D 线文件（本包修改仅 B 线；工作区另有他线脏文件与本包无关）
- 未 mutate 既有 LIVE_PASS live 根（含 B-FM-39 subsidiary / compensation）
- 未 PDF / OCR / DB / MinIO / RAG
- 未 commit / push

## 11. 文件清单（ready_for_commit；不含 console 日志）

| 路径 | 角色 |
|------|------|
| `config/cninfo_announcement_categories.yaml` | +对外担保的情况简报 / Corporate Governance Report |
| `lab/validate_cninfo_b_class_category_routing.py` | `_general_document_type` 早退 |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表更新 |
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +guarantee brief / esg known_001 |
| `lab/test_cninfo_b_class_category_routing_guarantee_brief_esg_edge.py` | routing 边角锁测 |
| `lab/test_cninfo_b_class_guarantee_brief_esg_known_001_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_guarantee_brief_esg_known_001_live.py` | live allow-list mock |
| `lab/test_cninfo_b_class_category_routing_subsidiary_compensation_edge.py` | 仍 other 锚点改名单/销售简报 |
| `lab/test_cninfo_b_class_category_routing_monetary_external_guarantee_system_edge.py` | 同上 |
| `lab/test_cninfo_b_class_category_routing_ined_gm_work_rules_edge.py` | 同上 |
| `lab/test_cninfo_b_class_category_routing_articles_raised_funds_system_edge.py` | 同上 |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_*` | ready 刷新（64） |
| `outputs/validation/cninfo_b_class_guarantee_brief_esg_known_001_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_guarantee_brief_esg_known_001_live_20260715/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_guarantee_brief_esg_known_001_promotion_live_20260715.md` | 本报告 |

## 12. 返回包

| 项 | 值 |
|----|-----|
| task | B-FM-40 对外担保情况简报/英文 ESG known_001 晋升 + bounded live（BD2E432/166） |
| files | routing harden + fixture + 3 tests + prior edge 锚点调整 + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | routing **5 OK** · promotion **7 OK** · live mock **3 OK** · subsidiary/monetary/ined/articles/incentive 不回退 · ready **64** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | 成功 live **4**；本任务合计 **14**（PDF=0） |
| allow-list | `external_guarantee_situation_brief_known_001`, `esg_report_known_001` |
| wall | 成功 live **~16.9 s** |
| ready_for_commit | **true** |

## 13. 下一步（Controller）

1. 可选：commit B-FM-40 包（不含 console 日志；勿 `git add .`）。
2. 剩余 other ~2 为激励名单/销售简报等低价值边角，可按需抽样或收口。
3. 勿重开已 LIVE_PASS known（含本包两案与 B-FM-39 及更早）。
4. 不 push，除非 human 明确要求。
