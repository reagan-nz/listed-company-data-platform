# CNINFO B 类 B-FM-01（R19）— 跟踪评级 Known-004/005 / 债券受托 Known-004 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-01  
> **性质：** offline harvest（deferred 薄）→ fallback residual 晋升 + allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 B-FM-54 及更早 LIVE_PASS

---

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | deferred second | independent_director_meeting_review_known_002 | **推迟** — harvest 仍无清晰第二案 |
| 2 | deferred second | asset_valuation_explanation_known_002 | **推迟** — 仅有 known_001 |
| 3 | deferred second | listing_sponsor_known_002 | **推迟** — 无清晰第二案；白云机场行含半年报污染 |
| 4 | deferred second | continuous_supervision_training_known_002 | **推迟** — 仅有 known_001 |
| 5 | reject | audit_report_known_002（川网传媒年报审计报告） | **拒绝** — 年报陷阱 |
| 6 | fallback residual | tracking_rating known_004/005 + bond_trustee known_004 | **执行** |

**价值判断：** deferred 四族第二案 harvest 仍薄；tracking/bond 余量子型证据清晰且路由已硬化，本包纯晋升+bounded live（3 案 meaningful sample）。equity_change known_002 仍薄，本包不推。

| case_id | 变更 | harvest | title_pattern / 窗 | 子类型 |
|---------|------|---------|-------------------|--------|
| `tracking_rating_report_known_004` | （新增）→ **ready** | BD2E606 南京聚隆 300644 · ann=1224014161 · 2025-06-27 | `相关债券2025年跟踪评级报告` · 2025-06-26~29 | 相关债券跟踪评级 |
| `tracking_rating_report_known_005` | （新增）→ **ready** | BD2E636 申昊科技 300853 · ann=1224016390 · 2025-06-27 | `主体及“申昊转债”2025年度跟踪评级报告` · 2025-06-26~29 | 主体及转债联合 |
| `bond_trustee_report_known_004` | （新增）→ **ready** | B2E013 京东方A 000725 · ann=1224036525 · 2025-06-30 | `可续期公司债券受托管理事务报告（2024年度）` · 2025-06-29~07-02 | 可续期公司债受托 |

### 明确不重开

| 包 | 状态 |
|----|------|
| `tracking_rating_report_known_001`–`003` | LIVE_PASS（勿重开） |
| `bond_trustee_report_known_001`–`003` | LIVE_PASS（勿重开） |
| `supervisory_board_known_005` / `continuous_supervision_annual_known_005` | LIVE_PASS（B-FM-54；勿重开） |
| deferred known_002 四族 / `audit_report_known_002` | 未晋升 |
| 其余已 LIVE_PASS known | 勿重开 |

### Allow-list

仅 `tracking_rating_report_known_004` + `tracking_rating_report_known_005` + `bond_trustee_report_known_004`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。  
（不含 console 日志。）

---

## 2. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_tracking_bond_residual_known_004_005_promotion.py` | **9 OK** |
| `python lab/test_cninfo_b_class_tracking_bond_residual_known_004_005_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_supervisory_supervision_known_005_promotion.py` | **7 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | ready=**95** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=95 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=3 |
| bounded live | **LIVE_PASS** · pass=**3**/0/0 |

---

## 3. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO（成功 live） | **6**（3×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计） | **6** |
| wall（成功 live） | **~22 s** |
| allow-list | `tracking_rating_report_known_004`, `tracking_rating_report_known_005`, `bond_trustee_report_known_004` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `tracking_rating_report_known_004` | 南京聚隆科技股份有限公司相关债券2025年跟踪评级报告 | 2025-06-27 | classified_correctly / announcement | **pass** |
| `tracking_rating_report_known_005` | 杭州申昊科技股份有限公司主体及“申昊转债”2025年度跟踪评级报告 | 2025-06-27 | classified_correctly / announcement | **pass** |
| `bond_trustee_report_known_004` | 京东方科技集团股份有限公司可续期公司债券受托管理事务报告（2024年度） | 2025-06-30 | classified_correctly / announcement | **pass** |

执行要点：

1. 首轮三案均 **pass**（无 ambiguous / 无重试）。
2. 无 orgId fallback；无 PDF。
3. 三案 predicted_type 均为 `announcement`。
4. 川网传媒「年报审计报告」仍落 annual_report（锁测覆盖）。
5. 新 pattern 与 known_001–003 互斥；不反向误抬旧 harvest。

---

## 4. 能力增益

- 跟踪评级**第四/五案**（相关债券 + 主体及转债联合）进入 **known-document ready** 并经公司窗 live metadata 确认
- 债券受托**第四案**（可续期公司债）进入 ready
- ready 计数 92 → **95**；deferred known_002 仍薄；remaining other 仍 ~0

---

## 5. Gate 摘要

```text
b_class_tracking_bond_residual_known_004_005_promotion_live_gate = LIVE_PASS
task_id = B-FM-01
cninfo_calls_success_live = 6
cninfo_calls_task_total = 6
pdf_downloads = 0
ready_for_commit = true
commit = not_done
push = not_done
```

---

## 6. 修改文件

| 路径 | 作用 |
|------|------|
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +tracking known_004/005 / bond_trustee known_004 |
| `lab/test_cninfo_b_class_tracking_bond_residual_known_004_005_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_tracking_bond_residual_known_004_005_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_r19_bfm01_offline_harvest_20260716.md` | offline harvest 决策 |
| `outputs/validation/cninfo_b_class_tracking_bond_residual_known_004_005_live_20260716/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_tracking_bond_residual_known_004_005_promotion_dry_run_*_20260716.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_*` | ready=95 刷新 |
| `outputs/validation/cninfo_b_class_tracking_bond_residual_known_004_005_promotion_live_20260716.md` | 本报告 |

---

## 7. 回报卡

| 项 | 值 |
|----|-----|
| task | B-FM-01 R19 tracking known_004/005 + bond_trustee known_004 晋升 + bounded live |
| files | fixtures known yaml · promotion/live 锁测 · harvest · live 包 · dry-run · 本报告 |
| tests | promotion **9 OK** · live mock **3 OK** · B-FM-54 不回退 · ready **95** · dry-run **PASS** · live **3/3 LIVE_PASS** |
| CNINFO | **6**（PDF=0） |
| allow-list | `tracking_rating_report_known_004`, `tracking_rating_report_known_005`, `bond_trustee_report_known_004` |
| wall | **~22 s** |
| gate | **LIVE_PASS** |
| ready_for_commit | **true**（未 commit / 未 push） |

---

## 8. 下一步

1. Controller commit 本包（见 commit path list；勿 `git add .`；排除 `.venv` symlink 与无关 untracked）。
2. 下一 B 候选：南方航空 A股可转债受托 / 华阳国际可转债2025跟踪评级 / 广联航空相关债券 等余量；或 deferred known_002 仍待独立第二 harvest；勿重开 closed LIVE_PASS。
