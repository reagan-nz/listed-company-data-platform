# CNINFO B 类 B-FM-13 — 监管工作函（Regulatory Work Letter）Promotion Bounded Live

_生成时间：2026-07-15 · bounded live metadata · **无 commit** · **无 push**_

> **性质：** B-FM-12 晋升闭环续包 — `inquiry_known_004` + `inquiry_sample_003` live metadata  
> **不造** validation_design §7 FP · **不**触碰 A/C/D · **不**写 verified · **不**下载 PDF

---

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | bounded live | 监管工作函 B-FM-12 新晋 2 条 | **执行** — 主路径 |
| 2 | harvest promotion | meeting_sample_002（股东大会通知） | **推迟** — live 优先闭合工作函 |
| 3 | harvest promotion | 更多 regulatory placeholder | **推迟** — 无新边角证据 |
| 4 | routing edges | 更多 document_type | **推迟** — B-FM-11 已清 route |
| 5 | fake §7 FP | 新造 FP lineage | **拒绝** — 禁止 |

---

## 2. Allow-list

| case_id | type | evidence |
|---------|------|----------|
| `inquiry_known_004` | known-document | 文投控股 600715 · CPA「…监管工作函的专项说明」全文 · 2025-04-27~30 · BD2E433 |
| `inquiry_sample_003` | category-sample | `监管工作函` · 2025-04-26~30（全市场窗） |

排除：既有 ready（含 CPA 问询函回复 known_001、警示函、IR 等）、全部 placeholder、guard。

---

## 3. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_regulatory_work_letter_promotion.py` | **5 OK**（B-FM-12 不回退） |
| `python lab/test_cninfo_b_class_regulatory_work_letter_promotion_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_category_routing_regulatory_work_letter_edge.py` | **9 OK**（不回退） |
| allow-list dry-run | **DRY_RUN_PASS** · ready=**2** · invalid_ready=0 · query=0 |
| bounded live（最终） | **LIVE_PASS** · pass=**2**/0/0 |

### Live 细节

| 项 | 值 |
|----|-----|
| allow-list | 仅 `inquiry_known_004` + `inquiry_sample_003` |
| 最终成功跑 CNINFO | **4**（1 topSearch + 3 query） |
| 本包 CNINFO 合计 | **~8**（含 2 次网络失败试跑） |
| wall（最终成功跑） | **~90 s**（`REQUEST_TIMEOUT=45`） |
| PDF | **0** |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `inquiry_known_004` | 中兴财光华…信息披露监管工作函的专项说明 | 2025-04-28 | classified_correctly / inquiry_reply | **pass** |
| `inquiry_sample_003` | 鹏博士…终止上市相关事项的监管工作函…（窗内 11 hits） | 2025-04-29 | classified_correctly / regulatory_inquiry | **pass** |

### 运行备注（显式，非静默）

1. 直跑两次失败：topSearch SSL EOF / 空响应 → known `orgId resolution failed`；category `network_timeout`（默认 timeout=10s 过短）。
2. 最终成功跑一次性 wrapper：`REQUEST_TIMEOUT=45`；topSearch 失败后使用已验证 registry orgId `gssh0600715`（C-class / harvest 同源）。**未**修改共享 `validate_cninfo_b_class_corpus_retrieval.py`。
3. category 命中「收到…监管工作函」→ `regulatory_inquiry`，落在 `expected_document_types` 内（与 CPA 专项说明 `inquiry_reply` 可区分）。

---

## 4. Capability Gain

- 「监管工作函的专项说明」known-document ready 经 **live metadata** 确认（标题/日期/pdf_url/路由）
- 「监管工作函」category-sample ready 经全市场窗 **live metadata** 确认
- 闭合 B-FM-11 → B-FM-12 → B-FM-13 live 链路；**不**声称 B complete / verified / full-market %

---

## 5. Gate

```text
b_class_regulatory_work_letter_promotion_live_gate = LIVE_PASS
task_id = B-FM-13
cninfo_calls_this_package = ~8
live_calls_final_success = 4
pdf_download = 0
allow_list = inquiry_known_004 + inquiry_sample_003
fake_section7_fp = no
ready_for_commit = true
```

---

## 6. 产物

| 路径 | 用途 |
|------|------|
| `lab/test_cninfo_b_class_regulatory_work_letter_promotion_live.py` | allow-list + mock live 锁测 |
| `outputs/validation/cninfo_b_class_regulatory_work_letter_promotion_live_20260715/` | allow-list + live 证据包 |
| 本文件 | 任务报告 |

---

## 7. Return Block

| 字段 | 值 |
|------|-----|
| task | B-FM-13 监管工作函 promotion bounded live（inquiry_known_004 + inquiry_sample_003） |
| files | live 证据包 · `lab/test_cninfo_b_class_regulatory_work_letter_promotion_live.py` · 本报告 |
| CNINFO | **~8**（最终成功 4；含 2 次失败试跑） |
| allow-list | `inquiry_known_004` + `inquiry_sample_003` |
| wall | offline tests + dry-run + live **~90 s**（最终）/ 包内另两次失败 ~44 s |
| ready_for_commit | **true** |

---

## 8. 下一步（Controller）

1. 人工审阅后 **commit** 剩余报告产物（`…_live_20260715.md` + metrics；executor **未** push）。核心 allow-list / LIVE_PASS CSV 若已由 controller 收入 `f213c2c`，勿重复。
2. 可选：`meeting_sample_002`（股东大会通知，锚定 BD2E574 / shareholder_meeting_known_001）。
3. 可选：若需可复现 live，可将 timeout/registry-orgId 提升为显式 CLI 开关（当前仅本包一次性 wrapper）。
