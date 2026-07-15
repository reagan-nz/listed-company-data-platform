# CNINFO B 类 B-FM-22 — 「年度股东会决议」Known-007 晋升 + Bounded Live

_生成时间：2026-07-15 · promote → dry-run → bounded live · **CNINFO = 2** · **无 PDF** · **无 commit** · **无 push**_

> **性质：** harvest 晋升 + allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 known_001–006（已 LIVE_PASS）· **不**触碰 A/C/D  
> standing_scope 允许 CNINFO live；本包仅新晋 `shareholder_meeting_known_007`（闭合 B-FM-21 推迟的 BD2E258）

---

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | harvest promotion | BD2E258 → shareholder_meeting_known_007（年度股东会决议） | **执行** — 主路径（B-FM-21 明确推迟项；闭合 B-FM-20 三锚点） |
| 2 | harvest promotion | 监事会决议 known（如 BD2E091） | **推迟** — 路由已有 general_006；低于闭合简称决议矩阵 |
| 3 | routing edges | 新 document_type | **拒绝** — B-FM-20 已覆盖简称「股东会」；无新 route 阻塞 |
| 4 | bounded live | known_001–006 再跑 | **拒绝** — 已 LIVE_PASS；capability_gain=0 |
| 5 | alternate | periodic_guard_001（延期披露） | **拒绝** — harvest 仍缺 |

**价值判断：** BD2E258 与 known_005 同属简称决议族，但 title_pattern `年度股东会决议` 与 `临时股东会决议` 互斥；晋升补齐年度简称边角，并闭合 B-FM-20 三 harvest 锚点（646/276/258）。高于另开监事会 / 法律意见书新族。

---

## 2. Promotion

| case_id | 状态 | harvest | title_pattern | 窗 |
|---------|------|---------|---------------|-----|
| `shareholder_meeting_known_007` | （新增）→ **ready** | BD2E258 信凯科技 001335 · ann=1223981729 · 2025-06-25 | `年度股东会决议` · 2025-06-24~27 | 简称年度决议 |

路由（依赖 B-FM-20）：「股东会」=「股东大会」同义 → `shareholder_meeting_material` / `cninfo_general_announcement_pdf`。

### 既有锚点（不重开）

| case_id | pattern | 公司 | LIVE |
|---------|---------|------|------|
| `shareholder_meeting_known_001` | `股东大会通知` | 航天智造 300446 | PASS |
| `shareholder_meeting_known_002` | `股东大会的通知` | 恒邦股份 002237 | PASS |
| `shareholder_meeting_known_003` | `股东大会决议` | 迈克生物 300463 | PASS |
| `shareholder_meeting_known_004` | `股东大会的公告` | 中信特钢 000708 | PASS |
| `shareholder_meeting_known_005` | `临时股东会决议` | 康平科技 300907 | PASS |
| `shareholder_meeting_known_006` | `股东会的通知` | 孚日股份 002083 | PASS |

---

## 3. Allow-list

仅 `shareholder_meeting_known_007`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。

---

## 4. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_shareholder_meeting_known_007_promotion.py` | **6 OK** |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_007_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_005_006_promotion.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_005_006_live.py` | **3 OK**（不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_003_004_promotion.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_003_004_live.py` | **3 OK**（不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_002_promotion.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_sample_promotion.py` | **6 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_shareholder_meeting_short_form_edge.py` | **10 OK**（B-FM-20 不回退） |
| `python lab/test_cninfo_b_class_category_routing_shareholder_meeting_resolution_edge.py` | **9 OK**（B-FM-18 不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | **PASS** · ready=**30** · invalid_ready=0 · placeholder=2 |
| fixture dry-run | **DRY_RUN_PASS** · ready=**30** · query=0 |
| allow-list dry-run | **DRY_RUN_PASS** · ready=**1** · query=0 |
| bounded live | **LIVE_PASS** · pass=**1**/0/0 |

### Live 细节

| 项 | 值 |
|----|-----|
| allow-list | `shareholder_meeting_known_007` |
| CNINFO | **2**（1 topSearch + 1 query；无 PDF） |
| wall | **~19.2 s** |
| PDF | **0** |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `shareholder_meeting_known_007` | 2024年年度股东会决议公告 | 2025-06-25 | classified_correctly / shareholder_meeting_material | **pass** |

### 运行备注（显式，非静默）

1. 首跑即 LIVE_PASS；无网络失败试跑；无 orgId fallback。
2. **未**修改共享 `validate_cninfo_b_class_corpus_retrieval.py`；默认 timeout 即可。
3. predicted_type=`shareholder_meeting_material`；route=`cninfo_general_announcement_pdf`（与 B-FM-20 对齐）。

---

## 5. Capability Gain

- 「年度股东会决议」进入 **known-document ready** 并经公司窗 live metadata 确认（known_007）
- 闭合 B-FM-20 route 三锚点（BD2E646 / BD2E276 / BD2E258）→ promote → live 链路
- 与 known_005「临时股东会决议」及 known_003 完整「股东大会决议」pattern 可区分
- **不**声称 B complete / verified / full-market %

---

## 6. Gate

```text
b_class_shareholder_meeting_known_007_promotion_live_gate = LIVE_PASS
task_id = B-FM-22
cninfo_calls_this_package = 2
live_calls_this_package = 1
pdf_download = 0
allow_list = shareholder_meeting_known_007
fake_section7_fp = no
ready_for_commit = true
```

---

## 7. 产物

| 路径 | 用途 |
|------|------|
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | 新晋 known_007 |
| `lab/test_cninfo_b_class_shareholder_meeting_known_007_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_shareholder_meeting_known_007_live.py` | allow-list + mock live 锁测 |
| `outputs/validation/cninfo_b_class_shareholder_meeting_known_007_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_shareholder_meeting_known_007_live_20260715/` | allow-list + live 证据包 |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_{report.csv,summary.md}` | selector 刷新 ready=30 |
| 本文件 | 任务报告 |

---

## 8. Return Block

| 字段 | 值 |
|------|-----|
| task | B-FM-22 「年度股东会决议」known_007 晋升 + bounded live（BD2E258） |
| files | known fixture · promotion/live 锁测 · allow-list · dry-run/live 证据 · selector 刷新 · 本报告 |
| tests | promotion **6 OK** · live mock **3 OK** · known_002/003/004/005/006/sample/short-form/resolution 不回退 · ready **30** · dry-run **PASS** · live **1/1 LIVE_PASS** |
| CNINFO | **2** |
| allow-list | `shareholder_meeting_known_007` |
| wall | live **~19.2 s** |
| ready_for_commit | **true** |

---

## 9. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选下一边角：监事会决议 known-document（路由已通；需独立 pattern 矩阵），或其它未覆盖 event category。
3. `periodic_guard_001`（延期披露）仍缺 harvest，不宜硬推。
4. 真·监管问询函原文仍缺 harvest，不宜硬推 `regulatory_known_003`。
