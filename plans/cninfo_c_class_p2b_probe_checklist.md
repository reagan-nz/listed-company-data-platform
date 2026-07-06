# CNINFO C Class P2-B Probe Checklist

_最后更新：2026-07-06_

> **P2-B Probe Plan：** [cninfo_c_class_p2b_probe_plan.md](cninfo_c_class_p2b_probe_plan.md)  
> **P2-B 记录文件：** [fixtures/c_class/probe/records/c_class_p2b_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p2b_probe_records.yaml)  
> **Status consolidation：** [cninfo_c_class_status_consolidation_summary.md](cninfo_c_class_status_consolidation_summary.md)  
> **P1 basic overlap reference：** [cninfo_c_class_basic_profile_field_mapping_draft.md](cninfo_c_class_basic_profile_field_mapping_draft.md)

人工 DevTools probe **P2-B source** 时使用本清单。**每探一个 source × 一家公司** 走一遍。

**建议首发：** `c_p2b_dividend_financing_600000`（`cninfo_dividend_financing_profile` · 浦发银行）。

---

## 1. Before probe

- [ ] 确认当前任务属于 **P2-B scope**（dividend_financing · contact · business_scope · industry recheck）
- [ ] `source_id` 在 [cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml) 中 `recommended_status` 仍为 **`candidate`**
- [ ] `company_code` 为 known-company 之一：`600000` / `300001` / `688001`
- [ ] `org_id` 已填入 probe record（见 P2-B plan §3）
- [ ] 已打开 [c_class_p2b_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p2b_probe_records.yaml) 中对应 `probe_id` 行
- [ ] **本轮仅人工单条 probe**，无脚本批量请求
- [ ] **不下载 PDF**、**不入库**、**不写 verified**
- [ ] **不登录**、不访问 `login` / `tenantLogin`、不绕验证码
- [ ] **不修改** candidate YAML 的 `endpoint` / `recommended_status`（probe 阶段只改 probe record 文件）
- [ ] P1 + P2-A 已 `testing` 的 6 源不得借机升级 `testing_stable_sample`
- [ ] 对 contact / business_scope：已浏览 P1 `basic_profile` 字段映射，准备记录 overlap

---

## 2. What to record

在浏览器 DevTools → Network（Fetch/XHR）中，probe 完成后 probe record **必须**填写：

| 字段 | 要求 |
|------|------|
| `request_url` | 实际 API URL（含 path；query 可拆入 `params`） |
| `method` | `GET` 或 `POST` |
| `params` | 实际参数键值（如 `scode`、`orgId`、`secCode`） |
| `headers_required_candidate` | 仅记 `Referer` / `X-Requested-With` 等候选头；**不记 Cookie** |
| `records_path` | JSON 中数组/对象路径（如 `data.records`、`data.list`） |
| `result_code_path` | 业务结果码路径（如 `data.resultCode`），若存在 |
| `sample_response_shape` | 结构摘要（非全量 body） |
| `sample_fields` | 行级或对象级字段名 |
| `candidate_field_mapping` | raw → candidate 语义字段（draft） |
| `row_count` | 列表行数（若适用） |
| `probe_status` | 见 P2-B plan §6 |
| `derived_from_candidate` | 若 `derived_candidate_from_basic_profile`，填 `cninfo_company_basic_profile` + path/fields |
| `blocked_or_empty` | `empty_but_valid` / `blocked` → `true`；`endpoint_found` → `false` |
| `notes` | 分页、board 差异、与 basic_profile 重叠、是否需第二家公司复现 |

**页面 URL：** 更新 `page_url` 为实际停留的 F10 标签地址。

---

## 3. What not to record

以下 **禁止** 写入 probe record、Git 或 `outputs/`：

- **Cookie** 全文
- **SID** / `JSESSIONID` / `sessionid`
- **Authorization** / Bearer token
- 验证码 payload
- 用户手机号 / 身份证等 PII 全量值
- 完整 live response body（仅结构 + 字段名）

仅保留 **字段名** 与 **脱敏后的结构样本**（本地笔记可存，勿提交仓库）。

---

## 4. Derived vs independent decision checklist

Probe 完成后，对 **contact** / **business_scope** / **industry** 填写：

- [ ] 是否发现 **独立于** `getCompanyIntroduction` 的 XHR？
- [ ] 若未发现：basicInformation 中哪些字段已覆盖 expected_fields？
- [ ] 若发现独立 endpoint：与 basic_profile 字段是否 **重复**？重复部分记入 `notes`
- [ ] `probe_status` 是否为 `endpoint_found` **或** `derived_candidate_from_basic_profile`（二选一，有证据）
- [ ] **industry：** 默认保持 derived；仅当 UI 触发明显独立 XHR 时才改为 `endpoint_found`
- [ ] **dividend_financing：** 不应在未 probe 前标记为 derived

| 若… | 则 `probe_status` |
|-----|-------------------|
| 独立 JSON API + 可映射字段 | `endpoint_found` |
| 无独立 API；basic_profile 字段足够 | `derived_candidate_from_basic_profile` |
| 200 但无业务数据 | `empty_but_valid_response` |
| 需换 tab / 第二家公司 | `needs_more_probe` |

---

## 5. How to update probe records

1. 在 [c_class_p2b_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p2b_probe_records.yaml) 找到对应 `probe_id`
2. 填写 §2 所列字段；将 `probe_status` 从 `manual_probe_pending` 改为实际状态
3. 若 derived：填写 `derived_from_candidate`（参考 industry 在 candidate YAML 中的格式）
4. 在 `notes` 保留：`Do not write verified.`
5. 同一 `source_id` 三家完成后再切下一 source
6. **不要**在本步骤修改 `config/cninfo_c_class_source_candidates.yaml`
7. 可选：创建 `plans/cninfo_c_class_p2b_probe_execution_notes.md` 记执行笔记

---

## 6. When YAML backfill decision is allowed

满足 **全部** 条件后，方可起草 P2-B backfill decision 文档（类似 [cninfo_c_class_p2a_yaml_backfill_decision.md](cninfo_c_class_p2a_yaml_backfill_decision.md)）：

- [ ] 该 `source_id` probe 矩阵完成（3/3 或 documented exception）
- [ ] `endpoint_found`：**或** `derived_candidate_from_basic_profile` 带 mapping evidence
- [ ] `request_url` + `params` + `records_path` 可复述（derived 源填 `derived_from_candidate`）
- [ ] `sample_fields` 与 [schemas/c_class/](../schemas/c_class/) 可对照
- [ ] 已确认 **非 B 类公告** / **非 D 类 metric** 边界
- [ ] `recommended_status` 拟议最高 **`testing`**（非 `testing_stable_sample` / `verified`）
- [ ] **`verified` 保持 false**
- [ ] 计划重跑 `lab/lint_cninfo_c_class_registry.py`
- [ ] **未**修改 B / D / Phase 1 文件

**Do not mark verified.** YAML 实际回填需 **单独批准**；probe checklist 完成 ≠ 自动升级 status。

---

## 7. P2-B probe 顺序建议

| 序 | probe_id | 说明 |
|----|----------|------|
| 1 | `c_p2b_dividend_financing_600000` | P2-B1 首发；沪市主板 |
| 2 | `c_p2b_dividend_financing_300001` | 创业板 |
| 3 | `c_p2b_dividend_financing_688001` | 科创板 |
| 4–6 | `c_p2b_contact_*` | derived vs independent |
| 7–9 | `c_p2b_business_scope_*` | derived vs independent |
| 10–12 | `c_p2b_industry_*` | derived recheck only |
