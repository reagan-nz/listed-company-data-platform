# CNINFO B 类 B-FM-09 — Warning-Letter（警示函）Promotion Bounded Live

_生成时间：2026-07-15 · bounded live metadata · **无 commit** · **无 push**_

> **性质：** B-FM-08 晋升闭环续包 — `regulatory_known_001` + `inquiry_sample_001` live metadata  
> **不造** validation_design §7 FP · **不**触碰 A/C/D · **不**写 verified · **不**下载 PDF

---

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | bounded live | 警示函 B-FM-08 新晋 2 条 | **执行** — 主路径 |
| 2 | bounded live | IR B-FM-05/06 新晋 metadata | **推迟** — 本包先闭合警示函 live |
| 3 | harvest promotion | 更多 regulatory / IR placeholder | **推迟** — 无新边角证据 |
| 4 | routing edges | 更多 document_type | **推迟** — B-FM-07 已清警示函 route |
| 5 | fake §7 FP | 新造 FP lineage | **拒绝** — 禁止 |

---

## 2. Allow-list

| case_id | type | evidence |
|---------|------|----------|
| `regulatory_known_001` | known-document | 壹网壹创 300792 · 「关于收到浙江证监局警示函的公告」 · 2025-06-22~25 · BD2E626 |
| `inquiry_sample_001` | category-sample | `警示函` · 2025-06-21~25（全市场窗） |

排除：既有 ready（含关注函 known_002、IR、CPA 等）、全部 placeholder、guard。

---

## 3. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_warning_letter_promotion.py` | **5 OK**（B-FM-08 不回退） |
| `python lab/test_cninfo_b_class_warning_letter_promotion_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_category_routing_warning_letter_edge.py` | **7 OK**（不回退） |
| allow-list dry-run | **DRY_RUN_PASS** · ready=**2** · invalid_ready=0 · query=0 |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

### Live 细节

| 项 | 值 |
|----|-----|
| allow-list | 仅 `regulatory_known_001` + `inquiry_sample_001` |
| CNINFO | **4**（1 topSearch + 3 query） |
| wall | **14.32 s** |
| PDF | **0** |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `regulatory_known_001` | 关于收到浙江证监局警示函的公告 | 2025-06-23 | classified_correctly / regulatory_inquiry | **pass** |
| `inquiry_sample_001` | …出具警示函措施的决定的公告（窗内 3 hits） | 2025-06-24 | classified_correctly / regulatory_inquiry | **pass** |

---

## 4. Capability Gain

- 警示函 known-document ready 经 **live metadata** 确认（标题/日期/pdf_url/路由）
- 警示函 category-sample ready 经全市场窗 **live metadata** 确认
- 闭合 B-FM-07 → B-FM-08 → B-FM-09 live 链路；**不**声称 B complete / verified / full-market %

---

## 5. Gate

```text
b_class_warning_letter_promotion_live_gate = LIVE_PASS
task_id = B-FM-09
cninfo_calls_this_package = 4
live_calls_this_package = 4
pdf_download = 0
allow_list = regulatory_known_001 + inquiry_sample_001
fake_section7_fp = no
ready_for_commit = true
```

---

## 6. 产物

| 路径 | 用途 |
|------|------|
| `lab/test_cninfo_b_class_warning_letter_promotion_live.py` | allow-list + mock live 锁测 |
| `outputs/validation/cninfo_b_class_warning_letter_promotion_live_20260715/` | allow-list + live 证据包 |
| 本文件 | 任务报告 |

---

## 7. Return Block

| 字段 | 值 |
|------|-----|
| task | B-FM-09 警示函 promotion bounded live（regulatory_known_001 + inquiry_sample_001） |
| files | live 证据包 · `lab/test_cninfo_b_class_warning_letter_promotion_live.py` · 本报告 |
| CNINFO | **4** |
| allow-list | `regulatory_known_001` + `inquiry_sample_001` |
| wall | offline tests + dry-run + live **14.32 s** |
| ready_for_commit | **true** |

---

## 8. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选：IR B-FM-05/06 新晋 case 的 bounded live；或新 harvest 边角晋升。
