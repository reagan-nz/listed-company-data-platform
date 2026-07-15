# CNINFO B 类 B-FM-43 — 持续督导年度 / 公司章程 Known-002 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-43  
> **性质：** harvest 晋升（known_002）+ allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 continuous_supervision / company_articles **known_001** 及 B-FM-42 及更早 LIVE_PASS  
> standing_scope 允许 CNINFO live；other backlog 已清零后，继续高价值族第二案覆盖

## 1. 决策表

| # | 选项 | 证据 | 结论 |
|---|------|------|------|
| 1 | known_002 promotion | BD2E775 → continuous_supervision_annual_known_002 | **执行** — 对称 known_001 恒立液压 |
| 2 | known_002 promotion | BD2E330 → company_articles_known_002 | **执行** — 对称 known_001 古麒绒材 |
| 3 | alternate | audit_report_known_002（BD2E653） | **拒绝** — 标题含「年报审计报告」路由落 annual_report / periodic |
| 4 | alternate | continuous_supervision_training_known_002 | **推迟** — harvest 仅见 known_001 一条培训案 |

## 2. 晋升案

| case_id | 状态 | harvest | title_pattern | 窗 |
|---------|------|---------|---------------|-----|
| `continuous_supervision_annual_known_002` | （新增）→ **ready** | BD2E775 国检集团 603060 · ann=1223348104 · 2025-04-27 | `国检测试控股集团股份有限公司2024年度持续督导年度报告书` · 2025-04-26~29 | 持续督导年度 |
| `company_articles_known_002` | （新增）→ **ready** | BD2E330 秀强股份 300160 · ann=1223952124 · 2025-06-20 | `秀强玻璃工艺股份有限公司章程（2025年6月修订）` · 2025-06-19~22 | 公司章程 |

## 3. 路由

本包 **不改** `cninfo_announcement_categories.yaml`。  
持续督导 / 公司章程分别已由 B-FM-30 / B-FM-36 硬化为 announcement → general。

## 4. 关闭边界（勿重开）

| 包 | 状态 |
|----|------|
| `continuous_supervision_annual_known_001` / `training_known_001` | LIVE_PASS（B-FM-30；勿重开 live 根） |
| `company_articles_known_001` / `raised_funds_management_system_known_001` | LIVE_PASS（B-FM-36） |
| `bond_trustee_report_known_002` / `tracking_rating_report_known_002` | LIVE_PASS（B-FM-42） |
| `incentive_object_list_known_001` / `sales_brief_known_001` | LIVE_PASS（B-FM-41） |
| `external_guarantee_situation_brief_known_001` / `esg_report_known_001` | LIVE_PASS（B-FM-40） |
| 其余已 LIVE_PASS known | 勿重开 |

## 5. Allow-list

仅 `continuous_supervision_annual_known_002` + `company_articles_known_002`；category 空。  
排除全部已 LIVE_PASS（含 known_001）/ placeholder / guard。  
**不含** console 日志。

## 6. 测试与门禁

| 命令 / 门 | 结果 |
|-----------|------|
| `python lab/test_cninfo_b_class_supervision_articles_known_002_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_supervision_articles_known_002_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_bond_trustee_rating_known_002_promotion.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_continuous_supervision_known_001_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_articles_raised_funds_system_known_001_live.py` | **3 OK** |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | ready=**70** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=70 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

## 7. Live 结果

| 字段 | 值 |
|------|-----|
| result | **LIVE_PASS** |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| wall（成功 live） | **~6.7 s** |
| allow-list | `continuous_supervision_annual_known_002`, `company_articles_known_002` |

| case_id | matched title | matched date | route | case_result |
|---------|---------------|--------------|-------|-------------|
| `continuous_supervision_annual_known_002` | 中国国际金融股份有限公司关于中国国检测试控股集团股份有限公司2024年度持续督导年度报告书 | 2025-04-27 | classified_correctly / announcement | **pass** |
| `company_articles_known_002` | 江苏秀强玻璃工艺股份有限公司章程（2025年6月修订） | 2025-06-20 | classified_correctly / announcement | **pass** |

## 8. Gate 声明

```
b_class_supervision_articles_known_002_promotion_live_gate = LIVE_PASS
task_id = B-FM-43
cninfo_calls_success_live = 4
pdf_download = 0
routing_changed = false
verified = false
production_ready = false
```

## 9. 文件清单

| 路径 | 说明 |
|------|------|
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +continuous_supervision_annual / company_articles known_002 |
| `lab/test_cninfo_b_class_supervision_articles_known_002_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_supervision_articles_known_002_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_{report,summary}.*` | ready 刷新（70） |
| `outputs/validation/cninfo_b_class_supervision_articles_known_002_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_supervision_articles_known_002_live_20260715/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_supervision_articles_known_002_promotion_live_20260715.md` | 本报告 |

## 10. 返回卡

| 字段 | 值 |
|------|-----|
| task | B-FM-43 持续督导年度/公司章程 known_002 晋升 + bounded live（BD2E775/330） |
| files | fixture + 2 tests + ready 刷新 + dry-run + live 包 + 本报告（无路由改动） |
| tests | promotion **7 OK** · live mock **3 OK** · known_001/B-FM-42 不回退 · ready **70** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | 成功 live **4**；本任务合计 **4**（PDF=0） |
| allow-list | `continuous_supervision_annual_known_002`, `company_articles_known_002` |
| wall | 成功 live **~6.7 s** |
| ready_for_commit | **true** |

## 11. 下一步（Controller）

1. 可选：commit B-FM-43 包（不含 console 日志；勿 `git add .`）。
2. 下一高价值第二案可优先：`audit_report` 需另寻无「年报」子串的 harvest；或 `esg_report_known_002` / `sales_brief_known_002`（若 harvest 有余量）。
3. 勿重开已 LIVE_PASS known（含本包两案与 B-FM-42 及更早）。
4. 不 push，除非 human 明确要求。
