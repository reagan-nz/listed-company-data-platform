# CNINFO B 类 B-FM-44 — 独立董事年报工作制度 Known-001/002 路由硬化 + 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-44  
> **性质：** routing harden（periodic 误抬）+ harvest 晋升 + allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 B-FM-43 及更早 LIVE_PASS（含 continuous_supervision / company_articles known_002、independent_ned、audit_report known_001）  
> **不**触碰 A/C/D · **不** commit / push · **不** PDF / OCR / DB / RAG  
> standing_scope 允许 CNINFO live；other backlog ~0；本包闭合「独立董事年报/年度报告工作制度」periodic 陷阱（非 audit_report_known_002 年报审计报告陷阱）

## 1. 候选决策

| # | 类型 | 候选 | 决策 |
|---|------|------|------|
| 1 | routing harden + promotion | BD2E028 → independent_director_annual_report_work_system_known_001 | **执行** — 标题含「年度报告」误进 periodic |
| 2 | routing harden + promotion | BD2E695 → independent_director_annual_report_work_system_known_002 | **执行** — 对称「年报」简称变体 |
| 3 | alternate | audit_report_known_002（BD2E653 川网传媒年报审计报告） | **拒绝** — 仍含「年报」→ periodic；与 B-FM-43 拒绝同陷阱 |
| 4 | alternate | esg_report_known_002 / sales_brief_known_002 | **推迟** — harvest 无第二案余量 |
| 5 | alternate | continuous_supervision_annual_known_003 | **推迟** — 族已有 known_002 LIVE_PASS；本包优先未覆盖治理制度边角 |

**价值判断：** 「独立董事年度报告工作制度」/「独立董事年报工作制度」为治理制度文本，非子串年报全文；旧逻辑因「年度报告」/「年报」误进 `annual_report`。对称硬化后可得 known_001+002，且与独立非执行董事工作制度 / 真·年报可区分。

## 2. Routing 变更

| 层 | 变更 |
|----|------|
| `config/cninfo_announcement_categories.yaml` | general positive_patterns +`独立董事年度报告工作制度` / `独立董事年报工作制度` |
| `lab/validate_cninfo_b_class_category_routing.py` | `_periodic_document_type` 早退（勿抬 annual_report）；`_general_document_type` 早退 → `announcement` |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表增独立董事年报/年度报告工作制度行 |

不扩 schema；不新造 document_type；不扩裸「工作制度」/「年报」进 unrelated。

## 3. 晋升内容

| case_id | 状态 | harvest | title_pattern | 窗 |
|---------|------|---------|---------------|-----|
| `independent_director_annual_report_work_system_known_001` | （新增）→ **ready** | BD2E028 宇通客车 600066 · ann=1223314160 · 2025-04-25 | `独立董事年度报告工作制度` · 2025-04-24~27 | 独立董事年度报告工作制度 |
| `independent_director_annual_report_work_system_known_002` | （新增）→ **ready** | BD2E695 喜悦智行 301198 · ann=1223763870 · 2025-06-04 | `独立董事年报工作制度` · 2025-06-03~06 | 独立董事年报工作制度 |

路由：含上述窄串 → `announcement` / `cninfo_general_announcement_pdf`（**非** `annual_report` / `other`）。

## 4. 明确不重开

| case_id / 族 | 说明 |
|--------------|------|
| `continuous_supervision_annual_known_001` / `known_002` / `training_known_001` | LIVE_PASS（B-FM-30 / B-FM-43；勿重开） |
| `company_articles_known_001` / `known_002` | LIVE_PASS（B-FM-36 / B-FM-43；勿重开） |
| `independent_ned_work_system_known_001` / `general_manager_work_rules_known_001` | LIVE_PASS（B-FM-37；勿重开） |
| `independent_director_meeting_review_known_001` / `nominee_declaration_known_001` | LIVE_PASS（B-FM-33；勿重开） |
| `bond_trustee_report_known_002` / `tracking_rating_report_known_002` | LIVE_PASS（B-FM-42；勿重开） |
| `audit_report_known_001` | LIVE_PASS（B-FM-34；勿重开；本包不推 known_002） |
| 其余已 LIVE_PASS known | 勿重开 |

## 5. Allow-list

仅 `independent_director_annual_report_work_system_known_001` + `independent_director_annual_report_work_system_known_002`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。  
**不含** console 日志。

## 6. 测试与门禁

| 命令 / 门 | 结果 |
|-----------|------|
| `python lab/test_cninfo_b_class_category_routing_ined_annual_work_system_edge.py` | **6 OK** |
| `python lab/test_cninfo_b_class_ined_annual_work_system_known_001_002_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_ined_annual_work_system_known_001_002_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_category_routing_continuous_supervision_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_ined_gm_work_rules_edge.py` | **5 OK**（不回退） |
| `python lab/test_cninfo_b_class_supervision_articles_known_002_promotion.py` | **7 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | ready=**72** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=72 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

## 7. Live 结果

| 字段 | 值 |
|------|-----|
| result | **LIVE_PASS** |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| wall（成功 live） | **~25.1 s** |
| allow-list | `independent_director_annual_report_work_system_known_001`, `independent_director_annual_report_work_system_known_002` |

| case_id | matched title | matched date | route | case_result |
|---------|---------------|--------------|-------|-------------|
| `independent_director_annual_report_work_system_known_001` | 独立董事年度报告工作制度 | 2025-04-25 | classified_correctly / announcement | **pass** |
| `independent_director_annual_report_work_system_known_002` | 独立董事年报工作制度 | 2025-06-04 | classified_correctly / announcement | **pass** |

## 8. Gate 声明

```
b_class_ined_annual_work_system_known_001_002_promotion_live_gate = LIVE_PASS
task_id = B-FM-44
cninfo_calls_success_live = 4
pdf_download = 0
routing_changed = true
verified = false
production_ready = false
```

## 9. 文件清单

| 路径 | 说明 |
|------|------|
| `config/cninfo_announcement_categories.yaml` | +独立董事年报/年度报告工作制度 patterns |
| `lab/validate_cninfo_b_class_category_routing.py` | periodic 早退 + general announcement 早退 |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表增行 |
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +known_001 / known_002 |
| `lab/test_cninfo_b_class_category_routing_ined_annual_work_system_edge.py` | routing 边角锁测 |
| `lab/test_cninfo_b_class_ined_annual_work_system_known_001_002_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_ined_annual_work_system_known_001_002_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_{report,summary}.*` | ready 刷新（72） |
| `outputs/validation/cninfo_b_class_ined_annual_work_system_known_001_002_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_ined_annual_work_system_known_001_002_live_20260715/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_ined_annual_work_system_known_001_002_promotion_live_20260715.md` | 本报告 |

## 10. 返回卡

| 字段 | 值 |
|------|-----|
| task | B-FM-44 独立董事年报工作制度 known_001/002 路由硬化 + 晋升 + bounded live（BD2E028/695） |
| files | routing + fixture + 3 tests + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | edge **6 OK** · promotion **7 OK** · live mock **3 OK** · 督导/NED/B-FM-43 不回退 · ready **72** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | 成功 live **4**；本任务合计 **4**（PDF=0） |
| allow-list | `independent_director_annual_report_work_system_known_001`, `independent_director_annual_report_work_system_known_002` |
| wall | 成功 live **~25.1 s** |
| ready_for_commit | **true** |

## 11. 下一步（Controller）

1. 可选：commit B-FM-44 包（不含 console 日志；勿 `git add .`）。
2. 下一高价值第二案可优先：`independent_director_nominee_declaration_known_002`（BD2E059）；或 `verification_opinion_known_003`；`audit_report_known_002` 仍需无「年报」子串 harvest。
3. 勿重开已 LIVE_PASS known（含本包两案与 B-FM-43 及更早）。
4. 不 push，除非 human 明确要求。
