# CNINFO B 类 B-FM-19 — 股东大会决议 / 召开公告 Known-Document Promotion + Bounded Live

_生成时间：2026-07-15 · promotion offline + bounded live metadata · **无 commit** · **无 push**_

> **性质：** B-FM-18 routing edge 后最高价值续包 — 晋升 BD2E578 / BD2E080 → known_003/004 并完成 allow-list live  
> **不造** validation_design §7 FP · **不**触碰 A/C/D · **不**写 verified · **不**下载 PDF  
> **不**重开已 LIVE_PASS 案例 · **不**改共享 corpus validator

---

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | harvest promotion | BD2E578 → shareholder_meeting_known_003（决议） | **执行** — 主路径 |
| 2 | harvest promotion | BD2E080 → shareholder_meeting_known_004（召开公告无通知） | **执行** — 同包第二边角 |
| 3 | bounded live | known_003/004 allow-list metadata | **执行** — dry-run 通过后同包闭合 |
| 4 | bounded live | 重跑 known_001/002 / meeting_sample_002 | **拒绝** — 不重开 closed LIVE_PASS |
| 5 | fake §7 FP | 新造 FP lineage | **拒绝** — 禁止 |

---

## 2. 晋升

| case_id | prior → new | evidence | title_pattern / window |
|---------|-------------|---------|------------------------|
| `shareholder_meeting_known_003` | （新增）→ **ready** | BD2E578 迈克生物 300463 · ann=1224015259 · 2025-06-27 | `股东大会决议` · 2025-06-26~29 |
| `shareholder_meeting_known_004` | （新增）→ **ready** | BD2E080 中信特钢 000708 · ann=1223998647 · 2025-06-26 | `股东大会的公告` · 2025-06-25~28 |

路由（依赖 B-FM-18）：股东大会+决议 / 召开+股东大会（无通知；排除法律意见/会议材料）→ `shareholder_meeting_material` / `cninfo_general_announcement_pdf`。

与既有可区分：

| case | pattern | 公司 |
|------|---------|------|
| `shareholder_meeting_known_001` | `股东大会通知` | 航天智造 300446 |
| `shareholder_meeting_known_002` | `股东大会的通知` | 恒邦股份 002237 |
| `shareholder_meeting_known_003` | `股东大会决议` | 迈克生物 300463 |
| `shareholder_meeting_known_004` | `股东大会的公告` | 中信特钢 000708 |

---

## 3. Allow-list（live）

仅 `shareholder_meeting_known_003` + `shareholder_meeting_known_004`；category 空。  
排除全部既有 LIVE_PASS / placeholder / guard。

---

## 4. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_shareholder_meeting_known_003_004_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_003_004_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_002_promotion.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_002_live.py` | **3 OK**（不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_sample_promotion.py` | **6 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_shareholder_meeting_resolution_edge.py` | **9 OK**（B-FM-18 不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | **PASS** · ready=**27** · invalid_ready=0 · placeholder=2 |
| fixture dry-run | **DRY_RUN_PASS** · ready=**27** · query=0 |
| allow-list dry-run | **DRY_RUN_PASS** · ready=**2** · query=0 |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

### Live 细节

| 项 | 值 |
|----|-----|
| allow-list | `shareholder_meeting_known_003` + `shareholder_meeting_known_004` |
| CNINFO | **4**（2 topSearch + 2 query；无 PDF） |
| wall | **~17.0 s**（`REQUEST_TIMEOUT=45`） |
| PDF | **0** |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `shareholder_meeting_known_003` | 2025年第二次临时股东大会决议公告 | 2025-06-27 | classified_correctly / shareholder_meeting_material | **pass** |
| `shareholder_meeting_known_004` | 关于召开2025年第二次临时股东大会的公告 | 2025-06-26 | classified_correctly / shareholder_meeting_material | **pass** |

### 运行备注（显式，非静默）

1. 一次性 wrapper：`REQUEST_TIMEOUT=45`（与 B-FM-15/17 同惯例）。**未**修改共享 `validate_cninfo_b_class_corpus_retrieval.py`。
2. 首跑即 LIVE_PASS；无网络失败试跑；无 orgId fallback。
3. predicted_type=`shareholder_meeting_material`；route=`cninfo_general_announcement_pdf`（与 B-FM-18 对齐）。

---

## 5. Capability Gain

- 「股东大会决议」进入 **known-document ready** 并经公司窗 live metadata 确认（known_003）
- 「召开…股东大会的公告」（无「通知」）进入 **known-document ready** 并经 live 确认（known_004）
- 闭合 B-FM-18 route → B-FM-19 promote → live 链路；与 known_001/002 通知类边角可区分
- **不**声称 B complete / verified / full-market %

---

## 6. Gate

```text
b_class_shareholder_meeting_known_003_004_promotion_live_gate = LIVE_PASS
task_id = B-FM-19
cninfo_calls_this_package = 4
live_calls_final_success = 4
pdf_download = 0
allow_list = shareholder_meeting_known_003,shareholder_meeting_known_004
fake_section7_fp = no
ready_for_commit = true
```

---

## 7. 产物

| 路径 | 用途 |
|------|------|
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | known_003/004 ready |
| `lab/test_cninfo_b_class_shareholder_meeting_known_003_004_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_shareholder_meeting_known_003_004_live.py` | allow-list + mock live 锁测 |
| `outputs/validation/cninfo_b_class_shareholder_meeting_known_003_004_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_shareholder_meeting_known_003_004_live_20260715/` | allow-list + live 证据包 |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_{report.csv,summary.md}` | ready 选择器刷新 |
| 本文件 | 任务报告 |

---

## 8. Return Block

| 字段 | 值 |
|------|-----|
| task | B-FM-19 股东大会决议 / 召开公告 known-document promotion + bounded live（BD2E578 / BD2E080） |
| files | fixtures known · promotion/live 锁测 · dry-run + live 证据包 · ready-case 报告 · 本报告 |
| tests | promotion **7 OK** · live allow-list **3 OK** · 既有 shareholder 锁测不回退 · select ready=27 · dry-run PASS · live **2/2 LIVE_PASS** |
| CNINFO | **4** |
| allow-list | `shareholder_meeting_known_003`, `shareholder_meeting_known_004` |
| wall | offline unit + select + dry-run + live **~17.0 s** |
| ready_for_commit | **true** |

---

## 9. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. `periodic_guard_001`（延期披露）仍缺 harvest，不宜硬推。
3. 真·监管问询函原文仍缺 harvest，不宜硬推 `regulatory_known_003`。
4. 可选：更多 IR / 监管边角 harvest 晋升（需新证据）。
