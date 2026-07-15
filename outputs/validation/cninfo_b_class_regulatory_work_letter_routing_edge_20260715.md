# CNINFO B 类 B-FM-11 — 监管工作函（Regulatory Work Letter）Routing Edge Hardening

_生成时间：2026-07-15 · offline only · **CNINFO = 0** · **无 live** · **无 commit** · **无 push**_

> **性质：** title routing document_type 边角硬化 · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**晋升 known-document / category-sample · **不**触碰 A/C/D  
> standing_scope 允许 bounded live，但本包优先解除 periodic 误路由阻塞（同 B-FM-07 模式）

---

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | routing edges | BD2E433「监管工作函的专项说明」误进 annual_report | **执行** — 主路径 |
| 2 | harvest promotion | meeting_sample_002（股东大会通知） | **推迟** — 无 route 阻塞；本包先清工作函边角 |
| 3 | bounded live | 既有 ready 再跑 metadata | **推迟** — capability_gain=0；新晋 case 尚未形成 |
| 4 | retrieval tooling | selector / dry-run 增强 | **推迟** — 低于 routing 阻塞解除 |
| 5 | fake §7 FP | 新造 FP lineage | **拒绝** — 禁止 |

---

## 2. Gap

| 项 | 说明 |
|----|------|
| gap_id | `GAP-B-REGULATORY-WORK-LETTER` |
| 来源 | B-FM-10 后诚实扫描：BD2E433 CPA「监管工作函的专项说明」含「年度报告」子串，旧路由 Priority 3 → `annual_report` / `cninfo_periodic_report_pdf` |
| 证据 | BD2E433 文投控股 600715「中兴财光华…2024年年度报告的信息披露监管工作函的专项说明」（ann=1223358761，2025-04-28，quality=pass；slice1 report） |
| 影响 | 监管/中介工作函类标题被当成年报全文；无法安全晋升 inquiry 边角样本 |
| 明确不改 | 「警示函/关注函/问询函的回复」既有路径；BD2E500「延期回复…问询函」仍为 `regulatory_inquiry`；裸「专项说明」（非工作函）不强制进 inquiry |

---

## 3. Fix（最小）

| 文件 | 变更 |
|------|------|
| `config/cninfo_announcement_categories.yaml` | `inquiry_reply.positive_patterns` 与 periodic `exclusion_patterns` 增补：`监管工作函` |
| `config/cninfo_b_class_source_registry_draft.yaml` | 同步 inquiry patterns + shared / periodic exclusion |
| `lab/validate_cninfo_b_class_category_routing.py` | `_inquiry_document_type`：`监管工作函的专项说明` / `监管工作函的回复` → inquiry_reply；裸/收到「监管工作函」→ regulatory_inquiry |
| `lab/test_cninfo_b_class_category_routing_regulatory_work_letter_edge.py` | 9 项边角单测 |

未改：known-document / category-sample fixture · §7 FP · A/C/D · live · commit/push。

---

## 4. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_category_routing_regulatory_work_letter_edge.py` | **9 OK** |
| `python lab/test_cninfo_b_class_category_routing_warning_letter_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_inquiry_reply_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_ir_activity_edge.py` | **8 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_preview_fp.py` | **9 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_wrong_company_fp.py` | **9 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_wrong_period_fp.py` | **10 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_unrelated_announcement_fp.py` | **10 OK**（不回退） |
| `python lab/validate_cninfo_b_class_category_routing.py` | **38/38 PASS** · fail=0 |
| CNINFO calls | **0** |
| live | **none** |
| allow-list | **无**（未开启 live） |

---

## 5. Capability Gain

- CPA「…监管工作函的专项说明」稳定预测 `inquiry_reply` / `cninfo_inquiry_reply_pdf`（不再误进年报）
- 「收到…监管工作函」预测 `regulatory_inquiry`
- 警示函 / 关注函 / CPA「问询函的回复」/ 延期回复问询函路径不回退
- 裸「专项说明」不因该词强制进 inquiry
- 为后续将 BD2E433 类样本晋升 inquiry known/sample 清除 route 障碍
- **不**声称 B complete / verified / full-market %

---

## 6. Gate

```text
b_class_regulatory_work_letter_routing_edge_gate = PASS_OFFLINE
task_id = B-FM-11
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
| `config/cninfo_announcement_categories.yaml` | 路由 patterns |
| `config/cninfo_b_class_source_registry_draft.yaml` | registry 同步 |
| `lab/validate_cninfo_b_class_category_routing.py` | `_inquiry_document_type` 边角 |
| `lab/test_cninfo_b_class_category_routing_regulatory_work_letter_edge.py` | 边角锁测 |
| `outputs/validation/cninfo_b_class_category_routing_{report.csv,summary.md}` | validator 刷新 |
| 本文件 | 任务报告 |

---

## 8. Return Block

| 字段 | 值 |
|------|-----|
| task | B-FM-11 监管工作函 routing-edge hardening（offline；BD2E433） |
| files | categories + registry + routing validator + edge test + routing report refresh + 本报告 |
| CNINFO | **0** |
| allow-list | **无** |
| wall | offline tests + validator **< 2 s** |
| ready_for_commit | **true** |

---

## 9. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选晋升：BD2E433 → inquiry known/sample（依赖本包 route）；和/或 `meeting_sample_002`（股东大会通知，route 已通）。
3. 真·监管问询函原文（「收到…问询函」且无回复）仍缺 harvest，不宜硬推 `regulatory_known_003`。
