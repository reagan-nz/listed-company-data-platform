# CNINFO B 类 B-FM-16 — 股东大会通知「的」助词变体 Known-Document Promotion（Offline）

_生成时间：2026-07-15 · offline only · **CNINFO = 0** · **无 live** · **无 commit** · **无 push**_

> **性质：** B-FM-15 LIVE_PASS 后最高价值续包 — 消费未占用 harvest BD2E292（恒邦股份「股东大会的通知」）  
> **不造** validation_design §7 FP · **不**触碰 A/C/D · **不**写 verified  
> **不**做 bounded live（本包优先消费晋升；live 留给后续 allow-list）

---

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | harvest promotion | BD2E292 → shareholder_meeting_known_002 | **执行** — 主路径（「的」助词变体；与 known_001 / sample_002 可区分） |
| 2 | bounded live | known_002 allow-list metadata | **推迟** — 晋升后独立任务 |
| 3 | harvest promotion | periodic_guard_001（延期披露） | **推迟** — harvest 仍无「延期披露」行 |
| 4 | harvest promotion | 真·监管问询函原文 known_003 | **拒绝** — harvest 仍无可区分样本；BD2E500 为「延期回复」边角（路由锁测已覆盖，不宜填 known_003） |
| 5 | fake §7 FP | 新造 FP lineage | **拒绝** — 禁止 |

---

## 2. 晋升

| case_id | prior → new | evidence | title_pattern / window |
|---------|-------------|---------|------------------------|
| `shareholder_meeting_known_002` | （新增槽位）→ **ready** | BD2E292 恒邦股份 002237 · ann=1224014462 · 2025-06-27 | `股东大会的通知` · 2025-06-26~29 |

路由：纯「股东大会」+「通知」（含「的」助词）→ `shareholder_meeting_material` / `cninfo_general_announcement_pdf`。

与既有可区分：

| case | pattern | 公司 |
|------|---------|------|
| `shareholder_meeting_known_001` | `股东大会通知`（连续子串） | 航天智造 300446 |
| `meeting_sample_002` | `股东大会通知` | 全市场窗（锚定 known_001） |
| `shareholder_meeting_known_002` | `股东大会的通知`（含「的」） | 恒邦股份 002237 |

`_title_matches`：known_002 pattern **不**命中 known_001 标题；known_001 pattern **不**命中 BD2E292 标题。

---

## 3. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_shareholder_meeting_known_002_promotion.py` | **7 OK** |
| `python lab/test_cninfo_b_class_shareholder_meeting_sample_promotion.py` | **6 OK**（B-FM-14 不回退） |
| `python lab/test_cninfo_b_class_shareholder_meeting_sample_promotion_live.py` | **3 OK**（B-FM-15 不回退） |
| `python lab/test_cninfo_b_class_regulatory_work_letter_promotion.py` | **5 OK**（不回退） |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | **PASS** · ready=**25** · invalid_ready=0 · placeholder=2 |
| dry-run corpus retrieval | **DRY_RUN_PASS** · ready=**25** · query=0 |
| CNINFO calls | **0** |
| live | **none** |
| allow-list | **无**（未开启 live） |

---

## 4. Capability Gain

- 「股东大会的通知」助词变体进入 **known-document ready**（槽位 `shareholder_meeting_known_002`）
- 闭合 B-FM-15 live 后未占用 harvest BD2E292 晋升链
- 显式锁住 title_pattern 与连续「股东大会通知」的互斥匹配行为
- **不**声称 B complete / verified / full-market %

---

## 5. Gate

```text
b_class_shareholder_meeting_known_002_promotion_gate = PASS_OFFLINE
task_id = B-FM-16
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
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | shareholder_meeting_known_002 ready |
| `lab/test_cninfo_b_class_shareholder_meeting_known_002_promotion.py` | 离线晋升锁测 |
| `outputs/validation/cninfo_b_class_shareholder_meeting_known_002_promotion_dry_run_*_20260715.*` | dry-run |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_{report.csv,summary.md}` | ready 选择器刷新 |
| 本文件 | 任务报告 |

---

## 7. Return Block

| 字段 | 值 |
|------|-----|
| task | B-FM-16 股东大会通知「的」助词变体 known-document promotion（offline；BD2E292） |
| files | fixtures known · `lab/test_cninfo_b_class_shareholder_meeting_known_002_promotion.py` · dry-run + ready-case 报告 · 本报告 |
| CNINFO | **0** |
| allow-list | **none** |
| wall | offline unit + select + dry-run only |
| ready_for_commit | **true** |

---

## 8. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选 bounded live：allow-list = `shareholder_meeting_known_002`；需独立批准。
3. `periodic_guard_001`（延期披露）仍缺 harvest，不宜硬推。
4. 真·监管问询函原文仍缺 harvest，不宜硬推 `regulatory_known_003`。
