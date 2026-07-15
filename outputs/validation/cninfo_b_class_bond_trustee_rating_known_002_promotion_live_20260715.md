# CNINFO B 类 B-FM-42 — 债券受托 / 跟踪评级 Known-002 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-42  
> **性质：** harvest 晋升（known_002）+ allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 bond_trustee / tracking_rating **known_001** 及 B-FM-41 及更早 LIVE_PASS  
> **不**触碰 A/C/D · **不** commit / push · **不** PDF / OCR / DB / RAG  
> standing_scope 允许 CNINFO live；other backlog 已清零后，转向高价值族第二案覆盖

## 1. 候选决策

| # | 类型 | 候选 | 决策 |
|---|------|------|------|
| 1 | known_002 promotion | BD2E054 → bond_trustee_report_known_002 | **执行** — 公司债券受托（对称 known_001 可转债受托） |
| 2 | known_002 promotion | BD2E086 → tracking_rating_report_known_002 | **执行** — 主体 2025 年跟踪评级（对称 known_001 可转债定期跟踪） |
| 3 | alternate | continuous_supervision_annual_known_002 | **推迟** — 同族第二案已有 training；本包优先债券披露族 |
| 4 | alternate | regulatory_known_003 / periodic_guard_001 | **拒绝** — harvest 仍缺真·问询函原文 / guard 非本包 |

**价值判断：** bond_trustee / tracking_rating 在 B-FM-29 仅各有 known_001；本包补第二案并覆盖「公司债 vs 可转债」「主体年度 vs 可转债定期」标题变体。路由已硬化，本包 **不改路由**。

## 2. Routing 变更

| 层 | 变更 |
|----|------|
| `config/cninfo_announcement_categories.yaml` | **无** |
| `lab/validate_cninfo_b_class_category_routing.py` | **无** |
| `plans/cninfo_b_class_category_routing_rules.md` | **无** |

复用 B-FM-29：含「受托管理事务报告」/「跟踪评级报告」→ `announcement`。

## 3. 晋升内容

| case_id | 状态 | harvest | title_pattern | 窗 |
|---------|------|---------|---------------|-----|
| `bond_trustee_report_known_002` | （新增）→ **ready** | BD2E054 深圳能源 000027 · ann=1224039075 · 2025-06-30 | `股份有限公司公司债券受托管理事务报告（2024年度）` · 2025-06-29~07-02 | 公司债券受托 |
| `tracking_rating_report_known_002` | （新增）→ **ready** | BD2E086 长江证券 000783 · ann=1224015907 · 2025-06-27 | `股份有限公司2025年跟踪评级报告` · 2025-06-26~29 | 主体跟踪评级 |

路由：既有 B-FM-29 → `announcement` / `cninfo_general_announcement_pdf`（**非** `other`）。

pattern 消歧：

- 「股份有限公司公司债券受托…」不命中「…可转换公司债券受托…」
- 「股份有限公司2025年跟踪评级报告」不命中 known_001「…可转换公司债券定期跟踪评级报告」

## 4. 明确不重开

| case_id / 族 | 说明 |
|--------------|------|
| `bond_trustee_report_known_001` / `tracking_rating_report_known_001` | LIVE_PASS（B-FM-29；勿重开 live 根） |
| `incentive_object_list_known_001` / `sales_brief_known_001` | LIVE_PASS（B-FM-41；勿重开） |
| `external_guarantee_situation_brief_known_001` / `esg_report_known_001` | LIVE_PASS（B-FM-40） |
| `legal_opinion_known_001`–`006` | LIVE_PASS |
| `listing_sponsor` / `equity_change` / `verification_opinion` / `supervisory_board` / `shareholder_meeting` / 其余已 LIVE_PASS known | 勿重开 |

## 5. Allow-list

仅 `bond_trustee_report_known_002` + `tracking_rating_report_known_002`；category 空。  
排除全部已 LIVE_PASS（含 known_001）/ placeholder / guard。  
ready_for_commit 文件清单**不含** console / terminal 日志。

## 6. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_bond_trustee_rating_known_002_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_bond_trustee_rating_known_002_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_bond_trustee_rating_known_001_promotion.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_bond_trustee_rating_edge.py` | **5 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | ready=**68** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=68 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

## 7. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计） | **4** |
| wall（成功 live） | **~6.8 s** |
| allow-list | `bond_trustee_report_known_002`, `tracking_rating_report_known_002` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `bond_trustee_report_known_002` | 深圳能源集团股份有限公司公司债券受托管理事务报告（2024年度） | 2025-06-30 | classified_correctly / announcement | **pass** |
| `tracking_rating_report_known_002` | 长江证券股份有限公司2025年跟踪评级报告 | 2025-06-27 | classified_correctly / announcement | **pass** |

执行要点：

1. 无 orgId fallback；无 PDF。
2. predicted_type=`announcement`；与 known_001 可转债变体可区分。
3. 未 mutate B-FM-29 known_001 live 根。

## 8. 能力增益

- 公司债券受托 / 主体年度跟踪评级进入 **known-document ready** 并经公司窗 live metadata 确认
- bond_trustee / tracking_rating 族覆盖 1→**2**
- ready 计数 66 → **68**

## 9. Gate 摘要

```text
b_class_bond_trustee_rating_known_002_promotion_live_gate = LIVE_PASS
task_id = B-FM-42
cninfo_calls_success_live = 4
cninfo_calls_task_total = 4
pdf_downloads = 0
ready_for_commit = true
commit = not_done
push = not_done
```

## 10. 受保护 / 隔离

- 未触碰 A/C/D 线文件
- 未 mutate 既有 LIVE_PASS live 根（含 B-FM-29 known_001 / B-FM-41）
- 未 PDF / OCR / DB / MinIO / RAG
- 未 commit / push
- 未改路由配置

## 11. 文件清单（ready_for_commit；不含 console 日志）

| 路径 | 角色 |
|------|------|
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +bond_trustee / tracking_rating known_002 |
| `lab/test_cninfo_b_class_bond_trustee_rating_known_002_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_bond_trustee_rating_known_002_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_*` | ready 刷新（68） |
| `outputs/validation/cninfo_b_class_bond_trustee_rating_known_002_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_bond_trustee_rating_known_002_live_20260715/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_bond_trustee_rating_known_002_promotion_live_20260715.md` | 本报告 |

## 12. 返回包

| 项 | 值 |
|----|-----|
| task | B-FM-42 债券受托/跟踪评级 known_002 晋升 + bounded live（BD2E054/086） |
| files | fixture + 2 tests + ready 刷新 + dry-run + live 包 + 本报告（无路由改动） |
| tests | promotion **7 OK** · live mock **3 OK** · known_001/edge 不回退 · ready **68** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | 成功 live **4**；本任务合计 **4**（PDF=0） |
| allow-list | `bond_trustee_report_known_002`, `tracking_rating_report_known_002` |
| wall | 成功 live **~6.8 s** |
| ready_for_commit | **true** |

## 13. 下一步（Controller）

1. 可选：commit B-FM-42 包（不含 console 日志；勿 `git add .`）。
2. 下一高价值第二案可优先：`continuous_supervision_annual_known_002` / `company_articles_known_002` / `audit_report_known_002`（harvest 有余量）。
3. 勿重开已 LIVE_PASS known（含本包两案与 B-FM-41 及更早）。
4. 不 push，除非 human 明确要求。
