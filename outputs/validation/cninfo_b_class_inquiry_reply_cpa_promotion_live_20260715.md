# CNINFO B 类 B-FM-03 — CPA Inquiry-Reply Promotion + Live

_生成时间：2026-07-15 · dry-run + bounded live metadata · **无 commit** · **无 push**_

> **性质：** B-FM-02 routing edge 闭环 — harvest 晋升 known-document + category-sample + live metadata  
> **不造** validation_design §7 FP · **不**触碰 A/C/D · **不**写 verified

---

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | routing edges | 更多 document_type 边角 | 已由 B-FM-02 完成；本包消费其结果 |
| 2 | larger sample | CPA「问询函的回复」晋升 | **执行** — 主路径 |
| 3 | generalization | category-sample `问询函的回复` 窗 | **执行** — 同包 |
| 4 | bounded live | 新晋 2 条 metadata | **执行** |
| 5 | next event class | 监管问询函原文 / IR 交流 | **拒绝** — harvest 仍无可区分样本 |

---

## 2. 晋升

| case_id | prior → new | evidence | title_pattern |
|---------|-------------|---------|---------------|
| `inquiry_known_001` | placeholder → ready | BD2E462 华钰矿业 601020 · ann=1223973177 · 2025-06-24 | CPA 全文「…问询函的回复」（无「回复公告」） |
| `inquiry_sample_002` | placeholder → ready | BD2E462 + BD2E794（兰石重装 603169 · ann=1224016689 · 2025-06-27） | `问询函的回复` · 2025-06-23~28 |

离线路由：两 harvest 标题经 B-FM-02 marker → `inquiry_reply` / `cninfo_inquiry_reply_pdf`。

---

## 3. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_inquiry_reply_cpa_promotion.py` | **4 OK** |
| `python lab/test_cninfo_b_class_category_routing_inquiry_reply_edge.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_corpus_retrieval_category_sample_live.py` | **4 OK**（不回退） |
| dry-run corpus retrieval | **DRY_RUN_PASS** · ready=**15** · invalid_ready=0 · query=0 |
| bounded live（最终 allow-list） | **LIVE_PASS** · pass=**2**/0/0 |

### Live 细节

| 项 | 值 |
|----|-----|
| allow-list | 仅 `inquiry_known_001` + `inquiry_sample_002` |
| 最终 CNINFO（本轮） | **4**（1 topSearch + 3 query） |
| 本包 CNINFO 合计 | **8**（含首次 pattern 过宽试跑 4 次 → ambiguous → 收紧重跑） |
| wall（最终 live） | **~12.6 s** |
| PDF | **0** |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `inquiry_known_001` | 立信…信息披露监管问询函的回复 | 2025-06-24 | classified_correctly | **pass** |
| `inquiry_sample_002` | …事后审核问询函的回复公告 | 2025-06-27 | classified_correctly | **pass** |

首次试跑 known pattern=`信息披露监管问询函的回复` 命中 3 条 → ambiguous；已收紧为 harvest 全文（仍无「回复公告」后缀）。

---

## 4. Capability Gain

- CPA「问询函的回复」边角进入 **known-document ready** 并经 live metadata 确认
- 同边角进入 **category-sample ready** 并经全市场窗 live 确认
- 闭合 B-FM-02 → 晋升 → live 链路；**不**声称 B complete / verified / full-market %

---

## 5. Gate

```text
b_class_inquiry_reply_cpa_promotion_live_gate = LIVE_PASS
task_id = B-FM-03
cninfo_calls_this_package = 8
live_calls_this_package = 8
pdf_download = 0
allow_list = inquiry_known_001 + inquiry_sample_002
fake_section7_fp = no
ready_for_commit = true
```

---

## 6. 产物

| 路径 | 用途 |
|------|------|
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | inquiry_known_001 ready |
| `fixtures/b_class/retrieval_validation/category_sample_cases.yaml` | inquiry_sample_002 ready |
| `lab/test_cninfo_b_class_inquiry_reply_cpa_promotion.py` | 离线晋升锁测 |
| `outputs/validation/cninfo_b_class_inquiry_reply_cpa_promotion_dry_run_*_20260715.*` | dry-run |
| `outputs/validation/cninfo_b_class_inquiry_reply_cpa_promotion_live_20260715/` | allow-list + live 证据包 |
| 本文件 | 任务报告 |

---

## 7. Return Block

| 字段 | 值 |
|------|-----|
| task | B-FM-03 CPA inquiry_reply promotion + bounded live |
| files | fixtures known/category · `lab/test_cninfo_b_class_inquiry_reply_cpa_promotion.py` · dry-run + live 证据包 · 本报告 |
| CNINFO | **8** |
| allow-list | `inquiry_known_001` + `inquiry_sample_002` |
| wall | offline tests + dry-run + live ~12.6s（最终）/ 包内两次 live |
| ready_for_commit | **true** |

---

## 8. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选：监管问询函原文 / 「投资者交流活动」仍需新 harvest 证据，不宜硬推 placeholder。
