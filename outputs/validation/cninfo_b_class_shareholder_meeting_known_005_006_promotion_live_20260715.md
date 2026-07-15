# CNINFO B 类 B-FM-21 — 「股东会」简称 Known-005/006 晋升 + Bounded Live

_生成时间：2026-07-15 · promote → dry-run → bounded live · **CNINFO = 4** · **无 PDF** · **无 commit** · **无 push**_

> **性质：** harvest 晋升 + allow-list live metadata · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 known_003/004（已 LIVE_PASS）· **不**触碰 A/C/D  
> standing_scope 允许 CNINFO live；本包仅新晋 `shareholder_meeting_known_005` / `006`

---

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | harvest promotion | BD2E646 → shareholder_meeting_known_005（临时股东会决议） | **执行** — 主路径 |
| 2 | harvest promotion | BD2E276 → shareholder_meeting_known_006（股东会的通知） | **执行** — 同包第二边角 |
| 3 | harvest promotion | BD2E258 → known_007（年度股东会决议） | **推迟** — 与 known_005 同属简称决议族；route 已 B-FM-20 锁测；capability_gain 边际 |
| 4 | bounded live | known_003/004 再跑 | **拒绝** — 已 LIVE_PASS；capability_gain=0 |
| 5 | alternate | periodic_guard_001（延期披露） | **拒绝** — harvest 仍缺 |

---

## 2. Promotion

| case_id | 状态 | harvest | title_pattern | 窗 |
|---------|------|---------|---------------|-----|
| `shareholder_meeting_known_005` | （新增）→ **ready** | BD2E646 康平科技 300907 · ann=1224039628 · 2025-06-30 | `临时股东会决议` · 2025-06-29~07-02 | 简称决议 |
| `shareholder_meeting_known_006` | （新增）→ **ready** | BD2E276 孚日股份 002083 · ann=1223997400 · 2025-06-26 | `股东会的通知` · 2025-06-25~28 | 简称通知 |

路由（依赖 B-FM-20）：「股东会」=「股东大会」同义 → `shareholder_meeting_material` / `cninfo_general_announcement_pdf`。

### 既有锚点（不重开）

| case_id | pattern | 公司 |
|---------|---------|------|
| `shareholder_meeting_known_001` | `股东大会通知` | 航天智造 300446 |
| `shareholder_meeting_known_002` | `股东大会的通知` | 恒邦股份 002237 |
| `shareholder_meeting_known_003` | `股东大会决议` | 迈克生物 300463 |
| `shareholder_meeting_known_004` | `股东大会的公告` | 中信特钢 000708 |

---

## 3. Allow-list

仅 `shareholder_meeting_known_005` + `shareholder_meeting_known_006`；category 空。  
排除全部已 LIVE_PASS / placeholder / guard。

---

## 4. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_shareholder_meeting_known_005_006_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_005_006_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_003_004_promotion.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_003_004_live.py` | **3 OK**（不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_known_002_promotion.py` | **7 OK**（不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_sample_promotion.py` | **6 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_shareholder_meeting_short_form_edge.py` | **10 OK**（B-FM-20 不回退） |
| `python lab/test_cninfo_b_class_category_routing_shareholder_meeting_resolution_edge.py` | **9 OK**（B-FM-18 不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | **PASS** · ready=**29** · invalid_ready=0 · placeholder=2 |
| fixture dry-run | **DRY_RUN_PASS** · ready=**29** · query=0 |
| allow-list dry-run | **DRY_RUN_PASS** · ready=**2** · query=0 |
| bounded live | **LIVE_PASS** · pass=**2**/0/0 |

### Live 细节

| 项 | 值 |
|----|-----|
| allow-list | `shareholder_meeting_known_005` + `shareholder_meeting_known_006` |
| CNINFO | **4**（2 topSearch + 2 query；无 PDF） |
| wall | **~23.2 s** |
| PDF | **0** |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `shareholder_meeting_known_005` | 2025年第五次临时股东会决议公告 | 2025-06-30 | classified_correctly / shareholder_meeting_material | **pass** |
| `shareholder_meeting_known_006` | 关于召开2025年第二次临时股东会的通知 | 2025-06-26 | classified_correctly / shareholder_meeting_material | **pass** |

### 运行备注（显式，非静默）

1. 首跑即 LIVE_PASS；无网络失败试跑；无 orgId fallback。
2. **未**修改共享 `validate_cninfo_b_class_corpus_retrieval.py`；默认 timeout 即可。
3. predicted_type=`shareholder_meeting_material`；route=`cninfo_general_announcement_pdf`（与 B-FM-20 对齐）。

---

## 5. Capability Gain

- 「临时股东会决议」进入 **known-document ready** 并经公司窗 live metadata 确认（known_005）
- 「股东会的通知」进入 **known-document ready** 并经 live 确认（known_006）
- 闭合 B-FM-20 route → B-FM-21 promote → live 链路；与 known_001–004 完整「股东大会」族 pattern 可区分
- BD2E258 年度简称决议仍可后续晋升 known_007（本包不占用）
- **不**声称 B complete / verified / full-market %

---

## 6. Gate

```text
b_class_shareholder_meeting_known_005_006_promotion_live_gate = LIVE_PASS
task_id = B-FM-21
cninfo_calls_this_package = 4
live_calls_final_success = 4
pdf_download = 0
allow_list = shareholder_meeting_known_005,shareholder_meeting_known_006
fake_section7_fp = no
ready_for_commit = true
```

---

## 7. 产物

| 路径 | 用途 |
|------|------|
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | + known_005 / known_006 |
| `lab/test_cninfo_b_class_shareholder_meeting_known_005_006_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_shareholder_meeting_known_005_006_live.py` | allow-list + mock live 锁测 |
| `outputs/validation/cninfo_b_class_shareholder_meeting_known_005_006_promotion_dry_run_*_20260715.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_shareholder_meeting_known_005_006_live_20260715/` | allow-list + live 证据包 |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_{report.csv,summary.md}` | ready=29 刷新 |
| 本文件 | 任务报告 |

---

## 8. Return Block

| 字段 | 值 |
|------|-----|
| task | B-FM-21 「股东会」简称 known_005/006 晋升 + bounded live（BD2E646 / BD2E276） |
| files | fixtures known_005/006 · promotion/live 锁测 · dry-run · live 证据包 · ready summary · 本报告 |
| tests | promotion **7 OK** · live mock **3 OK** · known_002/003/004/sample/short-form/resolution 不回退 · ready **29** · dry-run **PASS** · live **2/2 LIVE_PASS** |
| CNINFO | **4** |
| allow-list | `shareholder_meeting_known_005`, `shareholder_meeting_known_006` |
| wall | live **~23.2 s** |
| ready_for_commit | **true** |

---

## 9. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选：BD2E258 → `shareholder_meeting_known_007`（年度股东会决议）并 bounded live。
3. `periodic_guard_001`（延期披露）仍缺 harvest，不宜硬推。
4. 真·监管问询函原文仍缺 harvest，不宜硬推 `regulatory_known_003`。
