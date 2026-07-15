# CNINFO B 类 B-FM-49 — 公司章程修订公告 Known-004 / ESOP 调价 Known-003 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-49  
> **性质：** harvest 晋升（known_004 / known_003）+ allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 B-FM-48 及更早 LIVE_PASS（含 articles known_001–003、board known_002、ESOP known_001/002）

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | known_004 promotion | BD2E736 → company_articles_known_004 | **执行** — 修订公告子类型；闭合 B-FM-48 推迟案 |
| 2 | known_003 promotion | BD2E800 → employee_stock_ownership_plan_known_003 | **执行** — 购买价格调整子类型；对称草案/持有人会议 |
| 3 | alternate | independent_director_meeting_review_known_002 | **推迟** — harvest 仍无清晰第二案 |
| 4 | alternate | asset_valuation_explanation_known_002 / listing_sponsor_known_002 | **推迟** — 仅有 known_001 同源行 |
| 5 | alternate | continuous_supervision_training_known_002 | **推迟** — harvest 仅见 known_001 |
| 6 | alternate | audit_report_known_002（川网传媒年报审计报告） | **拒绝** — 仍含「年报」→ periodic |
| 7 | alternate | BD2E674 工商变更+修订章程 | **推迟** — 与修订公告子类型可区分但价值低于纯修订公告 |

**价值判断：** meeting_review / asset_valuation / listing_sponsor / training 仍无独立第二 harvest；BD2E736 修订公告与 BD2E800 ESOP 调价均有现成 pass 证据，路由已硬化，本包纯晋升+bounded live。

## 2. 晋升明细

| case_id | 变更 | harvest | title_pattern / 窗 | 子类型 |
|---------|------|---------|-------------------|--------|
| `company_articles_known_004` | （新增）→ **ready** | BD2E736 美信科技 301577 · ann=1224673306 · 2025-06-19 | `关于修订《公司章程》的公告` · 2025-06-18~21 | 章程修订公告 |
| `employee_stock_ownership_plan_known_003` | （新增）→ **ready** | BD2E800 快克智能 603203 · ann=1223972100 · 2025-06-24 | `员工持股计划购买价格` · 2025-06-23~26 | ESOP 调价 |

## 3. 明确不重开

| case / 包 | 状态 |
|-----------|------|
| `company_articles_known_001` / `known_002` / `known_003` | LIVE_PASS（B-FM-36/43/48；勿重开） |
| `board_resolution_known_001` / `known_002` | LIVE_PASS（含 B-FM-48；勿重开） |
| `employee_stock_ownership_plan_known_001` / `known_002` | LIVE_PASS（B-FM-35/46；勿重开） |
| `audit_report_known_001` | LIVE_PASS（B-FM-34；本包不推 known_002） |
| 其余已 LIVE_PASS known | 勿重开 |

## 4. Allow-list

仅 `company_articles_known_004` + `employee_stock_ownership_plan_known_003`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。  
ready_for_commit 文件清单不含 console / terminal 日志。

## 5. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_articles_esop_known_003_004_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_articles_esop_known_003_004_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_articles_board_known_002_003_promotion.py` | **7 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | ready=**82** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=82 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

## 6. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计） | **4** |
| wall（成功 live） | **~21.9 s** |
| allow-list | `company_articles_known_004`, `employee_stock_ownership_plan_known_003` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `company_articles_known_004` | 关于修订《公司章程》的公告 | 2025-06-19 | classified_correctly / announcement | **pass** |
| `employee_stock_ownership_plan_known_003` | 快克智能关于调整公司2025年员工持股计划购买价格的公告 | 2025-06-24 | classified_correctly / announcement | **pass** |

执行要点：

1. 首轮两案均 **pass**（无 ambiguous / 无重试）。
2. 无 orgId fallback；无 PDF。
3. 两案 predicted_type 均为 `announcement`。
4. 川网传媒「年报审计报告」仍落 annual_report（锁测覆盖）。
5. 修订公告 pattern 与「…修订《公司章程》完成工商变更登记…」不连续互斥；ESOP 调价与草案/持有人会议互斥。

## 7. 能力增益

- 公司章程**修订公告**子类型进入 **known-document ready** 并经公司窗 live metadata 确认
- ESOP **购买价格调整**子类型进入 ready（第三边角）
- ready 计数 80 → **82**；remaining other 仍 ~0

## 8. Gate 摘要

```text
b_class_articles_esop_known_003_004_promotion_live_gate = LIVE_PASS
task_id = B-FM-49
cninfo_calls_success_live = 4
cninfo_calls_task_total = 4
pdf_downloads = 0
ready_for_commit = true
commit = not_done
push = not_done
```

## 9. 受保护 / 隔离

- 未触碰 A/C/D 线文件（本包修改仅 B 线；工作树内其他线脏文件与本任务无关）
- 未改路由配置
- 未 commit / push

## 修改文件

| 路径 | 说明 |
|------|------|
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +articles known_004 / ESOP known_003 |
| `lab/test_cninfo_b_class_articles_esop_known_003_004_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_articles_esop_known_003_004_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_report.csv` | ready 刷新 |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_summary.md` | ready 刷新 |
| `outputs/validation/cninfo_b_class_articles_esop_known_003_004_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_articles_esop_known_003_004_live_20260715/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_articles_esop_known_003_004_promotion_live_20260715.md` | 本报告 |

## 10. 返回卡

| 字段 | 值 |
|------|-----|
| task | B-FM-49 公司章程修订公告 known_004 + ESOP 调价 known_003 晋升 + bounded live（BD2E736/800） |
| files | fixture + 2 tests + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | promotion **7 OK** · live mock **3 OK** · B-FM-48 不回退 · ready **82** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | 成功 live **4**；本任务合计 **4**（PDF=0） |
| allow-list | `company_articles_known_004`, `employee_stock_ownership_plan_known_003` |
| wall | 成功 live **~21.9 s** |
| ready_for_commit | **true** |

## 11. 下一步（Controller）

1. 可选：commit B-FM-49 包（不含 console 日志；勿 `git add .`）；B-FM-48 若尚未 commit 可一并或分轨。
2. 下一高价值第二案仍优先：`independent_director_meeting_review_known_002` / `asset_valuation_explanation_known_002` / `listing_sponsor_known_002` / `continuous_supervision_training_known_002`（均需独立第二 harvest）；或 `supervisory_board_known_003`（BD2E702 届次监事会）/ `company_articles` 工商变更修订边角（BD2E674）。
3. `audit_report_known_002` 仍需无「年报」子串 harvest。
4. 勿重开已 LIVE_PASS known（含本包两案与 B-FM-48 及更早）。
5. 不 push，除非 human 明确要求。
