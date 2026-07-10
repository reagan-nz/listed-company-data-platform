# CNINFO D 类 Known Event Targeted Probe — Live Implementation Summary

_生成时间：2026-07-09_

> **性质：** live 路径离线实现 + mock tests only · **CNINFO calls = 0** · **NOT APPROVED for live**

---

## 1. Implemented Live Path

| 项 | 状态 |
|----|------|
| `--known-event-targeted-probe --live` | **已实现** |
| `--approve-d-class-known-event-targeted-probe` | **已实现**（approval guard） |
| `execute_known_event_targeted_probe_live()` | **已实现** |
| 真实 CNINFO live | **未执行** |

---

## 2. Anchor-Date Probe Behavior

| targeted_probe_id | component | anchor | strategy |
|-------------------|-----------|--------|----------|
| DLC003R-T01 | `restricted_shares_unlock` | 2024-02-19 | anchor ±7d · ±30d · month-end `tdate`（liftBan/detail） |
| DLC006R-T01 | `shareholder_change` | 2024-07-16 | anchor ±7d · `type=inc/desc` + `tdate`（shareholeder/detail） |

- 仅使用既有 D-class endpoint/probe family
- 无 PDF/OCR/extraction
- early stop on company-level hit

---

## 3. Request Caps

| 项 | cap |
|----|-----|
| DLC003R-T01 | ≤ **12** |
| DLC006R-T01 | ≤ **12** |
| total | ≤ **24** |

---

## 4. Approval Guard

- live 无 `--approve-d-class-known-event-targeted-probe` → 拒绝 · **0 CNINFO**
- 错误 approval flag → 拒绝 · **0 CNINFO**
- targeted probe 与 replacement/v2 模式互斥

---

## 5. Target-Only Scope

- 仅处理 **DLC003R-T01** · **DLC006R-T01**
- 拒绝 old DLC003/DLC006
- 拒绝 baseline DLC001–DLC007
- 不 rerun replacement live DLC003R/DLC006R

---

## 6. Output Isolation & Write Protection

```text
outputs/validation/cninfo_d_class_known_event_targeted_probe/
```

写保护：v1/v2 tiny-live · replacement live · original/calibrated universe · dry-run reports 不被 live writers 覆盖

---

## 7. Report Paths

| 报告 | 路径 |
|------|------|
| live report | `reports/d_class_known_event_targeted_probe_live_report.csv` |
| live summary | `reports/d_class_known_event_targeted_probe_live_summary.md` |
| quality report | `reports/d_class_known_event_targeted_probe_quality_report.csv` |

---

## 8. Execution Gate Logic

| 结果 | gate |
|------|------|
| 双 case 可接受（found+records 或 needs_review+records） | `PASS_WITH_CAVEAT` |
| 一成功一失败 / 双失败 | `FAIL_REVIEW_REQUIRED` |

**永不使用 `PASS`** · **不标记 verified / production_ready**

---

## 9. Tests

| 项 | 结果 |
|----|------|
| runner tests | **27/27 PASS** |
| live-path tests | **29/29 PASS**（mock `_cninfo_request` · **无真实 CNINFO**） |
| test file | `lab/test_cninfo_d_class_known_event_targeted_probe_live_path.py` |

---

## 10. Safety Confirmations

| 项 | 状态 |
|----|------|
| CNINFO calls（本回合） | **0** |
| 真实 live executed | **no** |
| old DLC003/DLC006 | **excluded** |
| baseline rows | **excluded** |
| replacement live reports | **untouched** |
| dry-run reports | **untouched**（live writers 使用独立文件名） |
| original/calibrated universe | **untouched** |
| PDF/OCR/extraction/DB/MinIO/RAG | **blocked** |

---

## 11. Future Live Command（NOT APPROVED）

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --known-event-targeted-probe \
  --live \
  --universe-csv outputs/validation/cninfo_d_class_known_event_targeted_probe_universe_draft.csv \
  --output-root outputs/validation/cninfo_d_class_known_event_targeted_probe/ \
  --approve-d-class-known-event-targeted-probe
```

**Do not execute**

---

## 12. Gate

```text
approval_status = NOT_APPROVED
approved_for_live = false
d_class_known_event_targeted_probe_live_implementation_gate = READY_FOR_APPROVAL
d_class_known_event_targeted_probe_runner_extension_gate = READY_FOR_APPROVAL
d_class_known_event_replacement_validation_execution_gate = FAIL_REVIEW_REQUIRED
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

---

## 13. Next Recommended Task

人工评审 live implementation gate → 批准后 **isolated targeted probe live**（cap ≤24 · 仅 DLC003R-T01/DLC006R-T01）
