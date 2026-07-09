# CNINFO B 类 Phase 1 Schema Freeze Review Summary

_生成时间：2026-07-09_

> **性质：** 离线设计评审快照；无 CNINFO · 无 live · 无 harvest · 无 PDF 下载/解析。  
> **评审文档：** [cninfo_b_class_phase1_schema_freeze_review.md](../../plans/cninfo_b_class_phase1_schema_freeze_review.md)

---

## Current State

B-class planning 与 artifact inventory 已完成（gate **`DESIGN_STARTED`** · inventory **`PASS`**）。

本轮将 inventory 发现转化为：

- endpoint candidate 结构化表
- Phase 1 minimum fields catalog
- registry alignment 报告
- schema freeze review（**待人工批准**）

C-class 状态保持 **`SNAPSHOT_GENERATED_QA_REVIEW`**；`outputs/harvest/cninfo_c_class/phase3_batch_500_001/` **未触碰**。

---

## Endpoint Candidates

| 指标 | 数量 |
|------|------|
| 总候选数 | **7** |
| high priority | **4**（EP001 · EP002 · EP004 · EP005） |
| endpoint null / unknown | **2**（EP006 · EP007） |
| UI-only / non-API | **1**（EP003 · risk=high） |
| live_validation_status | **7/7 = not_run** |

明细：[cninfo_b_class_endpoint_candidate_table.csv](cninfo_b_class_endpoint_candidate_table.csv)

---

## Minimum Fields

| 指标 | 数量 |
|------|------|
| 总字段数 | **46** |
| required | **17** |
| recommended | **14** |
| optional | **2** |
| raw_only | **1** |
| review_later | **12** |

明细：[cninfo_b_class_phase1_minimum_fields.csv](cninfo_b_class_phase1_minimum_fields.csv)

Phase 1 **不包含** PDF 正文字段、page_count、sha256（文件级）、storage_uri、embedding 字段。

---

## Registry Alignment

明细：[cninfo_b_class_source_registry_alignment_report.csv](cninfo_b_class_source_registry_alignment_report.csv)

| 结论 | 数量 |
|------|------|
| registry 源总数 | **4** |
| endpoint present | **2**（periodic · general） |
| endpoint null | **2**（inquiry · meeting） |
| keep | **1** |
| revise | **1** |
| add_missing_endpoint | **2** |

主要缺口：

- `cninfo_general_announcement_pdf`：官方 category code 与 title_positive_patterns 待修订
- `cninfo_inquiry_reply_pdf` / `cninfo_meeting_notice_pdf`：endpoint null、params_template 空、缺专用 fixture

---

## Gate

```text
b_class_phase1_schema_freeze_review_gate = READY_FOR_APPROVAL
```

**未**标记为最终 frozen（不是 `PASS` / `FROZEN`）。

---

## Next Recommended Task

**人工 review / approve schema freeze v1**（审阅 minimum fields CSV + endpoint candidate 表 + registry alignment 报告）。

批准后下一步（仍 offline 优先）：

1. 修订 `config/cninfo_b_class_source_registry_draft.yaml`（补 inquiry/meeting endpoint 或显式 defer 注释）
2. 为 inquiry / meeting 源补专用 fixture 草案
3. 再申请 tiny live metadata sample（需单独 live approval）

**No live execution yet.**

---

## Parallel Safety

- No B-class live execution in this round
- No C-class Phase 3 output modification
- C-class status: **`SNAPSHOT_GENERATED_QA_REVIEW`**
