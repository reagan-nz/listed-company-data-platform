# CNINFO D 类 Known Event Targeted Probe — Runner Extension Summary

_生成时间：2026-07-09_

> **性质：** offline runner extension + dry-run only · **CNINFO calls = 0** · **NOT APPROVED for live**

---

## 1. Implemented Flags

| Flag | 状态 |
|------|------|
| `--known-event-targeted-probe` | **已实现** |
| `--approve-d-class-known-event-targeted-probe` | **已实现**（live guard only · live 路径未实现） |
| `--universe-csv` | 必需显式 universe |
| `--output-root` | 默认 `cninfo_d_class_known_event_targeted_probe/` |
| `--dry-run` | 默认模式 |

---

## 2. Universe Validation Rules

- universe size **= 2**
- 仅允许 `DLC003R-T01` · `DLC006R-T01`
- `replacement_case_id` 仅 `DLC003R` · `DLC006R`
- 拒绝 old `DLC003` / `DLC006`
- 拒绝 baseline `DLC001`–`DLC007`
- `targeted_probe_include = yes` 必需

---

## 3. Anchor-Date Validation

| targeted_probe_id | anchor_date | component |
|-------------------|-------------|-----------|
| DLC003R-T01 | **2024-02-19** | `restricted_shares_unlock` |
| DLC006R-T01 | **2024-07-16** | `shareholder_change` |

---

## 4. Company Code Validation

| targeted_probe_id | company_code |
|-------------------|--------------|
| DLC003R-T01 | **688671** |
| DLC006R-T01 | **301259** |

---

## 5. Request Cap Validation

| 项 | cap |
|----|-----|
| per row | ≤ **12** |
| total | ≤ **24** |

---

## 6. Output Root Isolation

```text
outputs/validation/cninfo_d_class_known_event_targeted_probe/
```

写保护：v1/v2 tiny-live · replacement live · original/calibrated universe

---

## 7. Approval Guard

- dry-run：无需 approval flag
- live：需 `--approve-d-class-known-event-targeted-probe`
- 错误 approval flag：拒绝 · **0 CNINFO**
- live 路径：返回 `known_event_targeted_probe_live_not_implemented`

---

## 8. Tests

| 项 | 结果 |
|----|------|
| test file | `lab/test_cninfo_d_class_known_event_targeted_probe_runner.py` |
| result | **27/27 PASS** |

---

## 9. Dry-Run Result

| 指标 | 值 |
|------|-----|
| cases | **2/2 planned_ok** |
| DLC003R-T01 planned | **12** |
| DLC006R-T01 planned | **12** |
| planned_request_count_total | **24** |
| CNINFO calls | **0** |
| dry-run report | [d_class_known_event_targeted_probe_dryrun_report.csv](reports/d_class_known_event_targeted_probe_dryrun_report.csv) |
| dry-run summary | [d_class_known_event_targeted_probe_dryrun_summary.md](reports/d_class_known_event_targeted_probe_dryrun_summary.md) |

---

## 10. Future Live Command（NOT APPROVED）

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

## 11. Safety Confirmations

| 项 | 状态 |
|----|------|
| CNINFO calls | **0** |
| live executed | **no** |
| old DLC003/DLC006 | **excluded** |
| baseline rows | **excluded** |
| original/calibrated universe | **untouched** |
| replacement live reports | **untouched** |
| PDF/OCR/extraction/DB/MinIO/RAG | **blocked** |
| verified / production_ready | **not marked** |

---

## 12. Gate

```text
approval_status = NOT_APPROVED
approved_for_implementation = true
approved_for_live = false
d_class_known_event_targeted_probe_runner_extension_gate = READY_FOR_APPROVAL
d_class_known_event_targeted_probe_planning_gate = READY_FOR_APPROVAL
d_class_known_event_replacement_validation_execution_gate = FAIL_REVIEW_REQUIRED
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

---

## 13. Next Recommended Task

人工评审 runner extension gate → 批准后 **实现 targeted probe live 路径** + mock tests（**仍无 live 直至显式 `--approve`**）
