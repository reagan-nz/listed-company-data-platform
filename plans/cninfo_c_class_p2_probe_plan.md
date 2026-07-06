# CNINFO C 类 P2 DevTools Probe Plan

_最后更新：2026-07-06_

> **P1 已完成：** basic_profile + security_profile YAML backfill、`testing` live validation、mapper + fixture + schema validation PASS。  
> **P2 记录：** [fixtures/c_class/probe/records/c_class_p2_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p2_probe_records.yaml)  
> **P2 Checklist：** [cninfo_c_class_p2_probe_checklist.md](cninfo_c_class_p2_probe_checklist.md)  
> **总 Probe Plan（P1–P3）：** [cninfo_c_class_devtools_probe_plan.md](cninfo_c_class_devtools_probe_plan.md)  
> **Candidate YAML：** [config/cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml)

---

## 1. 目的

P2 目标是发现 **高管 / 股本结构 / 十大股东 / 十大流通股东** 四类 C 类 F10 profile source 的 **endpoint candidate**：

- 记录 `request_url`、`method`、`params`、`records_path`
- 记录 `sample_fields` 与 `sample_response_shape`（字段结构，非全量 body）
- 为后续 **YAML backfill decision**、mapper draft、known-company live validation 提供证据

**本计划仅为准备文档；本轮不发起 CNINFO 请求、不写 live validation、不入库。**

---

## 2. P2 source scope

| source_id | priority | expected_page_area | expected_data_shape | status |
|-----------|----------|-------------------|---------------------|--------|
| `cninfo_executive_profile` | P2-A | 高管 / 董监高 | list records | **3/3 endpoint_found** |
| `cninfo_share_capital_profile` | P2-A | 股本结构 / 股本变动 | object or list | **3/3 endpoint_found** |
| `cninfo_top_shareholders_profile` | P2-A | 十大股东 | list records | **3/3 endpoint_found** |
| `cninfo_top_float_shareholders_profile` | P2-A | 十大流通股东 | list records | **3/3 endpoint_found** |

### 2.1 暂缓（不在 P2 本轮）

| source_id | 原因 |
|-----------|------|
| `cninfo_dividend_financing_profile` | P3 文本/摘要型；待 P2 结构型 source 完成后再做 |
| `cninfo_company_contact_profile` | 可能与 basic_profile 重叠；P3 |
| `cninfo_company_business_scope` | P3 文本型 |
| `getHeadStripData` annex | 已记入 P1 `security_profile_annex`；语义未确认，不并入 share_capital |

### 2.2 Candidate `expected_fields`（probe 对照）

| source_id | expected_fields（来自 candidate YAML） |
|-----------|----------------------------------------|
| `cninfo_executive_profile` | `person_name`, `position`, `term_start_candidate`, `term_end_candidate` |
| `cninfo_share_capital_profile` | `report_date`, `total_share_capital`, `float_share_capital`, `restricted_share_capital`, `share_unit` |
| `cninfo_top_shareholders_profile` | `shareholder_name`, `holding_shares`, `holding_ratio`, `rank`, `report_period` |
| `cninfo_top_float_shareholders_profile` | 同上（`shareholder_scope: top_float_shareholder`） |

对应 JSON Schema：`c_executive_profile`、`c_share_capital_profile`、`c_shareholder_profile`（[schemas/c_class/](../schemas/c_class/)）。

### 2.3 `cninfo_executive_profile` 当前观察摘要（2026-07-06）

- **P2 probe：** `cninfo_executive_profile` **3/3 `endpoint_found`**（600000 / 300001 / 688001）。
- **Endpoint candidate：** `GET https://www.cninfo.com.cn/data20/companyOverview/getCompanyExecutives?scode={company_code}`
- **records_path：** `data.records`
- **result_code_path：** `data.resultCode`（期望 `"200"`）
- **共享行级字段：** `F002V`, `F010V`, `F012V`, `F017V`, `F009V`, `F005N`, `F012N`, `SEQID`, `F001V`
- **row_count：** 600000 → 19；300001 → 17；688001 → 13
- **candidate_field_mapping：** `F002V`→executive_name, `F009V`→position_titles, `F010V`→gender, `F012V`→birth_year, `F017V`→education（nullable）, `F005N`/`F012N`→quantity/compensation candidate
- **F005N / F012N** 语义仍为 candidate-level；单位待 UI 对照确认
- **YAML backfill：** 尚未回填 `cninfo_c_class_source_candidates.yaml`（需单独 backfill decision）
- **无 verified**；**无 testing_stable_sample**

### 2.4 P2-A 当前观察摘要（2026-07-06）

| source_id | endpoint_found | Endpoint candidate |
|-----------|----------------|-------------------|
| `cninfo_executive_profile` | **3/3** | `GET /data20/companyOverview/getCompanyExecutives?scode={company_code}` |
| `cninfo_share_capital_profile` | **3/3** | `GET /data20/stockholderCapital/getStockStructure?scode={company_code}` |
| `cninfo_top_shareholders_profile` | **3/3** | `GET /data20/stockholderCapital/getTopTenStockholders?scode={company_code}` |
| `cninfo_top_float_shareholders_profile` | **3/3** | `GET /data20/stockholderCapital/getTopTenCirculatingStockholders?scode={company_code}` |

**合计：** P2-A manual probe **12/12 `endpoint_found`**（4 sources × 3 known companies）。

**共享约定：**
- **records_path：** `data.records`（all P2-A sources）
- **result_code_path：** `data.resultCode`（期望 `"200"`）
- **params：** `scode={company_code}`
- **无 blocked / login / captcha** 观察
- **无 schema_unexpected** 观察
- **无 YAML backfill**（本轮）；**无 verified**；**无 testing_stable_sample**

**share_capital 字段：** VARYDATE, F002V, F021N, F022N, F023N, F024N, F028N, F003N（FxxxN 单位 candidate-level）

**shareholders 字段（top + float 同形）：** F001D, F002V, F003N, F004N, F005N, F006V, F007V；通常 5 报告期 × 10 股东 = **50 rows**

**row_count 摘要：**
- executive：19 / 17 / 13
- share_capital：**5 / 5 / 5**
- top_shareholders：**50 / 50 / 50**
- top_float_shareholders：**50 / 50 / 50**

---

## 3. Known companies

继续使用 P1 三家公司（主板 / 创业板 / 科创板）：

| company_code | company_name | org_id | 板块 |
|--------------|--------------|--------|------|
| `600000` | 浦发银行 | `gssh0600000` | 沪市主板 |
| `300001` | 特锐德 | `9900008270` | 创业板 |
| `688001` | 华兴源创 | `9900038969` | 科创板 |

**矩阵：** 4 sources × 3 companies = **12** probe records（**12/12 `endpoint_found`**）。

**建议 probe 顺序：** `cninfo_executive_profile` @ `600000` 优先 → 同 source 扩至 300001 / 688001 → 再切 `share_capital` → `top_shareholders` → `top_float_shareholders`。

---

## 4. Manual DevTools method

1. **打开** CNINFO 个股 F10 company profile 页面  
   `https://www.cninfo.com.cn/new/disclosure/stock?stockCode={code}&orgId={org_id}#companyProfile`
2. **切换** 到目标 F10 标签页（高管 / 股本结构 / 十大股东 / 十大流通股东）
3. **打开** DevTools → Network，过滤 **Fetch / XHR**
4. **触发** 页面加载或 tab 切换，观察新出现的 JSON API 请求
5. **记录**（写入 probe record，不提交 Git 全量 response）：
   - `request_url`（path + query）
   - `method`
   - `params`（实际键名：`scode` / `orgId` / `secCode` 等）
   - `records_path`（如 `data.records`、`$.list`）
   - `sample_response_shape`（`array` / `object` / `object_with_nested_list`）
   - `sample_fields`（顶层或行级字段名列表）
   - `row_count`（列表行数，与页面大致一致）
6. **只记录字段结构**，不保存 cookie / token / 完整 live raw response 到 `outputs/`
7. **不访问** `login` / `tenantLogin`；不绕验证码
8. **不做批量请求**；每家公司 probe 间隔 ≥ 0.6s；非全市场

---

## 5. Endpoint classification rules

| probe_status | 判定条件 |
|--------------|----------|
| `endpoint_found` | HTTP **200** + 预期 records/object 存在 + **关键字段**可对应 `expected_fields` / schema |
| `empty_but_valid_response` | HTTP **200** + JSON 结构合法，但 records 为空或业务数据为空壳 |
| `needs_more_probe` | endpoint 不清晰；需额外 tab 点击 / 分页 / 第二家公司交叉验证 |
| `blocked` | 登录墙 / 验证码 / 403 / 429 / 权限不足 |
| `schema_unexpected` | 有 JSON 但 shape 与预期 list/object 不兼容，或字段名无法映射 |

**初始状态：** 全部 `manual_probe_pending`（尚未开始人工 probe）。

**与 P1 对齐：** `blocked_or_empty` 在 `empty_but_valid_response` 或 `blocked` 时设为 `true`，否则 `false`；`manual_probe_pending` 时为 `null`。

---

## 6. Red lines

- **不写 verified**（probe record、`recommended_status`、schema enum 均禁止 `verified`）
- **不升级 `testing_stable_sample`**（P2 probe 阶段最高拟议 `testing`，需单独 backfill 决策）
- **不入库**；不创建 migration
- **不做全市场 validation**；仅 1–3 家 known-company
- **不修改** B 类 / D 类 / Phase 1 文件
- **本轮不自动回填** `cninfo_c_class_source_candidates.yaml`（probe 完成后另写 backfill decision）
- **不下载 PDF**；不把完整 live response body 写入 `outputs/validation/`

---

## 7. 产出与下一步

| 产出 | 路径 | 本轮状态 |
|------|------|----------|
| P2 probe plan | 本文件 | **已创建** |
| P2 checklist | [cninfo_c_class_p2_probe_checklist.md](cninfo_c_class_p2_probe_checklist.md) | **已创建** |
| P2 probe records | [c_class_p2_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p2_probe_records.yaml) | **12/12 `endpoint_found`**（P2-A complete） |

**下一步：** 起草 **C-class P2-A YAML backfill decision**（executive + share_capital + shareholders）；尚未修改 candidate YAML。

---

## 参考

| 文档 | 路径 |
|------|------|
| P1 probe records | [c_class_p1_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p1_probe_records.yaml) |
| P1 probe review | [cninfo_c_class_p1_probe_review.md](cninfo_c_class_p1_probe_review.md) |
| Probe record 模板 | [c_class_probe_record_template.yaml](../fixtures/c_class/probe/c_class_probe_record_template.yaml) |
| F10 discovery 设计 | [cninfo_c_class_f10_source_discovery_design.md](cninfo_c_class_f10_source_discovery_design.md) |
