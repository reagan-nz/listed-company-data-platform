# CNINFO B 类 B-FM-32 — 非标准审计意见 / 前次募集资金使用情况报告 Known-001 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-32  
> **性质：** routing harden + harvest 晋升 + allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 continuous_supervision / bond_trustee / tracking_rating / listing_sponsor / equity_change / verification_opinion / legal_opinion_known_001–006 / supervisory_board / shareholder_meeting known LIVE_PASS  
> **不**触碰 A/C/D · **不** commit / push · **不** PDF / OCR / DB / RAG  
> standing_scope 允许 CNINFO live；本包闭合 B-FM-31 之后最高价值 remaining-other：非标准审计意见消除专项说明（BD2E366）+ 前次募集资金使用情况报告（BD2E234）

## 1. 候选决策

| # | 类型 | 候选 | 决策 |
|---|------|------|------|
| 1 | routing harden + promotion | BD2E366 → nonstandard_audit_opinion_known_001 | **执行** — B-FM-31 明确可选下一边角；「非标准审计意见」≠「非标意见」子串，旧逻辑落 other |
| 2 | routing harden + promotion | BD2E234 → raised_funds_usage_report_known_001 | **执行** — 同包 remaining-other 第二高价值中介/披露文书 |
| 3 | remaining other | 章程/制度/薪酬/激励名单/简报等 ~21 | **推迟** — 低价值边角，不硬推 routing |
| 4 | alternate | BD2E426 独立董事专门会议的审核意见 | **推迟** — 裸「审核意见」会波及 BD2E501 年报审核意见 periodic 路径 |
| 5 | alternate | periodic_guard_001 / regulatory_known_003 | **拒绝** — harvest 仍缺 |

**价值判断：** remaining other ~23 中，仅 BD2E366（非标准审计意见消除专项说明）与 BD2E234（前次募集资金使用情况报告）为清晰、可窄 pattern 硬化的中介/披露文书。既有 §7 仅覆盖短串「非标意见」；全称「非标准审计意见」不含该子串。不泛化「专项说明」，不扩「审核意见」。

## 2. Routing 变更

| 层 | 变更 |
|----|------|
| `config/cninfo_announcement_categories.yaml` | periodic exclusion + unrelated_announcement +`非标准审计意见`；general positive_patterns +`非标准审计意见` / `募集资金使用情况报告` |
| `lab/validate_cninfo_b_class_category_routing.py` | `_UNRELATED_ANNOUNCEMENT_MARKERS` +`非标准审计意见`；`_general_document_type` 早退：含「非标准审计意见」或「募集资金使用情况报告」→ `announcement` |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表增非标准审计意见 / 募集资金使用情况报告行 |

不扩 schema；不新造 document_type；不泛化「专项说明」。

## 3. 晋升内容

| case_id | 状态 | harvest | title_pattern | 窗 |
|---------|------|---------|---------------|-----|
| `nonstandard_audit_opinion_known_001` | （新增）→ **ready** | BD2E366 永鼎股份 600105 · ann=1223956135 · 2025-06-23 | `非标准审计意见审计报告所涉及事项在2024年度消除情况的专项说明` · 2025-06-22~25 | 非标准审计意见消除专项说明 |
| `raised_funds_usage_report_known_001` | （新增）→ **ready** | BD2E234 东方钽业 000962 · ann=1223958745 · 2025-06-23 | `前次募集资金使用情况报告` · 2025-06-22~25 | 前次募集资金使用情况报告 |

路由：含「非标准审计意见」或「募集资金使用情况报告」→ `announcement` / `cninfo_general_announcement_pdf`（**非** `other` / `annual_report`）。

## 4. 明确不重开

| case_id / 族 | 说明 |
|--------------|------|
| `legal_opinion_known_001`–`006` | LIVE_PASS（含 B-FM-31；勿重开） |
| `continuous_supervision_annual_known_001` / `training_known_001` | LIVE_PASS（勿重开） |
| `bond_trustee_report_known_001` / `tracking_rating_report_known_001` | LIVE_PASS（勿重开） |
| `listing_sponsor_known_001` / `equity_change_report_known_001` | LIVE_PASS（勿重开） |
| `verification_opinion_known_001`–`002` | LIVE_PASS（勿重开） |
| `supervisory_board_known_001`–`002` | LIVE_PASS（勿重开） |
| `shareholder_meeting_known_001`–`007` | LIVE_PASS（勿重开） |
| `board_resolution_known_001` | LIVE_PASS（勿重开） |

## 5. Allow-list

仅 `nonstandard_audit_opinion_known_001` + `raised_funds_usage_report_known_001`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。  
ready_for_commit 文件清单不含 console / terminal 日志。

## 6. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_category_routing_nonstandard_audit_raised_funds_edge.py` | **7 OK** |
| `python lab/test_cninfo_b_class_nonstandard_audit_raised_funds_known_001_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_nonstandard_audit_raised_funds_known_001_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_category_routing_continuous_supervision_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_legal_opinion_non_meeting_edge.py` | **10 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_bond_trustee_rating_edge.py` | **5 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py` | ready=**48** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=48 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

## 7. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO | **4**（2×(topSearch+query)；PDF=0） |
| wall | **~21.4 s** |
| allow-list | `nonstandard_audit_opinion_known_001`, `raised_funds_usage_report_known_001` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `nonstandard_audit_opinion_known_001` | …出具非标准审计意见审计报告所涉及事项在2024年度消除情况的专项说明 | 2025-06-23 | classified_correctly / announcement | **pass** |
| `raised_funds_usage_report_known_001` | 公司前次募集资金使用情况报告 | 2025-06-23 | classified_correctly / announcement | **pass** |

执行要点：

1. 单跑即 **LIVE_PASS**；无 ambiguous / PARTIAL。
2. 无 orgId fallback；无 PDF。
3. predicted_type=`announcement`；与章程/制度/薪酬 other、真·年报、监管工作函专项说明可区分。
4. 裸「专项说明」仍落 other（锁测覆盖）。

## 8. 能力增益

- 非标准审计意见消除专项说明 / 前次募集资金使用情况报告进入 **known-document ready** 并经公司窗 live metadata 确认
- 闭合 B-FM-31 推迟的 BD2E366 边角；remaining other 23→**21**（章程/制度/薪酬/名单/简报等低价值边角）
- ready 计数 46 → **48**

## 9. Gate 摘要

```text
b_class_nonstandard_audit_raised_funds_known_001_promotion_live_gate = LIVE_PASS
task_id = B-FM-32
cninfo_calls = 4
pdf_downloads = 0
ready_for_commit = true
commit = not_done
push = not_done
```

## 10. 受保护 / 隔离

- 未触碰 A/C/D 线文件（本包修改仅 B 线；工作区另有他线脏文件与本包无关）
- 未 mutate 既有 LIVE_PASS live 根（legal_001–006 / continuous_supervision / bond_trustee / tracking_rating / listing_sponsor / equity_change / verification / supervisory / shareholder）
- 未 PDF / OCR / DB / MinIO / RAG
- 未 commit / push

## 11. 文件清单（ready_for_commit；不含 console 日志）

| 路径 | 角色 |
|------|------|
| `config/cninfo_announcement_categories.yaml` | +非标准审计意见 / 募集资金使用情况报告 |
| `lab/validate_cninfo_b_class_category_routing.py` | markers + `_general_document_type` 早退 |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表更新 |
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +nonstandard_audit / raised_funds known_001 |
| `lab/test_cninfo_b_class_category_routing_nonstandard_audit_raised_funds_edge.py` | routing 边角锁测 |
| `lab/test_cninfo_b_class_nonstandard_audit_raised_funds_known_001_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_nonstandard_audit_raised_funds_known_001_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_*` | ready 刷新（48） |
| `outputs/validation/cninfo_b_class_nonstandard_audit_raised_funds_known_001_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_nonstandard_audit_raised_funds_known_001_live_20260715/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_nonstandard_audit_raised_funds_known_001_promotion_live_20260715.md` | 本报告 |

## 12. 返回包

| 项 | 值 |
|----|-----|
| task | B-FM-32 非标准审计意见/前次募集资金使用情况报告 known_001 晋升 + bounded live（BD2E366/234） |
| files | routing harden + fixture + 3 tests + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | routing **7 OK** · promotion **7 OK** · live mock **3 OK** · continuous_supervision/legal/bond_trustee 不回退 · ready **48** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | **4**（PDF=0） |
| allow-list | `nonstandard_audit_opinion_known_001`, `raised_funds_usage_report_known_001` |
| wall | live **~21.4 s** |
| ready_for_commit | **true** |

## 13. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 剩余 other ~21 多为章程/制度/薪酬方案/激励名单/简报等低价值边角，可按需抽样而非硬推。
3. 可选：BD2E426「独立董事专门会议的审核意见」若要硬化，需窄 pattern（避免波及年报「审核意见」）。
4. `periodic_guard_001`（延期披露）仍缺 harvest，不宜硬推。
5. 真·监管问询函原文仍缺 harvest，不宜硬推 `regulatory_known_003`。
