# CNINFO B 类 B-FM-06 — IR Open-Day Promotion（Offline）

_生成时间：2026-07-15 · offline only · **CNINFO = 0** · **无 live** · **无 commit** · **无 push**_

> **性质：** B-FM-04 routing edge 闭环续包 — BD2E232「投资者开放日」晋升 known-document + category-sample（dry-run）  
> **不造** validation_design §7 FP · **不**触碰 A/C/D · **不**写 verified  
> **不**做 bounded live（`controller_execution_allowed=false`）

---

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | routing edges | 更多 document_type 边角 | 已由 B-FM-04 完成；本包消费其结果 |
| 2 | larger sample / next event class | BD2E232 开放日独立 known 槽位 | **执行** — 主路径 |
| 3 | generalization | category-sample `投资者开放日` 窗 | **执行** — 同包 |
| 4 | bounded live | 新晋 2 条 metadata | **推迟** — controller_execution_allowed=false |
| 5 | alternate | B-FM-05 集体接待日 live | **推迟** — 同上 |

---

## 2. 晋升

| case_id | prior → new | evidence | title_pattern |
|---------|-------------|---------|---------------|
| `ir_activity_known_003` | **新增** ready | BD2E232 新乡化纤 000949 · ann=1223746795 · 2025-06-03 | `投资者开放日` · 2025-06-02~05 |
| `ir_activity_sample_002` | **新增** ready | 同上（全市场窗锚定该证据） | `投资者开放日` · 2025-06-01~05 |

离线路由：标题经 B-FM-04 marker → `investor_relations_activity` / `cninfo_meeting_notice_pdf`。

与既有 IR ready 可区分：`ir_activity_known_001`（活动记录表）/ `ir_activity_known_002`（集体接待日）/ `ir_activity_known_003`（开放日）。

---

## 3. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_ir_activity_open_day_promotion.py` | **4 OK** |
| `python lab/test_cninfo_b_class_ir_activity_promotion.py` | **5 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_ir_activity_edge.py` | **8 OK**（不回退） |
| `python lab/test_cninfo_b_class_inquiry_reply_cpa_promotion.py` | **4 OK**（不回退） |
| `python lab/test_cninfo_b_class_corpus_retrieval_category_sample_live.py` | **4 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | **PASS** · ready=**19** · invalid_ready=0 · placeholder=5 |
| dry-run corpus retrieval | **DRY_RUN_PASS** · ready=**19** · query=0 |
| CNINFO calls | **0** |
| live | **none** |
| allow-list | **无**（未开启 live） |

---

## 4. Capability Gain

- 「投资者开放日」边角进入 **known-document ready**（独立槽位 `ir_activity_known_003`）
- 同边角进入 **category-sample ready**（`ir_activity_sample_002`）
- 闭合 B-FM-04 → B-FM-05（集体接待日）→ B-FM-06（开放日）晋升链；为后续 bounded live 准备 allow-list 候选
- **不**声称 B complete / verified / full-market %

---

## 5. Gate

```text
b_class_ir_activity_open_day_promotion_gate = PASS_OFFLINE
task_id = B-FM-06
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
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | ir_activity_known_003 ready |
| `fixtures/b_class/retrieval_validation/category_sample_cases.yaml` | ir_activity_sample_002 ready |
| `lab/test_cninfo_b_class_ir_activity_open_day_promotion.py` | 离线晋升锁测 |
| `outputs/validation/cninfo_b_class_ir_activity_open_day_promotion_dry_run_*_20260715.*` | dry-run |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_{report.csv,summary.md}` | ready 选择器刷新 |
| 本文件 | 任务报告 |

---

## 7. Return Block

| 字段 | 值 |
|------|-----|
| task | B-FM-06 IR open-day promotion（offline；BD2E232） |
| files | fixtures known/category · `lab/test_cninfo_b_class_ir_activity_open_day_promotion.py` · dry-run + ready-case 报告 · 本报告 |
| CNINFO | **0** |
| allow-list | **none** |
| wall | offline unit + select + dry-run only |
| ready_for_commit | **true** |

---

## 8. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选 bounded live：allow-list = `ir_activity_known_003` + `ir_activity_sample_002`（和/或 B-FM-05 的 known_002 + sample_001）；需 `controller_execution_allowed` + 独立批准。
3. 监管问询函原文等仍需新 harvest 证据，不宜硬推 placeholder。
