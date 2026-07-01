# CNINFO F10 / 公司资料验证最终总结（Issue #84）

## 1. 验证目标

Issue #84 的目标是验证 CNINFO 个股 F10 / 公司资料是否能提供公司基础属性与公司资料属性，重点关注以下字段是否可从小样本中稳定获取：

- `industry`
- `company_profile`
- `main_business_summary`
- `registered_address`
- `office_address`
- `contact_phone`
- `contact_email`
- `board_secretary`

以及辅助字段如 `stock_short_name`、`listing_status`、`website` 等。

**边界强调：**

- 本轮为 **P0 小样本验证**（40 家公司），不是生产采集。
- **不做** PostgreSQL / MongoDB / MinIO 数据库接入。
- **不使用** BrowserUser；不绕过登录 / 验证码 / 权限。
- 验证产物为 lab 脚本输出 CSV / summary，供后续决策参考。

---

## 2. 第一轮：旧接口验证失败

**尝试路径：** `/new/information/topSearch/detailOfQuery`（HTTP POST）

**结果：**

| 指标 | 数值 |
|---|---|
| 样本数 | 40 |
| success | 0 |
| partial | 0 |
| failed | 40 |
| 主要失败原因 | http_error（39）、network_timeout（1） |

**结论：**

- 40 家样本在该接口上 **全部 failed**，未能获取有效 F10 / 公司资料字段。
- 后续人工检查发现，该路径 **不是合适的 F10 / 公司资料入口**（返回 500 / timeout，且无法定位 `#companyProfile` 页面）。
- **这不等于 CNINFO F10 数据源整体不可用**，而是说明：**旧入口 / 旧参数方式失败**，需要寻找正确的页面入口与映射方式。

相关产物：`cninfo_f10_company_profile_validation.csv`、`cninfo_f10_company_profile_validation_summary.md`

---

## 3. 第二轮：新入口发现

**新入口形式：**

```
https://www.cninfo.com.cn/new/disclosure/stock?stockCode=<stockCode>&orgId=<orgId>#companyProfile
```

**参数说明：**

| 参数 | 含义 |
|---|---|
| `stockCode` | CNINFO 页面实际使用的股票代码（可能与样本 `company_code` 不同，如北交所 430→920） |
| `orgId` | CNINFO 内部公司 ID，**不能随意伪造** |
| `#companyProfile` | 公司资料锚点，指向「公司概况 / 公司资料」区块 |

**要点：** `company_code` **不能直接替代** `stockCode + orgId` 组合；必须先完成 entry mapping，才能构造有效 URL。

相关产物：`cninfo_f10_entry_mapping.csv`、`cninfo_f10_entry_discovery_notes.md`、`cninfo_f10_orgid_mapping_analysis.md`

---

## 4. entry mapping 与 orgId 规则

### 4.1 已验证 / 已采用的映射方式

| 板块 | stockCode 规则 | orgId 规则 | 当前判断 |
|---|---|---|---|
| 600 / 300 | stockCode = 原代码 | orgId = `gssh0` + 原代码 | 小样本中 **部分有效**；reachability 10 success / 7 partial |
| BSE 430 | 430xxx → 920xxx（后缀替换） | **人工 orgId**（无公式） | 6 家人工映射后 **reachability 6/6 success** |
| STAR 688 | stockCode = 原代码 | ~~`gshk0000`+后三位~~ **已推翻**；改用 **人工 orgId** | 7 家人工映射后 **reachability 7/7 success** |
| 000 深交所主板 | 未知 | 未知 | **10 家 needs_orgid_mapping**，尚未解决 |

### 4.2 orgId 核心观察

- **orgId 暂无可靠统一公式**；形态包括 `gssh0...`、`99000...`、`gfbj...` 等，需逐板块 / 逐家确认。
- BSE 6 家、STAR 7 家的人工映射均来自 **公司名称搜索 / 页面人工核对**，只适用于当前 P0 小样本。
- 688 原经验规则 `gshk0000 + 后三位` 经 Playwright 验证 **全部 failed**，已废弃。
- 后续应从 CNINFO **搜索结果页、页面跳转链接或公开接口** 中自动解析 orgId，再扩展映射表。

### 4.3 entry mapping 概况（40 家 P0 样本）

- 已通过经验规则或人工映射得到 `cninfo_profile_url`：**30 家**
- 仍标记 `needs_orgid_mapping`：**10 家**（000001–000012 深交所主板）

---

## 5. 页面可达性验证结果

基于最新 `cninfo_f10_profile_page_reachability.csv` / summary：

| 指标 | 数值 |
|---|---|
| entry mapping 总数 | 40 |
| success | 23 |
| partial | 7 |
| failed | 10 |
| HTTP 200 | 30 / 40 |

**按 profile_url_rule 分布：**

| profile_url_rule | 数量 | success | partial | failed |
|---|---|---|---|---|
| manual_rule_600_300_gssh0 | 17 | 10 | 7 | 0 |
| manual_star_orgid_mapping | 7 | 7 | 0 | 0 |
| manual_bse_430_to_920_orgid_mapping | 6 | 6 | 0 | 0 |
| needs_orgid_mapping | 10 | 0 | 0 | 10 |

**观察：**

- 600 / 300 经验规则：17 家全部 HTTP 200，但 7 家为 partial（疑似 JS shell，关键词不可见于静态 HTML）。
- BSE 6 家、STAR 7 家：人工 orgId 映射后 **全部 reachability success**。
- needs_orgid_mapping 10 家：无 profile URL，未尝试访问。

相关产物：`cninfo_f10_profile_page_reachability.csv`、`cninfo_f10_profile_page_reachability_summary.md`

---

## 6. 静态 HTML 字段验证结果

基于最新 `cninfo_f10_static_html_field_validation.csv` / summary：

| 指标 | 数值 |
|---|---|
| 输入（reachability success 页面） | 23 |
| success | 0 |
| partial | 0 |
| failed | 23 |
| 各目标字段可得性 | **0 / 23** |

**结论：**

- 静态 HTML **不足以** 支持 F10 / 公司资料字段抽取。
- 即使页面 HTTP 200 且 reachability success，HTML 中也不包含可解析的公司资料字段。
- 字段内容需依赖 **前端 JS 渲染** 后才可见。

相关产物：`cninfo_f10_static_html_field_validation.csv`、`cninfo_f10_static_html_field_validation_summary.md`

---

## 7. Playwright 字段验证结果

基于最新 `cninfo_f10_playwright_profile_field_validation.csv` / summary：

### 7.1 整体验证概况

| 指标 | 数值 |
|---|---|
| 实际验证 | 30 |
| success | 22 |
| partial | 1 |
| failed | 7 |

### 7.2 按 sample_source 分布

| sample_source | 数量 | success | partial | failed |
|---|---|---|---|---|
| static_html_no_fields | 23 | 22 | 1 | 0 |
| reachability_partial | 7 | 0 | 0 | 7 |

### 7.3 按 profile_url_rule 分布

| profile_url_rule | success | partial | failed |
|---|---|---|---|
| manual_bse_430_to_920_orgid_mapping | 6 | 0 | 0 |
| manual_star_orgid_mapping | 6 | 1 | 0 |
| manual_rule_600_300_gssh0 | 10 | 0 | 7 |

### 7.4 字段可得性（30 家验证样本）

| 字段 | 可得 / 总数 |
|---|---|
| company_profile | 23 / 30 |
| industry | 22 / 30 |
| main_business_summary | 22 / 30 |
| registered_address | 22 / 30 |
| office_address | 22 / 30 |
| contact_phone | 22 / 30 |
| contact_email | 22 / 30 |
| board_secretary | 22 / 30 |
| stock_short_name | 0 / 30 |
| listing_status | 0 / 30 |
| website | 0 / 30 |

**观察：**

- 对 **映射正确且 JS 渲染完成** 的页面，Playwright 可提取核心公司资料字段（company_profile、主营业务、地址、联系方式、董秘等）。
- `static_html_no_fields` 来源 23 家中 22 success / 1 partial，说明静态 HTML 失败样本在 Playwright 后大多可恢复。
- `reachability_partial` 来源 7 家 **全部 failed**（7/7），说明 partial 标记的 600/300 页面即使 Playwright 仍未能稳定提取字段，需进一步排查页面结构或等待策略。
- `stock_short_name`、`listing_status`、`website` 在当前轻量正则规则下 **未提取成功**，需后续优化抽取规则或 DOM 定位。

相关产物：`cninfo_f10_playwright_profile_field_validation.csv`、`cninfo_f10_playwright_profile_field_validation_summary.md`

---

## 8. 当前结论

综合 #84 完整验证链路（旧接口 → 新入口 → entry mapping → reachability → static HTML → Playwright）：

1. **CNINFO F10 / 公司资料数据源有价值**：在正确入口与正确 orgId 映射下，页面包含 industry、company_profile、main_business_summary、地址、联系方式、董秘等字段。

2. **旧接口不可用**：`/new/information/topSearch/detailOfQuery` 不应作为 F10 / 公司资料主入口。

3. **静态 HTML 不足**：23 家 reachability success 页面静态 HTML 字段抽取 **0/23**，必须依赖 JS 渲染（Playwright 或等效方案）。

4. **Playwright 可提取核心字段**：30 家验证样本中 22 success / 1 partial；核心资料字段可得性约 22–23 / 30。

5. **最大阻塞是 stockCode + orgId 映射**，而非页面本身是否存在：
   - 600/300 经验规则部分有效（10 success / 7 failed in Playwright）；
   - BSE / STAR 需人工 orgId，但映射正确后 reachability 与 Playwright 表现良好；
   - 000 深交所 10 家仍缺 orgId，无法进入验证链。

6. **生产化前仍需解决：**
   - orgId 自动化获取与映射维护；
   - 字段抽取规则稳定性（含 partial / failed 页面、reachability_partial 7 家全 failed）；
   - 请求节流、失败重试、验证码 / 登录检测；
   - 合规边界与长期可用性监控。

---

## 9. recommended_status

**建议状态：`partial / testing`**

| 不应写入 | 原因 |
|---|---|
| `verified` | 仅 40 家小样本；orgId 大量依赖人工映射；600/300 仍有 7 家 Playwright failed |
| `rejected` | 数据源有价值；Playwright 已证明核心字段可提取 |

**说明：**

- 该状态 **只代表当前 P0 小样本验证结果**。
- **不代表** 长期稳定可用或可直接进入生产采集。
- F10 / 公司资料可作为 **candidate 数据源** 继续迭代 mapping 与抽取规则。

---

## 10. 后续建议

1. **设计持久化字段**：在 schema 中单独设计 `cninfo_stock_code`、`cninfo_org_id`、`cninfo_profile_url`、`profile_url_rule`、`mapping_status`，与 `company_code` 解耦。

2. **orgId 自动化**：从 CNINFO 搜索结果页、披露列表跳转链接或公开接口自动解析 orgId，减少人工维护。

3. **补全映射**：对 000 / remaining `needs_orgid_mapping` 10 家样本继续人工或半自动补映射；扩展 BSE / STAR 映射表验证泛化性。

4. **抽取规则稳定性**：对 Playwright success 页面做字段抽取规则回归测试；优化 `stock_short_name`、`listing_status`、`website` 提取；排查 reachability_partial 7 家 Playwright 全 failed 原因。

5. **再评估 schema 接入**：在 mapping 自动化与抽取稳定性达标后，再决定是否进入 `company_profile` schema 设计或数据库接入。

6. **不建议现在直接全量 Playwright 抓取**：当前 mapping 未完成、规则未稳定、合规与节流策略未定型；应继续小样本迭代。

---

## 11. 边界确认

- **未使用** BrowserUser。
- **未绕过** 登录 / 验证码 / 权限。
- **未做** PostgreSQL / MongoDB / MinIO 接入。
- **未修改** `docs/data_sources.md`。
- **未修改** `plans/storage_schema_design_plan.md`。
- **未将** F10 数据源写成长期稳定可用（`verified`）。
- 本文档为 Issue #84 验证链路的 **归纳总结**，基于已有 CSV / summary 整理；撰写时未联网、未运行新验证、未修改验证结果 CSV。

---

## 附录：验证链路一览

```
P0 样本（40 家）
    │
    ├─► 第一轮：旧接口 detailOfQuery ──► 40 failed
    │
    ├─► 第二轮：新入口 #companyProfile + entry mapping
    │       ├─ 600/300：gssh0+code（17 家）
    │       ├─ BSE：430→920 + 人工 orgId（6 家）
    │       ├─ STAR：688 + 人工 orgId（7 家）
    │       └─ needs_orgid_mapping（10 家）
    │
    ├─► 页面可达性 ──► 23 success / 7 partial / 10 failed
    │
    ├─► 静态 HTML 字段 ──► 0/23 字段可得（全部 failed）
    │
    └─► Playwright 字段 ──► 22 success / 1 partial / 7 failed（30 家）
            └─ 核心字段 ~22–23/30 可得
```

**主要产物索引：**

| 阶段 | 文件 |
|---|---|
| 样本 | `cninfo_p0_sample_companies.csv` |
| 旧接口 | `cninfo_f10_company_profile_validation.csv` |
| Entry mapping | `cninfo_f10_entry_mapping.csv` |
| orgId 分析 | `cninfo_f10_orgid_mapping_analysis.md` |
| 可达性 | `cninfo_f10_profile_page_reachability.csv` |
| 静态 HTML | `cninfo_f10_static_html_field_validation.csv` |
| Playwright | `cninfo_f10_playwright_profile_field_validation.csv` |
