## CNINFO F10 / 公司资料入口发现（Issue #84）

- 旧接口 `/new/information/topSearch/detailOfQuery` 小样本验证全部失败（http 500/timeout），暂不视为有效 F10 入口。
- 人工发现公司概况入口：`/new/disclosure/stock?stockCode=...&orgId=...#companyProfile`。
- 样例：
  - 600000 → stockCode=600000, orgId=gssh0600000, anchor `#companyProfile`
  - 300750 → stockCode=300750, orgId=gssh0300750, anchor `#companyProfile`
  - 688981 → stockCode=688981, orgId=gshk0000981, anchor `#companyProfile`
  - 430017（星昊医药）若用 stockCode=920017, orgId=9900003482 可到 `#companyProfile`（特例，不可泛化；430017 默认跳到公告页）
- 经验规则（仅供小样本验证，不代表长期稳定）：
  - 600/300：stockCode=code；orgId=`gssh0`+code；anchor `#companyProfile`
  - 688：stockCode=code；orgId=`gshk0000`+后三位；anchor `#companyProfile`
  - 430：需单独映射，目前仅记录 430017→920017/orgId 9900003482，其他 430 需获取 orgId 后再测
- 当前不应将 F10 数据源标记为 rejected；需先完成 entry mapping，再做第二轮 companyProfile 可达性验证。
