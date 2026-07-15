# CNINFO B 类 B-FM-12 — 监管工作函（Regulatory Work Letter）Promotion（Offline）

_生成时间：2026-07-15 · offline only · **CNINFO = 0** · **无 live** · **无 commit** · **无 push**_

> **性质：** B-FM-11 routing edge 闭环续包 — BD2E433「监管工作函的专项说明」晋升 known-document + category-sample（dry-run）  
> **不造** validation_design §7 FP · **不**触碰 A/C/D · **不**写 verified  
> **不**做 bounded live（本包优先消费晋升；live 留给后续 allow-list）

---

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | harvest promotion | BD2E433 → inquiry_known_004 + inquiry_sample_003 | **执行** — 主路径 |
| 2 | harvest promotion | meeting_sample_002（股东大会通知） | **推迟** — 无 route 阻塞；工作函闭环优先 |
| 3 | bounded live | 本包新晋 allow-list metadata | **推迟** — 晋升后独立任务 |
| 4 | routing edges | 更多 document_type | **推迟** — B-FM-11 已清 route |
| 5 | alternate | 真·监管问询函原文 known_003 | **拒绝** — harvest 仍无「收到…问询函」且无回复的可区分样本 |

---

## 2. 晋升

| case_id | prior → new | evidence | title_pattern |
|---------|-------------|---------|---------------|
| `inquiry_known_004` | **新增 ready** | BD2E433 文投控股 600715 · ann=1223358761 · 2025-04-28 | 全文 CPA「…监管工作函的专项说明」 · 2025-04-27~30 |
| `inquiry_sample_003` | **新增 ready** | 同上（全市场窗锚定该证据） | `监管工作函` · 2025-04-26~30 |

离线路由：标题经 B-FM-11 marker → `inquiry_reply` / `cninfo_inquiry_reply_pdf`（含「年度报告」子串亦不再误进 periodic）。

与既有 inquiry ready 可区分：`inquiry_known_001`（CPA 问询函的回复）/ `inquiry_known_004`（CPA 监管工作函的专项说明）。

category-sample FP guard 用「年度报告全文」而非裸「年度报告」，避免误伤含年报子串的工作函标题。

---

## 3. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_regulatory_work_letter_promotion.py` | **5 OK** |
| `python lab/test_cninfo_b_class_category_routing_regulatory_work_letter_edge.py` | **9 OK**（不回退） |
| `python lab/test_cninfo_b_class_inquiry_reply_cpa_promotion.py` | **4 OK**（不回退） |
| `python lab/test_cninfo_b_class_warning_letter_promotion.py` | **5 OK**（不回退） |
| `python lab/test_cninfo_b_class_ir_activity_open_day_promotion.py` | **4 OK**（不回退） |
| `python lab/test_cninfo_b_class_corpus_retrieval_category_sample_live.py` | **4 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | **PASS** · ready=**23** · invalid_ready=0 · placeholder=3 |
| dry-run corpus retrieval | **DRY_RUN_PASS** · ready=**23** · query=0 |
| CNINFO calls | **0** |
| live | **none** |
| allow-list | **无**（未开启 live） |

---

## 4. Capability Gain

- 「监管工作函的专项说明」边角进入 **known-document ready**（槽位 `inquiry_known_004`）
- 同边角进入 **category-sample ready**（`inquiry_sample_003`）
- 闭合 B-FM-11 → B-FM-12 晋升链；为后续 bounded live 准备 allow-list 候选
- **不**声称 B complete / verified / full-market %

---

## 5. Gate

```text
b_class_regulatory_work_letter_promotion_gate = PASS_OFFLINE
task_id = B-FM-12
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
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | inquiry_known_004 ready |
| `fixtures/b_class/retrieval_validation/category_sample_cases.yaml` | inquiry_sample_003 ready |
| `lab/test_cninfo_b_class_regulatory_work_letter_promotion.py` | 离线晋升锁测 |
| `outputs/validation/cninfo_b_class_regulatory_work_letter_promotion_dry_run_*_20260715.*` | dry-run |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_{report.csv,summary.md}` | ready 选择器刷新 |
| 本文件 | 任务报告 |

---

## 7. Return Block

| 字段 | 值 |
|------|-----|
| task | B-FM-12 监管工作函 promotion（offline；BD2E433） |
| files | fixtures known/category · `lab/test_cninfo_b_class_regulatory_work_letter_promotion.py` · dry-run + ready-case 报告 · 本报告 |
| CNINFO | **0** |
| allow-list | **none** |
| wall | offline unit + select + dry-run only |
| ready_for_commit | **true** |

---

## 8. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选 bounded live：allow-list = `inquiry_known_004` + `inquiry_sample_003`；需独立批准。
3. 可选：`meeting_sample_002`（股东大会通知，锚定 BD2E574 / shareholder_meeting_known_001）。
4. 真·监管问询函原文（「收到…问询函」且无回复）仍缺 harvest，不宜硬推 `regulatory_known_003`。
