# CNINFO B 类 Document Corpus Validation 设计

_最后更新：2026-07-05_

> **性质：** 设计草案；不下载 PDF、不解析、不写 verified。  
> **前置：** [cninfo_b_class_source_registry_design.md](cninfo_b_class_source_registry_design.md) · [cninfo_b_class_category_routing_rules.md](cninfo_b_class_category_routing_rules.md)  
> **配置：** [config/cninfo_announcement_categories.yaml](../config/cninfo_announcement_categories.yaml) · [config/cninfo_b_class_source_registry_draft.yaml](../config/cninfo_b_class_source_registry_draft.yaml)

---

## 1. 目的

B 类 validation 验证的是 **document discovery 与 classification** 是否可工程化，**不是** D 类 fixed-table JSON row 的 schema 校验，也 **不是** Phase 1 之前混用的「随机公司 × 多 query strategy success rate」。

| 验证什么 | 不验证什么 |
|----------|------------|
| 能否按规则检索到目标 **PDF metadata**（`pdf_url`、title、date） | PDF 正文、OCR、chunk 质量 |
| `document_type` / `source_id` **路由是否正确** | D 类 `records_path`、metric 拆行 |
| corpus 在样本窗内 **非空率、分类置信度** | 全市场长期稳定性、verified |
| known-document / known-event **命中率** | 单一关键词 luck rate |

---

## 2. 与 Phase 1 的关系

| 维度 | Phase 1 A 类 | B 类 corpus validation（本文） |
|------|--------------|-------------------------------|
| 已验证范围 | `cninfo_periodic_report_pdf` retrieval | 同上 **仅继承** 定期报告 |
| 主指标 | company × report_type × expected_period → **749/796 = 94.10%** | 定期报告继续用此口径 |
| 脚本 | `lab/validate_cninfo_report_coverage.py` | 未来改造 `validate_cninfo_announcement_categories.py` |
| 不能推广 | — | **不得** 将 94.10% 当作普通公告 / 问询函 / 说明会 corpus coverage |

**继承规则：**

- `periodic_report` category → `validation_method: expected_period` → 与 Phase 1 计行一致。
- Phase 1 的 `title_excluded` 行在 B 类中 **保留审计**，并尝试 **二次路由** 到 `inquiry_reply` / `meeting_notice` / `general_announcement`（见 routing rules）。
- Phase 1 **未做** parse/chunk；B 类 validation 同样 **只到 retrieval + classification**。

---

## 3. Validation 口径分类

### 3.1 expected-period validation

**适用：** `annual_report`、`semi_annual_report`、`quarterly_report_q1`、`quarterly_report_q3`  
**source：** `cninfo_periodic_report_pdf`  
**category：** `periodic_report`

| 项 | 规则 |
|----|------|
| **分母** | mapped company × report_type × expected_period（与 Phase 1 一致） |
| **分子（effective found）** | `pdf_url` 非空 + `parsed_report_period == expected_period` + 命中 `positive_patterns` + **未**命中 `exclusion_patterns` |
| **失败类型** | `not_found`、`period_mismatch`、`title_excluded`（若未二次路由成功） |
| **证据** | [cninfo_report_phase1_final_summary.md](../outputs/validation/cninfo_report_phase1_final_summary.md) |

### 3.2 known-document validation

**适用：** 问询函、回复公告、业绩说明会、特定治理/风险公告等 **标题与日期已知** 的样本。

| 项 | 规则 |
|----|------|
| **输入** | benchmark 表：`company_code` + `announcement_date`（或窄窗口）+ `expected_title_substring` + `expected_source_id` |
| **通过** | retrieval 返回标题匹配 + `pdf_url` 可用 + `route_to.source_id` 与预期一致 |
| **失败** | `not_found`、`misclassified`、`ambiguous` |
| **source 示例** | `cninfo_inquiry_reply_pdf`、`cninfo_meeting_notice_pdf` |
| **样本规模** | 小样本（每类 5–15 条），**非**全市场 |

### 3.3 category-sample validation

**适用：** `cninfo_general_announcement_pdf`、宽 corpus、未来 event category 扩展。

| 项 | 规则 |
|----|------|
| **抽样** | 时间窗 × `category` / title pattern × 板块分层样本公司 |
| **指标** | corpus **非空率**、字段可得性%（title、date、pdf_url）、`classified_correctly` 占比 |
| **分类审计** | high + medium 规则置信度占比；`misclassified` / `ambiguous` 清单 |
| **禁止** | 用「N 家公司 × M 关键词 success/fail 行数」当唯一 coverage |

---

## 4. 不再使用的错误口径

| 错误口径 | 为何废弃 |
|----------|----------|
| **query_strategy 级 success/fail 混计** | 一行 ≠ 一份文档；与 Phase 1 旧 `368/780` 同类问题 |
| **随机公司 × 随机关键词 success rate** | 瓶颈在检索覆盖与规则，非单一 luck 关键词（见 [cninfo_announcement_acquisition_mechanism_summary.md](../outputs/validation/cninfo_announcement_acquisition_mechanism_summary.md)） |
| **把 `title_excluded` 当 document 不存在** | exclusion 是 **路由**；语料可能存在于其他 B source |
| **定期报告 found 率推广到全 B 类** | 仅 `periodic_report` 适用 expected-period |
| **verified / full-market stable** | Era C 红线 |

---

## 5. Validation 输出字段

未来 `cninfo_b_class_corpus_validation_report.csv`（或改造后 announcement validation CSV）建议列：

| 字段 | 说明 |
|------|------|
| `validation_id` | 行主键 |
| `source_id` | B 类 registry source |
| `category_key` | `cninfo_announcement_categories.yaml` 键 |
| `document_type` | 目标 document_type |
| `company_code` | |
| `company_name` | |
| `expected_title_pattern` | 规则或 benchmark 期望 |
| `expected_period` | 报告类；否则空 |
| `date_window` | seDate 或 benchmark 窗口 |
| `retrieval_status` | found / not_found / title_excluded / … |
| `classification_status` | §6 |
| `title_match_status` | positive_hit / exclusion_hit / no_match |
| `pdf_url_available` | yes / no |
| `false_positive_reason` | §7；无则空 |
| `matched_route_source_id` | 实际路由到的 source |
| `rule_confidence` | high / medium / low |
| `notes` | |

---

## 6. classification_status

| 值 | 说明 |
|----|------|
| `classified_correctly` | 路由与 `document_type` 符合规则 |
| `misclassified` | 路由到错误 source（如问询函进 periodic） |
| `ambiguous` | 多规则命中或置信不足；**不强行归类** |
| `title_excluded_from_periodic_but_routed` | 自 periodic 排除后落入其他 corpus |
| `not_found` | 检索无匹配 |
| `unknown` | 未分类 |

---

## 7. false_positive 类型

用于定期报告 **effective found** 审计与非预期命中分析（对齐 Phase 1 quality audit）：

| 值 | 说明 |
|----|------|
| `announcement_preview` | 预告类 |
| `summary` | 摘要 / 解读 |
| `inquiry_reply_as_report` | 问询函 / 回复被误判为报告 |
| `meeting_notice_as_report` | 说明会被误判为报告 |
| `delayed_disclosure_notice` | 延期披露提示 |
| `wrong_company` | 交叉披露其他公司 |
| `wrong_period` | 报告期不匹配 |
| `unrelated_announcement` | 其他无关公告 |

---

## 8. 与 registry / category 配置的协作

```
cninfo_announcement_categories.yaml  (category routing rules)
        │
        ├─► route_to.source_id ──► cninfo_b_class_source_registry_draft.yaml
        │
        └─► validation_method ──► 本设计 §3.1–3.3
```

| category_key | validation_method | registry source |
|--------------|-------------------|-----------------|
| `periodic_report` | expected_period | `cninfo_periodic_report_pdf` |
| `inquiry_reply` | known_document | `cninfo_inquiry_reply_pdf` |
| `meeting_notice` | known_document | `cninfo_meeting_notice_pdf` |
| `general_announcement` | category_sample | `cninfo_general_announcement_pdf` |

---

## 9. 当前不做

| 不做 | 原因 |
|------|------|
| 下载 / 解析 PDF | Era C 红线 |
| OCR | 红线 |
| 向量库 / embedding | 未来阶段 |
| 写 verified | 红线 |
| 改造 validation 脚本（本批） | 仅设计；下一步实现 |
| 修改 Phase 1 CSV / `validate_cninfo_report_coverage.py` | 边界 |

---

## 10. 预期输出（未来脚本）

| 文件 | 内容 |
|------|------|
| `outputs/validation/cninfo_b_class_corpus_validation_report.csv` | 逐 validation 行 |
| `outputs/validation/cninfo_b_class_corpus_validation_summary.md` | 分 source / 分 method 汇总 |
| `outputs/validation/cninfo_announcement_category_validation_summary.md` | 改造后可选沿用旧名 |

---

## 11. 下一步

1. **改造** `lab/validate_cninfo_announcement_categories.py` — 读取新 YAML 结构，实现 §3.2 / §3.3。
2. **离线 seed** Phase 1 `found` 行为 `fixtures/b_class/document/`（metadata only）。
3. **建立 known-document benchmark** — 问询函 / 说明会各 5–15 条（来自历史 validation 笔记，不新抓 CNINFO）。
4. 可选：`lint_cninfo_b_class_registry.py` 检查 category `route_to.source_id` 与 registry 一致。

---

## 12. 产物索引

| 文档 | 说明 |
|------|------|
| [cninfo_b_class_category_routing_rules.md](cninfo_b_class_category_routing_rules.md) | Title 路由优先级与示例 |
| [cninfo_b_class_corpus_design.md](cninfo_b_class_corpus_design.md) | Corpus 总设计 |
| [cninfo_report_phase1_final_summary.md](../outputs/validation/cninfo_report_phase1_final_summary.md) | A 类证据 |
