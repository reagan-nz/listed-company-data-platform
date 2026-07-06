# CNINFO C 类 DevTools Probe Plan

_最后更新：2026-07-05_

> **Candidate YAML：** [config/cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml)  
> **Probe 记录模板：** [fixtures/c_class/probe/c_class_probe_record_template.yaml](../fixtures/c_class/probe/c_class_probe_record_template.yaml)  
> **Probe Checklist：** [cninfo_c_class_probe_checklist.md](cninfo_c_class_probe_checklist.md)  
> **权威设计：** [cninfo_c_class_f10_source_discovery_design.md](cninfo_c_class_f10_source_discovery_design.md)

---

## 1. 目的

本计划用于 **人工 DevTools 探测** C 类 F10 / company profile 数据入口，发现并记录：

- **endpoint**（`request_url`）
- **method**（GET / POST）
- **params**（`stockCode` / `orgId` / `companyCode` 等）
- **records_path**（响应 JSON 中数组/对象路径）
- **字段样本**（`sample_fields` / `sample_response_shape`）

探测结果写入 **probe record**（YAML），供后续 **candidate YAML 回填** 与 **known-company profile validation** 使用。

**本计划仅为准备文档；执行 probe 需单独批准，且须遵守项目网络红线。**

---

## 2. 当前状态

| 项 | 状态 |
|----|------|
| C 类 candidate source | **10** 个，全部 `recommended_status: candidate` |
| `endpoint` | 全部 **null**（尚未 probe） |
| `verified` | 全部 **false** |
| JSON Schema | **6** 个 draft-07（[schemas/c_class/](../schemas/c_class/)） |
| Registry lint | **PASS**（12 rules，fail=0） |
| Offline fixture validation | **12/12 PASS** |
| 实际 CNINFO 请求 | **0**（本阶段未 probe） |
| 入库 | **无** |

前置设计已完成：source discovery、profile data model、C/B/D 边界、registry lint、known-company fixture shape test。

**下一步动作：** 按本计划与 checklist，对 P1 source 做 1–3 家 known-company DevTools probe，填写 probe record；**不在本轮自动回填 YAML**。

---

## 3. Probe 范围

### 3.1 Known companies（优先）

| company_code | company_name | 板块 | 用途 |
|--------------|--------------|------|------|
| `600000` | 浦发银行 | 沪市主板 | SSE 代表 |
| `300001` | 特锐德 | 创业板 | SZSE 创业板代表 |
| `688001` | 华兴源创 | 科创板 | SSE 科创板代表 |

三家公司覆盖 **主板 / 创业板 / 科创板**，便于发现 board / market 参数差异。

### 3.2 每 source 样本量

- 每个 `source_id` **先 probe 1–3 家公司**（建议 P1 做满 3 家，P2/P3 至少 1 家）。
- 同一 source 在不同公司上 **request 结构应一致**；若不一致，在 `notes` 中标注 market/board 差异。
- **不做全市场遍历**；不批量脚本抓取。

### 3.3 org_id 获取

probe 前需确认 `org_id`（CNINFO `orgId`）：

- 优先从既有 identity mapping / Phase 1 产物 / `topSearch` 手工查一次（**仅 identity 用途，不计入 profile probe 证据**）。
- probe record 中 `org_id` 可为 null，但应在 notes 说明是否已解析。

---

## 4. Probe source 优先级

按 F10 标签页依赖与 schema 覆盖顺序，建议：

### P1（先做 — 基础画像与证券元数据）

| 序 | source_id | source_category | 说明 |
|----|-----------|-----------------|------|
| 1 | `cninfo_company_basic_profile` | basic_profile | 基本资料；与 P0 `validate_cninfo_f10_company_profile.py` 部分重叠，需 per-source endpoint |
| 2 | `cninfo_company_security_profile` | security_profile | 证券代码、板块、上市状态 |
| 3 | `cninfo_company_industry_profile` | industry_profile | 行业分类 |

### P2（结构型 profile — 高管 / 股本 / 股东）

| 序 | source_id | source_category | 说明 |
|----|-----------|-----------------|------|
| 4 | `cninfo_executive_profile` | executive_profile | 董事高管名单（非 D 类人事变动事件） |
| 5 | `cninfo_share_capital_profile` | share_capital_profile | 股本结构 |
| 6 | `cninfo_top_shareholders_profile` | shareholder_profile | 十大股东 |
| 7 | `cninfo_top_float_shareholders_profile` | shareholder_profile | 十大流通股东 |

### P3（文本型 / 联系 / 分红融资摘要）

| 序 | source_id | source_category | 说明 |
|----|-----------|-----------------|------|
| 8 | `cninfo_company_business_scope` | business_scope | 经营范围 / 公司简介 |
| 9 | `cninfo_company_contact_profile` | contact_profile | 联系方式（可能与 basic 重叠） |
| 10 | `cninfo_dividend_financing_profile` | dividend_financing_profile | 分红融资摘要（非 B/D 事件流） |

**原则：** P1 未 `endpoint_found` 前，P2/P3 可并行准备页面 URL，但 **records_path 回填仍按 P1 → P2 → P3 顺序审查**。

---

## 5. DevTools 记录字段

每次 probe **必须**填写以下字段（见 [c_class_probe_record_template.yaml](../fixtures/c_class/probe/c_class_probe_record_template.yaml)）：

| 字段 | 说明 |
|------|------|
| `probe_id` | 唯一 ID，建议 `C_PROBE_{source_id}_{company_code}_{seq}` |
| `source_id` | candidate YAML 中的 source_id |
| `company_code` | 证券代码 |
| `company_name` | 公司简称（页面显示） |
| `org_id` | CNINFO orgId（若已知） |
| `page_url` | F10 标签页浏览器地址 |
| `request_url` | Network 中实际 API URL（含 path） |
| `method` | `GET` / `POST` |
| `params` | query / body 参数对象 |
| `headers_required_candidate` | 疑似必需请求头（如 `Referer`）；**不记录 Cookie / Token** |
| `records_path` | 响应中数据数组路径，如 `data.records` |
| `sample_response_shape` | 顶层结构简述（object keys / 数组长度） |
| `sample_fields` | 响应中出现的字段名列表（可截断） |
| `row_count` | 数组行数（若适用） |
| `probe_status` | 见 §6 |
| `blocked_or_empty` | 是否空响应 / 被挡 / 仅 HTML |
| `notes` | 自由文本；须含 probe 日期、操作者、异常说明 |

**可选附加：** 将完整响应 JSON 存为本地文件（**不入库、不进 Git 大文件**），在 `notes` 中引用路径。

---

## 6. Probe 判断标准

`probe_status` 枚举与含义：

| probe_status | 含义 | 后续动作 |
|--------------|------|----------|
| `endpoint_found` | 明确 JSON API；params + records_path 可复述 | 可进入回填审查（§8） |
| `endpoint_not_found` | 页面无独立 XHR / 仅 SSR HTML | 标记 `needs_more_probe` 或 Playwright 备选（另案） |
| `empty_but_valid_response` | HTTP 200，结构合法但无业务行 | 记录为合法空态；不升级 status |
| `blocked` | 403 / 429 / 验证码 / 需登录 | **停止该 source 批量 probe** |
| `schema_unknown` | 有数据但字段与 expected_fields 无法对应 | 保留 raw sample；更新 schema draft notes |
| `needs_more_probe` | 信息不足（如仅探 1 家、分页未确认） | 补探 2–3 家或换公司 |

**与 candidate YAML `recommended_status` 的关系：**

- probe 过程中 **保持 `candidate`**。
- 仅当 §8 回填条件满足后，方可改为 **`testing`**（仍 **不得** `verified`）。

---

## 7. 不允许的事

执行 DevTools probe 时 **禁止**：

| 红线 | 说明 |
|------|------|
| 不全市场抓取 | 仅 1–3 家 known company / source |
| 不高频请求 | 请求间隔 ≥ `defaults.sleep_seconds`（0.6s）；避免刷新轰炸 |
| 不登录 | 不使用账号、Cookie、付费接口 |
| 不绕 captcha | 遇验证码即停，记 `blocked` |
| 不写 `verified` | registry / YAML / probe record 均不得出现 verified=true |
| 不入库 | 不写 PostgreSQL / SQLite / MinIO |
| 不下载 PDF | C 类为 profile 表格，非 B 类文档流 |
| 不自动改 YAML | 回填须人工审查 + checklist（§8） |

---

## 8. Probe 后如何回填

**回填对象：** [config/cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml)（**须单独 PR / 人工编辑，不在 probe 脚本中自动写**）。

### 8.1 回填前置条件（全部满足才可改 YAML）

1. 同一 `source_id` 在 **至少 1–3 家** known company 上 `probe_status=endpoint_found`。
2. `request_url`、`method`、`params`、`records_path` 可 **跨公司复述**（或 market 差异已文档化）。
3. `sample_fields` 与 candidate `expected_fields` **大部分可映射**。
4. 已完成 [cninfo_c_class_probe_checklist.md](cninfo_c_class_probe_checklist.md) §4 回填前检查。
5. `raw_record_json` 样本可保留（本地或 probe record 附件），供 offline mapper 草案使用。

### 8.2 允许修改的 YAML 字段

| 字段 | 说明 |
|------|------|
| `endpoint` | 填入 `request_url`（或模板 URL） |
| `page_url` | F10 标签页 URL |
| `records_path` | JSON 路径 |
| `required_keys` | 根据 params 补全 |
| `notes` | 追加 probe 证据摘要与日期 |
| `recommended_status` | 最多 **`testing`** |

### 8.3 禁止修改

- `verified` — **必须保持 false**
- `recommended_status: verified` — **不允许**
- `testing_stable_sample` — **需多公司稳定性复测后另案批准**
- Phase 1 / B / D 类配置文件

### 8.4 回填后下一步

1. 重跑 `lab/lint_cninfo_c_class_registry.py`（endpoint 非 null 后规则行为可能变化）。
2. 用真实 probe 样本更新 / 扩充 offline fixtures（可选）。
3. 建立 **C 类 known-company profile validation 脚本**（小样本 live，config 驱动）。
4. P1 三源稳定后，再推进 P2/P3 probe。

---

## 附录：与既有 P0 脚本关系

`lab/validate_cninfo_f10_company_profile.py` 为早期 **字段可得性** 探索，**不是** per-source registry endpoint 证据。本计划 probe 结果 **取代** P0 中模糊的 endpoint 假设，并以 `source_id` 粒度写入 candidate YAML。
