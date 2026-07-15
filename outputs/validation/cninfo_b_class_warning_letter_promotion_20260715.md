# CNINFO B 类 B-FM-08 — Warning-Letter（警示函）Promotion（Offline）

_生成时间：2026-07-15 · offline only · **CNINFO = 0** · **无 live** · **无 commit** · **无 push**_

> **性质：** B-FM-07 routing edge 闭环续包 — BD2E626「警示函」晋升 known-document + category-sample（dry-run）  
> **不造** validation_design §7 FP · **不**触碰 A/C/D · **不**写 verified  
> **不**做 bounded live（本包优先消费晋升；live 留给后续 allow-list）

---

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | harvest promotion | BD2E626 → regulatory_known_001 + inquiry_sample_001 | **执行** — 主路径 |
| 2 | bounded live | IR B-FM-05/06 新晋 metadata | **推迟** — 本包先完成警示函晋升闭环 |
| 3 | bounded live | 本包新晋警示函 allow-list | **推迟** — 晋升后独立任务 |
| 4 | routing edges | 更多 document_type | **推迟** — B-FM-07 已清 route |
| 5 | alternate | 真·监管问询函原文 known | **拒绝** — harvest 仍无「收到…问询函」且无回复的可区分样本 |

---

## 2. 晋升

| case_id | prior → new | evidence | title_pattern |
|---------|-------------|---------|---------------|
| `regulatory_known_001` | placeholder → **ready** | BD2E626 壹网壹创 300792 · ann=1223957037 · 2025-06-23 | `关于收到浙江证监局警示函的公告` · 2025-06-22~25 |
| `inquiry_sample_001` | placeholder → **ready** | 同上（全市场窗锚定该证据） | `警示函` · 2025-06-21~25 |

离线路由：标题经 B-FM-07 marker → `regulatory_inquiry` / `cninfo_inquiry_reply_pdf`。

与既有 regulatory ready 可区分：`regulatory_known_002`（关注函）/ `regulatory_known_001`（警示函）。

---

## 3. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_warning_letter_promotion.py` | **5 OK** |
| `python lab/test_cninfo_b_class_category_routing_warning_letter_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_inquiry_reply_cpa_promotion.py` | **4 OK**（不回退） |
| `python lab/test_cninfo_b_class_ir_activity_open_day_promotion.py` | **4 OK**（不回退） |
| `python lab/test_cninfo_b_class_corpus_retrieval_category_sample_live.py` | **4 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | **PASS** · ready=**21** · invalid_ready=0 · placeholder=3 |
| dry-run corpus retrieval | **DRY_RUN_PASS** · ready=**21** · query=0 |
| CNINFO calls | **0** |
| live | **none** |
| allow-list | **无**（未开启 live） |

---

## 4. Capability Gain

- 「警示函」边角进入 **known-document ready**（槽位 `regulatory_known_001`）
- 同边角进入 **category-sample ready**（`inquiry_sample_001`）
- 闭合 B-FM-07 → B-FM-08 晋升链；为后续 bounded live 准备 allow-list 候选
- **不**声称 B complete / verified / full-market %

---

## 5. Gate

```text
b_class_warning_letter_promotion_gate = PASS_OFFLINE
task_id = B-FM-08
cninfo_calls_this_package = 0
live_calls_this_package = 0
pdf_download = 0
allow_list = none
fake_section7_fp = no
ready_for_commit = true
```

---

## 6. 产物

| 路径 | 用途 |
|------|------|
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | regulatory_known_001 ready |
| `fixtures/b_class/retrieval_validation/category_sample_cases.yaml` | inquiry_sample_001 ready |
| `lab/test_cninfo_b_class_warning_letter_promotion.py` | 离线晋升锁测 |
| `outputs/validation/cninfo_b_class_warning_letter_promotion_dry_run_*_20260715.*` | dry-run |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_{report.csv,summary.md}` | ready 选择器刷新 |
| 本文件 | 任务报告 |

---

## 7. Return Block

| 字段 | 值 |
|------|-----|
| task | B-FM-08 警示函 promotion（offline；BD2E626） |
| files | fixtures known/category · `lab/test_cninfo_b_class_warning_letter_promotion.py` · dry-run + ready-case 报告 · 本报告 |
| CNINFO | **0** |
| allow-list | **none** |
| wall | offline unit + select + dry-run only |
| ready_for_commit | **true** |

---

## 8. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选 bounded live：allow-list = `regulatory_known_001` + `inquiry_sample_001`（和/或 IR B-FM-05/06）；需独立批准。
3. 真·监管问询函原文（「收到…问询函」且无回复）仍缺 harvest，不宜硬推 `regulatory_known_003`。
