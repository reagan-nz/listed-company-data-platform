# 爬虫策略

## 总体原则

**第一阶段不追求广泛爬取，而是先做稳定、公开、可复现的数据。**

年报数据优先使用普通程序化方式（HTTP API + PDF 下载 + 规则抽取）；BrowserUser 作为后续补充，用于复杂网页和交互式页面。

## 分阶段策略

### 阶段一（当前）：CNINFO 年报程序化获取

- **方式**：HTTP API 查询 + 静态 PDF 下载
- **工具**：`lab/probe_cninfo.py` + `requests`
- **频率**：1 req/s（`--throttle`）
- **缓存**：PDF + parsed-page cache，支持断点续跑
- **状态**：946/1020 成功，链路稳定

### 阶段二：全 A 股批量跑

- 复用阶段一链路，按 `sample_universe.py` 生成全量列表
- 断点续跑 + 失败重试（network timeout → 重跑跳过已缓存）
- 不并行（避免 CNINFO 限流）

### 阶段三：BrowserUser 补充

- **适用场景**：
  - 需要 JavaScript 渲染的页面（公司官网 IR）
  - 需要搜索/翻页/点击的交互式页面（e 互动问答列表）
  - 表单查询类页面（政采网搜索）
  - PDF 中不存在但网页上有结构化数据的字段
- **不适用**：
  - CNINFO 年报（已有稳定程序化链路，BrowserUser 无优势）
  - 需要登录/付费的数据源
  - 强反爬且有明确 ToS 限制的站点

### 阶段四：多源融合

- 每个字段标注数据来源（年报 / 公告 / 互动 / 官网）
- 冲突时以官方披露（年报 > 公告 > 其他）为准
- 保留所有来源的 evidence

## BrowserUser 定位

BrowserUser 是**后续补充工具**，不是当前主链路：

| 维度 | 程序化爬虫 | BrowserUser |
|---|---|---|
| 适用 | API、静态 PDF、结构化页面 | JS 渲染、交互、复杂导航 |
| 成本 | 低（无 LLM） | 较高（智能体调用） |
| 稳定性 | 高（确定性） | 中（页面变化敏感） |
| 当前优先级 | **主链路** | 补充 |

## 合规红线

对以下数据源**不绕过、不硬爬**，先记录为限制：

- 需要登录/注册的页面
- 付费/API 授权不清楚的平台（企查查、Wind 等）
- 有明确反爬且 ToS 禁止自动化的站点
- 个人隐私信息

处理方式：在 `source_coverage.csv` 或数据库中标记 `needs_legal_review` / `blocked`，等待合规评估后再决定。

## 与现有代码的关系

- **当前主链路**：`lab/probe_cninfo.py` → `lab/extract_annual_report.py`（不涉及 BrowserUser）
- **早期框架**：`collectors/` 下 15 类 collector 实现了 metadata-only 的存在性检查，可作为新源接入的模板
- **BrowserUser 接入点**：计划在 `collectors/` 下新增 `browser_agent_collector.py`，或在独立模块中实现，输出格式与 `company_profile.json` 对齐

详见 [plans/v0.5_next_step_browser_agent_plan.md](../plans/v0.5_next_step_browser_agent_plan.md)。
