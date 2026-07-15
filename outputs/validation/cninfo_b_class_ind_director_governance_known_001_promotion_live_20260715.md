# CNINFO B 类 B-FM-33 — 独立董事专门会议审核意见 / 提名人声明 Known-001 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-33  
> **性质：** routing harden + harvest 晋升 + allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 continuous_supervision / bond_trustee / tracking_rating / listing_sponsor / equity_change / verification_opinion / legal_opinion_known_001–006 / supervisory_board / shareholder_meeting / nonstandard_audit / raised_funds known LIVE_PASS  
> **不**触碰 A/C/D · **不** commit / push · **不** PDF / OCR / DB / RAG  
> standing_scope 允许 CNINFO live；本包闭合 B-FM-32 之后最高价值 remaining-other：独立董事专门会议的审核意见（BD2E426）+ 独立董事提名人声明与承诺（BD2E264）

## 1. 候选决策

| # | 类型 | 候选 | 决策 |
|---|------|------|------|
| 1 | routing harden + promotion | BD2E426 → independent_director_meeting_review_known_001 | **执行** — B-FM-32 明确可选下一边角；窄 pattern「独立董事专门会议的审核意见」 |
| 2 | routing harden + promotion | BD2E264 → independent_director_nominee_declaration_known_001 | **执行** — 同包治理披露第二边角；title_pattern 含姓名消歧 |
| 3 | remaining other | 章程/制度/薪酬/激励名单/简报/资产评估说明等 | **推迟** — 低价值边角，不硬推 routing |
| 4 | alternate | BD2E430 资产评估说明 | **推迟** — 长尾评估文书，价值低于治理会议/提名人披露 |
| 5 | alternate | periodic_guard_001 / regulatory_known_003 | **拒绝** — harvest 仍缺 |

**价值判断：** remaining other ~21 中，BD2E426（独立董事专门会议的审核意见）为 B-FM-32 已标出的最高价值可选边角；BD2E264（提名人声明与承诺）为清晰可窄 pattern 的对称治理披露。裸「审核意见」会波及 BD2E501 年报审核意见 periodic 路径，故只用「独立董事专门会议的审核意见」。

## 2. Routing 变更

| 层 | 变更 |
|----|------|
| `config/cninfo_announcement_categories.yaml` | general positive_patterns +`独立董事专门会议的审核意见` / `独立董事提名人声明与承诺` |
| `lab/validate_cninfo_b_class_category_routing.py` | `_general_document_type` 早退：含上述两串 → `announcement` |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表增独立董事专门会议审核意见 / 提名人声明行 |

不扩 schema；不新造 document_type；不扩裸「审核意见」进 periodic exclusion / unrelated。

## 3. 晋升内容

| case_id | 状态 | harvest | title_pattern | 窗 |
|---------|------|---------|---------------|-----|
| `independent_director_meeting_review_known_001` | （新增）→ **ready** | BD2E426 金枫酒业 600616 · ann=1223951163 · 2025-06-20 | `独立董事专门会议的审核意见` · 2025-06-19~22 | 独立董事专门会议审核意见 |
| `independent_director_nominee_declaration_known_001` | （新增）→ **ready** | BD2E264 伟星股份 002003 · ann=1223973877 · 2025-06-24 | `独立董事提名人声明与承诺（张永炬）` · 2025-06-23~26 | 提名人声明（姓名消歧） |

路由：含「独立董事专门会议的审核意见」或「独立董事提名人声明与承诺」→ `announcement` / `cninfo_general_announcement_pdf`（**非** `other` / `annual_report`）。

## 4. 明确不重开

| case_id / 族 | 说明 |
|--------------|------|
| `legal_opinion_known_001`–`006` | LIVE_PASS（勿重开） |
| `continuous_supervision_annual_known_001` / `training_known_001` | LIVE_PASS（勿重开） |
| `bond_trustee_report_known_001` / `tracking_rating_report_known_001` | LIVE_PASS（勿重开） |
| `listing_sponsor_known_001` / `equity_change_report_known_001` | LIVE_PASS（勿重开） |
| `verification_opinion_known_001`–`002` | LIVE_PASS（勿重开） |
| `supervisory_board_known_001`–`002` | LIVE_PASS（勿重开） |
| `shareholder_meeting_known_001`–`007` | LIVE_PASS（勿重开） |
| `board_resolution_known_001` | LIVE_PASS（勿重开） |
| `nonstandard_audit_opinion_known_001` / `raised_funds_usage_report_known_001` | LIVE_PASS（B-FM-32；勿重开） |

## 5. Allow-list

仅 `independent_director_meeting_review_known_001` + `independent_director_nominee_declaration_known_001`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。  
ready_for_commit 文件清单不含 console / terminal 日志。

## 6. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_category_routing_ind_director_governance_edge.py` | **7 OK** |
| `python lab/test_cninfo_b_class_ind_director_governance_known_001_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_ind_director_governance_known_001_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_category_routing_nonstandard_audit_raised_funds_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_continuous_supervision_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_legal_opinion_non_meeting_edge.py` | **10 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_bond_trustee_rating_edge.py` | **5 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py` | ready=**50** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=50 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live（消歧后） | **LIVE_PASS** · pass=**2**/0/0 |

## 7. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计） | **8**（含首轮 PARTIAL 消歧重试） |
| wall（成功 live） | **~27.8 s** |
| allow-list | `independent_director_meeting_review_known_001`, `independent_director_nominee_declaration_known_001` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `independent_director_meeting_review_known_001` | 金枫酒业2025年第二次独立董事专门会议的审核意见 | 2025-06-20 | classified_correctly / announcement | **pass** |
| `independent_director_nominee_declaration_known_001` | 独立董事提名人声明与承诺（张永炬） | 2025-06-24 | classified_correctly / announcement | **pass** |

执行要点：

1. 首轮 nominee **ambiguous**（同窗 3 条提名人声明）；收窄 pattern 含「（张永炬）」后重试即 **LIVE_PASS**。
2. 无 orgId fallback；无 PDF。
3. predicted_type=`announcement`；与章程/制度/薪酬 other、真·年报审核意见（BD2E501 periodic）可区分。
4. 裸「审核意见」仍落 other（锁测覆盖）。

## 8. 能力增益

- 独立董事专门会议审核意见 / 提名人声明与承诺进入 **known-document ready** 并经公司窗 live metadata 确认
- 闭合 B-FM-32 推迟的 BD2E426 边角；remaining other 21→**19**（章程/制度/薪酬/名单/简报/资产评估等低价值边角）
- ready 计数 48 → **50**

## 9. Gate 摘要

```text
b_class_ind_director_governance_known_001_promotion_live_gate = LIVE_PASS
task_id = B-FM-33
cninfo_calls_success_live = 4
cninfo_calls_task_total = 8
pdf_downloads = 0
ready_for_commit = true
commit = not_done
push = not_done
```

## 10. 受保护 / 隔离

- 未触碰 A/C/D 线文件（本包修改仅 B 线；工作区另有他线脏文件与本包无关）
- 未 mutate 既有 LIVE_PASS live 根（含 B-FM-32 nonstandard_audit / raised_funds）
- 未 PDF / OCR / DB / MinIO / RAG
- 未 commit / push

## 11. 文件清单（ready_for_commit；不含 console 日志）

| 路径 | 角色 |
|------|------|
| `config/cninfo_announcement_categories.yaml` | +独立董事专门会议审核意见 / 提名人声明 |
| `lab/validate_cninfo_b_class_category_routing.py` | `_general_document_type` 早退 |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表更新 |
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +meeting_review / nominee_declaration known_001 |
| `lab/test_cninfo_b_class_category_routing_ind_director_governance_edge.py` | routing 边角锁测 |
| `lab/test_cninfo_b_class_ind_director_governance_known_001_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_ind_director_governance_known_001_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_*` | ready 刷新（50） |
| `outputs/validation/cninfo_b_class_ind_director_governance_known_001_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_ind_director_governance_known_001_live_20260715/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_ind_director_governance_known_001_promotion_live_20260715.md` | 本报告 |

## 12. 返回包

| 项 | 值 |
|----|-----|
| task | B-FM-33 独立董事专门会议审核意见/提名人声明 known_001 晋升 + bounded live（BD2E426/264） |
| files | routing harden + fixture + 3 tests + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | routing **7 OK** · promotion **7 OK** · live mock **3 OK** · nonstandard/continuous/legal/bond 不回退 · ready **50** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | 成功 live **4**；本任务合计 **8**（含消歧重试；PDF=0） |
| allow-list | `independent_director_meeting_review_known_001`, `independent_director_nominee_declaration_known_001` |
| wall | 成功 live **~27.8 s** |
| ready_for_commit | **true** |

## 13. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 剩余 other ~19 多为章程/制度/薪酬方案/激励名单/简报/资产评估说明等低价值边角，可按需抽样而非硬推。
3. 可选：BD2E430「资产评估说明」若要硬化，需窄 pattern（避免泛化「说明」）。
4. `periodic_guard_001`（延期披露）仍缺 harvest，不宜硬推。
5. 真·监管问询函原文仍缺 harvest，不宜硬推 `regulatory_known_003`。
