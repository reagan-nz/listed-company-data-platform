# CNINFO B 类 B-FM-17 — 股东大会通知「的」助词变体 Known-Document Bounded Live

_生成时间：2026-07-15 · bounded live metadata · **无 commit** · **无 push**_

> **性质：** B-FM-16 晋升闭环续包 — `shareholder_meeting_known_002` live metadata  
> **不造** validation_design §7 FP · **不**触碰 A/C/D · **不**写 verified · **不**下载 PDF

---

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | bounded live | known_002 allow-list metadata | **执行** — 主路径（B-FM-16 明确推迟） |
| 2 | harvest promotion | periodic_guard_001（延期披露） | **推迟** — harvest 仍无「延期披露」行 |
| 3 | harvest promotion | 真·监管问询函原文 known_003 | **拒绝** — harvest 仍无可区分样本 |
| 4 | routing edges | 更多 document_type | **推迟** — 「的」助词变体 route 已通 |
| 5 | fake §7 FP | 新造 FP lineage | **拒绝** — 禁止 |

---

## 2. Allow-list

| case_id | type | evidence |
|---------|------|----------|
| `shareholder_meeting_known_002` | known-document | 恒邦股份 002237 · `股东大会的通知` · 2025-06-26~29（BD2E292 / ann=1224014462） |

排除：`shareholder_meeting_known_001`（已 B-R16 LIVE_PASS）、`meeting_sample_002`（已 B-FM-15 LIVE_PASS）、既有 ready、全部 placeholder、guard。

---

## 3. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_shareholder_meeting_known_002_promotion.py` | **7 OK**（B-FM-16 不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_002_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_shareholder_meeting_sample_promotion.py` | **6 OK**（不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_sample_promotion_live.py` | **3 OK**（不回退） |
| allow-list dry-run | **DRY_RUN_PASS** · ready=**1** · invalid_ready=0 · query=0 |
| bounded live | **LIVE_PASS** · pass=**1**/0/0 |

### Live 细节

| 项 | 值 |
|----|-----|
| allow-list | 仅 `shareholder_meeting_known_002` |
| CNINFO | **2**（1 topSearch + 1 query；无 PDF） |
| wall | **~4.3 s**（`REQUEST_TIMEOUT=45`） |
| PDF | **0** |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `shareholder_meeting_known_002` | 关于召开2025年第三次临时股东大会的通知 | 2025-06-27 | classified_correctly / shareholder_meeting_material | **pass** |

### 运行备注（显式，非静默）

1. 一次性 wrapper：`REQUEST_TIMEOUT=45`（与 B-FM-15 同惯例）。**未**修改共享 `validate_cninfo_b_class_corpus_retrieval.py`。
2. 首跑即 LIVE_PASS；无网络失败试跑；无 orgId fallback。
3. predicted_type=`shareholder_meeting_material`；route=`cninfo_general_announcement_pdf`（与 B-FM-16 晋升一致）。

---

## 4. Capability Gain

- 「股东大会的通知」助词变体 known-document ready 经公司窗 **live metadata** 确认（标题/日期/pdf_url/路由）
- 闭合 B-FM-16 promotion → B-FM-17 live 链路（与 known_001 / meeting_sample_002 可区分边角）
- **不**声称 B complete / verified / full-market %

---

## 5. Gate

```text
b_class_shareholder_meeting_known_002_live_gate = LIVE_PASS
task_id = B-FM-17
cninfo_calls_this_package = 2
live_calls_final_success = 2
pdf_download = 0
allow_list = shareholder_meeting_known_002
fake_section7_fp = no
ready_for_commit = true
```

---

## 6. 产物

| 路径 | 用途 |
|------|------|
| `lab/test_cninfo_b_class_shareholder_meeting_known_002_live.py` | allow-list + mock live 锁测 |
| `outputs/validation/cninfo_b_class_shareholder_meeting_known_002_live_20260715/` | allow-list + live 证据包 |
| 本文件 | 任务报告 |

---

## 7. Return Block

| 字段 | 值 |
|------|-----|
| task | B-FM-17 股东大会通知「的」助词变体 known-document bounded live（shareholder_meeting_known_002） |
| files | live 证据包 · `lab/test_cninfo_b_class_shareholder_meeting_known_002_live.py` · 本报告 |
| CNINFO | **2** |
| allow-list | `shareholder_meeting_known_002` |
| wall | offline tests + dry-run + live **~4.3 s** |
| ready_for_commit | **true** |

---

## 8. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. `periodic_guard_001`（延期披露）仍缺 harvest，不宜硬推。
3. 真·监管问询函原文仍缺 harvest，不宜硬推 `regulatory_known_003`。
4. 可选：更多 IR / 监管边角 harvest 晋升（需新证据）。
