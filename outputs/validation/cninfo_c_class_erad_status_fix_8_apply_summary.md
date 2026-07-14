# CNINFO C 类 Era D — Status-fix-8 Apply Summary

_生成时间：2026-07-10_

> **Human approval（verbatim）：**  
> I approve applying C-class Era D status-fix-8 proposed rows to production company_harvest_status.csv.

---

## 执行摘要

| 项 | 值 |
|----|-----|
| Production CSV | `outputs/harvest/cninfo_c_class/quality/company_harvest_status.csv` |
| Backup | `outputs/harvest/cninfo_c_class/quality/company_harvest_status.csv.bak_erad_status_fix_8_20260710T080910Z` |
| Rows before | **853** |
| Rows after | **861**（**+8** appended） |
| Apply outcomes | **8 appended** · **0 already_present** · **0 skipped** |
| Post-verify | **8/8 ok** · `harvest_status=complete` |
| CNINFO | **0** |

---

## 8/8 Apply Outcomes

| company_code | action | after_status | post_verify_ok |
|--------------|--------|--------------|----------------|
| 000009 | appended | complete | yes |
| 000011 | appended | complete | yes |
| 000021 | appended | complete | yes |
| 000034 | appended | complete | yes |
| 000050 | appended | complete | yes |
| 000069 | appended | complete | yes |
| 000155 | appended | complete | yes |
| 000166 | appended | complete | yes |

---

## 唯一生产写入

- **仅** `company_harvest_status.csv` append（8 行）+ timestamped backup
- **未** 修改 normalized / raw / snapshot
- **未** 触及 6 家 needs_human_review 公司

---

## 产出物

| 文件 | 说明 |
|------|------|
| [backup path note](cninfo_c_class_erad_status_fix_8_apply/reports/status_fix_8_apply_backup_path.txt) | 备份路径 |
| [apply ledger](cninfo_c_class_erad_status_fix_8_apply/reports/status_fix_8_apply_ledger.csv) | 逐公司结果 |
| [run_meta.json](cninfo_c_class_erad_status_fix_8_apply/run_meta.json) | 元数据 |
| Runner | `lab/run_cninfo_c_class_erad_status_fix_8_apply.py` |

---

## Gate

```
c_class_erad_status_fix_8_apply_gate = PASS_WITH_CAVEAT
```

**NOT verified** · **NOT live** · **NOT snapshot rebuild**

保留：

- `approved_for_live_resume = false`
- `approved_for_snapshot_rebuild = false`

---

## 红线确认

No CNINFO · no live · no normalized/snapshot writes · no holdout promotion · no commit/push · Era D **not finished**
