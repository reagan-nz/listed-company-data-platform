# CNINFO C 类 P1 Probe Execution Notes

_最后更新：2026-07-05_

> **Probe records：** [fixtures/c_class/probe/records/c_class_p1_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p1_probe_records.yaml)  
> **Probe plan：** [cninfo_c_class_devtools_probe_plan.md](cninfo_c_class_devtools_probe_plan.md)  
> **Checklist：** [cninfo_c_class_probe_checklist.md](cninfo_c_class_probe_checklist.md)  
> **Record template：** [c_class_probe_record_template.yaml](../fixtures/c_class/probe/c_class_probe_record_template.yaml)

---

## 1. 目的

本文件用于指导 **P1 三个 source** 的 **人工 DevTools probe** 执行与填写。

- 探测 F10 / company profile 的 **endpoint、params、records_path、字段样本**。
- 将结果填入 [c_class_p1_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p1_probe_records.yaml) 对应 `probe_records[]` 条目。
- **不**在本轮自动回填 candidate YAML；**不**写 `verified`；**不**入库。

当前文件状态：`status: manual_probe_pending`；**9 条记录均为占位，不代表真实 CNINFO 证据。**

---

## 2. Probe 范围

### 2.1 P1 sources（3）

| source_id | source_category | 对应 schema / 逻辑表 |
|-----------|-----------------|----------------------|
| `cninfo_company_basic_profile` | basic_profile | `c_company_basic_profile` |
| `cninfo_company_security_profile` | security_profile | `c_company_basic_profile`（证券字段子集） |
| `cninfo_company_industry_profile` | industry_profile | `c_company_basic_profile`（行业字段子集） |

### 2.2 Known companies（3）

| company_code | company_name | 板块 |
|--------------|--------------|------|
| `600000` | 浦发银行 | 沪市主板 |
| `300001` | 特锐德 | 创业板 |
| `688001` | 华兴源创 | 科创板 |

**矩阵：** 3 source × 3 company = **9** 条 `probe_records`（见 YAML 中 `probe_id`：`c_p1_{basic|security|industry}_{code}`）。

probe 前在 YAML `probe_scope.companies[].org_id` 与各条 `org_id` 中填入 CNINFO `orgId`（identity 查询不计入 profile endpoint 证据，但 probe 需要）。

---

## 3. 执行顺序

建议按 source 顺序执行，每家公司在同一 F10 会话内尽量连续完成，减少重复打开页面：

1. **`cninfo_company_basic_profile`** — 600000 → 300001 → 688001  
2. **`cninfo_company_security_profile`** — 600000 → 300001 → 688001  
3. **`cninfo_company_industry_profile`** — 600000 → 300001 → 688001  

每完成一条，立即更新 YAML 对应 `probe_id` 字段，避免事后遗漏。

**请求间隔：** ≥ 0.6s（与 candidate YAML `defaults.sleep_seconds` 一致）；不高频刷新。

---

## 4. 每次 probe 要记录什么

执行前走 [cninfo_c_class_probe_checklist.md](cninfo_c_class_probe_checklist.md) §1；DevTools 中走 §2–§3。

每条 `probe_records[]` **至少填写**：

| 字段 | 说明 |
|------|------|
| `org_id` | CNINFO orgId |
| `page_url` | F10 标签页浏览器 URL |
| `request_url` | Network 中 API 完整 URL |
| `method` | `GET` / `POST` |
| `params` | query / body 键值（如 `stockCode`、`orgId`） |
| `headers_required_candidate` | 疑似必需头（如 `Referer`）；**不记 Cookie** |
| `records_path` | 响应 JSON 中数据路径 |
| `sample_response_shape` | 顶层结构简述 |
| `sample_fields` | 响应字段名列表 |
| `row_count` | 列表行数（若适用） |
| `probe_status` | 见 §5 |
| `blocked_or_empty` | 空响应 / 被挡 / 仅 HTML |
| `notes` | 日期、操作者、异常；**替换** “pending” 占位文案 |

**本地保留（不入 Git 大文件）：** 完整 `raw_record_json` 样本路径写在 `notes` 中，供后续 mapper / fixture 使用。

---

## 5. 如何判断 endpoint_found

将 `probe_status` 设为 **`endpoint_found`** 须 **同时** 满足：

1. **HTTP 成功**（通常 200；非 200 用 `blocked` 或 `endpoint_not_found`）。
2. **Response 能对应公司**：返回中的代码/名称与 `company_code` / `company_name` 一致或可映射。
3. **字段能解释到 profile schema**：`sample_fields` 与 candidate `expected_fields` 及 [schemas/c_class/](../schemas/c_class/) 大部分可对应。
4. **`records_path` 可描述**：他人可按路径在同类响应中定位数据。
5. **至少保留 `raw_record_json`**：本地保存一份解析后 JSON（probe record 或附件文件）。

若仅探 1 家公司或分页未确认 → 保持 **`needs_more_probe`**。  
200 但空数组 → **`empty_but_valid_response`**。  
有数据但字段对不上 → **`schema_unknown`**。

同一 `source_id` 在 **至少 1–3 家** 公司上为 `endpoint_found` 后，方可进入 candidate YAML 回填审查（见 §7）。

---

## 6. 不允许的事

| 红线 | 说明 |
|------|------|
| 不全市场抓取 | 仅 YAML 中 9 条矩阵 |
| 不高频请求 | 间隔 ≥ 0.6s |
| 不登录 | 不用账号 / Cookie / Token |
| 不绕 captcha | 遇验证码记 `blocked` 并停止 |
| 不写 `verified` | YAML / probe record / candidate registry 均保持 `verified: false` |
| 不入库 | 不写 DB / MinIO |
| 不自动改 candidate YAML | endpoint 回填须 checklist §4 + 人工批准 |

---

## 7. Probe 后下一步

1. **人工填写** [c_class_p1_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p1_probe_records.yaml) 全部 9 条（或按 source 分批提交）。
2. 将文件 `status` 从 `manual_probe_pending` 改为 `manual_probe_complete`（全部填完时）。
3. 按 [cninfo_c_class_probe_checklist.md](cninfo_c_class_probe_checklist.md) **§4 回填前检查** 审查每个 `source_id`。
4. 若某 source 在 1–3 家公司上 **`endpoint_found` 且可复述**，再 **人工编辑** [cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml)：
   - 填入 `endpoint` / `page_url` / `records_path`（及 notes）
   - `recommended_status` **最多** `testing`
   - **`verified` 保持 false**
5. 重跑 `lab/lint_cninfo_c_class_registry.py`。
6. 可选：用真实样本更新 offline fixtures；建立 C 类 known-company **live** profile validation 脚本（另案批准）。

**P2 源**（executive / share_capital / shareholders 等）在本 P1 完成并审查后再启动，结构可复用本 YAML 模式。
