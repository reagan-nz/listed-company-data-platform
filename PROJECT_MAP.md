# 仓库地图（PROJECT_MAP）

_最后更新：2026-07-02_

> **这份文件是"仓库导航图"。** 目的很直接：让任何人（包括你自己、以及便宜/换代的 AI 模型）打开仓库后，**不用逐个文件猜用途**，就能知道「现在聚焦什么、哪个文件属于哪条线、哪个能删/能停/要留」。
>
> 阅读顺序建议：先读本文件 → 再读 [CURRENT_STATUS.md](CURRENT_STATUS.md)（当前具体在做什么）→ 需要背景再看 [ROADMAP.md](ROADMAP.md) / [CHANGELOG.md](CHANGELOG.md)。

---

## 0. 一句话现状

仓库里叠了**三代方向**的代码与文档。**当前唯一聚焦的是第三代：系统盘点巨潮（CNINFO）能稳定拿到哪些数据，先把"类年报（定期报告）"这条最成熟的路径做扎实，再研究其他数据。** 前两代（通用多源采集框架、2024 全市场年报数据底座）**已冻结**——保留、可参考、但当前不再推进，也**不要删**（磁盘不紧张，删了反而丢背景）。

---

## 1. 三代方向速览

| 代 | 名称 | 状态 | 一句话 | 代表目录/文件 |
|---|---|---|---|---|
| **Era A** | 通用多源采集框架（v0.1 设想） | **冻结·基本未使用** | 想从新闻/官网/专利/招投标/政策等"所有来源"采集，只搭了框架没真正跑起来 | `collectors/`、`main.py`、`config/sources.yaml`、`config/companies.yaml` |
| **Era B** | 2024 全市场年报数据底座 | **冻结·已完成** | 从 CNINFO 年报 PDF 批量抽 11 个字段 + 质量审计，入 SQLite（6124 家）。已交付，不再改 | `lab/` 里的年报/全市场/审计脚本、`outputs/generalization/`、`outputs/db/` |
| **Era C** | CNINFO 数据源能力研究 | **活跃·当前聚焦** | 盘点巨潮所有栏目能拿到什么 → 分类 → 先做"类年报"稳定抽取 → 再研究其他 | `lab/validate_cninfo_*.py`、`outputs/validation/`、`plans/cninfo_data_source_value_inventory.md` |

> 为什么感觉"偏"了：顶层文档（ROADMAP/CURRENT_STATUS）一度把重心写成"动态平台架构 + PostgreSQL/MinIO/MongoDB 三层存储设计"。那是**在数据源还没验证透之前就先设计数据库**，属于超前。当前把重心**拉回 Era C**：先回答"巨潮到底能稳定拿到什么"。存储架构设计（`plans/storage_schema_design_plan.md`、`plans/dynamic_data_platform_plan.md`）**暂缓**，留作未来参考。

---

## 2. 当前聚焦（Era C）用哪些文件

这是你现在真正要看、要用的东西。

### 2.1 活跃脚本（`lab/`）
| 文件 | 用途 | 是否独立可跑 |
|---|---|---|
| `validate_cninfo_report_announcements.py` | **当前主力**：验证年报/半年报/季报（"类年报"定期报告）能否稳定检索到，解析 `report_period`。支持 `--summary-only` 只重生成摘要 | 是（独立，不依赖 Era B） |
| `validate_cninfo_announcement_categories.py` | 验证 14 类公告的可检索性 | 是 |
| `validate_cninfo_latest_announcements.py` | 验证"最新公告列表"栏目 | 是 |
| `validate_cninfo_pdf_metadata.py` | 验证公告 PDF 元数据（URL/hash 规则，不下载正文） | 是 |
| `validate_cninfo_f10_company_profile.py` | 验证个股 F10 公司资料字段 | 是 |
| `validate_cninfo_f10_profile_page_reachability.py` | F10 页面可达性 | 是 |
| `validate_cninfo_f10_static_html_fields.py` | F10 静态 HTML 字段 | 是 |
| `validate_cninfo_f10_playwright_profile_fields.py` | F10 Playwright 渲染字段 | 是 |
| `test_cninfo_announcement_retrieval_rules.py` | 检索规则回放测试 | 是 |
| `build_cninfo_p0_sample_companies.py` | 生成 40 家 P0 样本公司清单 | 是 |

### 2.2 活跃配置（`config/`）
- `cninfo_announcement_categories.yaml` — 14 类公告定义
- `cninfo_announcement_retrieval_strategies.yaml` — 检索策略（must/optional/exclude 关键词）

### 2.3 活跃文档
- `plans/cninfo_data_source_value_inventory.md` — **这条线的核心文档**：巨潮栏目盘点 + 数据类型分类（属性/文档/事件/证据/候选）+ P0/P1/P2 优先级 + 验证记录模板。你想要的"盘点→分类"其实已经在这里。
- `plans/cninfo_p0_sample_company_selection.md` — P0 样本公司选取说明
- `outputs/validation/` — 所有 CNINFO 验证的产物（CSV + summary.md），见第 4 节

### 2.4 "类年报 vs 非类年报"的现成分类
`plans/cninfo_data_source_value_inventory.md` 第 3–4 节已经做了分类。用你的话对齐一下：

- **类年报（定期报告，路径最成熟，优先做）**：年报、半年报、季报 → 共同特征是"定期披露 + 标题模式稳定 + 有 PDF"，能复用同一套检索机制（`validate_cninfo_report_announcements.py` 已跑通）。
- **非类年报（后续研究）**：最新公告流、个股 F10/公司资料（结构化字段）、风险/监管/分红/治理等事件公告、股本/股东/解禁等结构化表、互动易问答等。它们要么字段结构不稳定、要么需要事件分类规则、要么需要 Playwright。

---

## 3. 冻结部分（Era A / Era B）——保留但当前不碰

### 3.1 Era B：年报抽取引擎（`lab/`，紧耦合，别单独挪）
> ⚠️ 这些文件用 `from lab.xxx import` **相互紧耦合**。核心是 `field_schema.py` / `extract_annual_report.py` / `probe_cninfo.py` / `eval_generalize.py`，被下面十几个脚本引用。**不要单独移动某一个文件**，否则会同时挪断多处 import。要动就整组一起动，并同步改 import。

| 分组 | 文件 | 说明 |
|---|---|---|
| 核心引擎（可复用） | `field_schema.py`、`extract_annual_report.py`、`probe_cninfo.py`、`eval_generalize.py` | 11 字段定义 + PDF 抽取 + CNINFO 探测 + 批量评估。若未来复用年报抽取能力，从这里入手 |
| 全市场运行 | `sample_universe.py`、`make_full_market_yaml.py`、`merge_full_market_batches.py`、`run_full_market_2024.sh` | 生成公司全集、批次 YAML、合并结果 |
| SQLite 原型 | `db_init.py`、`db_import.py` | 建表 + 导入（生成 `outputs/db/*.db`，已 gitignore） |
| 一次性审计/修复（几乎不会再跑） | `strict_audit_full_market.py`、`strict_audit_financial_full_market.py`、`refresh_revenue_full_market.py`、`refresh_rnd_full_market.py`、`financial_calibration_sample.py`、`calibration_sample.py`、`financial_audit_fix_30{d,e,f}_dryrun.py`、`revenue_residual_fix_32b_dryrun.py`、`rnd_residual_fix_32c_{dryrun,r3_dryrun,post_apply_verify}.py` | 都是特定 issue 的一次性 dryrun/写回脚本。历史价值：记录了当时怎么修数据。当前价值：几乎为零 |
| 输入清单 | `eval_companies*.yaml`、`batch_*_2024.yaml`、`eval_companies_full_market_2024.yaml` | 评估/批次的公司清单，是可复现输入 |

### 3.2 Era A：通用采集框架（基本未使用）
| 文件/目录 | 说明 |
|---|---|
| `collectors/`（16 个 collector + `base.py` + `registry.py`） | 按 `category` 分发的采集器框架，由 `main.py` + `config/sources.yaml` 驱动。**只有 `main.py` 用到它**，当前流程不走这条线 |
| `main.py` | Era A 的入口，读 `config/sources.yaml` + `companies.yaml` 跑采集覆盖率检查 |
| `config/sources.yaml`、`config/companies.yaml` | Era A 的数据源与公司配置 |
| `outputs/raw_samples/`、`outputs/catl_test/`、`test_catl.yaml` | Era A / 早期单公司测试产物 |

### 3.3 共享基础设施（Era A + Era B 都在用，保留）
- `utils/`（`fetcher.py`/`llm.py`/`logger.py`/`coverage.py`/`summary.py`/`text_cleaner.py`/`url_tools.py`）
- `parsers/`（`html_parser.py`/`pdf_parser.py`/`table_parser.py`）
- `requirements.txt`

---

## 4. outputs/ 怎么看

| 子目录 | 属于 | 是否入库(Git) | 说明 |
|---|---|---|---|
| `outputs/validation/` | **Era C（活跃）** | 是（CSV + md） | 当前 CNINFO 验证的全部产物。**这是你现在该看的** |
| `outputs/generalization/` | Era B（冻结） | 仅 summary.md/部分 csv 入库；每公司明细 + PDF + 大 JSON 已 gitignore（本地约 25GB） | 2024 全市场抽取与审计的历史产物 |
| `outputs/db/` | Era B（冻结） | `*.db` 已 gitignore | SQLite 原型库 |
| `outputs/extraction/` | Era B（冻结） | 已整体 gitignore | 单/小样本抽取缓存 + PDF |
| `outputs/raw_samples/`、`outputs/catl_test/` | Era A（冻结） | 大部分 gitignore | 早期样本 |

> Git 现状健康：`.git` 仅约 5.6MB，25GB 重产物**没有进版本库**，也**没有污染历史**。所以不需要重写历史，也不急着删本地文件。

---

## 5. 活文档 vs 快照（回答"很多要更新的 md 没法更新了怎么办"）

把文档分成两类，就不用为"更新不动的 md"焦虑了：

- **活文档（需要手动维护，尽量少）**：只有 3 份——
  - `CURRENT_STATUS.md`（现在在做什么）
  - `PROJECT_MAP.md`（本文件，仓库地图）
  - `plans/cninfo_data_source_value_inventory.md`（CNINFO 盘点主表）
- **快照 / 产物（不用手动更新）**：`outputs/**/*.md`、`outputs/**/*.csv` 都是**脚本跑出来的时点快照**，重跑脚本就重新生成，不是手写维护的。所以它们"更新不动"是正常的——它们记录的是"某次运行当时的结果"，不需要你去手动改。
  - 处理原则：**保留**（当历史记录），不用删。若担心误解，可在标题下加一句"本文件为 YYYY-MM-DD 某次运行的快照"。
- **历史阶段计划**（`plans/v0.1`~`v0.6`、`full_market_2024_extraction_plan.md`、`storage_schema_design_plan.md`、`dynamic_data_platform_plan.md`）：都是**归档/暂缓**文档，保留即可，不需要持续更新。

---

## 6. 给未来会话（包括便宜模型）的操作指南

为了省钱、也为了让任何模型都能接手，约定几条：

1. **开工前先读这份 `PROJECT_MAP.md` + `CURRENT_STATUS.md`**，就能定位在哪条线、该改哪些文件，不用满仓库搜。
2. **当前只在 Era C 范围内改动**：`lab/validate_cninfo_*.py`、`config/cninfo_*.yaml`、`outputs/validation/`、`plans/cninfo_data_source_value_inventory.md`。
3. **不要动 Era A / Era B 的代码**（冻结）。确需复用年报抽取，从 `lab/extract_annual_report.py` + `lab/field_schema.py` 入手，且注意紧耦合 import。
4. **网络与合规红线**（沿用既有约定）：不绕过登录/验证码/付费/权限；请求之间 sleep；不做大规模抓取；`recommended_status` 只用 `candidate`/`testing`/`partial`，**不写 `verified`**。
5. **数据库红线**：当前阶段**不接** PostgreSQL/MinIO/MongoDB，验证结果只作为未来设计依据。
6. **新脚本产物**统一写到 `outputs/validation/`，重产物（PDF/大 JSON/db）确保被 `.gitignore` 挡住。

---

## 7. 一步步该怎么推进 Era C（建议路线）

1. **把盘点表当成唯一事实来源**：所有 CNINFO 验证结论回填到 `plans/cninfo_data_source_value_inventory.md` 的状态列。
2. **先把"类年报"做扎实**：`validate_cninfo_report_announcements.py` 已跑通年报/半年报/季报检索；下一步可扩展到业绩预告/业绩快报/招股书等同样"定期+标题稳定+PDF"的类型。
3. **再逐个啃非类年报**：按盘点表 P0→P1→P2 顺序，每个栏目做小样本验证、记录成功率与失败原因。
4. **每验证完一个栏目**：更新盘点表状态 + 在 `outputs/validation/` 留 summary，不做数据库接入。
