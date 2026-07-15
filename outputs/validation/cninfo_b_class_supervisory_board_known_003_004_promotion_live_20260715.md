# CNINFO B 类 B-FM-51 — 监事会决议 Known-004 / 董事会决议 Known-003 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-51  
> **性质：** harvest 晋升（known_004 / known_003）+ allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 B-FM-50 及更早 LIVE_PASS（含 supervisory known_001–003、articles known_005、board known_001/002）

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | known_004 promotion | BD2E778 → supervisory_board_known_004 | **执行** — 届次全锚定监事会决议；闭合 B-FM-50 推迟案 |
| 2 | known_003 promotion | BD2E668 → board_resolution_known_003 | **执行** — 另一届次全锚定董事会决议；对称 board known_002 |
| 3 | alternate | independent_director_meeting_review_known_002 | **推迟** — harvest 仍无清晰第二案 |
| 4 | alternate | asset_valuation_explanation_known_002 / listing_sponsor_known_002 | **推迟** — 仅有 known_001 同源行 |
| 5 | alternate | continuous_supervision_training_known_002 | **推迟** — harvest 仅见 known_001 |
| 6 | alternate | audit_report_known_002（川网传媒年报审计报告） | **拒绝** — 仍含「年报」→ periodic |

**价值判断：** meeting_review / asset_valuation / listing_sponsor / training 仍无独立第二 harvest；BD2E778 与 BD2E668 均有现成 pass 证据，路由已硬化，本包纯晋升+bounded live。

## 2. 晋升明细

| case_id | 变更 | harvest | title_pattern / 窗 | 子类型 |
|---------|------|---------|-------------------|--------|
| `supervisory_board_known_004` | （新增）→ **ready** | BD2E778 海汽集团 603069 · ann=1224016686 · 2025-06-27 | `第四届监事会第三十次会议决议公告` · 2025-06-26~29 | 监事会届次全锚定 |
| `board_resolution_known_003` | （新增）→ **ready** | BD2E668 华蓝集团 301027 · ann=1224036271 · 2025-06-30 | `第五届董事会第五次会议决议公告` · 2025-06-29~07-02 | 董事会届次全锚定 |

## 3. 明确不重开

| case / 包 | 状态 |
|-----------|------|
| `supervisory_board_known_001`–`003` | LIVE_PASS（含 B-FM-50；勿重开） |
| `board_resolution_known_001` / `known_002` | LIVE_PASS（含 B-FM-48；勿重开） |
| `company_articles_known_001`–`005` | LIVE_PASS（含 B-FM-50；勿重开） |
| `employee_stock_ownership_plan_known_001`–`003` | LIVE_PASS（含 B-FM-49；勿重开） |
| `audit_report_known_001` | LIVE_PASS（B-FM-34；本包不推 known_002） |
| 其余已 LIVE_PASS known | 勿重开 |

## 4. Allow-list

仅 `supervisory_board_known_004` + `board_resolution_known_003`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。  
ready_for_commit 文件清单不含 console / terminal 日志。

## 5. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_supervisory_board_known_003_004_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_supervisory_board_known_003_004_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_supervisory_articles_known_003_005_promotion.py` | **7 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | ready=**86** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=86 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

## 6. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计） | **4** |
| wall（成功 live） | **~9.4 s** |
| allow-list | `supervisory_board_known_004`, `board_resolution_known_003` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `supervisory_board_known_004` | 海汽集团第四届监事会第三十次会议决议公告 | 2025-06-27 | classified_correctly / announcement | **pass** |
| `board_resolution_known_003` | 第五届董事会第五次会议决议公告 | 2025-06-30 | classified_correctly / board_resolution | **pass** |

执行要点：

1. 首轮两案均 **pass**（无 ambiguous / 无重试）。
2. 无 orgId fallback；无 PDF。
3. 监事会案 predicted_type=`announcement`；董事会案 predicted_type=`board_resolution`。
4. 川网传媒「年报审计报告」与「监事会关于…年度报告的审核意见」仍落 annual_report（锁测覆盖）。
5. known_004 届次 pattern 与 known_003「第四届监事会第五次」互斥；board known_003 与 known_002「第三届董事会第四次」互斥。

## 7. 能力增益

- 监事会决议**届次全锚定**第四案（海汽集团第三十次）进入 **known-document ready** 并经公司窗 live metadata 确认
- 董事会决议**届次全锚定**第三案（华蓝集团第五届第五次）进入 ready
- ready 计数 84 → **86**；remaining other 仍 ~0

## 8. Gate 摘要

```text
b_class_supervisory_board_known_003_004_promotion_live_gate = LIVE_PASS
task_id = B-FM-51
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
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +supervisory known_004 / board known_003 |
| `lab/test_cninfo_b_class_supervisory_board_known_003_004_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_supervisory_board_known_003_004_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_report.csv` | ready 刷新 |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_summary.md` | ready 刷新 |
| `outputs/validation/cninfo_b_class_supervisory_board_known_003_004_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_supervisory_board_known_003_004_live_20260715/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_supervisory_board_known_003_004_promotion_live_20260715.md` | 本报告 |

## 10. 返回卡

| 字段 | 值 |
|------|-----|
| task | B-FM-51 监事会决议 known_004 + 董事会决议 known_003 晋升 + bounded live（BD2E778/668） |
| files | fixture + 2 tests + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | promotion **7 OK** · live mock **3 OK** · B-FM-50 不回退 · ready **86** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | 成功 live **4**；本任务合计 **4**（PDF=0） |
| allow-list | `supervisory_board_known_004`, `board_resolution_known_003` |
| wall | 成功 live **~9.4 s** |
| ready_for_commit | **true** |

## 11. 下一步（Controller）

1. 可选：commit B-FM-51 包（不含 console 日志；勿 `git add .`）；B-FM-50 若尚未 commit 可一并或分轨。
2. 下一高价值第二案仍优先：`independent_director_meeting_review_known_002` / `asset_valuation_explanation_known_002` / `listing_sponsor_known_002` / `continuous_supervision_training_known_002`（均需独立第二 harvest）；或 board/supervisory 余量届次案（如 BD2E658/730）。
3. `audit_report_known_002` 仍需无「年报」子串 harvest。
4. 勿重开已 LIVE_PASS known（含本包两案与 B-FM-50 及更早）。
5. 不 push，除非 human 明确要求。
