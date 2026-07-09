# CNINFO B 类 Phase 1 Schema Freeze Signoff Summary

_生成时间：2026-07-09_

> **性质：** signoff 文档化快照；无 CNINFO · 无 live · 无 harvest · registry YAML **未修改**。  
> **批准记录：** [cninfo_b_class_phase1_schema_freeze_approval_draft.md](../../plans/cninfo_b_class_phase1_schema_freeze_approval_draft.md)

---

## Signoff Counts

| 指标 | 数量 |
|------|------|
| Approved required fields | **15** |
| Downgraded fields | **2** |
| Moved outside Phase 1 | **4** |
| Phase 1 in-scope endpoints | **4** |
| Deferred Phase 2 endpoints | **2** |
| Removed endpoints | **1** |

---

## Approved Required Fields（15）

`company_code` · `org_id` · `announcement_id` · `announcement_title` · `announcement_time` · `announcement_date` · `document_id` · `retrieval_time` · `raw_hash` · `quality_status` · `pdf_url` · `adjunct_url` · `source_endpoint` · `lineage_status` · `announcement_category`

---

## Downgraded Fields（2）

- `timeline_company_code` — required → recommended
- `timeline_announcement_date` — required → recommended

---

## Endpoint Decisions

### In scope（4）

- EP001 hisAnnouncement/query
- EP002 topSearch/query（linkage helper）
- EP004 cninfo_periodic_report_pdf
- EP005 cninfo_general_announcement_pdf

### Deferred Phase 2（2）

- EP006 cninfo_inquiry_reply_pdf
- EP007 cninfo_meeting_notice_pdf

### Removed（1）

- EP003 disclosure/list/notice UI hint

---

## Remaining Risks

| 风险 | 级别 | 说明 |
|------|------|------|
| Live validation not run | high | 所有 endpoint `live_validation_status=not_run`；signoff 仅基于离线评审 |
| EP006/EP007 endpoint null | high | registry 中 query_endpoint 为空；Phase 2 前须补 endpoint 或显式 defer |
| EP005 category alignment | medium | `cninfo_general_announcement_pdf` 官方 category code 未完全对齐 |
| Dedup policy | medium | 仅假设 `announcement_id` 唯一；无实现 |
| Rate limit policy | low | registry 默认 sleep 0.6s；无并发执行器 |
| C-class Phase 3 parallel | medium | live harvest 可能在另一终端；B-class implementation 须隔离带宽 |
| Minimum fields CSV stale | low | 原始 catalog 仍为 17 required；freeze v1 catalog 待 implementation 生成 |

---

## Next Implementation Step

执行 [cninfo_b_class_phase1_freeze_v1_implementation_plan.md](../../plans/cninfo_b_class_phase1_freeze_v1_implementation_plan.md) **Step 1–5（全部 offline）**：

1. 更新 `config/cninfo_b_class_source_registry_draft.yaml`（general revise · inquiry/meeting defer 注释）
2. 生成 Phase 1 freeze v1 fixtures
3. 发布 freeze v1 field catalog CSV
4. 创建 offline schema lint
5. 扩展 ready-case benchmark

**Step 6（live validation approval）仅在 Step 1–5 完成后申请。**

---

## Gate

```text
b_class_phase1_schema_freeze_signoff_gate = READY_FOR_IMPLEMENTATION
```

**不是 PASS** — freeze implementation 尚未启动。

---

## Parallel Safety

- C-class status: **`SNAPSHOT_GENERATED_QA_REVIEW`**
- `outputs/harvest/cninfo_c_class/phase3_batch_500_001/`: **untouched**
- No B-class live execution
