# CNINFO B 类 B-FM-48 — 公司章程 Known-003 / 董事会决议 Known-002 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-48  
> **性质：** harvest 晋升（known_003 / known_002）+ allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 B-FM-47 及更早 LIVE_PASS（含 supervision/trustee known_003、articles known_001/002、board known_001）  
> **不**触碰 A/C/D · **不** commit / push · **不** PDF / OCR / DB / RAG  
> standing_scope 允许 CNINFO live；other backlog ~0；本包继续高价值族第三/第二案子类型覆盖

## 1. 候选决策

| # | 类型 | 候选 | 决策 |
|---|------|------|------|
| 1 | known_003 promotion | BD2E189 → company_articles_known_003 | **执行** — 短标题无修订日期；闭合 B-FM-36 章程×3 末案 |
| 2 | known_002 promotion | BD2E648 → board_resolution_known_002 | **执行** — 届次/次数决议子类型；对称 known_001 宽串 |
| 3 | alternate | independent_director_meeting_review_known_002 | **推迟** — harvest 仍无清晰第二案 |
| 4 | alternate | asset_valuation_explanation_known_002 / listing_sponsor_known_002 | **推迟** — 仅有 known_001 同源行 |
| 5 | alternate | continuous_supervision_training_known_002 | **推迟** — harvest 仅见 known_001 一条培训案 |
| 6 | alternate | audit_report_known_002（川网传媒年报审计报告） | **拒绝** — 仍含「年报」→ periodic |
| 7 | alternate | BD2E736 关于修订《公司章程》的公告 | **推迟** — 已含「公告」；本包优先短标题章程正文 + 董事会届次 |

**价值判断：** meeting_review / asset_valuation / listing_sponsor / training 仍无独立第二 harvest；通程控股短标题章程与屹通新材届次董事会决议均有现成 pass 证据，路由已硬化，本包纯晋升+bounded live。

## 2. Routing 变更

本包 **不改** `cninfo_announcement_categories.yaml` / routing 脚本。  
公司章程 / 董事会决议分别已由 B-FM-36 / 既有董事会规则硬化。

## 3. 晋升内容

| case_id | 状态 | harvest | title_pattern | 窗 | 子类型 |
|---------|------|---------|---------------|-----|--------|
| `company_articles_known_003` | （新增）→ **ready** | BD2E189 通程控股 000419 · ann=1223954488 · 2025-06-20 | `【通程控股】公司章程` · 2025-06-19~22 | 短标题公司章程 |
| `board_resolution_known_002` | （新增）→ **ready** | BD2E648 屹通新材 300930 · ann=1223953622 · 2025-06-20 | `第三届董事会第四次会议决议公告` · 2025-06-19~22 | 届次董事会决议 |

## 4. 明确不重开

| case_id / 族 | 说明 |
|--------------|------|
| `company_articles_known_001` / `known_002` | LIVE_PASS（B-FM-36/43；勿重开） |
| `board_resolution_known_001` | LIVE_PASS（早包；勿重开） |
| `continuous_supervision_annual_known_001`–`003` / `bond_trustee_report_known_001`–`003` | LIVE_PASS（含 B-FM-47；勿重开） |
| `tracking_rating_report_known_001`–`003` / `employee_stock_ownership_plan_known_001`–`002` | LIVE_PASS（含 B-FM-46；勿重开） |
| `audit_report_known_001` | LIVE_PASS（B-FM-34；本包不推 known_002） |
| 其余已 LIVE_PASS known | 勿重开 |

## 5. Allow-list

仅 `company_articles_known_003` + `board_resolution_known_002`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。  
ready_for_commit 文件清单不含 console / terminal 日志。

## 6. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_articles_board_known_002_003_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_articles_board_known_002_003_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_supervision_trustee_known_003_promotion.py` | **7 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | ready=**80** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=80 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

## 7. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计） | **4** |
| wall（成功 live） | **~23.6 s** |
| allow-list | `company_articles_known_003`, `board_resolution_known_002` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `company_articles_known_003` | 【通程控股】公司章程 | 2025-06-20 | classified_correctly / announcement | **pass** |
| `board_resolution_known_002` | 第三届董事会第四次会议决议公告 | 2025-06-20 | classified_correctly / board_resolution | **pass** |

执行要点：

1. 首轮两案均 **pass**（无 ambiguous / 无重试）。
2. 无 orgId fallback；无 PDF。
3. 章程 predicted_type=`announcement`；董事会 predicted_type=`board_resolution`。
4. 川网传媒「年报审计报告」仍落 annual_report（锁测覆盖）。
5. 届次标题「第三届董事会第四次会议决议公告」与宽串「董事会决议公告」不连续互斥。

## 8. 能力增益

- 短标题/方括号前缀公司章程进入 **known-document ready** 并经公司窗 live metadata 确认
- 届次董事会决议子类型进入 ready（第二边角）
- ready 计数 78 → **80**；remaining other 仍 ~0

## 9. Gate 摘要

```text
b_class_articles_board_known_002_003_promotion_live_gate = LIVE_PASS
task_id = B-FM-48
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
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +articles known_003 / board known_002 |
| `lab/test_cninfo_b_class_articles_board_known_002_003_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_articles_board_known_002_003_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_report.csv` | ready 刷新 |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_summary.md` | ready 刷新 |
| `outputs/validation/cninfo_b_class_articles_board_known_002_003_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_articles_board_known_002_003_live_20260715/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_articles_board_known_002_003_promotion_live_20260715.md` | 本报告 |

## 11. 返回卡

| 字段 | 值 |
|------|-----|
| task | B-FM-48 公司章程 known_003 + 董事会决议 known_002 晋升 + bounded live（BD2E189/648） |
| files | fixture + 2 tests + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | promotion **7 OK** · live mock **3 OK** · B-FM-47 不回退 · ready **80** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | 成功 live **4**；本任务合计 **4**（PDF=0） |
| allow-list | `company_articles_known_003`, `board_resolution_known_002` |
| wall | 成功 live **~23.6 s** |
| ready_for_commit | **true** |

## 12. 下一步（Controller）

1. 可选：commit B-FM-48 包（不含 console 日志；勿 `git add .`）；B-FM-47 若尚未 commit 可一并或分轨。
2. 下一高价值第二案仍优先：`independent_director_meeting_review_known_002` / `asset_valuation_explanation_known_002` / `listing_sponsor_known_002` / `continuous_supervision_training_known_002`（均需独立第二 harvest）；或 `company_articles` 修订公告子类型（BD2E736）。
3. `audit_report_known_002` 仍需无「年报」子串 harvest。
4. 勿重开已 LIVE_PASS known（含本包两案与 B-FM-47 及更早）。
5. 不 push，除非 human 明确要求。
