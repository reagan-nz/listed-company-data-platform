# CNINFO B 类 B-FM-31 — 可转债 / 激励行权法律意见书 Known-005/006 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-31  
> **性质：** harvest 晋升 + allow-list live metadata（路由已通；无新 routing harden）· **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 continuous_supervision / bond_trustee / tracking_rating / listing_sponsor / equity_change / verification_opinion / legal_opinion_known_001–004 / supervisory_board / shareholder_meeting known LIVE_PASS  
> **不**触碰 A/C/D · **不** commit / push · **不** PDF / OCR / DB / RAG  
> standing_scope 允许 CNINFO live；本包闭合 B-FM-30 之后最高价值 known-doc：可转债法律意见书（BD2E472）+ 激励行权价格调整法律意见书（BD2E168）

## 1. 候选决策

| # | 类型 | 候选 | 决策 |
|---|------|------|------|
| 1 | harvest promotion | BD2E472 → legal_opinion_known_005（可转债法律意见书） | **执行** — B-FM-30 明确下一边角；路由已通 |
| 2 | harvest promotion | BD2E168 → legal_opinion_known_006（激励行权价格调整法律意见书） | **执行** — 同包非会议法律意见第二锚点 |
| 3 | remaining other | 章程/制度/薪酬/激励名单等 ~23 | **推迟** — 低价值边角，不硬推 routing |
| 4 | alternate | periodic_guard_001 / regulatory_known_003 | **拒绝** — harvest 仍缺 |
| 5 | alternate | BD2E366 非标审计意见消除专项说明 | **推迟** — 仍落 other，但「专项说明」泛化风险高，不宜本包硬扩 |

**价值判断：** 剩余 other ~23 均为章程/制度/薪酬/激励名单/销售简报等低价值边角。B-FM-26 已通「法律意见书」→ announcement；最高价值是补齐可转债法律意见书 known live 锚点（B-FM-30 推迟项），并以激励行权价格调整法律意见书作对称第二案。

## 2. Routing 变更

无。沿用 B-FM-26 `_general_document_type` 对「法律意见书」早退 + 既有 config。  
仅扩展 `test_cninfo_b_class_category_routing_legal_opinion_non_meeting_edge.py` 锁测 BD2E168。

## 3. 晋升内容

| case_id | 状态 | harvest | title_pattern | 窗 |
|---------|------|---------|---------------|-----|
| `legal_opinion_known_005` | （新增）→ **ready** | BD2E472 天准科技 688003 · ann=1223956527 · 2025-06-23 | `可转换公司债券的法律意见书` · 2025-06-22~25 | 可转债法律意见书 |
| `legal_opinion_known_006` | （新增）→ **ready** | BD2E168 恒生电子 600570 · ann=1223877213 · 2025-06-13 | `调整2024年股票期权激励计划行权价格的法律意见书` · 2025-06-12~15 | 激励行权价格调整法律意见书 |

路由：含「法律意见书」→ `announcement` / `cninfo_general_announcement_pdf`（**非** `other` / `shareholder_meeting_material`）。

## 4. 明确不重开

| case_id / 族 | 说明 |
|--------------|------|
| `continuous_supervision_annual_known_001` / `training_known_001` | LIVE_PASS（B-FM-30；勿重开） |
| `bond_trustee_report_known_001` / `tracking_rating_report_known_001` | LIVE_PASS（勿重开） |
| `listing_sponsor_known_001` / `equity_change_report_known_001` | LIVE_PASS（勿重开） |
| `verification_opinion_known_001`–`002` | LIVE_PASS（勿重开） |
| `legal_opinion_known_001`–`004` | LIVE_PASS（勿重开） |
| `supervisory_board_known_001`–`002` | LIVE_PASS（勿重开） |
| `shareholder_meeting_known_001`–`007` | LIVE_PASS（勿重开） |
| `board_resolution_known_001` | LIVE_PASS（勿重开） |

## 5. Allow-list

仅 `legal_opinion_known_005` + `legal_opinion_known_006`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。  
ready_for_commit 文件清单不含 console / terminal 日志。

## 6. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_category_routing_legal_opinion_non_meeting_edge.py` | **10 OK** |
| `python lab/test_cninfo_b_class_legal_opinion_known_005_006_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_legal_opinion_known_005_006_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_category_routing_continuous_supervision_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_bond_trustee_rating_edge.py` | **5 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py` | ready=**46** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=46 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live（消歧后） | **LIVE_PASS** · pass=**2**/0/0 |

## 7. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO（成功跑） | **4**（2×(topSearch+query)；PDF=0） |
| CNINFO（含首跑 PARTIAL） | **8** |
| wall（成功跑） | **~30.4 s** |
| allow-list | `legal_opinion_known_005`, `legal_opinion_known_006` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `legal_opinion_known_005` | …向不特定对象发行可转换公司债券的法律意见书 | 2025-06-23 | classified_correctly / announcement | **pass** |
| `legal_opinion_known_006` | …调整2024年股票期权激励计划行权价格的法律意见书 | 2025-06-13 | classified_correctly / announcement | **pass** |

执行要点：

1. 首跑 known_005 pass；known_006 短 pattern 同窗 3 命中 → ambiguous（PARTIAL）。
2. 收紧 known_006 pattern 为「调整2024年股票期权激励计划行权价格的法律意见书」后复跑 **LIVE_PASS**。
3. 无 orgId fallback；无 PDF。
4. predicted_type=`announcement`；与保荐书 / 受托管理 / 会议法律意见 / other 可区分。

## 8. 能力增益

- 可转债法律意见书 / 激励行权价格调整法律意见书进入 **known-document ready** 并经公司窗 live metadata 确认
- 闭合 B-FM-30 推迟的可转债法律意见书 known 扩展；remaining other 仍约 23（章程/制度/薪酬等低价值边角）
- ready 计数 44 → **46**

## 9. Gate 摘要

```text
b_class_legal_opinion_known_005_006_promotion_live_gate = LIVE_PASS
task_id = B-FM-31
cninfo_calls = 8  # 含首跑 PARTIAL；成功跑 = 4
pdf_downloads = 0
ready_for_commit = true
commit = not_done
push = not_done
```

## 10. 受保护 / 隔离

- 未触碰 A/C/D 线文件（本包修改仅 B 线）
- 未 mutate 既有 LIVE_PASS live 根（continuous_supervision / bond_trustee / tracking_rating / listing_sponsor / equity_change / verification / legal_001–004 / supervisory / shareholder）
- 未 PDF / OCR / DB / MinIO / RAG
- 未 commit / push

## 11. 文件清单（ready_for_commit；不含 console 日志）

| 路径 | 角色 |
|------|------|
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +legal_opinion known_005 / known_006 |
| `lab/test_cninfo_b_class_category_routing_legal_opinion_non_meeting_edge.py` | +BD2E168 锁测 |
| `lab/test_cninfo_b_class_legal_opinion_known_005_006_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_legal_opinion_known_005_006_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_*` | ready 刷新（46） |
| `outputs/validation/cninfo_b_class_legal_opinion_known_005_006_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_legal_opinion_known_005_006_live_20260715/` | live 包（不含 console） |
| `outputs/validation/cninfo_b_class_legal_opinion_known_005_006_promotion_live_20260715.md` | 本报告 |

## 12. 返回包

| 项 | 值 |
|----|-----|
| task | B-FM-31 可转债/激励行权法律意见书 known_005/006 晋升 + bounded live（BD2E472/168） |
| files | fixture + routing edge 锁测 + 2 tests + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | routing **10 OK** · promotion **7 OK** · live mock **3 OK** · continuous_supervision/bond_trustee 不回退 · ready **46** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | **8**（含首跑 PARTIAL；成功跑 **4**；PDF=0） |
| allow-list | `legal_opinion_known_005`, `legal_opinion_known_006` |
| wall | live 成功跑 **~30.4 s** |
| ready_for_commit | **true** |

## 13. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 剩余 other ~23 多为章程/制度/薪酬方案/激励名单等低价值边角，可按需抽样而非硬推。
3. 可选：BD2E366「非标准审计意见…专项说明」若要硬化，需窄 pattern（避免泛化「专项说明」）。
4. `periodic_guard_001`（延期披露）仍缺 harvest，不宜硬推。
5. 真·监管问询函原文仍缺 harvest，不宜硬推 `regulatory_known_003`。
