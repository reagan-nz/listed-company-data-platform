# CNINFO B 类 B-FM-52 — 董事会决议 Known-004 / Known-005 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-52  
> **性质：** harvest 晋升（board known_004 / known_005）+ allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 B-FM-51 及更早 LIVE_PASS（含 board known_001–003、supervisory known_001–004）

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | known_004 promotion | BD2E658 → board_resolution_known_004 | **执行** — 届次全锚定董事会决议余量（第十四次） |
| 2 | known_005 promotion | BD2E730 → board_resolution_known_005 | **执行** — 另一届次全锚定董事会决议余量（第十三次） |
| 3 | alternate | independent_director_meeting_review_known_002 | **推迟** — harvest 仍无清晰第二案 |
| 4 | alternate | asset_valuation_explanation_known_002 / listing_sponsor_known_002 | **推迟** — 仅有 known_001 同源行 |
| 5 | alternate | continuous_supervision_training_known_002 | **推迟** — harvest 仅见 known_001 |
| 6 | alternate | audit_report_known_002（川网传媒年报审计报告） | **拒绝** — 仍含「年报」→ periodic |

**价值判断：** 高价值第二案 harvest 仍薄；BD2E658/730 均有现成 pass 证据且与 known_002「第四次」子串互斥，路由已硬化，本包纯晋升+bounded live。

## 2. 晋升明细

| case_id | 变更 | harvest | title_pattern / 窗 | 子类型 |
|---------|------|---------|-------------------|--------|
| `board_resolution_known_004` | （新增）→ **ready** | BD2E658 宁波方正 300998 · ann=1224037323 · 2025-06-30 | `第三届董事会第十四次会议决议公告` · 2025-06-29~07-02 | 董事会届次全锚定 |
| `board_resolution_known_005` | （新增）→ **ready** | BD2E730 德福科技 301511 · ann=1224016561 · 2025-06-27 | `第三届董事会第十三次会议决议公告` · 2025-06-26~29 | 董事会届次全锚定 |

## 3. 明确不重开

| case / 包 | 状态 |
|-----------|------|
| `board_resolution_known_001`–`003` | LIVE_PASS（含 B-FM-51；勿重开） |
| `supervisory_board_known_001`–`004` | LIVE_PASS（含 B-FM-51；勿重开） |
| `company_articles_known_001`–`005` | LIVE_PASS（勿重开） |
| `employee_stock_ownership_plan_known_001`–`003` | LIVE_PASS（勿重开） |
| `audit_report_known_001` | LIVE_PASS（本包不推 known_002） |
| 其余已 LIVE_PASS known | 勿重开 |

## 4. Allow-list

仅 `board_resolution_known_004` + `board_resolution_known_005`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。  
ready_for_commit 文件清单不含 console / terminal 日志。

## 5. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_board_resolution_known_004_005_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_board_resolution_known_004_005_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_supervisory_board_known_003_004_promotion.py` | **7 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | ready=**88** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=88 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

## 6. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计） | **4** |
| wall（成功 live） | **~8.5 s** |
| allow-list | `board_resolution_known_004`, `board_resolution_known_005` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `board_resolution_known_004` | 第三届董事会第十四次会议决议公告 | 2025-06-30 | classified_correctly / board_resolution | **pass** |
| `board_resolution_known_005` | 第三届董事会第十三次会议决议公告 | 2025-06-27 | classified_correctly / board_resolution | **pass** |

执行要点：

1. 首轮两案均 **pass**（无 ambiguous / 无重试）。
2. 无 orgId fallback；无 PDF。
3. 两案 predicted_type 均为 `board_resolution`。
4. 川网传媒「年报审计报告」仍落 annual_report（锁测覆盖）。
5. known_004「第十四次」与 known_002「第四次」、known_005「第十三次」子串互斥。

## 7. 能力增益

- 董事会决议**届次全锚定**第四案（宁波方正第十四次）进入 **known-document ready** 并经公司窗 live metadata 确认
- 董事会决议**届次全锚定**第五案（德福科技第十三次）进入 ready
- ready 计数 86 → **88**；remaining other 仍 ~0

## 8. Gate 摘要

```text
b_class_board_resolution_known_004_005_promotion_live_gate = LIVE_PASS
task_id = B-FM-52
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
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +board known_004 / known_005 |
| `lab/test_cninfo_b_class_board_resolution_known_004_005_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_board_resolution_known_004_005_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_board_resolution_known_004_005_live_20260716/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_board_resolution_known_004_005_promotion_dry_run_*_20260716.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_board_resolution_known_004_005_promotion_live_20260716.md` | 本报告 |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_{report,summary}.*` | ready 选择器刷新 |

## 10. 返回摘要

| 项 | 值 |
|----|-----|
| task | B-FM-52 董事会决议 known_004 + known_005 晋升 + bounded live（BD2E658/730） |
| files | fixtures + 2 tests + live/dry-run 产物 + ready 选择器 |
| tests | promotion 7 OK · live mock 3 OK · B-FM-51 regression 7 OK · select ready=88 |
| CNINFO | **4**（live）；PDF=0 |
| allow-list | `board_resolution_known_004`, `board_resolution_known_005` |
| wall | **~8.5 s** |
| ready_for_commit | **true**（不含 console 日志；勿 `git add .`） |
| gate | **LIVE_PASS** |
| live | **done**（bounded；非 production） |
| 受保护文件 | 未改路由 / 未触 A/C/D |
| git status | 本包文件已改/未跟踪；**未 commit** |

## 11. 下一步

1. 可选：commit B-FM-52 包（不含 console 日志；勿 `git add .`）；B-FM-51 若尚未 commit 可一并或分轨。
2. 下一高价值第二案仍优先：`independent_director_meeting_review_known_002` / `asset_valuation_explanation_known_002` / `listing_sponsor_known_002` / `continuous_supervision_training_known_002`（均需独立第二 harvest）；或 short-form/event 路由 harden→promote。
