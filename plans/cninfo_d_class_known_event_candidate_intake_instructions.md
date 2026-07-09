# CNINFO D 类 Known Event Replacement Candidate — Intake Instructions

_生成时间：2026-07-09_

> **性质：** 人工候选 intake 说明 · **无 CNINFO** · **无 web lookup** · **无 auto-fill**

**模板文件：** [cninfo_d_class_known_event_replacement_candidate_template.csv](../outputs/validation/cninfo_d_class_known_event_replacement_candidate_template.csv)

---

## 1. What Human Must Provide

人工须为 **DLC003R** 与 **DLC006R** 各填写一行完整候选信息。Agent **不得**代填 `company_code` 或事件证据。

### DLC003R（restricted_shares_unlock）

| 字段 | 必填 | 说明 |
|------|------|------|
| company_code | **是** | 6 位 A 股代码 · **人工提供** |
| company_name | **是** | 公司简称 |
| event_evidence_type | **是** | 见 §2 接受类型 |
| event_evidence_description | **是** | 已知解禁事件描述 |
| event_date_or_period | **是** | 解禁日或区间 |
| source_reference | **是** | 人工内部记录来源（公告名/文档 ID） |
| notes | 推荐 | **为何** 预期 `restricted_shares_unlock` `captured_normal` |
| human_provided | **是** | 填完后设为 `true` |
| candidate_status | **是** | 填完后设为 `human_candidate_provided` |

### DLC006R（shareholder_change）

| 字段 | 必填 | 说明 |
|------|------|------|
| company_code | **是** | 6 位 A 股代码 · **人工提供** |
| company_name | **是** | 公司简称 |
| event_evidence_type | **是** | 见 §2 接受类型 |
| event_evidence_description | **是** | 已知增减持事件描述 |
| event_date_or_period | **是** | 事件日或区间 |
| source_reference | **是** | 人工内部记录来源 |
| notes | 推荐 | **为何** 预期 `shareholder_change` `captured_normal` |
| human_provided | **是** | 填完后设为 `true` |
| candidate_status | **是** | 填完后设为 `human_candidate_provided` |

---

## 2. Accepted Evidence Types

| type | 适用于 | 说明 |
|------|--------|------|
| `regulatory_disclosure` | DLC003R · DLC006R | 监管披露/公告类人工记录 |
| `unlock_schedule_record` | DLC003R | 解禁日程/限售解禁人工记录 |
| `shareholder_change_announcement` | DLC006R | 股东增减持公告人工记录 |
| `internal_research_note` | 两者 | 内部研究笔记（须含 source_reference） |
| `prior_validation_record` | 两者 | 既往验证记录引用 |

---

## 3. Required Fields（不可为空）

填码完成后以下字段 **均不可空**：

`replacement_case_id` · `replaces_case_id` · `component` · `required_behavior` · `company_code` · `company_name` · `event_evidence_type` · `event_evidence_description` · `event_date_or_period` · `source_reference` · `human_provided` · `candidate_status`

固定值（勿改）：
- `required_behavior` = `captured_normal`
- `replacement_case_id` = `DLC003R` 或 `DLC006R`

---

## 4. Rejected Evidence Types

| 类型 | 原因 |
|------|------|
| web-scraped without human curation | 违反 no-web 规则 |
| agent-guessed event dates | 违反 no-guessing 规则 |
| invented company codes | 禁止 |
| empty evidence with human_provided=true | 逻辑矛盾 |
| duplicate company_code（无 justification） | DLC003R/DLC006R 不得同码除非 notes 说明 |

---

## 5. Validation Steps

1. 人工编辑 [candidate template](../outputs/validation/cninfo_d_class_known_event_replacement_candidate_template.csv)
2. 运行离线校验：

```bash
python lab/validate_cninfo_d_class_known_event_candidates.py
```

3. 查看 [validation report](../outputs/validation/cninfo_d_class_known_event_candidate_validation_report.csv) 与 [validation summary](../outputs/validation/cninfo_d_class_known_event_candidate_validation_summary.md)
4. 状态 `WAITING_FOR_HUMAN_INPUT` → 继续填码；`HUMAN_CANDIDATE_VALIDATED` → 进入批准包评审
5. **不修改** original / calibrated universe 直至批准包显式通过

---

## 6. No-Web / No-Guessing Rule

| 规则 | 说明 |
|------|------|
| no web lookup | agent / runner **不得**联网查公司或事件 |
| no guessing | 不得推测 `company_code` · 事件日 · 证据内容 |
| no auto-fill | 校验脚本 **只读** 模板 · 不写回 |
| human_provided=true | 仅人工确认填码完成后设置 |

---

## 7. Approval Process

| 步骤 | 动作 |
|------|------|
| 1 | intake validation 通过（`HUMAN_CANDIDATE_VALIDATED`） |
| 2 | 更新 [replacement universe draft](../outputs/validation/cninfo_d_class_tiny_live_replacement_universe_draft.csv)（**未来 · 人工**） |
| 3 | 完成 [approval checklist](../outputs/validation/cninfo_d_class_known_event_replacement_approval_checklist.md) |
| 4 | 显式 `--approve-d-class-known-event-replacement-validation` |
| 5 | 未来 isolated live（**NOT APPROVED**） |

**当前 intake gate：** `d_class_known_event_candidate_intake_gate = WAITING_FOR_HUMAN_INPUT`

---

## 8. Red Lines

No CNINFO · No live · No harvest · No web · No invented codes · No universe mutation · No verified · No production_ready
