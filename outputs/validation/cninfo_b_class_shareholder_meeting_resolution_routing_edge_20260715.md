# CNINFO B 类 B-FM-18 — 股东大会决议 / 召开公告 Routing Edge Hardening

_生成时间：2026-07-15 · offline only · **CNINFO = 0** · **无 live** · **无 commit** · **无 push**_

> **性质：** title routing document_type 边角硬化 · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**晋升 known-document / category-sample · **不**触碰 A/C/D  
> standing_scope 允许 bounded live，但本包优先解除 shareholder_meeting 族 document_type 阻塞（同 B-FM-07/11 模式）

---

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | routing edges | BD2E578「股东大会决议」/ BD2E080「召开…股东大会的公告」落 announcement | **执行** — 主路径（高于再造 通知 category-sample） |
| 2 | harvest promotion | meeting_sample_003（股东大会的通知窗） | **推迟** — known_002 已 LIVE_PASS；增量低于决议边角解锁 |
| 3 | harvest promotion | BD2E578 → shareholder_meeting_known_003 | **推迟** — 本包先清 route；晋升留给后续 |
| 4 | bounded live | 既有 LIVE_PASS 再跑 | **拒绝** — capability_gain=0；不重开 closed LIVE_PASS |
| 5 | alternate | periodic_guard_001 / regulatory_known_003 | **拒绝** — harvest 仍缺延期披露 / 真·问询函原文 |

---

## 2. Gap

| 项 | 说明 |
|----|------|
| gap_id | `GAP-B-SHAREHOLDER-MEETING-RESOLUTION` |
| 来源 | B-FM-17 后诚实扫描：大量未占用 harvest「股东大会决议公告」与「关于召开…股东大会的公告」（无「通知」）旧 `_general_document_type` 一律 `announcement` |
| 证据 | BD2E578 迈克生物 300463「2025年第二次临时股东大会决议公告」（ann=1224015259，2025-06-27）；BD2E080 中信特钢 000708「关于召开2025年第二次临时股东大会的公告」（ann=1223998647，2025-06-26）；另有 10+ 同构决议行 |
| 影响 | 无法按 `shareholder_meeting_material` 安全晋升 known/sample；与 retrieval strategy `股东大会决议` must_any 不对齐 |
| 明确不改 | 「股东大会通知 / 的通知」既有路径；董事会决议 → `board_resolution`；法律意见书 / 会议材料仍为 `announcement`；说明会 → `meeting_notice` |

---

## 3. Fix（最小）

| 文件 | 变更 |
|------|------|
| `lab/validate_cninfo_b_class_category_routing.py` | `_general_document_type`：股东大会+决议；召开+股东大会（排除法律意见/会议材料/会议资料）→ `shareholder_meeting_material` |
| `config/cninfo_announcement_categories.yaml` | general_announcement notes 登记 B-FM-18 边角 |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表 + §6 example 9b/9c |
| `lab/test_cninfo_b_class_category_routing_shareholder_meeting_resolution_edge.py` | 9 项边角单测 |

未改：known-document / category-sample fixture · 共享 corpus retrieval validator · §7 FP · A/C/D · live · commit/push。

---

## 4. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_category_routing_shareholder_meeting_resolution_edge.py` | **9 OK** |
| `python lab/test_cninfo_b_class_category_routing_warning_letter_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_inquiry_reply_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_ir_activity_edge.py` | **8 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_regulatory_work_letter_edge.py` | **9 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_preview_fp.py` | **9 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_wrong_company_fp.py` | **9 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_wrong_period_fp.py` | **10 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_unrelated_announcement_fp.py` | **10 OK**（不回退） |
| `python lab/validate_cninfo_b_class_category_routing.py` | **38/38 PASS** · fail=0 |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_002_promotion.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_002_live.py` | **3 OK**（不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_sample_promotion.py` | **6 OK**（不回退） |
| CNINFO calls | **0** |
| live | **none** |
| allow-list | **无**（未开启 live） |

---

## 5. Capability Gain

- 「…股东大会决议公告」稳定预测 `shareholder_meeting_material` / `cninfo_general_announcement_pdf`
- 「关于召开…股东大会的公告」（无「通知」）预测 `shareholder_meeting_material`
- 法律意见书 / 会议材料仍为 `announcement`
- 股东大会通知 / 「的」助词变体 / 董事会决议 / 说明会路径不回退
- 为后续将 BD2E578 / BD2E080 类样本晋升 known/sample 清除 route 障碍
- **不**声称 B complete / verified / full-market %

---

## 6. Gate

```text
b_class_shareholder_meeting_resolution_routing_edge_gate = PASS_OFFLINE
task_id = B-FM-18
cninfo_calls_this_package = 0
live_calls_this_package = 0
pdf_download = 0
allow_list = none
fake_section7_fp = no
ready_for_commit = true
```

---

## 7. 产物

| 路径 | 用途 |
|------|------|
| `lab/validate_cninfo_b_class_category_routing.py` | `_general_document_type` 边角 |
| `lab/test_cninfo_b_class_category_routing_shareholder_meeting_resolution_edge.py` | 边角单测 |
| `config/cninfo_announcement_categories.yaml` | notes |
| `plans/cninfo_b_class_category_routing_rules.md` | 规则表 + example 9b/9c |
| `outputs/validation/cninfo_b_class_category_routing_{report.csv,summary.md}` | benchmark 刷新（38/38） |
| 本文件 | 任务报告 |

---

## 8. Return Block

| 字段 | 值 |
|------|-----|
| task | B-FM-18 股东大会决议 / 召开公告 routing-edge hardening（offline；BD2E578 / BD2E080） |
| files | routing validator · edge 单测 · categories notes · routing rules · category_routing 报告 · 本报告 |
| tests | edge **9 OK** · 既有 routing/FP/shareholder 锁测不回退 · benchmark **38/38** |
| CNINFO | **0** |
| allow-list | **none** |
| wall | offline unit + benchmark only |
| ready_for_commit | **true** |

---

## 9. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选晋升：BD2E578 → `shareholder_meeting_known_003`（决议）和/或 BD2E080 → known/sample（召开公告无「通知」）；依赖本包 route。
3. `periodic_guard_001`（延期披露）仍缺 harvest，不宜硬推。
4. 真·监管问询函原文仍缺 harvest，不宜硬推 `regulatory_known_003`。
