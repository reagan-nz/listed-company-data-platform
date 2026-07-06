# CNINFO hisAnnouncement/query 参数诊断（Era C Phase 1）

- 生成时间：2026-07-02T09:31:54.966625+00:00
- 脚本：lab/validate_cninfo_report_coverage.py
- 映射输入：outputs/validation/cninfo_company_identity_mapping.csv

## 1. 根因摘要（SZSE / BSE coverage=0）

| 板块 | 旧行为 | 问题 | 修正 |
|------|--------|------|------|
| SSE 主板 / 科创板 | `column=sse`，`stock=code,orgId` | 无（100%） | 保持 |
| SZSE 创业板 | `column=szse`，orgId=`gssh0{code}`（F10 经验规则） | `gssh*` 对 **公告查询** 无效 → `empty_response` | 优先 `CHINEXT_ANNOUNCEMENT_ORGID_OVERRIDES`（numeric orgId）；fallback topSearch |
| BSE 北交所 | `column=neeq`（旧脚本） | probe/eval 使用 `column=bj`；`neeq` 导致 `empty_response` | `column=bj`，fallback `neeq`；stock 试 `920xxx` 与 `430xxx` |

## 2. BOARD_COLUMN_MAP（board × exchange → column）

| board | exchange | column | column fallbacks |
|-------|----------|--------|------------------|
| 主板 | SSE | `sse` | `sse` |
| 主板 | SZSE | `szse` | `szse` |
| 创业板 | SZSE | `szse` | `szse` |
| 北交所 | BSE | `bj` | `bj, neeq` |
| 科创板 | SSE | `sse` | `sse` |

## 3. 与 probe_cninfo EXCHANGE_COLUMN 对照

| exchange | probe_cninfo column | 本脚本 primary column |
|----------|---------------------|-------------------------|
| SSE | `sse` | `sse` |
| SZSE | `szse` | `szse` |
| BSE | `bj` | `bj`（旧为 `neeq`） |

## 4. 公共 payload 字段（build_payload）

- `stock`：`{stock_code},{orgid}`（orgId 非空时）
- `column`：见上表
- `plate` / `category` / `trade`：空字符串
- `tabName`：`fulltext`
- `seDate`：策略相关（`keyword_with_year` 等为空；`longer_time_window` 为近三年）
- `searchkey`：策略关键词
- `isHLtitle`：`true`
- `secid`：空

## 5. 各 exchange / board 请求参数样例

### BSE / 北交所（样本：430017 星昊医药）

| 字段 | 映射 CSV | 查询用值 |
|------|----------|----------|
| company_code | `430017` | — |
| exchange | `BSE` | — |
| board | `北交所` | — |
| cninfo_stock_code | `920017` | stock 候选 |
| cninfo_announcement_query_code | `920017` | stock 候选 |
| cninfo_org_id（CSV） | `9900003482` | orgId 候选 |
| column | — | `bj` |

**参数组合数（内部 fallback，不拆 coverage 行）**：4

前 3 组 param variant：

1. `stock=cninfo_stock_code; orgid=mapping_csv_orgid; column=bj`
   - `stock=920017,9900003482`
   - `column=bj` `searchkey=2024年年度报告` `seDate=` `plate=` `category=`

2. `stock=cninfo_stock_code; orgid=mapping_csv_orgid; column=neeq`
   - `stock=920017,9900003482`
   - `column=neeq` `searchkey=2024年年度报告` `seDate=` `plate=` `category=`

3. `stock=company_code; orgid=mapping_csv_orgid; column=bj`
   - `stock=430017,9900003482`
   - `column=bj` `searchkey=2024年年度报告` `seDate=` `plate=` `category=`

### SSE / 主板（样本：600000 浦发银行）

| 字段 | 映射 CSV | 查询用值 |
|------|----------|----------|
| company_code | `600000` | — |
| exchange | `SSE` | — |
| board | `主板` | — |
| cninfo_stock_code | `600000` | stock 候选 |
| cninfo_announcement_query_code | `600000` | stock 候选 |
| cninfo_org_id（CSV） | `gssh0600000` | orgId 候选 |
| column | — | `sse` |

**参数组合数（内部 fallback，不拆 coverage 行）**：1

前 3 组 param variant：

1. `stock=cninfo_stock_code; orgid=mapping_csv_orgid; column=sse`
   - `stock=600000,gssh0600000`
   - `column=sse` `searchkey=2024年年度报告` `seDate=` `plate=` `category=`

### SSE / 科创板（样本：688001 华兴源创）

| 字段 | 映射 CSV | 查询用值 |
|------|----------|----------|
| company_code | `688001` | — |
| exchange | `SSE` | — |
| board | `科创板` | — |
| cninfo_stock_code | `688001` | stock 候选 |
| cninfo_announcement_query_code | `688001` | stock 候选 |
| cninfo_org_id（CSV） | `9900038969` | orgId 候选 |
| column | — | `sse` |

**参数组合数（内部 fallback，不拆 coverage 行）**：1

前 3 组 param variant：

1. `stock=cninfo_stock_code; orgid=mapping_csv_orgid; column=sse`
   - `stock=688001,9900038969`
   - `column=sse` `searchkey=2024年年度报告` `seDate=` `plate=` `category=`

### SZSE / 创业板（样本：300001 特锐德）

| 字段 | 映射 CSV | 查询用值 |
|------|----------|----------|
| company_code | `300001` | — |
| exchange | `SZSE` | — |
| board | `创业板` | — |
| cninfo_stock_code | `300001` | stock 候选 |
| cninfo_announcement_query_code | `300001` | stock 候选 |
| cninfo_org_id（CSV） | `gssh0300001` | orgId 候选 |
| column | — | `szse` |

**参数组合数（内部 fallback，不拆 coverage 行）**：2

前 3 组 param variant：

1. `stock=cninfo_stock_code; orgid=chinext_announcement_orgid_override; column=szse`
   - `stock=300001,9900008270`
   - `column=szse` `searchkey=2024年年度报告` `seDate=` `plate=` `category=`

2. `stock=cninfo_stock_code; orgid=mapping_csv_orgid; column=szse`
   - `stock=300001,gssh0300001`
   - `column=szse` `searchkey=2024年年度报告` `seDate=` `plate=` `category=`

- 创业板 orgId override：`300001` → `9900008270` （替代 CSV 中 `gssh0300001`）

## 6. 创业板 P0 样本 orgId override 表

| company_code | CSV orgId (gssh) | announcement orgId override |
|--------------|------------------|----------------------------|
| 300001 | `gssh0300001` | `9900008270` |
| 300002 | `gssh0300002` | `9900008268` |
| 300003 | `gssh0300003` | `9900008269` |
| 300004 | `gssh0300004` | `9900008272` |
| 300005 | `gssh0300005` | `9900008308` |
| 300006 | `gssh0300006` | `9900008273` |
| 300007 | `gssh0300007` | `9900008312` |

## 7. 说明

- 多种 stock / orgId / column 组合仅在 `try_find_report` 内部 fallback，**一行仍 = company × report_type × expected_period**。
- 未下载 PDF；未改 `parse_report_period`。
- 完整 coverage 请运行：`python lab/validate_cninfo_report_coverage.py`
- 仅生成本诊断（可加 `--probe-samples` 做一次探测）：`python lab/validate_cninfo_report_coverage.py --diagnostics-only`
