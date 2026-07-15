# CNINFO B 类 B-FM-45 — 提名人声明 Known-002 / 核查意见 Known-003 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-45  
> **性质：** harvest 晋升（known_002/003）+ allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 B-FM-44 及更早 LIVE_PASS（含 independent_director_annual_report_work_system / continuous_supervision / company_articles / nominee known_001 / VO known_001/002）  
> **不**触碰 A/C/D · **不** commit / push · **不** PDF / OCR / DB / RAG  
> standing_scope 允许 CNINFO live；other backlog ~0；本包不改路由（复用 B-FM-33 / B-FM-27）

## 1. 候选决策

| # | 类型 | 候选 | 决策 |
|---|------|------|------|
| 1 | known_002 promotion | BD2E059 → independent_director_nominee_declaration_known_002 | **执行** — 对称 known_001 伟星/张永炬；治理披露第二案 |
| 2 | known_003 promotion | BD2E524 → verification_opinion_known_003 | **执行** — 募资结项/节余补流第三边角；对称等额置换/限售流通 |
| 3 | alternate | audit_report_known_002（BD2E653 川网传媒年报审计报告） | **拒绝** — 仍含「年报」→ periodic；与 B-FM-43/44 拒绝同陷阱 |
| 4 | alternate | independent_director_meeting_review_known_002 | **推迟** — harvest 无清晰第二案余量 |

**价值判断：** 提名人声明族仅有 known_001 LIVE_PASS，盐田港冯天俊为清晰姓名消歧第二案；核查意见族已有置换/限售两案，结项补流为高价值第三子类型。路由均已硬化，本包纯晋升+bounded live。

## 2. Routing 变更

本包 **不改** `cninfo_announcement_categories.yaml` / `validate_cninfo_b_class_category_routing.py`。  
- 「独立董事提名人声明与承诺」已由 B-FM-33 → `announcement`  
- 「核查意见」已由 B-FM-27 → `announcement`

## 3. 晋升内容

| case_id | 状态 | harvest | title_pattern | 窗 |
|---------|------|---------|---------------|-----|
| `independent_director_nominee_declaration_known_002` | （新增）→ **ready** | BD2E059 盐田港 000088 · ann=1223951151 · 2025-06-20 | `独立董事提名人声明与承诺（冯天俊）` · 2025-06-19~22 | 提名人声明（姓名消歧） |
| `verification_opinion_known_003` | （新增）→ **ready** | BD2E524 通达股份 002560 · ann=1223981802 · 2025-06-25 | `节余募集资金永久补充流动资金的核查意见` · 2025-06-24~27 | 募资结项/节余补流核查 |

路由：既有硬化 → `announcement` / `cninfo_general_announcement_pdf`（**非** `other`）。

## 4. 明确不重开

| case_id / 族 | 说明 |
|--------------|------|
| `independent_director_nominee_declaration_known_001` / `meeting_review_known_001` | LIVE_PASS（B-FM-33；勿重开） |
| `verification_opinion_known_001` / `known_002` | LIVE_PASS（B-FM-27；勿重开） |
| `independent_director_annual_report_work_system_known_001` / `known_002` | LIVE_PASS（B-FM-44；勿重开） |
| `continuous_supervision_annual_known_001` / `known_002` / `company_articles_known_001` / `known_002` | LIVE_PASS（B-FM-30/36/43；勿重开） |
| `audit_report_known_001` | LIVE_PASS（B-FM-34；本包不推 known_002） |
| 其余已 LIVE_PASS known | 勿重开 |

## 5. Allow-list

仅 `independent_director_nominee_declaration_known_002` + `verification_opinion_known_003`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。  
**不含** console 日志。

## 6. 测试与门禁

| 命令 / 门 | 结果 |
|-----------|------|
| `python lab/test_cninfo_b_class_nominee_vo_known_002_003_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_nominee_vo_known_002_003_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_ined_annual_work_system_known_001_002_promotion.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_supervision_articles_known_002_promotion.py` | **7 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | ready=**74** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=74 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

## 7. Live 结果

| 字段 | 值 |
|------|-----|
| result | **LIVE_PASS** |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| wall（成功 live） | **~20.6 s** |
| allow-list | `independent_director_nominee_declaration_known_002`, `verification_opinion_known_003` |

| case_id | matched title | matched date | route | case_result |
|---------|---------------|--------------|-------|-------------|
| `independent_director_nominee_declaration_known_002` | 独立董事提名人声明与承诺（冯天俊） | 2025-06-20 | classified_correctly / announcement | **pass** |
| `verification_opinion_known_003` | 国泰海通证券…节余募集资金永久补充流动资金的核查意见 | 2025-06-25 | classified_correctly / announcement | **pass** |

## 8. Gate 声明

```
b_class_nominee_vo_known_002_003_promotion_live_gate = LIVE_PASS
task_id = B-FM-45
cninfo_calls_success_live = 4
pdf_download = 0
routing_changed = false
verified = false
production_ready = false
```

## 9. 文件清单

| 路径 | 说明 |
|------|------|
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +nominee known_002 / VO known_003 |
| `lab/test_cninfo_b_class_nominee_vo_known_002_003_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_nominee_vo_known_002_003_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_{report,summary}.*` | ready 刷新（74） |
| `outputs/validation/cninfo_b_class_nominee_vo_known_002_003_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_nominee_vo_known_002_003_live_20260715/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_nominee_vo_known_002_003_promotion_live_20260715.md` | 本报告 |

## 10. 返回卡

| 字段 | 值 |
|------|-----|
| task | B-FM-45 提名人声明 known_002 + 核查意见 known_003 晋升 + bounded live（BD2E059/524） |
| files | fixture + 2 tests + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | promotion **7 OK** · live mock **3 OK** · B-FM-44/43 不回退 · ready **74** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | 成功 live **4**；本任务合计 **4**（PDF=0） |
| allow-list | `independent_director_nominee_declaration_known_002`, `verification_opinion_known_003` |
| wall | 成功 live **~20.6 s** |
| ready_for_commit | **true** |

## 11. 下一步（Controller）

1. 可选：commit B-FM-45 包（不含 console 日志；勿 `git add .`）；B-FM-44 若尚未 commit 可一并或分轨。
2. 下一高价值第二案可优先：`independent_director_meeting_review_known_002`（需 harvest）；或 `asset_valuation_explanation_known_002` / `listing_sponsor_known_002`；`audit_report_known_002` 仍需无「年报」子串 harvest。
3. 勿重开已 LIVE_PASS known（含本包两案与 B-FM-44 及更早）。
4. 不 push，除非 human 明确要求。
