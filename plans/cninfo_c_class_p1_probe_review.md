# CNINFO C 类 P1 Probe Review

_最后更新：2026-07-06_

> **Probe records：** [fixtures/c_class/probe/records/c_class_p1_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p1_probe_records.yaml)  
> **回填决策：** [cninfo_c_class_p1_yaml_backfill_decision.md](cninfo_c_class_p1_yaml_backfill_decision.md)  
> **字段映射：** [cninfo_c_class_basic_profile_field_mapping_draft.md](cninfo_c_class_basic_profile_field_mapping_draft.md)

---

## 1. 目的

本文件审查 **P1 三个 source** 的人工 DevTools probe 结果，汇总 endpoint 证据与 caveat，作为是否 **回填** [cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml) 的审查依据。

**性质：** 设计审查文档；**不代表** endpoint 已 verified；**不触发**自动 YAML 修改。

---

## 2. Probe 范围

### 2.1 Sources（P1）

| source_id | source_category |
|-----------|-----------------|
| `cninfo_company_basic_profile` | basic_profile |
| `cninfo_company_security_profile` | security_profile |
| `cninfo_company_industry_profile` | industry_profile |

### 2.2 Known companies

| company_code | company_name | org_id（probe 记录） |
|--------------|--------------|----------------------|
| `600000` | 浦发银行 | `gssh0600000` |
| `300001` | 特锐德 | `9900008270` |
| `688001` | 华兴源创 | `9900038969` |

**矩阵：** 3 source × 3 company = 9 条 `probe_records`（见 YAML）。

---

## 3. 总体结果

| source_id | endpoint_found | empty_but_valid | needs_more_probe | conclusion |
|-----------|----------------|-----------------|------------------|------------|
| `cninfo_company_basic_profile` | **2** | **1** | **0** | 可回填 candidate endpoint；标注 600000 空数组 caveat |
| `cninfo_company_security_profile` | **3** | **0** | **0** | 可回填 marketOverview 主 endpoint |
| `cninfo_company_industry_profile` | **0** | **0** | **3** | 无独立 endpoint；建议 derived_from basic_profile |

**附属观察：** `getHeadStripData` 对 3/3 有 numeric 返回，记为 `security_profile_annex`，**不**作为独立 source 结论。

---

## 4. basic_profile review

### Endpoint

```
GET https://www.cninfo.com.cn/data20/companyOverview/getCompanyIntroduction?scode=<company_code>
```

| 项 | 值 |
|----|-----|
| Method | GET |
| params | `scode` = 证券代码 |
| records_path | `data.records[0]` |
| headers（candidate） | `Referer` |

### 子路径

| 路径 | 内容 |
|------|------|
| `data.records[0].basicInformation[0]` | 公司基本资料（Fxxx 字段） |
| `data.records[0].listingInformation[0]` | 上市/发行相关字段 |

### 逐公司结果

| company_code | probe_status | 说明 |
|--------------|--------------|------|
| `300001` | `endpoint_found` | basicInformation / listingInformation 非空 |
| `688001` | `endpoint_found` | basicInformation / listingInformation 非空 |
| `600000` | `empty_but_valid_response` | HTTP 200，`records[0]` 存在，但 basicInformation / listingInformation 为空数组 |

### 结论

- **300001 / 688001** 非空，endpoint 行为可解释。
- **600000** 返回 empty arrays，属 **合法空态**，非 blocked。
- **endpoint 可作为 candidate endpoint** 写入 YAML（见回填决策文档）。
- 回填时必须标注 caveat：**部分公司可能 `empty_but_valid_response`**。
- 字段语义为 candidate-level，见 [basic profile field mapping draft](cninfo_c_class_basic_profile_field_mapping_draft.md)。

---

## 5. security_profile review

### Endpoint

```
GET https://www.cninfo.com.cn/new/newInterface/marketOverview?secCode=<code>&orgId=<orgId>&secType=szshe
```

| 项 | 值 |
|----|-----|
| Method | GET |
| params | `secCode`, `orgId`, `secType` |
| records_path | `$`（根对象） |
| headers（candidate） | `Referer`, `X-Requested-With` |

### 逐公司结果

| company_code | probe_status |
|--------------|--------------|
| `600000` | `endpoint_found` |
| `300001` | `endpoint_found` |
| `688001` | `endpoint_found` |

### sample_fields（candidate）

`secCode`, `secName`, `secType`, `tradingStatus`, `age`, `finance`, `delisted`, `sshk`, `szhk`

### 结论

- **3/3 endpoint_found**。
- 可回填为 `cninfo_company_security_profile` 的 **主 endpoint**。
- 字段为 **证券概览**（上市状态、通港股标识等候选语义）。
- **`sshk` / `szhk`** 含义未完全确认，保持 candidate，保留 `raw_record_json`。
- **`secType=szshe`** 在三家样本中相同，需更多 board 样本验证（caveat）。

---

## 6. getHeadStripData annex review

### Endpoint

```
GET https://www.cninfo.com.cn/data20/companyOverview/getHeadStripData?scode=<company_code>
```

| 项 | 值 |
|----|-----|
| records_path | `data.records[0]` |
| observed_for | 600000 / 300001 / 688001（3/3） |

### sample_fields（candidate）

`ENDDATE`, `F005N`, `F020N`, `F021N`, `F041N`, `F081N`, `F089N`, `F102N`, `F109N`, `F111N`, `F115N`

### 结论

- **3/3 有返回**；字段为 **FxxxN numeric** 条带数据。
- **语义未确认**（可能与市值、股本、行情相关，待 UI 对照）。
- 暂作为 **`security_profile_annex`**（见 probe YAML `security_profile_annex` 块）。
- **不标准化**为独立 logical source；**不并入** `share_capital_profile`。
- **不回填**为 candidate YAML 独立 source。

---

## 7. industry_profile review

### 观察

在 `getCompanyIntroduction` → `basicInformation[0]` 中观察到与行业/板块相关的字段：

| raw_field | 候选语义 |
|-----------|----------|
| `F032V` | 所属行业名称 |
| `MARKET` | 上市板块 / 交易所板块 |
| `F044V` | 指数 / 板块标签 |

三家 industry probe record 均为 **`needs_more_probe`**；**未发现**独立 `industry_profile` XHR endpoint。

### 结论

- **未发现**独立 `cninfo_company_industry_profile` endpoint。
- `industry_profile` **可暂时**标记为 **`derived_from` `cninfo_company_basic_profile`**（逻辑派生，非第二 HTTP 源）。
- **不单独回填** endpoint；YAML 中保持 `candidate` / probe 保持 `needs_more_probe`。
- 若未来发现独立 API，再修订本 review。

---

## 8. 红线

本审查与后续回填均须遵守：

| 红线 | 说明 |
|------|------|
| **不写 verified** | registry / YAML / probe record 均 `verified: false` |
| **不入库** | 无 DB / MinIO 写入 |
| **不做全市场** | 仅 3 家 known-company 证据 |
| **不升级 testing_stable_sample** | 回填后最多 `testing`；稳定性需另案复测 |
| **不自动脚本批量 probe** | 回填前须人工 checklist §4 |

---

## 附录：相关文件

| 文件 | 用途 |
|------|------|
| [c_class_p1_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p1_probe_records.yaml) | 原始 probe 证据 |
| [cninfo_c_class_p1_yaml_backfill_decision.md](cninfo_c_class_p1_yaml_backfill_decision.md) | 回填 / 暂缓决策 |
| [cninfo_c_class_probe_checklist.md](cninfo_c_class_probe_checklist.md) | 回填前 checklist |
