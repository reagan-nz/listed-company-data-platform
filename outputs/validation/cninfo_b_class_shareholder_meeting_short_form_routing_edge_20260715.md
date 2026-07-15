# CNINFO B 类 B-FM-20 — 「股东会」同义简称 Routing Edge Hardening

_生成时间：2026-07-15 · offline only · **CNINFO = 0** · **无 live** · **无 commit** · **无 push**_

> **性质：** title routing document_type 边角硬化 · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**晋升 known-document / category-sample · **不**触碰 A/C/D  
> **不**重开 known_003/004（已 LIVE_PASS）· standing_scope 允许 bounded live，但本包先解除简称 route 阻塞（同 B-FM-18 模式）

---

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | routing edges | BD2E646/276/258「股东会」决议/通知仍落 announcement/other | **执行** — 主路径 |
| 2 | harvest promotion | BD2E646 → shareholder_meeting_known_005 | **推迟** — 本包先清 route；晋升留给 B-FM-21 |
| 3 | bounded live | known_003/004 再跑 | **拒绝** — 已 LIVE_PASS；capability_gain=0 |
| 4 | alternate | periodic_guard_001（延期披露） | **拒绝** — harvest 仍缺 |
| 5 | alternate | regulatory_known_003（真·问询函原文） | **拒绝** — harvest 仍缺 |

---

## 2. Gap

| 项 | 说明 |
|----|------|
| gap_id | `GAP-B-SHAREHOLDER-MEETING-SHORT-FORM` |
| 来源 | B-FM-19 后诚实扫描：harvest 大量「临时/年度股东会决议」「召开…股东会的通知」因仅认「股东大会」落入 `announcement`/`other` |
| 关键点 | 「股东会」**不是**「股东大会」子串（中间有「大」），不可靠子串折叠 |
| 证据 | BD2E646 康平科技 300907「2025年第五次临时股东会决议公告」（ann=1224039628，2025-06-30）；BD2E276 孚日股份 002083「关于召开2025年第二次临时股东会的通知」（ann=1223997400，2025-06-26）；BD2E258 信凯科技 001335「2024年年度股东会决议公告」（ann=1223981729，2025-06-25） |
| 影响 | 无法按 `shareholder_meeting_material` 安全晋升简称 known/sample；与 B-FM-18 完整「股东大会」族不对齐 |
| 明确不改 | 完整「股东大会」路径（B-FM-18）；董事会决议；法律意见书 / 会议材料·资料仍为 `announcement`；known_003/004 fixture |

---

## 3. Fix（最小）

| 文件 | 变更 |
|------|------|
| `lab/validate_cninfo_b_class_category_routing.py` | 新增 `_is_shareholder_meeting_title`；`_general_document_type` / `_filter_meeting_hits` 同时认「股东大会」与「股东会」 |
| `config/cninfo_announcement_categories.yaml` | `positive_patterns` 增「股东会」；notes 登记 B-FM-20 |
| `plans/cninfo_b_class_category_routing_rules.md` | §3 表 + §4 + §6 example 9d/9e |
| `lab/test_cninfo_b_class_category_routing_shareholder_meeting_short_form_edge.py` | 10 项边角单测 |

未改：known-document / category-sample fixture · 共享 corpus retrieval validator · §7 FP · A/C/D · live · commit/push。

---

## 4. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_category_routing_shareholder_meeting_short_form_edge.py` | **10 OK** |
| `python lab/test_cninfo_b_class_category_routing_shareholder_meeting_resolution_edge.py` | **9 OK**（B-FM-18 不回退） |
| `python lab/test_cninfo_b_class_category_routing_warning_letter_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_inquiry_reply_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_ir_activity_edge.py` | **8 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_regulatory_work_letter_edge.py` | **9 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_preview_fp.py` | **9 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_wrong_company_fp.py` | **9 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_wrong_period_fp.py` | **10 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_unrelated_announcement_fp.py` | **10 OK**（不回退） |
| `python lab/validate_cninfo_b_class_category_routing.py` | **38/38 PASS** · fail=0 |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_003_004_promotion.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_002_promotion.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_sample_promotion.py` | **6 OK**（不回退） |
| CNINFO calls | **0** |
| live | **none** |
| allow-list | **无**（未开启 live） |

### 路由抽检（修复后）

| ID | title | predicted_document_type |
|----|-------|-------------------------|
| BD2E646 | 2025年第五次临时股东会决议公告 | `shareholder_meeting_material` |
| BD2E276 | 关于召开2025年第二次临时股东会的通知 | `shareholder_meeting_material` |
| BD2E258 | 2024年年度股东会决议公告 | `shareholder_meeting_material` |
| BD2E438 | …临时股东会会议资料 | `announcement`（排除保持） |
| BD2E416 | …年度股东会的法律意见书 | `announcement`（排除保持） |
| BD2E578 | …临时股东大会决议公告 | `shareholder_meeting_material`（不回退） |

---

## 5. Capability Gain

- 「临时/年度股东会决议」稳定预测 `shareholder_meeting_material` / `cninfo_general_announcement_pdf`
- 「召开…股东会的通知」预测 `shareholder_meeting_material`（不再落 `other`）
- 简称法律意见书 / 会议资料仍为 `announcement`
- 完整「股东大会」B-FM-18 路径与 known_003/004 不回退
- 为后续将 BD2E646 / BD2E276 类样本晋升 known/sample 清除 route 障碍
- **不**声称 B complete / verified / full-market %

---

## 6. Gate

```text
b_class_shareholder_meeting_short_form_routing_edge_gate = PASS_OFFLINE
task_id = B-FM-20
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
| `lab/validate_cninfo_b_class_category_routing.py` | `_is_shareholder_meeting_title` + 简称边角 |
| `config/cninfo_announcement_categories.yaml` | patterns + notes |
| `plans/cninfo_b_class_category_routing_rules.md` | 规则表 / 示例 9d/9e |
| `lab/test_cninfo_b_class_category_routing_shareholder_meeting_short_form_edge.py` | 边角锁测 |
| `outputs/validation/cninfo_b_class_category_routing_{report.csv,summary.md}` | benchmark 刷新 |
| 本文件 | 任务报告 |

---

## 8. Return Block

| 字段 | 值 |
|------|-----|
| task | B-FM-20 「股东会」同义简称 routing-edge hardening（offline；BD2E646 / BD2E276 / BD2E258） |
| files | routing helper · categories yaml · rules md · short-form edge 锁测 · routing report 刷新 · 本报告 |
| tests | short-form **10 OK** · B-FM-18 resolution **9 OK** · 其余 routing edges / FP / known_002/003/004 / sample 不回退 · validate **38/38** |
| CNINFO | **0** |
| allow-list | **none** |
| wall | offline unit + validate **~3 s** |
| ready_for_commit | **true** |

---

## 9. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. B-FM-21 候选：晋升 BD2E646 / BD2E276 → known_005/006（或合并 known+sample）并 bounded live。
3. `periodic_guard_001`（延期披露）仍缺 harvest，不宜硬推。
4. 真·监管问询函原文仍缺 harvest，不宜硬推 `regulatory_known_003`。
