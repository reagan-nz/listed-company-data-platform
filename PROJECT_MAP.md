# 仓库地图（PROJECT_MAP）

_最后更新：2026-07-05_

> **这份文件是"仓库导航图"。** 目的很直接：让任何人（包括你自己、以及便宜/换代的 AI 模型）打开仓库后，**不用逐个文件猜用途**，就能知道「现在聚焦什么、哪个文件属于哪条线、哪个能删/能停/要留」。
>
> 阅读顺序建议：先读本文件 → 再读 [CURRENT_STATUS.md](CURRENT_STATUS.md)（当前具体在做什么）→ 需要背景再看 [ROADMAP.md](ROADMAP.md) / [CHANGELOG.md](CHANGELOG.md)。

---

## 0. 一句话现状

仓库里叠了**三代方向**的代码与文档。**当前聚焦：Era C Phase 3** — D 类设计已收口；**B 类 corpus 设计草案**进行中。前两代**已冻结**。

---

## 1. 三代方向速览

| 代 | 名称 | 状态 | 一句话 | 代表目录/文件 |
|---|---|---|---|---|
| **Era A** | 通用多源采集框架（v0.1 设想） | **冻结·基本未使用** | 想从新闻/官网/专利/招投标/政策等"所有来源"采集，只搭了框架没真正跑起来 | `collectors/`、`main.py`、`config/sources.yaml`、`config/companies.yaml` |
| **Era B** | 2024 全市场年报数据底座 | **冻结·已完成** | 从 CNINFO 年报 PDF 批量抽 11 个字段 + 质量审计，入 SQLite（6124 家）。已交付，不再改 | `lab/` 里的年报/全市场/审计脚本、`outputs/generalization/`、`outputs/db/` |
| **Era C** | CNINFO 数据源能力研究 | **活跃·Phase 3 B 类** | D 类十源 + schema validation；B 类 corpus 设计 | `cninfo_b_class_corpus_design.md` |

> 为什么感觉"偏"了：顶层文档（ROADMAP/CURRENT_STATUS）一度把重心写成"动态平台架构 + PostgreSQL/MinIO/MongoDB 三层存储设计"。那是**在数据源还没验证透之前就先设计数据库**，属于超前。当前把重心**拉回 Era C**：先回答"巨潮到底能稳定拿到什么"。存储架构设计（`plans/storage_schema_design_plan.md`、`plans/dynamic_data_platform_plan.md`）**暂缓**，留作未来参考。

---

## 2. 当前聚焦（Era C）用哪些文件

这是你现在真正要看、要用的东西。

### 2.1 活跃脚本（`lab/`）
| 文件 | 用途 | 是否独立可跑 |
|---|---|---|
| `validate_cninfo_report_coverage.py` | **Phase 1 主力（已收口）**：A 类 per-company coverage% | 是 |
| `validate_cninfo_table_sources.py` | **Phase 2 主力**：D 类固定表格入口探测（config 驱动） | 是 |
| `validate_cninfo_table_sources_multidate.py` | Phase 2：priority-1 多日期稳定性复测 | 是 |
| `validate_cninfo_table_sources_priority2_stability.py` | Phase 2：priority-2 多参数稳定性复测 | 是 |
| `lint_cninfo_d_class_registry.py` | **Phase 3**：registry YAML 离线 lint（无网络、无 DB） | 是 |
| `cninfo_d_class_mappers.py` | **Phase 3**：raw → 逻辑 record mapper 草案 | 是 |
| `validate_cninfo_d_class_schema.py` | **Phase 3**：fixture JSON Schema 离线校验 | 是 |
| `validate_cninfo_report_announcements.py` | 旧 A 类策略探测（deprecated 参考） | 是 |
| `validate_cninfo_b_class_category_routing.py` | **Phase 3**：B 类离线 title routing 验证（无网络） | 是 |
| `seed_cninfo_b_class_document_fixtures.py` | **Phase 3**：Phase 1 found → B 类 document metadata fixture（无网络、无 PDF） | 是 |
| `validate_cninfo_b_class_document_schema.py` | **Phase 3**：B 类 document JSONL fixture 离线 schema 校验 | 是 |
| `seed_cninfo_b_class_raw_file_fixtures.py` | **Phase 3**：document → raw_file metadata fixture（无网络、无 PDF） | 是 |
| `validate_cninfo_b_class_raw_file_schema.py` | **Phase 3**：B 类 raw_file JSONL fixture 离线 schema 校验 | 是 |
| `seed_cninfo_b_class_non_periodic_document_fixtures.py` | **Phase 3**：benchmark → non-periodic document metadata（无网络） | 是 |
| `validate_cninfo_b_class_non_periodic_document_schema.py` | **Phase 3**：non-periodic document fixture schema 校验 + summary | 是 |
| `seed_cninfo_b_class_parse_run_dry_run_fixtures.py` | **Phase 3**：document → parse_run dry-run fixture（无 PDF 解析） | 是 |
| `validate_cninfo_b_class_parse_run_schema.py` | **Phase 3**：parse_run dry-run schema 校验 + summary | 是 |
| `lint_cninfo_b_class_registry.py` | **Phase 3**：B 类 registry/category/schema/fixture 离线 lint | 是 |
| `select_cninfo_b_class_retrieval_ready_cases.py` | **Phase 3**：retrieval ready-case 筛选（无 CNINFO 请求） | 是 |
| `validate_cninfo_b_class_corpus_retrieval.py` | **Phase 3**：dry-run + `--live-metadata`（known-document + `periodic_guard_*` guard audit） | 是 |
| `validate_cninfo_announcement_categories.py` | 旧版 14 类公告验证（**待迁移**至新 YAML） | 是 |
| `validate_cninfo_latest_announcements.py` | 验证"最新公告列表"栏目 | 是 |
| `validate_cninfo_pdf_metadata.py` | 验证公告 PDF 元数据（URL/hash 规则，不下载正文） | 是 |
| `validate_cninfo_f10_company_profile.py` | 验证个股 F10 公司资料字段 | 是 |
| `cninfo_c_class_mappers.py` | **Phase 4**：C 类 basic_profile + security_profile mapper 草案 | 是 |
| `seed_cninfo_c_class_basic_profile_fixtures.py` | **Phase 4**：内置样本 → basic_profile fixture JSONL（无网络） | 是 |
| `seed_cninfo_c_class_security_profile_fixtures.py` | **Phase 4**：内置 marketOverview 样本 → security_profile fixture JSONL（无网络） | 是 |
| `validate_cninfo_c_class_basic_profile_schema.py` | **Phase 4**：basic_profile fixture JSON Schema 校验 | 是 |
| `validate_cninfo_c_class_security_profile_schema.py` | **Phase 4**：security_profile fixture JSON Schema 校验 | 是 |
| `validate_cninfo_c_class_live_sources.py` | **Phase 4**：C 类 P1 basic/security live validation（`--dry-run` 默认） | 是 |
| `validate_cninfo_c_class_p2a_live_sources.py` | **Phase 4**：C 类 P2-A executive/share_capital/shareholders live validation（`--dry-run` 默认） | 是 |
| `lint_cninfo_c_class_registry.py` | **Phase 4**：C 类 candidate registry 离线 lint（无网络、无 DB） | 是 |
| `validate_cninfo_c_class_profile_schema.py` | **Phase 4**：C 类 known-company profile fixture 离线 schema 校验 | 是 |
| `validate_cninfo_f10_profile_page_reachability.py` | F10 页面可达性 | 是 |
| `validate_cninfo_f10_static_html_fields.py` | F10 静态 HTML 字段 | 是 |
| `validate_cninfo_f10_playwright_profile_fields.py` | F10 Playwright 渲染字段 | 是 |
| `test_cninfo_announcement_retrieval_rules.py` | 检索规则回放测试 | 是 |
| `build_cninfo_p0_sample_companies.py` | 生成 40 家 P0 样本公司清单 | 是 |
| `build_cninfo_report_p1_identity_mapping.py` | P1 identity mapping（离线） | 是 |

### 2.2 活跃配置（`config/`）
- `cninfo_table_sources.yaml` — **Phase 2** 验证脚本驱动配置（12 source；10 stable + 2 candidate）
- `schemas/d_class/` — **Phase 3** 10 个逻辑表 JSON Schema draft（draft-07）
- `schemas/c_class/` — **Phase 4** 7 个 C 类 company profile JSON Schema draft（draft-07，含 `c_company_security_profile`）
- `schemas/b_class/` — **Phase 3** 8 个 B 类 document corpus JSON Schema draft（draft-07）
- `fixtures/d_class/` — **Phase 3** 11 个 raw record fixture（Phase 2 文档摘录）
- `fixtures/b_class/known_documents/` — B 类 known-document title routing benchmark（16 条）
- `fixtures/b_class/document/` — periodic（20 条）+ non-periodic（13 条）document metadata JSONL
- `fixtures/b_class/raw_file/` — periodic raw_file（20 条）；non-periodic 空文件（无 pdf_url）
- `fixtures/b_class/parse_run/` — parse_run dry-run（33 条；`not_started` / `skipped`）
- `fixtures/b_class/retrieval_validation/` — corpus retrieval benchmark（**5 ready** + 16 placeholder）+ example-only 参考
- `fixtures/c_class/` — known-company fixtures（12 条）+ probe records（P1 9 条 + P2 **12/12 endpoint_found**）+ basic_profile（2）+ security_profile（3）
- `config/cninfo_c_class_source_candidates.yaml` — **Phase 4** C 类 company_profile 候选源（**P1 + P2-A backfill v1**：**6** 源 `testing` + endpoint；**4** 源 `candidate`）
- `config/cninfo_b_class_source_registry_draft.yaml` — Phase 3 B 类 document_corpus registry 草案（4 source）
- `config/cninfo_d_class_source_registry_draft.yaml` — Phase 3 D 类 registry YAML 草案
- `cninfo_announcement_categories.yaml` — **Phase 3 B 类** document corpus category routing 草案（4 路由组 + legacy 映射）
- `cninfo_announcement_retrieval_strategies.yaml` — 检索策略（must/optional/exclude 关键词）

### 2.3 活跃文档
- `plans/cninfo_data_source_layered_inventory.md` — **Era C 权威文档**：A–F 六层分类 + 每类分母/分子/成功指标 + Phase 推进顺序
- `plans/cninfo_data_source_value_inventory.md` — 栏目细节、P0 验证模板、事件/证据类型（与分层表交叉引用，分类以分层表为准）
- `plans/cninfo_d_class_source_registry_design.md` — **Phase 3** D 类 source registry 设计草案
- `plans/cninfo_d_class_schema_draft.md` — D 类逻辑 schema 草案（10 逻辑表含 d_event_party_detail）
- `plans/cninfo_d_class_ingestion_status_model.md` — source/fetch/field/stability 状态模型
- `plans/cninfo_d_class_source_to_schema_mapping_review.md` — 逐 source 映射审查与缺口清单
- `plans/cninfo_d_class_source_registry_draft_notes.md` — registry YAML draft 说明
- `plans/cninfo_d_class_json_schema_draft_notes.md` — JSON Schema draft 说明
- `plans/cninfo_c_class_json_schema_draft_notes.md` — C 类 JSON Schema 草案说明
- `plans/cninfo_c_class_registry_lint_design.md` — C 类 registry lint 规则（R001–R012）
- `plans/cninfo_c_class_devtools_probe_plan.md` — **Phase 4** C 类 F10 DevTools endpoint discovery 计划（P1–P3 优先级）
- `plans/cninfo_c_class_probe_checklist.md` — C 类人工 probe 前 / DevTools / 回填前检查清单
- `plans/cninfo_c_class_p1_probe_execution_notes.md` — **Phase 4** P1 三源 × 三公司 DevTools probe 执行说明
- `plans/cninfo_c_class_p1_probe_review.md` — P1 probe 结果审查（basic / security / industry / annex）
- `plans/cninfo_c_class_p2_probe_plan.md` — **Phase 4** P2 DevTools probe 计划（executive / share_capital / shareholders）
- `plans/cninfo_c_class_p2a_yaml_backfill_decision.md` — **Phase 4** P2-A YAML 回填决策（4 source · `testing` only · decision only）
- `plans/cninfo_c_class_p1_yaml_backfill_decision.md` — P1 candidate YAML 回填 / 暂缓决策（**YAML 未改**）
- `plans/cninfo_c_class_basic_profile_field_mapping_draft.md` — getCompanyIntroduction → basic profile 字段映射草案
- `plans/cninfo_c_class_f10_source_discovery_design.md` — **Phase 4** C 类 F10 / company profile source discovery 设计草案
- `plans/cninfo_c_class_profile_data_model_draft.md` — C 类 profile snapshot 逻辑数据模型
- `plans/cninfo_c_vs_b_vs_d_boundary.md` — C 类与 B / D 类边界
- `plans/cninfo_b_class_corpus_design.md` — **Phase 3** B 类 document corpus 设计草案
- `plans/cninfo_b_class_document_model_draft.md` — B 类 document / chunk / citation 逻辑模型
- `plans/cninfo_b_class_source_registry_design.md` — B 类 document_corpus source registry 设计
- `plans/cninfo_b_class_validation_design.md` — B 类 corpus validation 口径（expected-period / known-document / category-sample）
- `plans/cninfo_b_class_category_routing_rules.md` — B 类 title → source 路由规则
- `plans/cninfo_b_class_json_schema_draft_notes.md` — B 类 JSON Schema 草案说明
- `plans/cninfo_b_class_parser_chunker_plan.md` — **Phase 3** B 类 parse → section → chunk → citation 流水线设计
- `plans/cninfo_b_class_chunking_strategy.md` — B 类 RAG chunk 切分策略草案
- `plans/cninfo_b_class_parse_quality_model.md` — B 类解析质量维度与 flags 模型
- `plans/cninfo_b_class_registry_lint_design.md` — B 类 registry lint 规则（R001–R023）
- `plans/cninfo_b_class_corpus_retrieval_validation_design.md` — **Phase 3** B 类 corpus retrieval 验证设计（known-document + category-sample）
- `plans/cninfo_b_class_retrieval_validation_next_steps.md` — live validation 前置条件与原则
- `plans/cninfo_b_class_retrieval_ready_case_rules.md` — ready-case 字段规则与 case_status 定义
- `plans/cninfo_b_class_ready_case_intake_template.md` — 人工补 ready case 填写模板
- `plans/cninfo_b_class_ready_case_review_checklist.md` — ready case 审核清单
- `plans/cninfo_b_class_corpus_retrieval_script_skeleton_notes.md` — corpus retrieval 脚本骨架说明（dry-run only）
- `plans/cninfo_b_class_source_registry_draft_notes.md` — B 类 registry YAML 说明
- `plans/cninfo_b_vs_d_class_boundary.md` — B 类 corpus 与 D 类 fixed-table 边界
- `plans/cninfo_d_class_registry_lint_design.md` — registry YAML 离线 lint 规则（R001–R023）
- `plans/cninfo_d_class_schema_validation_plan.md` — fixture / mapper / schema 校验路线图
- `plans/eraC_execution_plan.md` — Composer / 便宜模型执行清单
- `plans/cninfo_p0_sample_company_selection.md` — P0 样本公司选取说明
- `outputs/validation/` — …；**Phase 2 总总结**见 [cninfo_table_sources_phase2_current_final_summary.md](outputs/validation/cninfo_table_sources_phase2_current_final_summary.md)；P1/P2 分源见 priority1/priority2 summary

### 2.4 Era C 验证框架（A–F 分层，取代旧 P0/P1/P2 success rate）

Era C 已从「所有公告混在一个 success rate 里」调整为 **A–F 分层验证框架**，详见 [plans/cninfo_data_source_layered_inventory.md](plans/cninfo_data_source_layered_inventory.md)：

| 层 | 类型 | 成功口径要点 |
|---|---|---|
| **A** | 类年报 PDF 文档流 | **per-company coverage%**（公司 × 期望报告期）；旧 `368/780` 行计数**不能**作最终结论 |
| **B** | 公告 PDF 事件流 | **corpus 可得性** + **known-event benchmark**；禁止随机公司覆盖率 |
| **C** | F10 / 公司资料表格 | **orgId mapping + 字段可得性%** |
| **D** | 固定表格 / 市场行为 | **字段可得性% + 入口稳定性**（config 驱动，手动抓 endpoint） |
| **E** | API / 商业服务 | **仅可达性三态**（公开 / 需登录 / 需权限） |
| **F** | 问答 / 服务入口 | **暂缓**，仅文本线索 |

### 2.5 旧「类年报 vs 非类年报」二分（仍适用，但归入 A 层）
`plans/cninfo_data_source_layered_inventory.md` 将「类年报」明确为 **A 类**；其余为 B–F。简要对应：

- **A 类（类年报）**：年报、半年报、一季报、三季报、IPO 招股书 → 定期披露 + 标题稳定 + PDF
- **B–F（非类年报路径）**：事件公告流、F10 表格、固定表格资讯、API 服务、问答入口

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

- **活文档（需要手动维护，尽量少）**：
  - `CURRENT_STATUS.md`（现在在做什么）
  - `PROJECT_MAP.md`（本文件，仓库地图）
  - `plans/cninfo_data_source_layered_inventory.md`（**A–F 分层 + 验证口径权威**）
  - `plans/eraC_execution_plan.md`（执行清单）
- **快照 / 产物（不用手动更新）**：`outputs/**/*.md`、`outputs/**/*.csv` 都是**脚本跑出来的时点快照**，重跑脚本就重新生成，不是手写维护的。所以它们"更新不动"是正常的——它们记录的是"某次运行当时的结果"，不需要你去手动改。
  - 处理原则：**保留**（当历史记录），不用删。若担心误解，可在标题下加一句"本文件为 YYYY-MM-DD 某次运行的快照"。
- **历史阶段计划**（`plans/v0.1`~`v0.6`、`full_market_2024_extraction_plan.md`、`storage_schema_design_plan.md`、`dynamic_data_platform_plan.md`）：都是**归档/暂缓**文档，保留即可，不需要持续更新。

---

## 6. 给未来会话（包括便宜模型）的操作指南

为了省钱、也为了让任何模型都能接手，约定几条：

1. **开工前先读这份 `PROJECT_MAP.md` + `CURRENT_STATUS.md`**，就能定位在哪条线、该改哪些文件，不用满仓库搜。
2. **当前只在 Era C 范围内改动**：`lab/validate_cninfo_*.py`、`config/cninfo_*.yaml`、`outputs/validation/`、`plans/cninfo_data_source_layered_inventory.md`、`plans/eraC_execution_plan.md`。
3. **不要动 Era A / Era B 的代码**（冻结）。确需复用年报抽取，从 `lab/extract_annual_report.py` + `lab/field_schema.py` 入手，且注意紧耦合 import。
4. **网络与合规红线**（沿用既有约定）：不绕过登录/验证码/付费/权限；请求之间 sleep；不做大规模抓取；`recommended_status` 只用 `candidate`/`testing`/`partial`，**不写 `verified`**。
5. **数据库红线**：当前阶段**不接** PostgreSQL/MinIO/MongoDB，验证结果只作为未来设计依据。
6. **新脚本产物**统一写到 `outputs/validation/`，重产物（PDF/大 JSON/db）确保被 `.gitignore` 挡住。

---

## 7. 一步步该怎么推进 Era C（建议路线）

1. **Phase 1 已收口**：A 类见 [cninfo_report_phase1_final_summary.md](outputs/validation/cninfo_report_phase1_final_summary.md)（**testing/usable candidate**，不写 verified）。
2. **Phase 2 已收口**；**Phase 3 D 类设计**见 [registry YAML](config/cninfo_d_class_source_registry_draft.yaml) / [schema validation summary](outputs/validation/cninfo_d_class_schema_validation_summary.md)。
3. **Phase 3 B 类**见 [validation design](plans/cninfo_b_class_validation_design.md) / [category routing](plans/cninfo_b_class_category_routing_rules.md) / [categories YAML](config/cninfo_announcement_categories.yaml) / [document seed summary](outputs/validation/cninfo_b_class_document_seed_summary.md) / [B schema validation](outputs/validation/cninfo_b_class_document_schema_validation_summary.md)。
4. **Phase 4 C 类**见 [registry lint](outputs/validation/cninfo_c_class_registry_lint_summary.md) / [fixture validation](outputs/validation/cninfo_c_class_profile_schema_validation_summary.md) / [probe plan](plans/cninfo_c_class_devtools_probe_plan.md) / [P2 probe plan](plans/cninfo_c_class_p2_probe_plan.md) / [candidates YAML](config/cninfo_c_class_source_candidates.yaml)。
5. **下一步**：P2-A mapper drafts（executive / share_capital / shareholders）；E/F 暂缓。
6. **每完成一个 Phase**：更新分层表状态 + `outputs/validation/` 留 summary；不做数据库接入。
