# CNINFO B 类 B-FM-47 — 持续督导年度 Known-003 / 债券受托 Known-003 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-47  
> **性质：** harvest 晋升（known_003）+ allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 B-FM-46 及更早 LIVE_PASS（含 ESOP/tracking / nominee/VO / continuous_supervision known_001/002 / bond_trustee known_001/002 / company_articles）  
> **不**触碰 A/C/D · **不** commit / push · **不** PDF / OCR / DB / RAG  
> standing_scope 允许 CNINFO live；other backlog ~0；本包继续高价值族第三案子类型覆盖

## 1. 候选决策

| # | 类型 | 候选 | 决策 |
|---|------|------|------|
| 1 | known_003 promotion | BD2E779 → continuous_supervision_annual_known_003 | **执行** — 可转债持续督导年度子类型 |
| 2 | known_003 promotion | BD2E061 → bond_trustee_report_known_003 | **执行** — 普通公司债分期受托；对称可转债 / 整包公司债 |
| 3 | alternate | independent_director_meeting_review_known_002 | **推迟** — harvest 仍无清晰第二案 |
| 4 | alternate | asset_valuation_explanation_known_002 / listing_sponsor_known_002 | **推迟** — 仅有 known_001 同源行（BD2E430/252 已占用） |
| 5 | alternate | audit_report_known_002（川网传媒年报审计报告） | **拒绝** — 仍含「年报」→ periodic |
| 6 | alternate | company_articles_known_003 | **推迟** — 本包优先督导/受托第三子类型 |

**价值判断：** meeting_review / asset_valuation / listing_sponsor 仍无独立第二 harvest；持续督导可转债子类型与受托分期子类型均有现成 pass 证据，路由已硬化，本包纯晋升+bounded live。

## 2. Routing 变更

本包 **不改** `cninfo_announcement_categories.yaml` / routing 脚本。  
持续督导 / 债券受托分别已由 B-FM-30 / B-FM-29 硬化为 announcement → general。

## 3. 晋升内容

| case_id | 状态 | harvest | title_pattern | 窗 | 子类型 |
|---------|------|---------|---------------|-----|--------|
| `continuous_supervision_annual_known_003` | （新增）→ **ready** | BD2E779 和邦生物 603077 · ann=1223365250 · 2025-04-28 | `可转换公司债券之2024年持续督导年度报告书` · 2025-04-27~30 | 可转债持续督导年度 |
| `bond_trustee_report_known_003` | （新增）→ **ready** | BD2E061 中联重科 000157 · ann=1224036909 · 2025-06-30 | `公开发行公司债券（第一期）受托管理事务报告（2024年度）` · 2025-06-29~07-02 | 普通公司债分期受托 |

## 4. 明确不重开

| case_id / 族 | 说明 |
|--------------|------|
| `continuous_supervision_annual_known_001` / `known_002` / `training_known_001` | LIVE_PASS（B-FM-30/43；勿重开） |
| `bond_trustee_report_known_001` / `known_002` | LIVE_PASS（B-FM-29/42；勿重开） |
| `tracking_rating_report_known_001`–`003` / `employee_stock_ownership_plan_known_001`–`002` | LIVE_PASS（含 B-FM-46；勿重开） |
| `company_articles_known_001` / `known_002` | LIVE_PASS（B-FM-36/43；勿重开） |
| `audit_report_known_001` | LIVE_PASS（B-FM-34；本包不推 known_002） |
| 其余已 LIVE_PASS known | 勿重开 |

## 5. Allow-list

仅 `continuous_supervision_annual_known_003` + `bond_trustee_report_known_003`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。  
ready_for_commit 文件清单不含 console / terminal 日志。

## 6. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_supervision_trustee_known_003_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_supervision_trustee_known_003_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_esop_tracking_rating_known_002_003_promotion.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_supervision_articles_known_002_promotion.py` | **7 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | ready=**78** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=78 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

## 7. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计） | **4** |
| wall（成功 live） | **~24.6 s** |
| allow-list | `continuous_supervision_annual_known_003`, `bond_trustee_report_known_003` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `continuous_supervision_annual_known_003` | 首创证券关于和邦生物…可转换公司债券之2024年持续督导年度报告书 | 2025-04-28 | classified_correctly / announcement | **pass** |
| `bond_trustee_report_known_003` | 中联重科…公开发行公司债券（第一期）受托管理事务报告（2024年度） | 2025-06-30 | classified_correctly / announcement | **pass** |

执行要点：

1. 首轮两案均 **pass**（无 ambiguous / 无重试）。
2. 无 orgId fallback；无 PDF。
3. predicted_type=`announcement`；可转债持续督导未误进 annual_report；分期受托与可转债/整包受托可区分。
4. 川网传媒「年报审计报告」仍落 annual_report（锁测覆盖）。

## 8. 能力增益

- 可转债持续督导年度进入 **known-document ready** 并经公司窗 live metadata 确认
- 普通公司债分期受托子类型进入 ready（第三边角）
- ready 计数 76 → **78**；remaining other 仍 ~0

## 9. Gate 摘要

```text
b_class_supervision_trustee_known_003_promotion_live_gate = LIVE_PASS
task_id = B-FM-47
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
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +supervision known_003 / bond_trustee known_003 |
| `lab/test_cninfo_b_class_supervision_trustee_known_003_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_supervision_trustee_known_003_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_report.csv` | ready 刷新 |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_summary.md` | ready 刷新 |
| `outputs/validation/cninfo_b_class_supervision_trustee_known_003_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_supervision_trustee_known_003_live_20260715/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_supervision_trustee_known_003_promotion_live_20260715.md` | 本报告 |

## 11. 返回卡

| 字段 | 值 |
|------|-----|
| task | B-FM-47 持续督导年度 known_003 + 债券受托 known_003 晋升 + bounded live（BD2E779/061） |
| files | fixture + 2 tests + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | promotion **7 OK** · live mock **3 OK** · B-FM-46/43 不回退 · ready **78** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | 成功 live **4**；本任务合计 **4**（PDF=0） |
| allow-list | `continuous_supervision_annual_known_003`, `bond_trustee_report_known_003` |
| wall | 成功 live **~24.6 s** |
| ready_for_commit | **true** |

## 12. 下一步（Controller）

1. 可选：commit B-FM-47 包（不含 console 日志；勿 `git add .`）；B-FM-46 若尚未 commit 可一并或分轨。
2. 下一高价值第二案仍优先：`independent_director_meeting_review_known_002` / `asset_valuation_explanation_known_002` / `listing_sponsor_known_002`（均需独立第二 harvest）；或 `company_articles_known_003` / `continuous_supervision_training_known_002`。
3. `audit_report_known_002` 仍需无「年报」子串 harvest。
4. 勿重开已 LIVE_PASS known（含本包两案与 B-FM-46 及更早）。
5. 不 push，除非 human 明确要求。
