# CNINFO C 类 P2 Probe Checklist

_最后更新：2026-07-06_

> **P2 Probe Plan：** [cninfo_c_class_p2_probe_plan.md](cninfo_c_class_p2_probe_plan.md)  
> **P2 记录文件：** [fixtures/c_class/probe/records/c_class_p2_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p2_probe_records.yaml)  
> **总 Checklist（P1）：** [cninfo_c_class_probe_checklist.md](cninfo_c_class_probe_checklist.md)  
> **Candidate YAML：** [config/cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml)

人工 DevTools probe **P2 source** 时使用本清单。**每探一个 source × 一家公司** 走一遍。

**建议首发：** `c_p2_executive_600000`（`cninfo_executive_profile` · 浦发银行）。

---

## 1. 每次 probe 前检查

- [ ] 确认当前任务属于 **P2 scope**（executive / share_capital / top_shareholders / top_float_shareholders）
- [ ] `source_id` 存在于 [cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml) 且 `recommended_status` 仍为 **`candidate`**
- [ ] `company_code` 为 known-company 之一：`600000` / `300001` / `688001`
- [ ] `org_id` 已填入 probe record（见 P2 plan §3）
- [ ] 已打开对应 [c_class_p2_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p2_probe_records.yaml) 中的 `probe_id` 行
- [ ] **本轮仅人工单条 probe**，无脚本批量请求
- [ ] **不下载 PDF**、**不入库**、**不写 verified**
- [ ] **不登录**、不访问 `login` / `tenantLogin`、不绕验证码
- [ ] **不修改** candidate YAML 的 `endpoint` / `recommended_status`（probe 阶段只改 probe record 文件）
- [ ] P1 basic + security 已 `testing`；P2 不得借机升级 `testing_stable_sample`

---

## 2. DevTools 记录字段

在浏览器 DevTools → Network（Fetch/XHR）中，probe 完成后 probe record **必须**填写：

| 字段 | 要求 |
|------|------|
| `request_url` | 实际 API URL（含 path；query 可拆入 `params`） |
| `method` | `GET` 或 `POST` |
| `params` | 实际参数键值（如 `scode`、`orgId`、`secCode`） |
| `headers_required_candidate` | 仅记 `Referer` / `X-Requested-With` 等候选头；**不记 Cookie** |
| `records_path` | JSON 中数组/对象路径（如 `data.records`、`data.list`） |
| `sample_response_shape` | `array` / `object` / `object_with_nested_list` 等 |
| `sample_fields` | 行级或对象级字段名（对应 candidate `expected_fields`） |
| `row_count` | 列表行数（高管/股东类应与页面大致一致） |
| `probe_status` | 见 §3 |
| `blocked_or_empty` | `empty_but_valid` / `blocked` → `true`；`endpoint_found` → `false` |
| `notes` | 分页、board 差异、与 D 类边界、是否需第二家公司复现 |

**页面 URL：** 更新 `page_url` 为实际停留的 F10 标签地址（若 hash 不同于 `#companyProfile`，如实记录）。

---

## 3. 判断 `probe_status` 的规则

| 观察 | `probe_status` |
|------|----------------|
| HTTP 200 + 清晰 JSON API + 有数据 + 关键字段可映射 | `endpoint_found` |
| HTTP 200 + 合法 JSON + records 空 / 无业务行 | `empty_but_valid_response` |
| 有请求但 endpoint 不确定；需换 tab / 点「更多」/ 第二家公司 | `needs_more_probe` |
| 403 / 429 / 验证码 / 需登录 | `blocked` |
| 有 JSON 但 shape 与 list/object 预期不符 | `schema_unexpected` |
| 尚未开始人工 probe | `manual_probe_pending` |

**P2 完成标准（单 source）：** 建议 **3/3** 公司 `endpoint_found` 或 documented `empty_but_valid_response` 后再进入 YAML backfill decision。

---

## 4. 不可记录项（安全 / 合规）

以下 **禁止** 写入 probe record、Git 或 `outputs/`：

- `Cookie` 全文
- `SID` / `JSESSIONID` / `sessionid`
- `Authorization` / Bearer token
- 验证码 payload
- 用户手机号 / 身份证等 PII 全量值

仅保留 **字段名** 与 **脱敏后的结构样本**（本地笔记可存，勿提交仓库）。

---

## 5. Probe 完成后如何更新 record

1. 在 [c_class_p2_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p2_probe_records.yaml) 找到对应 `probe_id`
2. 填写 §2 所列字段；将 `probe_status` 从 `manual_probe_pending` 改为实际状态
3. 在 `notes` 末尾保留：`Do not write verified.`
4. 若同一 source 在第二家公司 probe，对比 `params` / `records_path` 是否一致
5. **不要**在本步骤修改 `config/cninfo_c_class_source_candidates.yaml`
6. 可选：在 `plans/cninfo_c_class_p2_probe_execution_notes.md` 记执行笔记（后续创建）

---

## 6. 何时允许进入 YAML backfill decision

满足 **全部** 条件后，方可起草 P2 backfill decision 文档（类似 [cninfo_c_class_p1_yaml_backfill_decision.md](cninfo_c_class_p1_yaml_backfill_decision.md)）：

- [ ] 该 `source_id` **至少 1 家** `endpoint_found`（**建议 3/3** known-company）
- [ ] `request_url` + `params` + `records_path` 在多家公司上 **可复述** 或差异已写入 `notes`
- [ ] `sample_fields` 与 [schemas/c_class/](../schemas/c_class/) 逻辑字段 **可对照**
- [ ] 已确认 **非 D 类 event**（高管名单 ≠ 人事变动；股东 snapshot ≠ `shareholder_data` metric）
- [ ] `recommended_status` 拟议最高 **`testing`**（非 `testing_stable_sample` / `verified`）
- [ ] `verified` **保持 false**
- [ ] 计划重跑 `lab/lint_cninfo_c_class_registry.py`
- [ ] **未**修改 B / D / Phase 1 文件

YAML 实际回填需 **单独批准**；probe checklist 完成 ≠ 自动升级 status。

---

## 7. P2 probe 顺序建议

| 序 | probe_id | 说明 |
|----|----------|------|
| 1 | `c_p2_executive_600000` | 首发；沪市主板 |
| 2 | `c_p2_executive_300001` | 创业板对照 |
| 3 | `c_p2_executive_688001` | 科创板对照 |
| 4–6 | `c_p2_share_capital_*` | 股本结构 |
| 7–9 | `c_p2_top_shareholders_*` | 十大股东 |
| 10–12 | `c_p2_top_float_shareholders_*` | 十大流通股东 |

同一 `source_id` 三家完成后再切下一 source，便于发现 board 参数差异。
