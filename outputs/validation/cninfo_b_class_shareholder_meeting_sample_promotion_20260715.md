# CNINFO B 类 B-FM-14 — 股东大会通知（Shareholder Meeting Notice）Category-Sample Promotion（Offline）

_生成时间：2026-07-15 · offline only · **CNINFO = 0** · **无 live** · **无 commit** · **无 push**_

> **性质：** B-FM-13 LIVE_PASS 后最高价值续包 — 消费长期推迟的 `meeting_sample_002`（锚定 BD2E574 / shareholder_meeting_known_001）  
> **不造** validation_design §7 FP · **不**触碰 A/C/D · **不**写 verified  
> **不**做 bounded live（本包优先消费晋升；live 留给后续 allow-list）

---

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | harvest promotion | BD2E574 → meeting_sample_002 | **执行** — 主路径（B-FM-11/12 多次推迟） |
| 2 | bounded live | meeting_sample_002 allow-list metadata | **推迟** — 晋升后独立任务 |
| 3 | harvest promotion | periodic_guard_001（延期披露） | **推迟** — harvest 仍无「延期披露」行 |
| 4 | routing edges | 更多 document_type | **推迟** — 股东大会通知 route 已通 |
| 5 | alternate | 真·监管问询函原文 known_003 | **拒绝** — harvest 仍无可区分样本 |

---

## 2. 晋升

| case_id | prior → new | evidence | title_pattern / window |
|---------|-------------|---------|------------------------|
| `meeting_sample_002` | placeholder → **ready** | BD2E574 航天智造 300446 · ann=1223974102 · 2025-06-24 | `股东大会通知` · 2025-06-22~26 |

路由校正（设计稿残留）：`source_id` 由误标的 `cninfo_meeting_notice_pdf` 改为 **`cninfo_general_announcement_pdf`**（与 known_001 LIVE_PASS 及 offline route 一致）。

纯「股东大会通知」（无说明会）→ `shareholder_meeting_material` / `cninfo_general_announcement_pdf`；窗内「股东大会通知暨…说明会」允许 `meeting_notice`。

与既有 meeting sample 可区分：`meeting_sample_001`（说明会 → meeting_notice）/ `meeting_sample_002`（股东大会通知 → general）。

---

## 3. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_shareholder_meeting_sample_promotion.py` | **6 OK** |
| `python lab/test_cninfo_b_class_regulatory_work_letter_promotion.py` | **5 OK**（不回退） |
| `python lab/test_cninfo_b_class_corpus_retrieval_category_sample_live.py` | **4 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | **PASS** · ready=**24** · invalid_ready=0 · placeholder=2 |
| dry-run corpus retrieval | **DRY_RUN_PASS** · ready=**24** · query=0 |
| CNINFO calls | **0** |
| live | **none** |
| allow-list | **无**（未开启 live） |

---

## 4. Capability Gain

- 「股东大会通知」边角进入 **category-sample ready**（槽位 `meeting_sample_002`）
- 闭合 known_001（B-R16 LIVE_PASS）→ category-sample 晋升链
- 纠正 placeholder 误标 source（meeting_notice → general_announcement）
- **不**声称 B complete / verified / full-market %

---

## 5. Gate

```text
b_class_shareholder_meeting_sample_promotion_gate = PASS_OFFLINE
task_id = B-FM-14
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
| `fixtures/b_class/retrieval_validation/category_sample_cases.yaml` | meeting_sample_002 ready + source 校正 |
| `lab/test_cninfo_b_class_shareholder_meeting_sample_promotion.py` | 离线晋升锁测 |
| `outputs/validation/cninfo_b_class_shareholder_meeting_sample_promotion_dry_run_*_20260715.*` | dry-run |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_{report.csv,summary.md}` | ready 选择器刷新 |
| 本文件 | 任务报告 |

---

## 7. Return Block

| 字段 | 值 |
|------|-----|
| task | B-FM-14 股东大会通知 category-sample promotion（offline；BD2E574） |
| files | fixtures category · `lab/test_cninfo_b_class_shareholder_meeting_sample_promotion.py` · dry-run + ready-case 报告 · 本报告 |
| CNINFO | **0** |
| allow-list | **none** |
| wall | offline unit + select + dry-run only |
| ready_for_commit | **true** |

---

## 8. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选 bounded live：allow-list = `meeting_sample_002`（可叠加 known_001 若需对照）；需独立批准。
3. `periodic_guard_001`（延期披露）仍缺 harvest，不宜硬推。
4. 真·监管问询函原文仍缺 harvest，不宜硬推 `regulatory_known_003`。
