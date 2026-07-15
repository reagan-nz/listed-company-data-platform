# CNINFO B 类 B-FM-25 — 「法律意见书」Known-001/002 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-25  
> **性质：** harvest 晋升 + allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 supervisory_board_known_001–002 / shareholder_meeting_known_001–007 / board_resolution_known_001  
> **不**触碰 A/C/D · **不** commit / push · **不** PDF / OCR / DB / RAG  
> standing_scope 允许 CNINFO live；本包新晋 `legal_opinion_known_001` + `legal_opinion_known_002`（闭合 B-FM-24 指出的「法律意见书保持 announcement」边角）

## 1. 候选决策

| # | 类型 | 候选 | 决策 |
|---|------|------|------|
| 1 | harvest promotion | BD2E544 → legal_opinion_known_001（股东大会的法律意见书） | **执行** — 主路径（完整「股东大会」+ 法律意见书） |
| 2 | harvest promotion | BD2E416 → legal_opinion_known_002（股东会的法律意见书） | **执行** — 同包第二边角（简称「股东会」对称） |
| 3 | category-sample | 短标题「监事会决议公告」全市场窗 | **拒绝** — harvest 仍无连续「监事会决议公告」子串 |
| 4 | harvest promotion | board_resolution / supervisory_board 再 live | **拒绝** — 已 LIVE_PASS；非新能力 |
| 5 | alternate | periodic_guard_001（延期披露） | **拒绝** — harvest 仍缺 |
| 6 | alternate | regulatory_known_003（真·问询函原文） | **拒绝** — harvest 仍缺 |

**价值判断：** 股东会 known_001–007 与监事会 known_001–002 已闭合；B-FM-18/20 路由锁测已要求法律意见书保持 `announcement`，但缺独立 known-document + live 锚点。harvest 充足（BD2E544/416）。高于再 live 已闭合包 / 硬推延期披露。

## 2. 晋升内容

| case_id | 状态 | harvest | title_pattern | 窗 |
|---------|------|---------|---------------|-----|
| `legal_opinion_known_001` | （新增）→ **ready** | BD2E544 永兴材料 002756 · ann=1223733432 · 2025-06-02 | `第一次临时股东大会的法律意见书` · 2025-06-01~04 | 股东大会法律意见书 |
| `legal_opinion_known_002` | （新增）→ **ready** | BD2E416 金自天正 600560 · ann=1223998801 · 2025-06-26 | `年度股东会的法律意见书` · 2025-06-25~28 | 股东会法律意见书（简称） |

路由（依赖既有 B-FM-18/20 排除逻辑）：含股东（大）会但为法律意见书 → `announcement` / `cninfo_general_announcement_pdf`（**非** `shareholder_meeting_material`）。本包**未**改共享 validator / routing 代码。

## 3. 明确不重开

| case_id / 族 | 说明 |
|--------------|------|
| `supervisory_board_known_001`–`002` | LIVE_PASS（勿重开） |
| `shareholder_meeting_known_001`–`007` | LIVE_PASS（勿重开） |
| `board_resolution_known_001` | 已有 LIVE_PASS（勿重开） |
| `meeting_sample_002` | LIVE_PASS（勿重开） |

## 4. Allow-list

仅 `legal_opinion_known_001` + `legal_opinion_known_002`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。

## 5. 测试

| 命令 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_legal_opinion_known_001_002_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_legal_opinion_known_001_002_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_supervisory_board_known_002_promotion.py` | **6 OK**（不回退） |
| `python lab/test_cninfo_b_class_supervisory_board_known_001_promotion.py` | **6 OK**（不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_007_promotion.py` | **6 OK**（不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_005_006_promotion.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_shareholder_meeting_short_form_edge.py` | **10 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_shareholder_meeting_resolution_edge.py` | **9 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py` | ready=**34** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=34 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=2 · would_query=true |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

## 6. Live 证据

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO | **4**（2×(topSearch+query)；PDF=0） |
| wall | **~23.1 s** |
| allow-list | `legal_opinion_known_001`, `legal_opinion_known_002` |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `legal_opinion_known_001` | 2025年第一次临时股东大会的法律意见书 | 2025-06-02 | classified_correctly / announcement | **pass** |
| `legal_opinion_known_002` | …2024年年度股东会的法律意见书 | 2025-06-26 | classified_correctly / announcement | **pass** |

执行要点：

1. 首跑即 LIVE_PASS；无网络失败试跑；无 orgId fallback。
2. 未修改共享 validator / routing 代码（法律意见书排除已由 B-FM-18/20 覆盖）。
3. predicted_type=`announcement`；与股东会 `shareholder_meeting_material`、监事会决议、董事会决议均可区分。

## 7. 能力增益

- 「股东大会/股东会 + 法律意见书」进入 **known-document ready** 并经公司窗 live metadata 确认（known_001/002）
- 闭合 B-FM-24 推迟的法律意见书边角；与股东会材料主类形成显式负例锚点
- ready 计数 32 → **34**

## 8. Gate 摘要

```text
b_class_legal_opinion_known_001_002_promotion_live_gate = LIVE_PASS
task_id = B-FM-25
cninfo_calls = 4
pdf_downloads = 0
allow_list = legal_opinion_known_001,legal_opinion_known_002
ready_for_commit = true
commit = not_done
push = not_done
```

## 9. 文件

| 路径 | 说明 |
|------|------|
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +legal_opinion_known_001/002 |
| `lab/test_cninfo_b_class_legal_opinion_known_001_002_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_legal_opinion_known_001_002_live.py` | allow-list + mock live 锁测 |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_*` | selector 刷新 ready=34 |
| `outputs/validation/cninfo_b_class_legal_opinion_known_001_002_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_legal_opinion_known_001_002_live_20260715/` | allow-list + live 证据包 |
| `outputs/validation/cninfo_b_class_legal_opinion_known_001_002_promotion_live_20260715.md` | 本报告 |

## 10. 回报卡

| 项 | 值 |
|----|-----|
| task | B-FM-25 「法律意见书」known_001/002 晋升 + bounded live（BD2E544/416） |
| files | fixture + 2 tests + ready 刷新 + dry-run + live 包 + 本报告 |
| tests | promotion **7 OK** · live mock **3 OK** · supervisory/shareholder/short-form/resolution 不回退 · ready **34** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | **4**（PDF=0） |
| allow-list | `legal_opinion_known_001`, `legal_opinion_known_002` |
| wall | live **~23.1 s** |
| ready_for_commit | **true** |

## 11. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选下一边角：非会议类法律意见书（如增持法律意见书，当前可能落 `other`）routing 硬化，或其它未覆盖 event（异常波动 / 业绩预告 category-sample）。
3. `periodic_guard_001`（延期披露）仍缺 harvest，不宜硬推。
4. 真·监管问询函原文仍缺 harvest，不宜硬推 `regulatory_known_003`。
5. 监事会短标题 category-sample 仍缺「监事会决议公告」连续子串 harvest。
