# CNINFO B 类 B-FM-53 — 核查意见 Known-004 / 持续督导年度 Known-004 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-53  
> **性质：** harvest 晋升（vo known_004 / supervision annual known_004）+ allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 B-FM-52 及更早 LIVE_PASS（含 board known_001–005、vo/supervision known_001–003）

---

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | known_004 promotion | BD2E550 → verification_opinion_known_004 | **执行** — 激励对象名单核查意见子类型（闭合 known_003 注明缺口） |
| 2 | known_004 promotion | BD2E785 → continuous_supervision_annual_known_004 | **执行** — 持续督导年度报告书余量（公司全称锚定） |
| 3 | alternate | independent_director_meeting_review_known_002 | **推迟** — harvest 仍无清晰第二案 |
| 4 | alternate | asset_valuation_explanation_known_002 / listing_sponsor_known_002 | **推迟** — 仅有 known_001 同源行 |
| 5 | alternate | continuous_supervision_training_known_002 | **推迟** — harvest 仅见 known_001 |
| 6 | alternate | audit_report_known_002（川网传媒年报审计报告） | **拒绝** — 仍含「年报」→ periodic |

**价值判断：** 高价值第二案 harvest 仍薄；BD2E550/785 均有现成 pass 证据且子类型可区分，路由已硬化，本包纯晋升+bounded live。

| case_id | 变更 | harvest | title_pattern / 窗 | 子类型 |
|---------|------|---------|-------------------|--------|
| `verification_opinion_known_004` | （新增）→ **ready** | BD2E550 高争民爆 002827 · ann=1223956618 · 2025-06-23 | `激励对象名单的核查意见` · 2025-06-22~25 | 激励名单核查 |
| `continuous_supervision_annual_known_004` | （新增）→ **ready** | BD2E785 上海汽配 603107 · ann=1223185374 · 2025-04-21 | `上海汽车空调配件…持续督导年度报告书` · 2025-04-20~23 | 督导年度公司全称 |

### 明确不重开

| 包 | 状态 |
|----|------|
| `board_resolution_known_001`–`005` | LIVE_PASS（含 B-FM-52；勿重开） |
| `verification_opinion_known_001`–`003` | LIVE_PASS（勿重开） |
| `continuous_supervision_annual_known_001`–`003` | LIVE_PASS（勿重开） |
| `audit_report_known_001` | LIVE_PASS（本包不推 known_002） |
| 其余已 LIVE_PASS known | 勿重开 |

### Allow-list

仅 `verification_opinion_known_004` + `continuous_supervision_annual_known_004`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。

---

## 2. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_verification_supervision_known_004_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_verification_supervision_known_004_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_board_resolution_known_004_005_promotion.py` | **7 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | ready=**90** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=90 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

---

## 3. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计） | **4** |
| wall（成功 live） | **~20 s** |
| allow-list | `verification_opinion_known_004`, `continuous_supervision_annual_known_004` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `verification_opinion_known_004` | 监事会关于公司2025年限制性股票激励计划激励对象名单的核查意见及公示情况说明 | 2025-06-23 | classified_correctly / announcement | **pass** |
| `continuous_supervision_annual_known_004` | 民生证券股份有限公司关于上海汽车空调配件股份有限公司2024年度持续督导年度报告书 | 2025-04-21 | classified_correctly / announcement | **pass** |

执行要点：

1. 首轮两案均 **pass**（无 ambiguous / 无重试）。
2. 无 orgId fallback；无 PDF。
3. 两案 predicted_type 均为 `announcement`（督导案 harvest 标 periodic_report 仍不进 annual_report）。
4. 川网传媒「年报审计报告」仍落 annual_report（锁测覆盖）。
5. vo known_004 pattern 与 known_001–003 募资/限售/节余串互斥；supervision known_004 公司全称与 known_001–003 互斥。

---

## 4. 能力增益

- 核查意见**激励对象名单**第四案进入 **known-document ready** 并经公司窗 live metadata 确认
- 持续督导年度报告书**第四案**（上海汽配公司全称）进入 ready
- ready 计数 88 → **90**；remaining other 仍 ~0

---

## 5. Gate 摘要

```text
b_class_verification_supervision_known_004_promotion_live_gate = LIVE_PASS
task_id = B-FM-53
cninfo_calls_success_live = 4
cninfo_calls_task_total = 4
pdf_downloads = 0
ready_for_commit = true
commit = not_done
```

---

## 6. 修改文件

| 路径 | 说明 |
|------|------|
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +vo known_004 / supervision annual known_004 |
| `lab/test_cninfo_b_class_verification_supervision_known_004_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_verification_supervision_known_004_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_verification_supervision_known_004_live_20260716/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_verification_supervision_known_004_promotion_dry_run_*_20260716.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_verification_supervision_known_004_promotion_live_20260716.md` | 本报告 |

---

## 7. 回传摘要

| 项 | 值 |
|----|-----|
| task | B-FM-53 核查意见 known_004 + 持续督导年度 known_004 晋升 + bounded live（BD2E550/785） |
| files | fixtures known yaml · promotion/live 锁测 · live 包 · dry-run · 本报告 |
| tests | promotion **7 OK** · live mock **3 OK** · board_004/005 不回退 · ready **90** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | **4**（PDF=0） |
| allow-list | `verification_opinion_known_004`, `continuous_supervision_annual_known_004` |
| wall | **~20 s** |
| gate | **LIVE_PASS** |
| ready_for_commit | **true**（未 commit / 未 push） |

---

## 8. 下一步

1. 可选：commit B-FM-53 包（不含 console 日志；勿 `git add .`）；B-FM-52 若尚未 commit 可一并或分轨。
2. 下一高价值第二案仍优先：`independent_director_meeting_review_known_002` / `asset_valuation_explanation_known_002` / `listing_sponsor_known_002` / `continuous_supervision_training_known_002`（均需独立第二 harvest）；或 continuous_supervision_annual known_005（BD2E791 万朗磁塑）/ supervisory_board known_005（BD2E322）/ tracking_rating 余量。
