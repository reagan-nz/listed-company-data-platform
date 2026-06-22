# 数据来源

## 当前已验证数据源

### 巨潮资讯网（CNINFO）

| 属性 | 说明 |
|---|---|
| **名称** | 巨潮资讯网（www.cninfo.com.cn） |
| **用途** | A 股上市公司年报 PDF 获取与基础字段抽取 |
| **当前状态** | **已验证可用**，1000 家评估中 946 家成功 |
| **获取方式** | HTTP API 查询公告列表 → 筛选全文年报 → 下载 static.cninfo.com.cn PDF |
| **实现** | [lab/probe_cninfo.py](../lab/probe_cninfo.py) |
| **可获得字段** | 11 项基础字段（见 [database_schema.md](database_schema.md)） |

**获取流程**：

1. 从 CNINFO 股票列表 API 获取 `orgId`（`lab/sample_universe.py`）
2. 按 stock_code + orgId 查询 2024–2025 年度公告
3. `pick_full_report()` 筛选全文年报（排除摘要/取消/更正/H 股优先选 A 股）
4. 下载 PDF 到 `outputs/generalization/<code>/<code>.pdf`
5. 解析并抽取字段

**优点**：

- 官方披露渠道，数据权威
- 覆盖全部 A 股（含主板/创业板/科创板/北交所）
- 年报结构相对标准化，锚点抽取可行
- 免费公开访问，无需登录

**限制**：

- 网络不稳定（VPN 断开导致 timeout；已实现断点续跑）
- 部分公司无 2024 年报（退市/ST，status=no_announcement）
- 扫描件 PDF 无文本层（status=no_text_layer，需 OCR）
- 摘要 vs 全文：probe 必须筛选全文（已实现 `pick_full_report`）
- A+H 双上市：H 股年报结构不同（已实现 A 股优先）
- 金融公司披露格式与工业 schema 不匹配

**合规注意事项**：

- 仅访问公开披露信息，符合信息披露法规
- 请求频率控制在 1 req/s（`--throttle 1.0`）
- 不绕过任何访问控制
- 存储 PDF 仅供内部分析，不对外再分发
- 遵守网站 robots.txt 与服务条款

**当前结论**：CNINFO 年报是当前最可靠、覆盖最广的数据源，作为第一阶段唯一数据源。后续可叠加其他源补充。

---

## 预留数据源（待接入）

以下数据源已在 [config/sources.yaml](../config/sources.yaml) 中定义框架，或在路线图中规划，**尚未接入抽取 pipeline**。

| 数据源 | 类别 | 预期用途 | 状态 | 备注 |
|---|---|---|---|---|
| 上交所 / 深交所公告 | 交易所 | 临时公告、重大事项 | 待接入 | collectors/ 有框架 |
| 公司官网 IR 页面 | 官网 | 投资者关系、业务介绍 | 待接入 | 需 BrowserUser |
| 上证 e 互动 / 深交所互动易 | 互动 | 投资者问答 | 待接入 | 需 BrowserUser |
| 政府采购网 | 政采 | 中标信息、合同 | 待接入 | 公开但需搜索 |
| 国家知识产权局 | 专利 | 专利数量、技术方向 | 待接入 | 公开 API 有限 |
| 商标局 | 商标 | 商标注册信息 | 待接入 | |
| 新闻 / 舆情 | 媒体 | 事件信号（标题+链接） | 待接入 | 不存全文 |
| 企查查 / 天眼查 | 商业 | 工商信息、关联关系 | 待评估 | 付费/授权限制 |
| 雪球 / 股吧 / 微博 | 社交 | 舆情信号 | 待评估 | 仅 metadata |
| Tushare / AkShare | 金融 API | 行情、财务指标 | 待评估 | 授权/许可不确定 |
| BrowserUser 可访问网页 | 智能体 | 上述复杂/交互页面的补充 | 规划中 | 见 v0.5 plan |

**接入原则**：

- 先验证公开可获取性，再写 collector
- 每条记录保留 `source_url` + 获取时间
- 强反爬/付费/需登录源：记录为限制，不绕过
- BrowserUser 仅作补充，不替代 CNINFO 年报主链路
