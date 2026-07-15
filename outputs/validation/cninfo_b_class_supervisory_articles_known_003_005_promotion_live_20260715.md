# CNINFO B 类 B-FM-50 — 监事会决议 Known-003 / 公司章程工商变更修订 Known-005 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-50  
> **性质：** harvest 晋升（known_003 / known_005）+ allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 B-FM-49 及更早 LIVE_PASS（含 articles known_001–004、supervisory known_001/002、ESOP known_003）

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | known_003 promotion | BD2E702 → supervisory_board_known_003 | **执行** — 届次全锚定监事会决议；闭合 B-FM-49 推迟案 |
| 2 | known_005 promotion | BD2E674 → company_articles_known_005 | **执行** — 工商变更+修订章程边角；与 known_004 修订公告互斥 |
| 3 | alternate | independent_director_meeting_review_known_002 | **推迟** — harvest 仍无清晰第二案 |
| 4 | alternate | asset_valuation_explanation_known_002 / listing_sponsor_known_002 | **推迟** — 仅有 known_001 同源行 |
| 5 | alternate | continuous_supervision_training_known_002 | **推迟** — harvest 仅见 known_001 |
| 6 | alternate | audit_report_known_002（川网传媒年报审计报告） | **拒绝** — 仍含「年报」→ periodic |
| 7 | alternate | BD2E778 海汽集团监事会第三十次 | **推迟** — 价值低于 BD2E702 全锚定第三案（可作 known_004） |

**价值判断：** meeting_review / asset_valuation / listing_sponsor / training 仍无独立第二 harvest；BD2E702 届次监事会与 BD2E674 工商变更修订章程均有现成 pass 证据，路由已硬化，本包纯晋升+bounded live。

## 2. 晋升明细

| case_id | 变更 | harvest | title_pattern / 窗 | 子类型 |
|---------|------|---------|-------------------|--------|
| `supervisory_board_known_003` | （新增）→ **ready** | BD2E702 华新科技 301265 · ann=1223955287 · 2025-06-23 | `第四届监事会第五次会议决议公告` · 2025-06-22~25 | 监事会届次全锚定 |
| `company_articles_known_005` | （新增）→ **ready** | BD2E674 大地海洋 301068 · ann=1223848298 · 2025-06-11 | `修订《公司章程》完成工商变更登记` · 2025-06-10~13 | 章程工商变更修订 |

## 3. 明确不重开

| case / 包 | 状态 |
|-----------|------|
| `supervisory_board_known_001` / `known_002` | LIVE_PASS（B-FM-23/24；勿重开） |
| `company_articles_known_001`–`004` | LIVE_PASS（含 B-FM-49；勿重开） |
| `employee_stock_ownership_plan_known_001`–`003` | LIVE_PASS（含 B-FM-49；勿重开） |
| `board_resolution_known_001` / `known_002` | LIVE_PASS（含 B-FM-48；勿重开） |
| `audit_report_known_001` | LIVE_PASS（B-FM-34；本包不推 known_002） |
| 其余已 LIVE_PASS known | 勿重开 |

## 4. Allow-list

仅 `supervisory_board_known_003` + `company_articles_known_005`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。  
ready_for_commit 文件清单不含 console / terminal 日志。

## 5. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_supervisory_articles_known_003_005_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_supervisory_articles_known_003_005_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_articles_esop_known_003_004_promotion.py` | **7 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | ready=**84** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=84 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

## 6. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计） | **4** |
| wall（成功 live） | **~10.6 s** |
| allow-list | `supervisory_board_known_003`, `company_articles_known_005` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `supervisory_board_known_003` | 第四届监事会第五次会议决议公告 | 2025-06-23 | classified_correctly / announcement | **pass** |
| `company_articles_known_005` | 关于变更公司注册资本、修订《公司章程》完成工商变更登记的公告 | 2025-06-11 | classified_correctly / announcement | **pass** |

执行要点：

1. 首轮两案均 **pass**（无 ambiguous / 无重试）。
2. 无 orgId fallback；无 PDF。
3. 两案 predicted_type 均为 `announcement`（监事会 ≠ board_resolution）。
4. 川网传媒「年报审计报告」与「监事会关于…年度报告的审核意见」仍落 annual_report（锁测覆盖）。
5. known_004 修订公告 pattern 与工商变更修订互斥；known_003 届次全锚定不命中 known_001/002 / 海汽 BD2E778。

## 7. 能力增益

- 监事会决议**届次全锚定**子类型进入 **known-document ready** 并经公司窗 live metadata 确认
- 公司章程**工商变更+修订**子类型进入 ready（第五边角；对称修订公告 known_004）
- ready 计数 82 → **84**；remaining other 仍 ~0

## 8. Gate 摘要

```text
b_class_supervisory_articles_known_003_005_promotion_live_gate = LIVE_PASS
task_id = B-FM-50
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
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +supervisory known_003 / articles known_005 |
| `lab/test_cninfo_b_class_supervisory_articles_known_003_005_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_supervisory_articles_known_003_005_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_report.csv` | ready 刷新 |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_summary.md` | ready 刷新 |
| `outputs/validation/cninfo_b_class_supervisory_articles_known_003_005_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_supervisory_articles_known_003_005_live_20260715/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_supervisory_articles_known_003_005_promotion_live_20260715.md` | 本报告 |

## 10. 返回卡

| 字段 | 值 |
|------|-----|
| task | B-FM-50 监事会决议 known_003 + 公司章程工商变更修订 known_005 晋升 + bounded live（BD2E702/674） |
| files | fixture + 2 tests + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | promotion **7 OK** · live mock **3 OK** · B-FM-49 不回退 · ready **84** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | 成功 live **4**；本任务合计 **4**（PDF=0） |
| allow-list | `supervisory_board_known_003`, `company_articles_known_005` |
| wall | 成功 live **~10.6 s** |
| ready_for_commit | **true** |

## 11. 下一步（Controller）

1. 可选：commit B-FM-50 包（不含 console 日志；勿 `git add .`）；B-FM-49 若尚未 commit 可一并或分轨。
2. 下一高价值第二案仍优先：`independent_director_meeting_review_known_002` / `asset_valuation_explanation_known_002` / `listing_sponsor_known_002` / `continuous_supervision_training_known_002`（均需独立第二 harvest）；或 `supervisory_board_known_004`（BD2E778 海汽集团第三十次）。
3. `audit_report_known_002` 仍需无「年报」子串 harvest。
4. 勿重开已 LIVE_PASS known（含本包两案与 B-FM-49 及更早）。
5. 不 push，除非 human 明确要求。
