# CNINFO A 类 Phase 1 Schema Freeze v1 人工批准清单

_生成时间：2026-07-09_

> **性质：** 人工批准准备包；不调用 CNINFO；不 live；不下载 PDF；gate **不改为 PASS**（仅人工批准后另开 implementation 回合）。  
> **输入：** [schema freeze review](../../plans/cninfo_a_class_phase1_schema_freeze_review.md) · [field decision matrix](cninfo_a_class_phase1_field_decision_matrix.csv) · [lint summary](cninfo_a_class_phase1_freeze_v1_lint_summary.md) · [fixtures](../../fixtures/a_class/phase1/)

---

## 评审前确认

- [ ] 已阅读 [cninfo_a_class_phase1_schema_freeze_review.md](../../plans/cninfo_a_class_phase1_schema_freeze_review.md)
- [ ] 已阅读 [cninfo_a_class_phase1_schema_freeze_review_summary.md](cninfo_a_class_phase1_schema_freeze_review_summary.md)
- [ ] 已阅读 [cninfo_a_class_phase1_schema_freeze_approval_summary.md](cninfo_a_class_phase1_schema_freeze_approval_summary.md)
- [ ] 确认 lint **10/10 PASS**（[lint summary](cninfo_a_class_phase1_freeze_v1_lint_summary.md)）
- [ ] 确认本轮 **不执行 live**、**不下载 PDF**、**不修改** C-class / B-class 输出
- [ ] 确认 gate **不自动改为 PASS**（须显式人工 signoff）

---

## Required Fields Review

对 freeze v1 提议的 **22** 个 required 字段逐项确认是否纳入 Phase 1 产出契约：

### report_document（13 required）

- [ ] `document_id` — 逻辑文档主键；dedup 与 lineage 锚点
- [ ] `company_code` — 关联 C-class company 与 coverage 分母
- [ ] `report_type` — 四类定期报告枚举（annual / semi_annual / q1 / q3）
- [ ] `report_period` — 报告期；`unknown` 不算 effective found
- [ ] `publish_date` — 规范化披露日
- [ ] `announcement_id` — CNINFO 公告主键
- [ ] `announcement_title` — 标题匹配与 QA
- [ ] `pdf_url` — Phase1 核心产出；not_found 时字段存在、值可为 null
- [ ] `source_endpoint` — metadata 谱系（hisAnnouncement/query）
- [ ] `retrieval_time` — ISO8601 抓取时间
- [ ] `raw_hash` — **自 recommended 升级**；响应级 hash 变更检测
- [ ] `lineage_status` — discovered / linked / needs_review / not_found
- [ ] `quality_status` — pass / caveat / blocked / needs_review

### report_period_snapshot（4 required）

- [ ] `company_code` — 覆盖视图聚合键
- [ ] `year` — 会计年度
- [ ] `report_type` — 与 report_document 对齐
- [ ] `document_id` — 命中链接；未命中时为 null

### document_lineage（5 required）

- [ ] `storage_status` — Phase1 唯一允许值 `not_attempted`
- [ ] `version` — lineage 版本号（初版 = 1）
- [ ] `source_endpoint` — 与 report_document 一致
- [ ] `retrieval_time` — 谱系记录时间
- [ ] `lineage_status` — 与 report_document.lineage_status 对齐

**Required 字段总数确认：** 13 + 4 + 5 = **22**

---

## Lineage Review

- [ ] `document_lineage` 与 `report_document` 通过 `document_id` 关联规则已理解
- [ ] Phase1 禁止填写 `download_time` / `file_hash` / `file_size` 非 null 值
- [ ] `storage_status` 在 Phase1 固定 `not_attempted`（不接受 `stored` / `failed`）
- [ ] `raw_hash` 为响应 JSON hash，**非** PDF 文件 hash
- [ ] `adjunct_url` → `pdf_url` 归一化规则继承 A-class Phase1 retrieval
- [ ] `lineage_status` 在 report_document 与 document_lineage 两处应一致
- [ ] 无 MinIO / object storage URI 字段进入 Phase1 契约

---

## Fixture Review

对 [fixtures/a_class/phase1/](../../fixtures/a_class/phase1/) 三份骨架 fixture 确认：

### report_document_fixture.json

- [ ] `_fixture_meta.cninfo_called = false`
- [ ] `_fixture_meta.pdf_downloaded = false`
- [ ] 含全部 13 个 freeze v1 required 字段
- [ ] URL 为合成占位符（`static.example.invalid`），非真实 CNINFO 抓取
- [ ] `report_type = annual_report` 枚举合法
- [ ] 无 parser / embedding 字段

### report_period_snapshot_fixture.json

- [ ] 含 `report_period_snapshot` found 样例（document_id 非 null）
- [ ] 含 `report_period_snapshot_not_found_example`（document_id = null · coverage_status = not_found）
- [ ] `document_id` 与 report_document_fixture 对齐（`a_doc_fixture_999001_2024_annual`）

### document_lineage_fixture.json

- [ ] `storage_status = not_attempted`
- [ ] 无 `download_time` / `file_hash` / `file_size` 字段
- [ ] `lineage_status` 与 report_document_fixture 一致（`discovered`）
- [ ] 顶层 `document_id` 与另两份 fixture 链接正确

---

## Removed Fields Review

确认以下 **2** 个字段**不进入** Phase1 归一化产出契约：

| 字段 | 对象 | 原 catalog 级别 | 移除理由 | 批准 |
|------|------|-----------------|----------|------|
| `notes` | report_document | future | 自由文本仅 QA 侧车；不进 harvest 产出 | [ ] |
| `mime_type` | document_lineage | recommended | 未下载 PDF 无法验证 MIME | [ ] |

- [ ] 确认 removed 字段不出现在 freeze v1 catalog 与 JSON Schema draft 的 required/recommended 列表中
- [ ] 确认 removed 字段可存在于人工 review artifact，但不进入 normalized 输出

---

## Deferred Fields Review

确认以下 **4** 个字段标记为 **future**，Phase1 不实现、不填值：

| 字段 | 对象 | 推迟理由 | 批准 |
|------|------|----------|------|
| `available_sections` | report_period_snapshot | 依赖 future parser | [ ] |
| `download_time` | document_lineage | PDF 下载层 deferred | [ ] |
| `file_hash` | document_lineage | PDF 内容 hash deferred | [ ] |
| `file_size` | document_lineage | 需下载后才有 | [ ] |

- [ ] 确认 deferred 字段不出现在 Phase1 lint required 检查中
- [ ] 确认 implementation 回合不提前实现 parser / download

---

## Recommended Fields Review（13 个 · 非门禁）

- [ ] 已知晓 recommended 字段缺失应产生 QA flag，但不阻塞 Phase1 metadata capture
- [ ] `company_name` · `adjunct_url` · `org_id` · `announcement_time` · `raw_metadata_json`（report_document）
- [ ] `quarter` · `coverage_status` · `expected_period`（report_period_snapshot）
- [ ] `source_url` · `raw_hash` · `adjunct_url` · `pdf_url`（document_lineage）

---

## 批准决策

| 选项 | 勾选 |
|------|------|
| **APPROVE** — 批准 freeze v1 schema，进入 implementation 回合（仍 offline） | [ ] |
| **APPROVE_WITH_CAVEAT** — 批准但附带书面 caveat（填写下方） | [ ] |
| **DEFER** — 不批准；退回修订 field decision matrix | [ ] |

**Caveat / 备注（若适用）：**

```
（人工填写）
```

**批准人 / 日期：**

```
（人工填写）
```

---

## Gate（本清单不改变 gate）

```text
a_class_phase1_schema_freeze_review_gate = READY_FOR_APPROVAL
```

人工 **APPROVE** 后，下一回合可将 gate 更新为 `READY_FOR_IMPLEMENTATION` 并执行 [implementation plan](../../plans/cninfo_a_class_phase1_freeze_v1_implementation_plan.md)。**本回合不自动更新 gate。**
