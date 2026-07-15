# CNINFO B 类 B-FM-05 — IR Collective-Reception Promotion（Offline）

_生成时间：2026-07-15 · offline only · **CNINFO = 0** · **无 live** · **无 commit** · **无 push**_

> **性质：** B-FM-04 routing edge 闭环 — harvest 晋升 known-document + category-sample（dry-run）  
> **不造** validation_design §7 FP · **不**触碰 A/C/D · **不**写 verified

---

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | routing edges | 更多 document_type 边角 | 已由 B-FM-04 完成；本包消费其结果 |
| 2 | larger sample | 集体接待日晋升 `ir_activity_known_002` | **执行** — 主路径 |
| 3 | generalization | category-sample `投资者网上集体接待日` 窗 | **执行** — 同包 |
| 4 | bounded live | 新晋 2 条 metadata | **推迟** — offline-first / controller_execution_allowed=false |
| 5 | next event class | 监管问询函原文 / 投资者开放日 known | **部分保留** — 开放日路由已通，本包 pattern 专锁集体接待日 |

---

## 2. 晋升

| case_id | prior → new | evidence | title_pattern |
|---------|-------------|---------|---------------|
| `ir_activity_known_002` | placeholder → ready | BD2E202 吉林化纤 000420 · ann=1223605360 · 2025-05-20 | `投资者网上集体接待日` · 2025-05-19~22 |
| `ir_activity_sample_001` | **新增** ready | BD2E202 + BD2E206（永安林业 000663 · ann=1223513724 · 2025-05-09） | `投资者网上集体接待日` · 2025-05-08~22 |

离线路由：两 harvest 标题经 B-FM-04 marker → `investor_relations_activity` / `cninfo_meeting_notice_pdf`。

同构未晋升为独立 known：BD2E232 新乡化纤「投资者开放日」（路由已通；留给后续 known 槽位）。

---

## 3. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_ir_activity_promotion.py` | **5 OK** |
| `python lab/test_cninfo_b_class_category_routing_ir_activity_edge.py` | **8 OK**（不回退） |
| `python lab/test_cninfo_b_class_inquiry_reply_cpa_promotion.py` | **4 OK**（不回退） |
| `python lab/test_cninfo_b_class_corpus_retrieval_category_sample_live.py` | **4 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | **PASS** · ready=**17** · invalid_ready=0 · placeholder=5 |
| dry-run corpus retrieval | **DRY_RUN_PASS** · ready=**17** · query=0 |
| CNINFO calls | **0** |
| live | **none** |
| allow-list | **无**（未开启 live） |

---

## 4. Capability Gain

- 「投资者网上集体接待日」边角进入 **known-document ready**（与活动记录表 `ir_activity_known_001` 可区分）
- 同边角进入 **category-sample ready**（全市场窗；允许窗内「暨…说明会」→ meeting_notice）
- 闭合 B-FM-04 → 晋升 → dry-run 链路；为后续 bounded live 准备 allow-list 候选
- **不**声称 B complete / verified / full-market %

---

## 5. Gate

```text
b_class_ir_activity_promotion_gate = PASS_OFFLINE
task_id = B-FM-05
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
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | ir_activity_known_002 ready |
| `fixtures/b_class/retrieval_validation/category_sample_cases.yaml` | ir_activity_sample_001 ready |
| `lab/test_cninfo_b_class_ir_activity_promotion.py` | 离线晋升锁测 |
| `outputs/validation/cninfo_b_class_ir_activity_promotion_dry_run_*_20260715.*` | dry-run |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_{report.csv,summary.md}` | ready 选择器刷新 |
| 本文件 | 任务报告 |

---

## 7. Return Block

| 字段 | 值 |
|------|-----|
| task | B-FM-05 IR collective-reception promotion（offline） |
| files | fixtures known/category · `lab/test_cninfo_b_class_ir_activity_promotion.py` · dry-run + ready-case 报告 · 本报告 |
| CNINFO | **0** |
| allow-list | **none** |
| wall | offline unit + select + dry-run only |
| ready_for_commit | **true** |

---

## 8. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选 bounded live：allow-list = `ir_activity_known_002` + `ir_activity_sample_001`（需独立批准；本包不做）。
3. 可选：BD2E232「投资者开放日」晋升独立 known（需新 case 槽位）。
