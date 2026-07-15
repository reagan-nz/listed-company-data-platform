# CNINFO B 类 B-FM-02 — inquiry_reply Routing Edge Hardening

_生成时间：2026-07-15 · offline only · **CNINFO = 0** · **无 live** · **无 commit** · **无 push**_

> **性质：** title routing document_type 边角硬化 · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**晋升 known-document / category-sample · **不**触碰 A/C/D

---

## 1. Gap

| 项 | 说明 |
|----|------|
| gap_id | `GAP-B-INQUIRY-REPLY-DE-PARTICLE` |
| 来源 | B-R16-03 IDLE：CPA「问询函的回复」在旧 `_inquiry_document_type` 下误判 `regulatory_inquiry` |
| 证据 | BD2E462 华钰矿业 / BD2E794 兰石重装 harvest 标题以「监管问询函的回复」结尾（无「回复公告」） |
| 影响 | 若晋升为 `expected_document_type=inquiry_reply` 的 known-document，live 会 misclassified |
| 明确不改 | BD2E500「延期回复…问询函」→ 仍为 `regulatory_inquiry`（非回复正文） |

---

## 2. Fix（最小）

| 文件 | 变更 |
|------|------|
| `lab/validate_cninfo_b_class_category_routing.py` | `_inquiry_document_type` 增补 reply marker：`问询函的回复`、`关注函的回复` |
| `lab/test_cninfo_b_class_category_routing_inquiry_reply_edge.py` | 7 项边角单测（CPA / 延期回复 / 既有路径 / 纯问询函） |

未改：fixture / category-sample / registry / §7 FP / A/C/D。

---

## 3. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_category_routing_inquiry_reply_edge.py` | **7 OK** |
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

- CPA「…问询函的回复」稳定预测 `inquiry_reply`（不再误判 `regulatory_inquiry`）
- 「延期回复…问询函」与纯问询/关注函原文路径不回退
- 为后续 harvest 晋升 inquiry reply 边角样本清除 document_type 误分类障碍
- **不**声称 B complete / verified / full-market %

---

## 5. Gate

```text
b_class_inquiry_reply_routing_edge_gate = PASS_OFFLINE
task_id = B-FM-02
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
| task | B-FM-02 inquiry_reply routing-edge hardening（offline） |
| files | `lab/validate_cninfo_b_class_category_routing.py` · `lab/test_cninfo_b_class_category_routing_inquiry_reply_edge.py` · `outputs/validation/cninfo_b_class_inquiry_reply_routing_edge_20260715.md` ·（validator 刷新）`outputs/validation/cninfo_b_class_category_routing_{report.csv,summary.md}` |
| CNINFO | **0** |
| allow-list | **none** |
| wall | offline unit + routing validate only |
| ready_for_commit | **true** |

---

## 7. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选：用硬化后的 document_type 规则评估 BD2E462 / BD2E794 是否可晋升 known-document（需独立批准；本包不做）。
