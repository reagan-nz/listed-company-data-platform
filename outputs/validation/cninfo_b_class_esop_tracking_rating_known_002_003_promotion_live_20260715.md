# CNINFO B 类 B-FM-46 — 员工持股计划 Known-002 / 跟踪评级 Known-003 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-46  
> **性质：** harvest 晋升（known_002/003）+ allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 B-FM-45 及更早 LIVE_PASS（含 nominee/VO / 独立董事年报工作制度 / continuous_supervision / company_articles / ESOP known_001 / tracking known_001/002）  
> **不**触碰 A/C/D · **不** commit / push · **不** PDF / OCR / DB / RAG  
> standing_scope 允许 CNINFO live；other backlog ~0；本包继续高价值族第二/第三案覆盖

## 1. 候选决策

| # | 类型 | 候选 | 决策 |
|---|------|------|------|
| 1 | known_002 promotion | BD2E672 → employee_stock_ownership_plan_known_002 | **执行** — ESOP 族仅 known_001；持有人会议决议子类型 |
| 2 | known_003 promotion | BD2E051 → tracking_rating_report_known_003 | **执行** — 普通公司债定期跟踪；对称可转债定期 / 主体年度 |
| 3 | alternate | independent_director_meeting_review_known_002 | **推迟** — harvest 仍无清晰第二案 |
| 4 | alternate | asset_valuation_explanation_known_002 / listing_sponsor_known_002 | **推迟** — harvest 仍无第二案余量 |
| 5 | alternate | audit_report_known_002（BD2E653 川网传媒年报审计报告） | **拒绝** — 仍含「年报」→ periodic；与 B-FM-43/44/45 同陷阱 |
| 6 | alternate | continuous_supervision_annual_known_003 / company_articles_known_003 | **推迟** — 族已有 known_002；本包优先仅 known_001 的 ESOP + 评级第三子类型 |

**价值判断：** meeting_review / asset_valuation / listing_sponsor 仍无 harvest 第二案；ESOP 持有人会议为未覆盖子类型；跟踪评级 known_003 补齐普通公司债定期边角。路由均已硬化，本包纯晋升+bounded live。

## 2. Routing 变更

本包 **不改** `cninfo_announcement_categories.yaml` / routing 脚本。  
员工持股计划 / 跟踪评级报告分别已由 B-FM-35 / B-FM-29 硬化为 announcement → general。

## 3. 晋升内容

| case_id | 状态 | harvest | title_pattern | 窗 | 子类型 |
|---------|------|---------|---------------|-----|--------|
| `employee_stock_ownership_plan_known_002` | （新增）→ **ready** | BD2E672 海锅股份 301063 · ann=1223951294 · 2025-06-20 | `员工持股计划第一次持有人会议决议` · 2025-06-19~22 | 持有人会议决议 |
| `tracking_rating_report_known_003` | （新增）→ **ready** | BD2E051 中国宝安 000009 · ann=1223886549 · 2025-06-16 | `公开发行公司债券(第一期)定期跟踪评级报告` · 2025-06-15~18 | 普通公司债定期跟踪 |

## 4. 明确不重开

| case_id / 族 | 说明 |
|--------------|------|
| `employee_stock_ownership_plan_known_001` / `incentive_trading_self_inspection_known_001` | LIVE_PASS（B-FM-35；勿重开） |
| `tracking_rating_report_known_001` / `known_002` | LIVE_PASS（B-FM-29 / B-FM-42；勿重开） |
| `independent_director_nominee_declaration_known_001` / `known_002` / `verification_opinion_known_001`–`003` | LIVE_PASS（B-FM-33/27/45；勿重开） |
| `independent_director_annual_report_work_system_known_001` / `known_002` | LIVE_PASS（B-FM-44；勿重开） |
| `continuous_supervision_annual_known_001` / `known_002` / `company_articles_known_001` / `known_002` | LIVE_PASS（B-FM-30/36/43；勿重开） |
| `audit_report_known_001` | LIVE_PASS（B-FM-34；本包不推 known_002） |
| 其余已 LIVE_PASS known | 勿重开 |

## 5. Allow-list

仅 `employee_stock_ownership_plan_known_002` + `tracking_rating_report_known_003`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。  
ready_for_commit 文件清单不含 console / terminal 日志。

## 6. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_esop_tracking_rating_known_002_003_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_esop_tracking_rating_known_002_003_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_nominee_vo_known_002_003_promotion.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_incentive_esop_known_001_promotion.py` | **7 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | ready=**76** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=76 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

## 7. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计） | **4** |
| wall（成功 live） | **~18.2 s** |
| allow-list | `employee_stock_ownership_plan_known_002`, `tracking_rating_report_known_003` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `employee_stock_ownership_plan_known_002` | 2025年员工持股计划第一次持有人会议决议公告 | 2025-06-20 | classified_correctly / announcement | **pass** |
| `tracking_rating_report_known_003` | 中国宝安…公开发行公司债券(第一期)定期跟踪评级报告 | 2025-06-16 | classified_correctly / announcement | **pass** |

执行要点：

1. 首轮两案均 **pass**（无 ambiguous / 无重试）。
2. 无 orgId fallback；无 PDF。
3. predicted_type=`announcement`；与草案 ESOP / 可转债定期 / 主体年度跟踪评级可区分。
4. 川网传媒「年报审计报告」仍落 annual_report（锁测覆盖）。

## 8. 能力增益

- 员工持股计划持有人会议决议进入 **known-document ready** 并经公司窗 live metadata 确认
- 跟踪评级普通公司债定期子类型进入 ready（第三边角）
- ready 计数 74 → **76**；remaining other 仍 ~0

## 9. Gate 摘要

```text
b_class_esop_tracking_rating_known_002_003_promotion_live_gate = LIVE_PASS
task_id = B-FM-46
cninfo_calls_success_live = 4
cninfo_calls_task_total = 4
pdf_downloads = 0
ready_for_commit = true
commit = not_done
push = not_done
```

## 10. 受保护 / 隔离

- 未触碰 A/C/D 线文件（本包修改仅 B 线）
- 未改路由配置
- 未 commit / push

## 修改文件

| 路径 | 说明 |
|------|------|
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +ESOP known_002 / tracking known_003 |
| `lab/test_cninfo_b_class_esop_tracking_rating_known_002_003_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_esop_tracking_rating_known_002_003_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_report.csv` | ready 刷新 |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_summary.md` | ready 刷新 |
| `outputs/validation/cninfo_b_class_esop_tracking_rating_known_002_003_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_esop_tracking_rating_known_002_003_live_20260715/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_esop_tracking_rating_known_002_003_promotion_live_20260715.md` | 本报告 |

## 11. 返回卡

| 字段 | 值 |
|------|-----|
| task | B-FM-46 员工持股计划 known_002 + 跟踪评级 known_003 晋升 + bounded live（BD2E672/051） |
| files | fixture + 2 tests + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | promotion **7 OK** · live mock **3 OK** · B-FM-45/35 不回退 · ready **76** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | 成功 live **4**；本任务合计 **4**（PDF=0） |
| allow-list | `employee_stock_ownership_plan_known_002`, `tracking_rating_report_known_003` |
| wall | 成功 live **~18.2 s** |
| ready_for_commit | **true** |

## 12. 下一步（Controller）

1. 可选：commit B-FM-46 包（不含 console 日志；勿 `git add .`）；B-FM-45 若尚未 commit 可一并或分轨。
2. 下一高价值第二案仍优先：`independent_director_meeting_review_known_002` / `asset_valuation_explanation_known_002` / `listing_sponsor_known_002`（均需 harvest）；或 `continuous_supervision_annual_known_003` / `bond_trustee_report_known_003`（harvest 已有余量）。
3. `audit_report_known_002` 仍需无「年报」子串 harvest。
4. 勿重开已 LIVE_PASS known（含本包两案与 B-FM-45 及更早）。
5. 不 push，除非 human 明确要求。
