# CNINFO B 类 B-FM-02（R19）— 跟踪评级 Known-006–010 / 债券受托 Known-005–007 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-02  
> **性质：** offline harvest（deferred 薄）→ fallback residual 晋升 + allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 B-FM-01 及更早 LIVE_PASS

---

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | deferred second | independent_director_meeting_review_known_002 | **推迟** — harvest 仍无清晰第二案 |
| 2 | deferred second | asset_valuation_explanation_known_002 | **推迟** — 仅有 known_001 |
| 3 | deferred second | listing_sponsor_known_002 | **推迟** — 无清晰第二案；半年报污染仍在 |
| 4 | deferred second | continuous_supervision_training_known_002 | **推迟** — 仅有 known_001 |
| 5 | reject | audit_report_known_002（川网传媒年报审计报告） | **拒绝** — 年报陷阱 |
| 6 | fallback residual | tracking_rating known_006–010 + bond_trustee known_005–007 | **执行** |

**价值判断：** deferred 四族第二案 harvest 仍薄；tracking/bond 余量子型证据清晰（含南方航空 / 华阳国际 / 广联航空 spotlight）且路由已硬化，本包纯晋升+bounded live（**8 案** meaningful sample）。equity_change known_002 仍薄，本包不推。

| case_id | 变更 | harvest | title_pattern / 窗 | 子类型 |
|---------|------|---------|-------------------|--------|
| `tracking_rating_report_known_006` | （新增）→ **ready** | BD2E558 华阳国际 002949 · ann=1223952243 · 2025-06-20 | 公司锚定可转债2025跟踪 · 2025-06-19~22 | 可转债跟踪（无定期） |
| `tracking_rating_report_known_007` | （新增）→ **ready** | BD2E644 广联航空 300900 · ann=1224016467 · 2025-06-27 | 公司锚定相关债券跟踪 · 2025-06-26~29 | 相关债券第二公司 |
| `tracking_rating_report_known_008` | （新增）→ **ready** | BD2E156 立讯精密 002475 · ann=1224016122 · 2025-06-27 | 公司锚定可转债2025跟踪 · 2025-06-26~29 | 可转债跟踪第二公司 |
| `tracking_rating_report_known_009` | （新增）→ **ready** | B2E012 天合光能 688599 · ann=1223956820 · 2025-06-23 | `向不特定对象发行可转换公司债券2025年跟踪评级报告` · 2025-06-22~25 | 向不特定对象可转债跟踪 |
| `tracking_rating_report_known_010` | （新增）→ **ready** | BD2E360 航新科技 300424 · ann=1224012941 · 2025-06-27 | 公司锚定可转债定期跟踪 · 2025-06-26~29 | 定期跟踪第二公司 |
| `bond_trustee_report_known_005` | （新增）→ **ready** | BD2E364 南方航空 600029 · ann=1224014795 · 2025-06-27 | `公开发行A股可转换公司债券受托管理事务报告（2024年度）` · 2025-06-26~29 | A股可转债受托 |
| `bond_trustee_report_known_006` | （新增）→ **ready** | BD2E076 铜陵有色 000630 · ann=1223997318 · 2025-06-26 | `向特定对象发行可转换公司债券受托管理事务报告（2024年度）` · 2025-06-25~28 | 特定对象可转债受托 |
| `bond_trustee_report_known_007` | （新增）→ **ready** | BD2E208 美锦能源 000723 · ann=1224016384 · 2025-06-29 | `公开发行可转换公司债券2024年度受托管理事务报告` · 2025-06-28~07-01 | 年度前置语序受托 |

### 明确不重开

| 包 | 状态 |
|----|------|
| `tracking_rating_report_known_001`–`005` | LIVE_PASS（勿重开） |
| `bond_trustee_report_known_001`–`004` | LIVE_PASS（勿重开） |
| `supervisory_board_known_005` / `continuous_supervision_annual_known_005` | LIVE_PASS（勿重开） |
| deferred known_002 四族 / `audit_report_known_002` | 未晋升 |
| 其余已 LIVE_PASS known | 勿重开 |

### Allow-list

仅本包 8 案；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。

---

## 2. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_tracking_bond_residual_known_006_010_promotion.py` | **8 OK** |
| `python lab/test_cninfo_b_class_tracking_bond_residual_known_006_010_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_tracking_bond_residual_known_004_005_promotion.py` | **9 OK**（不回退） |
| `python lab/test_cninfo_b_class_supervisory_supervision_known_005_promotion.py` | **7 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | ready=**103** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=103 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=8 |
| bounded live | **LIVE_PASS** · pass=**8**/0/0 |

---

## 3. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO（成功 live） | **16**（8×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计） | **16** |
| wall（成功 live） | **~64 s** |
| allow-list | known_006–010 + bond_trustee known_005–007 |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `tracking_rating_report_known_006` | 2020年深圳市华阳国际工程设计股份有限公司公开发行可转换公司债券2025年跟踪评级报告 | 2025-06-20 | classified_correctly / announcement | **pass** |
| `tracking_rating_report_known_007` | 广联航空工业股份有限公司相关债券2025年跟踪评级报告 | 2025-06-27 | classified_correctly / announcement | **pass** |
| `tracking_rating_report_known_008` | 立讯精密工业股份有限公司公开发行可转换公司债券2025年跟踪评级报告 | 2025-06-27 | classified_correctly / announcement | **pass** |
| `tracking_rating_report_known_009` | 天合光能股份有限公司向不特定对象发行可转换公司债券2025年跟踪评级报告 | 2025-06-23 | classified_correctly / announcement | **pass** |
| `tracking_rating_report_known_010` | 广州航新航空科技股份有限公司公开发行可转换公司债券定期跟踪评级报告 | 2025-06-27 | classified_correctly / announcement | **pass** |
| `bond_trustee_report_known_005` | 中国南方航空股份有限公司公开发行A股可转换公司债券受托管理事务报告（2024年度） | 2025-06-27 | classified_correctly / announcement | **pass** |
| `bond_trustee_report_known_006` | 铜陵有色金属集团股份有限公司向特定对象发行可转换公司债券受托管理事务报告（2024年度） | 2025-06-26 | classified_correctly / announcement | **pass** |
| `bond_trustee_report_known_007` | 山西美锦能源股份有限公司公开发行可转换公司债券2024年度受托管理事务报告 | 2025-06-29 | classified_correctly / announcement | **pass** |

执行要点：

1. 八案均 **pass**（无 ambiguous / 无重试）。
2. 无 orgId fallback；无 PDF。
3. 八案 predicted_type 均为 `announcement`。
4. 川网传媒「年报审计报告」仍落 annual_report（锁测覆盖）。
5. 新 pattern 与 known_001–005 互斥；不反向误抬旧 harvest。

---

## 4. 能力增益

- 跟踪评级**第六–十案**进入 **known-document ready** 并经公司窗 live metadata 确认
- 债券受托**第五–七案**（A股可转债 / 特定对象 / 年度前置语序）进入 ready
- ready 计数 95 → **103**；deferred known_002 仍薄；remaining other 仍 ~0

---

## 5. Gate 摘要

```text
b_class_tracking_bond_residual_known_006_010_promotion_live_gate = LIVE_PASS
task_id = B-FM-02
cninfo_calls_success_live = 16
cninfo_calls_task_total = 16
pdf_downloads = 0
ready_for_commit = true
commit = not_done
push = not_done
```

---

## 6. 修改文件

| 路径 | 作用 |
|------|------|
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +tracking known_006–010 / bond_trustee known_005–007 |
| `lab/test_cninfo_b_class_tracking_bond_residual_known_006_010_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_tracking_bond_residual_known_006_010_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_r19_bfm02_offline_harvest_20260716.md` | offline harvest 决策 |
| `outputs/validation/cninfo_b_class_tracking_bond_residual_known_006_010_live_20260716/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_tracking_bond_residual_known_006_010_promotion_dry_run_*_20260716.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_*` | ready=103 刷新 |
| `outputs/validation/cninfo_b_class_tracking_bond_residual_known_006_010_promotion_live_20260716.md` | 本报告 |

---

## 7. Commit path（显式；executor 不执行 commit）

```text
fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml
lab/test_cninfo_b_class_tracking_bond_residual_known_006_010_promotion.py
lab/test_cninfo_b_class_tracking_bond_residual_known_006_010_live.py
outputs/validation/cninfo_b_class_r19_bfm02_offline_harvest_20260716.md
outputs/validation/cninfo_b_class_tracking_bond_residual_known_006_010_live_20260716/
outputs/validation/cninfo_b_class_tracking_bond_residual_known_006_010_promotion_dry_run_20260716.csv
outputs/validation/cninfo_b_class_tracking_bond_residual_known_006_010_promotion_dry_run_summary_20260716.md
outputs/validation/cninfo_b_class_tracking_bond_residual_known_006_010_promotion_live_20260716.md
outputs/validation/cninfo_b_class_retrieval_ready_case_report.csv
outputs/validation/cninfo_b_class_retrieval_ready_case_summary.md
```

Suggested message:

```text
feat(b-class): promote tracking/bond residual known_006-010 (B-FM-02)

Deferred known_002 families stayed thin; promote eight coherent tracking_rating
and bond_trustee residual cases (incl. spotlight 华阳/广联/南航) with bounded live.
```

---

## 8. Next B candidate

1. 继续 tracking/bond 余量（如精测电子/润禾材料/奥飞数据「向不特定对象」受托；润达医疗/中天精装「跟踪评级结果的公告」子型）— 若 harvest 仍清晰可再组 3–10 案。
2. 或 deferred known_002 第二案：若出现清晰命中再开；**勿**晋升 audit_report_known_002。
3. **勿**重开本包及更早 LIVE_PASS。
