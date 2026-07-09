# CNINFO B 类 Phase 1 Live Validation Checklist

_生成时间：2026-07-09_

> **性质：** 未来 live 执行前检查清单；**本轮不执行 live**。  
> **批准计划：** [cninfo_b_class_phase1_live_validation_approval_plan.md](../../plans/cninfo_b_class_phase1_live_validation_approval_plan.md)

---

## 执行前全局检查

- [ ] `b_class_phase1_freeze_v1_implementation_gate = PASS_OFFLINE`
- [ ] `b_class_ready_case_benchmark_gate = READY_FOR_REVIEW` 已人工审阅
- [ ] C-class Phase 3 live harvest **未在并发运行**
- [ ] 输出根 = `outputs/validation/cninfo_b_class_live_validation/` only
- [ ] **不**下载 PDF · **不**解析 PDF · **不**写 verified

---

## EP001 — hisAnnouncement/query

| 项 | 内容 |
|----|------|
| **Purpose** | 主公告列表检索；获取 announcement metadata + adjunctUrl |
| **Expected fields** | `announcementId` · `announcementTitle` · `announcementTime` · `adjunctUrl` · `secCode` · `orgId` |
| **Rate limit concern** | POST 分页请求；须 sleep ≥0.6s；禁止 burst |
| **Failure handling** | `empty_response` · `network_error` · HTTP 429 → 停止并记录，不 retry storm |
| **Quality checks** | required 字段映射完整；`pdf_url` 由 `adjunctUrl` 规范化；`source_endpoint` 记录本 URL |

---

## EP002 — topSearch/query

| 项 | 内容 |
|----|------|
| **Purpose** | orgId 发现辅助；**非**文档列表 endpoint |
| **Expected fields** | `orgId` · `code` · `zwjc`（records[]） |
| **Rate limit concern** | 仅在 `org_id` 缺失时调用；每公司最多 1 次 |
| **Failure handling** | 无 orgId → 标记 `needs_review`；不 fallback 猜测 orgId |
| **Quality checks** | 不得将 topSearch 响应误当作 announcement 列表；无 PDF metadata 期望 |

---

## EP004 — cninfo_periodic_report_pdf

| 项 | 内容 |
|----|------|
| **Purpose** | 定期报告 PDF metadata 源（年报/半年报/季报） |
| **Expected fields** | 15 required + title/period 规则；`document_type` periodic enum |
| **Rate limit concern** | 继承 EP001；每公司每 report_type 单独查询时注意日期窗 |
| **Failure handling** | `title_excluded` · `period_mismatch` · `not_found` 分别记录 |
| **Quality checks** | 不得将问询函/说明会标题误入 periodic；`quality_status` 按 fixture 口径 |

---

## EP005 — cninfo_general_announcement_pdf

| 项 | 内容 |
|----|------|
| **Purpose** | 非定期公告 PDF metadata 源 |
| **Expected fields** | 15 required；category 可为 unknown/review_later |
| **Rate limit concern** | 同 EP001；category 参数对齐 TODO 时先用宽窗 + title routing |
| **Failure handling** | 未知 category → `needs_review`（见 RC005）；不 forced mapping |
| **Quality checks** | RC003 路径：无 pdf_url 时 `needs_review`；不得标 verified |

---

## Post-run 检查

- [ ] live_report.csv 写入 isolation root
- [ ] 所有 endpoint `live_validation_status` 在报告中更新为 `ran`（仅 live 回合）
- [ ] 无 PDF 文件落盘
- [ ] C-class Phase 3 输出根未被触碰
- [ ] gate **仍不是** verified / PASS（仅 live sample 完成）

---

## Gate Reference

```text
b_class_phase1_live_validation_gate = READY_FOR_APPROVAL
```

Live 执行前须用户显式批准。
