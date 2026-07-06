# CNINFO C 类 Basic Profile Field Mapping Draft

_最后更新：2026-07-06_

> **数据来源：** `GET .../getCompanyIntroduction?scode=<company_code>`  
> **Probe review：** [cninfo_c_class_p1_probe_review.md](cninfo_c_class_p1_probe_review.md)  
> **目标 schema：** [c_company_basic_profile.schema.json](../schemas/c_class/c_company_basic_profile.schema.json)

---

## 1. 目的

记录 `getCompanyIntroduction` 响应中 **basicInformation** / **listingInformation** 原始字段到 C 类 profile logical schema **候选标准字段** 的映射草案。

**性质：** UI/DevTools 初步观察；**非 verified**；mapper / live validation 实施前须复测。

---

## 2. basicInformation 字段映射

路径前缀：`data.records[0].basicInformation[0]`

| raw_field | candidate_standard_field | confidence | notes |
|-----------|--------------------------|------------|-------|
| `ASECCODE` | `company_code` | high | A股代码 |
| `ASECNAME` | `company_name` | high | A股简称 |
| `ORGNAME` | `legal_name` | high | 公司全称 |
| `F001V` | `english_name` | high | 英文名 |
| `F003V` | `legal_representative` | high | 法定代表人 |
| `F004V` | `registered_address` | high | 注册地址 |
| `F005V` | `office_address` | high | 办公地址 |
| `F006D` | `listing_date` | high | 上市日期（与 listingInformation 交叉核对） |
| `F006V` | `postal_code` | medium | 邮政编码；schema 暂无标准字段，保留 raw |
| `F007N` | `registered_capital_candidate` | medium | 注册资本；单位待确认 |
| `F010D` | `establishment_date` | high | 成立日期；schema 暂无标准字段，保留 raw |
| `F011V` | `company_website` | high | 官网 |
| `F012V` | `email` | high | 邮箱；schema 暂无标准字段，可映射 contact 扩展 |
| `F013V` | `phone` | high | 电话；schema 暂无标准字段，可映射 contact 扩展 |
| `F014V` | `fax` | high | 传真；schema 暂无标准字段，可映射 contact 扩展 |
| `F015V` | `main_business` | high | 主营业务 |
| `F016V` | `business_scope` | high | 经营范围 |
| `F017V` | `company_history_or_introduction` | high | 公司简介 / 历史沿革 |
| `F018V` | `board_secretary_candidate` | medium | 董秘候选 |
| `F032V` | `industry` | high | 所属行业（**industry_profile 派生来源**） |
| `MARKET` | `listed_board` | high | 上市板块 / 交易所板块 |
| `F044V` | `index_or_plate_labels` | medium | 指数 / 板块标签 |
| `F042V` | `controller_or_representative_candidate` | low | 待确认 |
| `F052V` | `unknown` | low | raw only |
| `F053V` | `unknown` | low | raw only |

---

## 3. listingInformation 字段映射

路径前缀：`data.records[0].listingInformation[0]`

| raw_field | candidate_standard_field | confidence | notes |
|-----------|--------------------------|------------|-------|
| `SECCODE` | `company_code` | high | 证券代码 |
| `F047V` | `sponsor_or_underwriter_candidate` | medium | 保荐/承销候选 |
| `F007N` | `listing_batch_or_issue_candidate` | low | 发行批次候选 |
| `F028N` | `issue_amount_candidate` | low | 发行量候选 |
| `F008N` | `issue_price_candidate` | medium | 发行价候选 |

---

## 4. 字段处理原则

| confidence | 处理 |
|------------|------|
| **high** | 可进入 `c_company_basic_profile` 标准字段（mapper 输出）；仍保留 `raw_record_json` |
| **medium** | 标准字段带 `_candidate` 后缀或进 notes；优先保留 raw |
| **low** / **unknown** | **仅** `raw_record_json`；不强行塞入 schema |
| schema 暂无字段 | 不强塞；待 schema draft 扩展或归入 contact / annex |

**通用：**

- 所有 logical record **必须**保留 `raw_record_json` + `raw_record_hash`。
- **`field_confidence`** 与上表 confidence 对齐（high → high，medium → medium，low/unknown → low 或 unknown）。
- **不写 verified**；mapper 输出 `source_status` 最高 `testing`。

---

## 5. 当前 caveat

| caveat | 说明 |
|--------|------|
| **600000 empty_but_valid** | `basicInformation` / `listingInformation` 为空数组；mapper 须处理空态，不得伪造字段 |
| **语义来源** | 字段含义来自 F10 UI + DevTools 初步观察，非官方字段字典 |
| **需 validation script** | 回填 YAML 后须对 600000 / 300001 / 688001 跑 live validation 确认 |
| **industry 派生** | `F032V` / `MARKET` / `F044V` 同时服务 `cninfo_company_industry_profile` 逻辑派生 |
| **contact 重叠** | `F011V`–`F014V` 与 `cninfo_company_contact_profile` expected_fields 重叠，跨 source 一致性待审 |

---

## 6. 与 security_profile / annex 的边界

| 数据 | 映射文档 |
|------|----------|
| `marketOverview` 根对象 | 见 probe review §5；映射至 security 字段（`secCode`, `tradingStatus` 等），**不在本文档** |
| `getHeadStripData` FxxxN | **暂不映射**；security annex raw-only |

---

## 下一步

1. 实施 `lab/cninfo_c_class_mappers.py`（或等价）草案：`getCompanyIntroduction` → `c_company_basic_profile`。
2. YAML 回填后 live validation 3 家 known company。
3. 根据 validation 结果修订 confidence 与 schema draft notes。
