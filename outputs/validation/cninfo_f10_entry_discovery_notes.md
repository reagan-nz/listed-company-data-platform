## CNINFO F10 / 公司资料入口发现（Issue #84）

- 旧接口 `/new/information/topSearch/detailOfQuery` 小样本验证全部失败（http 500/timeout），暂不视为有效 F10 入口。
- 人工发现公司概况入口：`/new/disclosure/stock?stockCode=...&orgId=...#companyProfile`。
- 样例：
  - 600000 → stockCode=600000, orgId=gssh0600000, anchor `#companyProfile`
  - 300750 → stockCode=300750, orgId=gssh0300750, anchor `#companyProfile`
- 经验规则（仅供小样本验证，不代表长期稳定）：
  - 600/300：stockCode=code；orgId=`gssh0`+code；anchor `#companyProfile`
  - 688：**原规则 `gshk0000`+后三位已被小样本推翻**；7 个 P0 样本需人工 orgId（见下节）
  - 430（北交所）：stockCode 可映射为 920xxx（430→920 后缀替换），但 orgId 无简单公式

## 科创板 688 / orgId 人工映射（小样本）

Playwright 验证显示，按 `gshk0000`+后三位构造的 688 URL **全部 failed**。人工搜索后补充 7 家映射：

| company_code | 公司简称 | cninfo_stock_code | cninfo_org_id |
|---|---|---|---|
| 688001 | 华兴源创 | 688001 | 9900038969 |
| 688002 | 睿创微纳 | 688002 | 9900038939 |
| 688003 | 天准科技 | 688003 | gfbj0833231 |
| 688004 | 博汇科技 | 688004 | gfbj0871038 |
| 688005 | 容百科技 | 688005 | 9900038937 |
| 688006 | 杭可科技 | 688006 | 9900037551 |
| 688007 | 光峰科技 | 688007 | 9900038970 |

观察：

- **688 stockCode 仍使用原代码**（688001 等）。
- **orgId 不可简单构造**；可能是 `99000...` 或 `gfbj...` 等形式，**没有统一公式**。
- 写入 `STAR_MANUAL_MAPPING`；`profile_url_rule = manual_star_orgid_mapping`。
- 688 开头但不在字典中：标记 `star_orgid_required`，不伪造 orgId。
- 后续应从 CNINFO 搜索结果、页面跳转或公开接口中获取 orgId。

## 北交所 430→920 / orgId 人工映射（小样本）

已人工补充 6 个北交所样本的 companyProfile URL（来源：公司名称搜索，非接口自动解析）：

| company_code | 公司简称 | cninfo_stock_code | cninfo_org_id |
|---|---|---|---|
| 430017 | 星昊医药 | 920017 | 9900003482 |
| 430047 | 诺思兰德 | 920047 | 9900006121 |
| 430090 | 同辉信息 | 920090 | 9900020567 |
| 430139 | 华岭股份 | 920139 | 9900024205 |
| 430198 | 微创光电 | 920198 | 9900024889 |
| 430300 | 辰光医疗 | 920300 | 9900023934 |

观察：

- **430→920 stockCode** 在这 6 个样本上成立（430017→920017 等）。
- **orgId 没有简单公式**，当前值均来自人工搜索结果，写入 `BSE_MANUAL_MAPPING`。
- 该映射**只适用于当前 P0 小样本**，不代表所有北交所公司可泛化。
- 430 开头但不在字典中的公司，仍标记为 `bse_orgid_required`，不伪造 orgId。
- `profile_url_rule = manual_bse_430_to_920_orgid_mapping`；`mapping_status = mapped`。

后续方向：

- 可考虑从 CNINFO 搜索结果页或相关接口自动解析 orgId，再扩展映射表。
- 映射更新后应重新运行 `validate_cninfo_f10_profile_page_reachability.py`，再纳入 Playwright 字段验证。

- 当前不应将 F10 数据源标记为 rejected；需先完成 entry mapping，再做 companyProfile 可达性与字段验证。
