# CNINFO B 类 B-FM-54 — 监事会决议 Known-005 / 持续督导年度 Known-005 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-54  
> **性质：** harvest 晋升（supervisory board known_005 / supervision annual known_005）+ allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 B-FM-53 及更早 LIVE_PASS（含 vo/supervision known_004、board known_001–005、supervisory known_001–004）

---

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | known_005 promotion | BD2E322 → supervisory_board_known_005 | **执行** — 监事会届次全锚定余量（第十二次） |
| 2 | known_005 promotion | BD2E791 → continuous_supervision_annual_known_005 | **执行** — 持续督导年度报告书余量（万朗磁塑公司全称） |
| 3 | alternate | independent_director_meeting_review_known_002 | **推迟** — harvest 仍无清晰第二案 |
| 4 | alternate | asset_valuation_explanation_known_002 / listing_sponsor_known_002 | **推迟** — 仅有 known_001 同源行 |
| 5 | alternate | continuous_supervision_training_known_002 | **推迟** — harvest 仅见 known_001 |
| 6 | alternate | audit_report_known_002（川网传媒年报审计报告） | **拒绝** — 仍含「年报」→ periodic |

**价值判断：** 高价值第二案 harvest 仍薄；BD2E322/791 均有现成 pass 证据且与 known_001–004 子串互斥，路由已硬化，本包纯晋升+bounded live。

| case_id | 变更 | harvest | title_pattern / 窗 | 子类型 |
|---------|------|---------|-------------------|--------|
| `supervisory_board_known_005` | （新增）→ **ready** | BD2E322 建新股份 300107 · ann=1223713207 · 2025-05-28 | `第六届监事会第十二次会议决议公告` · 2025-05-27~30 | 监事会届次全锚定 |
| `continuous_supervision_annual_known_005` | （新增）→ **ready** | BD2E791 万朗磁塑 603150 · ann=1223409628 · 2025-04-29 | `安徽万朗磁塑…持续督导年度报告书` · 2025-04-28~05-01 | 督导年度公司全称 |

### 明确不重开

| 包 | 状态 |
|----|------|
| `verification_opinion_known_004` / `continuous_supervision_annual_known_004` | LIVE_PASS（B-FM-53；勿重开） |
| `board_resolution_known_001`–`005` | LIVE_PASS（勿重开） |
| `supervisory_board_known_001`–`004` | LIVE_PASS（勿重开） |
| `continuous_supervision_annual_known_001`–`003` | LIVE_PASS（勿重开） |
| `audit_report_known_001` | LIVE_PASS（本包不推 known_002） |
| 其余已 LIVE_PASS known | 勿重开 |

### Allow-list

仅 `supervisory_board_known_005` + `continuous_supervision_annual_known_005`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。  
（不含 console 日志。）

---

## 2. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_supervisory_supervision_known_005_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_supervisory_supervision_known_005_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_verification_supervision_known_004_promotion.py` | **7 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | ready=**92** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=92 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

---

## 3. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计） | **4** |
| wall（成功 live） | **~16 s** |
| allow-list | `supervisory_board_known_005`, `continuous_supervision_annual_known_005` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `supervisory_board_known_005` | 建新股份第六届监事会第十二次会议决议公告 | 2025-05-28 | classified_correctly / announcement | **pass** |
| `continuous_supervision_annual_known_005` | 国元证券股份有限公司关于安徽万朗磁塑股份有限公司2024年度持续督导年度报告书 | 2025-04-29 | classified_correctly / announcement | **pass** |

执行要点：

1. 首轮两案均 **pass**（无 ambiguous / 无重试）。
2. 无 orgId fallback；无 PDF。
3. 两案 predicted_type 均为 `announcement`（督导案 harvest 标 periodic_report 仍不进 annual_report）。
4. 川网传媒「年报审计报告」仍落 annual_report（锁测覆盖）。
5. supervisory known_005 pattern 与 known_001–004 届次/次数互斥；supervision known_005 公司全称与 known_001–004 互斥。

---

## 4. 能力增益

- 监事会决议**第五案**（建新股份届次全锚定）进入 **known-document ready** 并经公司窗 live metadata 确认
- 持续督导年度报告书**第五案**（万朗磁塑公司全称）进入 ready
- ready 计数 90 → **92**；remaining other 仍 ~0

---

## 5. Gate 摘要

```text
b_class_supervisory_supervision_known_005_promotion_live_gate = LIVE_PASS
task_id = B-FM-54
cninfo_calls_success_live = 4
cninfo_calls_task_total = 4
pdf_downloads = 0
ready_for_commit = true
commit = not_done
push = not_done
```

---

## 6. 修改文件

| 路径 | 作用 |
|------|------|
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +supervisory known_005 / supervision annual known_005 |
| `lab/test_cninfo_b_class_supervisory_supervision_known_005_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_supervisory_supervision_known_005_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_supervisory_supervision_known_005_live_20260716/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_supervisory_supervision_known_005_promotion_dry_run_*_20260716.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_supervisory_supervision_known_005_promotion_live_20260716.md` | 本报告 |

---

## 7. 回报卡

| 项 | 值 |
|----|-----|
| task | B-FM-54 监事会决议 known_005 + 持续督导年度 known_005 晋升 + bounded live（BD2E322/791） |
| files | fixtures known yaml · promotion/live 锁测 · live 包 · dry-run · 本报告 |
| tests | promotion **7 OK** · live mock **3 OK** · vo/sup_004 不回退 · ready **92** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | **4**（PDF=0） |
| allow-list | `supervisory_board_known_005`, `continuous_supervision_annual_known_005` |
| wall | **~16 s** |
| gate | **LIVE_PASS** |
| ready_for_commit | **true**（未 commit / 未 push） |

---

## 8. 下一步

1. 可选：commit B-FM-54 包（不含 console 日志；勿 `git add .`）；B-FM-53 若尚未 commit 可一并或分轨。
2. 下一高价值第二案仍优先：`independent_director_meeting_review_known_002` / `asset_valuation_explanation_known_002` / `listing_sponsor_known_002` / `continuous_supervision_training_known_002`（均需独立第二 harvest）；或 tracking_rating / bond_trustee / equity_change 余量；或 short-form/event 路由 harden→promote。
