# CNINFO B 类 B-FM-04 — IR Activity Routing Edge Hardening

_生成时间：2026-07-15 · offline only · **CNINFO = 0** · **无 live** · **无 commit** · **无 push**_

> **性质：** title routing document_type 边角硬化 · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**晋升 known-document / category-sample · **不**触碰 A/C/D

---

## 1. Gap

| 项 | 说明 |
|----|------|
| gap_id | `GAP-B-IR-COLLECTIVE-RECEPTION-OPEN-DAY` |
| 来源 | B-FM-03 后仍缺可区分 IR 样本；harvest 已有「集体接待日 / 投资者开放日」但旧 meeting patterns 未覆盖 |
| 证据 | BD2E202 吉林化纤 / BD2E206 永安林业「投资者网上集体接待日」；BD2E232 新乡化纤「投资者开放日」→ 旧规则落入 `cninfo_general_announcement_pdf` / `announcement` |
| 影响 | 若晋升为 `expected_document_type=investor_relations_activity` 的 known-document，live 会 route 到 general |
| 明确不改 | BD2E088「集体接待日暨…业绩说明会」→ 仍为 `meeting_notice`；「引入投资者」「面向…投资者」债券/股权类 → 仍非 meeting |

---

## 2. Fix（最小）

| 文件 | 变更 |
|------|------|
| `config/cninfo_announcement_categories.yaml` | `meeting_notice.positive_patterns` 与 periodic `exclusion_patterns` 增补：`集体接待日`、`投资者开放日` |
| `config/cninfo_b_class_source_registry_draft.yaml` | 同步 IR patterns + shared periodic exclusion |
| `lab/validate_cninfo_b_class_category_routing.py` | `_meeting_document_type`：无「说明会」的集体接待日/开放日 → `investor_relations_activity` |
| `lab/test_cninfo_b_class_category_routing_ir_activity_edge.py` | 8 项边角单测 |

未改：known-document / category-sample fixture · §7 FP · A/C/D · live。

---

## 3. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_category_routing_ir_activity_edge.py` | **8 OK** |
| `python lab/test_cninfo_b_class_category_routing_inquiry_reply_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_preview_fp.py` | **9 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_wrong_company_fp.py` | **9 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_wrong_period_fp.py` | **10 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_unrelated_announcement_fp.py` | **10 OK**（不回退） |
| `python lab/validate_cninfo_b_class_category_routing.py` | **38/38 PASS** · fail=0 |
| CNINFO calls | **0** |
| live | **none** |
| allow-list | **无**（未开启 live） |

---

## 4. Capability Gain

- 「投资者网上集体接待日」「投资者开放日」稳定预测 `investor_relations_activity` / `cninfo_meeting_notice_pdf`
- 「集体接待日暨…业绩说明会」与既有说明会 / 活动记录表路径不回退
- 「引入投资者」「面向专业投资者」等假友标题不误进 meeting
- 为后续将 BD2E202/206/232 类样本晋升 `ir_activity_known_*` 清除 route 障碍
- **不**声称 B complete / verified / full-market %

---

## 5. Gate

```text
b_class_ir_activity_routing_edge_gate = PASS_OFFLINE
task_id = B-FM-04
cninfo_calls_this_package = 0
live_calls_this_package = 0
allow_list = none
fake_section7_fp = no
ready_for_commit = true
```

---

## 6. Return Block

| 字段 | 值 |
|------|-----|
| task | B-FM-04 IR activity routing-edge hardening（offline） |
| files | `config/cninfo_announcement_categories.yaml` · `config/cninfo_b_class_source_registry_draft.yaml` · `lab/validate_cninfo_b_class_category_routing.py` · `lab/test_cninfo_b_class_category_routing_ir_activity_edge.py` · `outputs/validation/cninfo_b_class_ir_activity_routing_edge_20260715.md` ·（validator 刷新）`outputs/validation/cninfo_b_class_category_routing_{report.csv,summary.md}` |
| CNINFO | **0** |
| allow-list | **none** |
| wall | offline unit + routing validate only |
| ready_for_commit | **true** |

---

## 7. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选：用硬化后的 IR 规则评估 BD2E202 / BD2E206 / BD2E232 是否可晋升 `ir_activity_known_002`（需独立批准；本包不做）。
