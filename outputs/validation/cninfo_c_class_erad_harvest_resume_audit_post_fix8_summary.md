# CNINFO C 类 Era D — Harvest Resume Audit Post Status-fix-8 Summary

_生成时间：2026-07-10_

> **offline dry-run · read-only harvest** · **CNINFO = 0** · **prior audit root untouched**

---

## 执行

```bash
python3 lab/run_cninfo_c_class_harvest_resume_audit.py --dry-run \
  --harvest-root outputs/harvest/cninfo_c_class \
  --protected-roots-csv outputs/validation/cninfo_c_class_erad_protected_output_roots.csv \
  --output-root outputs/validation/cninfo_c_class_erad_harvest_resume_audit_post_fix8/
```

**新输出根：** `outputs/validation/cninfo_c_class_erad_harvest_resume_audit_post_fix8/`  
**先验审计根（未覆盖）：** `outputs/validation/cninfo_c_class_erad_harvest_resume_audit/`

---

## 863_primary 计数对比

| resume_state | 先验（pre-fix8） | 本次（post-fix8） | Δ |
|--------------|------------------|-------------------|---|
| **complete** | **805** | **813** | **+8** |
| **needs_review** | **58** | **50** | **−8** |
| partial | 0 | 0 | 0 |
| missing | 0 | 0 | 0 |
| unknown | 0 | 0 | 0 |
| **合计** | **863** | **863** | 0 |

**结论：** status-fix-8 生效符合预期 · **needs_review 58 → 50** · **complete 805 → 813**

---

## Status-fix-8 八家逐公司

| company_code | prior | new | changed |
|--------------|-------|-----|---------|
| 000009 | needs_review | **complete** | yes |
| 000011 | needs_review | **complete** | yes |
| 000021 | needs_review | **complete** | yes |
| 000034 | needs_review | **complete** | yes |
| 000050 | needs_review | **complete** | yes |
| 000069 | needs_review | **complete** | yes |
| 000155 | needs_review | **complete** | yes |
| 000166 | needs_review | **complete** | yes |

**先验 notes：** `normalized_on_disk_without_status_row`  
**本次 notes：** `status_csv_complete_sources_ok`

**仅 8 家公司 state 变化** · 其余 855 家不变。

---

## 剩余 needs_review（50）

- **6** 家 partial-6：`accept_with_caveat` · needs_live_resume **0/6**
- **44** 家：`source_count_mismatch` / `accept_as_complete_with_caveat`（58 triage 分类）
- **无** partial / missing on 863_primary

---

## 产出物

| 文件 | 说明 |
|------|------|
| [reports/c_class_erad_harvest_resume_audit_report.csv](cninfo_c_class_erad_harvest_resume_audit_post_fix8/reports/c_class_erad_harvest_resume_audit_report.csv) | 全量报告 |
| [reports/c_class_erad_harvest_resume_audit_summary.md](cninfo_c_class_erad_harvest_resume_audit_post_fix8/reports/c_class_erad_harvest_resume_audit_summary.md) | runner 摘要 |
| [reports/c_class_erad_harvest_resume_audit_metrics.csv](cninfo_c_class_erad_harvest_resume_audit_post_fix8/reports/c_class_erad_harvest_resume_audit_metrics.csv) | 指标 |
| [reports/c_class_erad_harvest_resume_audit_source_ledger.csv](cninfo_c_class_erad_harvest_resume_audit_post_fix8/reports/c_class_erad_harvest_resume_audit_source_ledger.csv) | 源 ledger |
| [delta CSV](cninfo_c_class_erad_harvest_resume_audit_post_fix8_delta.csv) | 863 逐公司 prior/new |
| [run_meta.json](cninfo_c_class_erad_harvest_resume_audit_post_fix8/run_meta.json) | 元数据 |

---

## Runner 小修

`run_cninfo_c_class_harvest_resume_audit.py` — `_write_csv` / `_write_json` / `_write_summary_md` 现传递 `allowed_audit_root_rel`，支持非默认 audit 输出根（仍经 cleanup_guard）。

---

## Gate

```
c_class_erad_harvest_resume_audit_post_fix8_gate = PASS_OFFLINE
```

**NOT APPROVED live** · **NOT verified**

保留：`approved_for_live_resume = false` · `approved_for_snapshot_rebuild = false`

---

## 红线

No CNINFO · read-only production · no live · no commit/push · Era D **not finished**
