# CNINFO C 类 Era D — Local Retention Summary

_生成时间：2026-07-10_

> **offline documentation only** · **CNINFO = 0** · **no production mutation**

---

## 包内容

| # | 文件 |
|---|------|
| 1 | [local retention policy](../../plans/cninfo_c_class_erad_local_retention_policy.md) |
| 2 | [local artifact index](cninfo_c_class_erad_local_artifact_index.md) |
| 3 | [gitignore retention notes](cninfo_c_class_erad_gitignore_retention_notes.md) |
| 4 | 本 summary |
| 5 | [next-step recommendation](cninfo_c_class_erad_local_retention_next_step_recommendation.md) |

---

## 关键保留规则（摘要）

1. **KEEP_LOCAL · gitignore：** 863 harvest（**~325M**）+ 491/863 snapshot（**~70M**）— Era D MVP 核心资产 · **Option A HOLD** 不删不 rebuild。
2. **生产根默认 read-only：** 写入仅在人批 + backup 后（status-fix-8 先例）；测试仅删 `_mock_*`。
3. **validation 可提交：** `plans/`、`lab/` guard/runner、`outputs/validation/cninfo_c_class_erad_*summary.md` 与小 ledger。
4. **备份纪律：** 生产 CSV 写入前 `*.bak_erad_<slice>_<timestamp>`（见 status-fix-8 backup）。
5. **无 MinIO：** 本地磁盘 ~**400M** C-line footprint · 不默认 prune 生产根。

---

## 当前状态快照

| 项 | 值 |
|----|-----|
| status CSV rows | **861**（post status-fix-8） |
| status backup | `.bak_erad_status_fix_8_20260710T080910Z`（853 rows） |
| 491 snapshot | **492** files · **~25M** |
| 863 snapshot | **863** JSON · **~45M** |
| partial-6 | needs_live_resume **0/6** |
| rebuild / live | **NOT APPROVED** |

---

## 附录：Post status-fix-8 audit 预期（未执行）

重跑 `run_cninfo_c_class_harvest_resume_audit.py`（CNINFO=0 · read-only）时，863_primary `needs_review` **可能从 58 降至 50**（8 家 missing_status_row 已 append complete）。**本包未执行**；留作下一可选切片。

---

## Gate

```
c_class_erad_local_retention_gate = PASS_OFFLINE
```

**NOT verified** · **NOT approved_for_live_resume** · **NOT approved_for_snapshot_rebuild**

---

## 红线

No CNINFO · no live · no production write · no commit/push · Era D **not finished** · C-line **continues**
