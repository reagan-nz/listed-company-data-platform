# CNINFO B 类 B-FM-07 — Warning-Letter（警示函）Routing Edge Hardening

_生成时间：2026-07-15 · offline only · **CNINFO = 0** · **无 live** · **无 commit** · **无 push**_

> **性质：** title routing document_type 边角硬化 · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**晋升 known-document / category-sample · **不**触碰 A/C/D  
> **不**做 bounded live（`controller_execution_allowed=false`）

---

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | bounded live | B-FM-05/06 IR 新晋 metadata | **推迟** — controller_execution_allowed=false |
| 2 | routing edges | BD2E626「警示函」落入 general | **执行** — 主路径 |
| 3 | harvest promotion | regulatory_known_001/003 | **推迟** — 本包先清 route；晋升留给后续 |
| 4 | retrieval tooling | selector / dry-run 增强 | **推迟** — 低于 routing 阻塞解除 |
| 5 | alternate | 监管问询函原文 known | **拒绝** — harvest 仍无「收到…问询函」且无回复的可区分样本 |

---

## 2. Gap

| 项 | 说明 |
|----|------|
| gap_id | `GAP-B-REGULATORY-WARNING-LETTER` |
| 来源 | B-R16-03 IDLE：BD2E626 警示函路由为 `announcement` / `cninfo_general_announcement_pdf`，不能填 `regulatory_inquiry` |
| 证据 | BD2E626 壹网壹创 300792「关于收到浙江证监局警示函的公告」（ann=1223957037，2025-06-23，quality=pass） |
| 影响 | 若晋升 `regulatory_known_*` 且 expected=`regulatory_inquiry`，live 会 route 到 general |
| 明确不改 | 「警示函的回复」→ `inquiry_reply`；BD2E500「延期回复…问询函」→ 仍为 `regulatory_inquiry`；既有关注函/CPA 回复路径不回退 |

---

## 3. Fix（最小）

| 文件 | 变更 |
|------|------|
| `config/cninfo_announcement_categories.yaml` | `inquiry_reply.positive_patterns` 与 periodic `exclusion_patterns` 增补：`警示函` |
| `config/cninfo_b_class_source_registry_draft.yaml` | 同步 inquiry patterns + shared / periodic exclusion |
| `lab/validate_cninfo_b_class_category_routing.py` | `_inquiry_document_type`：`警示函` → regulatory；`警示函回复` / `警示函的回复` → inquiry_reply |
| `lab/test_cninfo_b_class_category_routing_warning_letter_edge.py` | 7 项边角单测 |

未改：known-document / category-sample fixture · §7 FP · A/C/D · live · commit/push。

---

## 4. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_category_routing_warning_letter_edge.py` | **7 OK** |
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

- 「关于收到…警示函的公告」稳定预测 `regulatory_inquiry` / `cninfo_inquiry_reply_pdf`
- 「警示函的回复」与既有关注函 / CPA「问询函的回复」路径不回退
- 「延期回复…问询函」仍为 `regulatory_inquiry`
- 为后续将 BD2E626 类样本晋升 `regulatory_known_*` 清除 route 障碍
- **不**声称 B complete / verified / full-market %

---

## 6. Gate

```text
b_class_warning_letter_routing_edge_gate = PASS_OFFLINE
task_id = B-FM-07
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
| `config/cninfo_announcement_categories.yaml` | 警示函 positive + periodic exclusion |
| `config/cninfo_b_class_source_registry_draft.yaml` | registry 同步 |
| `lab/validate_cninfo_b_class_category_routing.py` | `_inquiry_document_type` 边角 |
| `lab/test_cninfo_b_class_category_routing_warning_letter_edge.py` | 离线锁测 |
| `outputs/validation/cninfo_b_class_category_routing_{report.csv,summary.md}` | validator 刷新 |
| 本文件 | 任务报告 |

---

## 8. Return Block

| 字段 | 值 |
|------|-----|
| task | B-FM-07 警示函 routing-edge hardening（offline；BD2E626） |
| files | config categories/registry · routing helper · warning-letter edge test · routing report/summary · 本报告 |
| CNINFO | **0** |
| allow-list | **none** |
| wall | offline unit + routing validate only |
| ready_for_commit | **true** |

---

## 9. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选：用硬化后的警示函规则晋升 `regulatory_known_001`（或 003）+ category-sample 窗（dry-run）；需独立任务。
3. 可选 bounded live：IR B-FM-05/06 与/或警示函晋升后的 allow-list；需 `controller_execution_allowed` + 独立批准。
4. 真·监管问询函原文（「收到…问询函」且无回复）仍缺 harvest，不宜硬推。
