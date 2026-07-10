# 仓库地图（PROJECT_MAP）

_最后更新：2026-07-10_

> **这份文件是"仓库导航图"。** 目的很直接：让任何人（包括你自己、以及便宜/换代的 AI 模型）打开仓库后，**不用逐个文件猜用途**，就能知道「现在聚焦什么、哪个文件属于哪条线、哪个能删/能停/要留」。
>
> 阅读顺序建议：先读本文件 → 再读 [CURRENT_STATUS.md](CURRENT_STATUS.md)（当前具体在做什么）→ 需要背景再看 [ROADMAP.md](ROADMAP.md) / [CHANGELOG.md](CHANGELOG.md)。

---

## 0. 一句话现状

仓库里叠了**三代方向**的代码与文档。**当前聚焦：Era C Phase 4 C 类** — Phase 3.5 expanded **491** snapshot commit boundary **就绪**；**`SNAPSHOT_GENERATED_QA_REVIEW`**；boundary gate **`READY_FOR_COMMIT_REVIEW`**。**并行：A-class Phase 2 final commit boundary review 已完成**（gate **`READY_FOR_COMMIT_REVIEW`** · CNINFO **0** · **无 commit** · **不是 verified**）。前两代**已冻结**。

---

## 1. 三代方向速览

| 代 | 名称 | 状态 | 一句话 | 代表目录/文件 |
|---|---|---|---|---|
| **Era A** | 通用多源采集框架（v0.1 设想） | **冻结·基本未使用** | 想从新闻/官网/专利/招投标/政策等"所有来源"采集，只搭了框架没真正跑起来 | `collectors/`、`main.py`、`config/sources.yaml`、`config/companies.yaml` |
| **Era B** | 2024 全市场年报数据底座 | **冻结·已完成** | 从 CNINFO 年报 PDF 批量抽 11 个字段 + 质量审计，入 SQLite（6124 家）。已交付，不再改 | `lab/` 里的年报/全市场/审计脚本、`outputs/generalization/`、`outputs/db/` |
| **Era C** | CNINFO 数据源能力研究 | **活跃·C 类 + A/B/D 类并行规划** | C 类 snapshot/QA；A/B 类元数据规划；D 类市场行为层（offline only） | `cninfo_d_class_market_data_architecture_plan.md` |

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
| `cninfo_c_class_mappers.py` | **Phase 4**：C 类 basic + security + executive + share_capital + shareholder + **dividend_history** mapper | 是 |
| `test_cninfo_c_class_dividend_history_mapper.py` | **Phase 4**：dividend_history mapper fixture test（5 cases · 无网络） | 是 |
| `seed_cninfo_c_class_basic_profile_fixtures.py` | **Phase 4**：内置样本 → basic_profile fixture JSONL（无网络） | 是 |
| `seed_cninfo_c_class_security_profile_fixtures.py` | **Phase 4**：内置 marketOverview 样本 → security_profile fixture JSONL（无网络） | 是 |
| `validate_cninfo_c_class_basic_profile_schema.py` | **Phase 4**：basic_profile fixture JSON Schema 校验 | 是 |
| `validate_cninfo_c_class_security_profile_schema.py` | **Phase 4**：security_profile fixture JSON Schema 校验 | 是 |
| `validate_cninfo_c_class_live_sources.py` | **Phase 4**：C 类 P1 basic/security live validation（`--dry-run` 默认） | 是 |
| `validate_cninfo_c_class_p2a_live_sources.py` | **Phase 4**：C 类 P2-A live validation（`--dry-run` 默认） | 是 |
| `validate_cninfo_c_class_scale_smoke.py` | **Phase 4**：C 类 30/200 scale smoke（fill_rate · `--sample-file` · `--dry-run` 默认） | 是 |
| `harvest_cninfo_c_class.py` | **Phase 4**：C 类 harvest（`--dry-run` · `--live --limit` smoke · `--approve-full-harvest` full · `--output-root` 隔离 · `--approve-phase2-smoke-harvest` phase2 · `--regenerate-summary`） | 是 |
| `review_cninfo_c_class_full_harvest_qa.py` | **Phase 4**：863 full harvest 离线 QA review（无网络） | 是 |
| `triage_cninfo_c_class_full_harvest_qa_flags.py` | **Phase 4**：QA flags 分层 triage / review planning（无网络） | 是 |
| `remap_cninfo_c_class_dividend_history_offline.py` | **Phase 4**：dividend_history 离线 re-map（读 raw · 写 normalized） | 是 |
| `test_cninfo_c_class_harvest_runner_safety.py` | **Phase 4**：harvest runner 安全控制测试（5 cases · 无网络） | 是 |
| `seed_cninfo_c_class_executive_profile_fixtures.py` | **Phase 4**：内置 getCompanyExecutives 行 → executive_profile fixture JSONL（无网络） | 是 |
| `validate_cninfo_c_class_executive_profile_schema.py` | **Phase 4**：executive_profile fixture JSON Schema 校验 | 是 |
| `seed_cninfo_c_class_share_capital_profile_fixtures.py` | **Phase 4**：内置 getStockStructure 行 → share_capital_profile fixture JSONL（无网络） | 是 |
| `validate_cninfo_c_class_share_capital_profile_schema.py` | **Phase 4**：share_capital_profile fixture JSON Schema 校验 | 是 |
| `seed_cninfo_c_class_shareholder_profile_fixtures.py` | **Phase 4**：内置 top-shareholder 行 → shareholder_profile fixture JSONL（无网络） | 是 |
| `validate_cninfo_c_class_shareholder_profile_schema.py` | **Phase 4**：shareholder_profile fixture JSON Schema 校验 | 是 |
| `lint_cninfo_c_class_registry.py` | **Phase 4**：C 类 candidate registry 离线 lint（无网络、无 DB） | 是 |
| `validate_cninfo_c_class_profile_schema.py` | **Phase 4**：C 类 known-company profile fixture 离线 schema 校验 | 是 |
| `validate_cninfo_f10_profile_page_reachability.py` | F10 页面可达性 | 是 |
| `validate_cninfo_f10_static_html_fields.py` | F10 静态 HTML 字段 | 是 |
| `validate_cninfo_f10_playwright_profile_fields.py` | F10 Playwright 渲染字段 | 是 |
| `test_cninfo_announcement_retrieval_rules.py` | 检索规则回放测试 | 是 |
| `build_cninfo_p0_sample_companies.py` | 生成 40 家 P0 样本公司清单 | 是 |
| `build_cninfo_report_p1_identity_mapping.py` | P1 identity mapping（离线） | 是 |

**C 类 smoke / retry / stable / harvest 样本（`lab/`）：** `eval_companies_200.yaml` · `eval_companies_c_class_smoke_200_active.yaml`（195）· universe split `*_195_*` · **1000-like** `eval_companies_c_class_smoke_1000_non_bse_candidate.yaml`（889）· **harvest** `eval_companies_c_class_harvest_863_non_bse.yaml`（863）· **889 rerun hold** `eval_companies_c_class_889_rerun_all6_hold.yaml`（26）· **889 rerun partial retry** `eval_companies_c_class_889_rerun_partial_fail_retry.yaml`（41）· **retry** `*_retry_889_*` · **stable 200 six-fail retry** `eval_companies_c_class_retry_stable_200_six_fail_12.yaml`（12）· **stable 200** `eval_companies_c_class_stable_200_non_bse.yaml`（200）

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
- `fixtures/c_class/` — known-company fixtures（12 条）+ probe records（P1 · P2-A · **P2-B 12 pending**）+ basic_profile（2）+ security_profile（3）+ executive_profile（6）+ share_capital_profile（6）+ shareholder_profile（12）
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
- `plans/cninfo_c_class_p2a_mapper_completion_summary.md` — **Phase 4** P2-A 四源 mapper 完成汇总（testing / prototype · 无 verified）
- `plans/cninfo_c_class_status_consolidation_summary.md` — **Phase 4** C 类 10 源状态总表（P1 + P2-A · 6 testing / 4 candidate）
- `plans/cninfo_c_class_p2b_probe_plan.md` — **Phase 4** P2-B DevTools probe 计划（dividend · contact · business_scope · industry）
- `plans/cninfo_c_class_p2b_probe_checklist.md` — **Phase 4** P2-B 人工 probe 清单
- `plans/cninfo_c_class_p2b_source_decision_table.md` — **Phase 4** P2-B 四源决策表（discovery closed · 无 YAML 执行）
- `plans/cninfo_c_class_stable_200_sample_plan.md` — **Phase 4** stable 200 non-BSE 清洗样本设计
- `plans/cninfo_c_class_manual_audit_12_six_fail_companies.md` — **Phase 4** stable 200 十二家 6/6 fail 人工审计结论（不剔除 · 不过拟合）
- `plans/cninfo_c_class_889_non_bse_rerun_plan.md` — **Phase 4** 889 non-BSE 新版 runner 重跑计划
- `plans/cninfo_c_class_889_rerun_retry_plan.md` — **Phase 4** 889 rerun partial-fail targeted retry 计划（26 hold + 41 retry）
- `plans/cninfo_c_class_889_post_retry_decision.md` — **Phase 4** 889 post-retry 决策与 harvest gate 初步判断
- `plans/cninfo_c_class_field_inventory.md` — **Phase 4** C-class 字段清单（raw/normalized harvest 准备）
- `plans/cninfo_c_class_harvest_plan.md` — **Phase 4** C-class harvest 执行方案（863 家 · planning only）
- `plans/cninfo_c_class_full_harvest_863_execution_plan.md` — **Phase 4** 863 full harvest 执行计划（**已执行 · PASS_WITH_RESUME**）
- `plans/cninfo_c_class_open_issues_closure_plan.md` — **Phase 4** C-class 开放问题与收口计划（**HARVEST_COMPLETED_QA_ONGOING** · 9 open issues）
- `outputs/validation/cninfo_c_class_field_quality_consolidation_batch_summary.md` — **Phase 4** Field & Quality Consolidation Batch 摘要
- `plans/cninfo_c_class_product_quality_rules_draft.md` — **Phase 4** 产品层质量规则初稿
- `outputs/validation/cninfo_c_class_establishment_date_mapper_patch_plan.md` — **Phase 4** establishment_date mapper patch 规划
- `outputs/validation/cninfo_c_class_establishment_date_remap_summary.md` — **Phase 4** establishment_date 离线 re-map 摘要（**IMPLEMENTED** · 863 parsed）
- `lab/remap_cninfo_c_class_basic_profile_offline.py` — **Phase 4** basic profile 离线 re-map 脚本
- `outputs/validation/cninfo_c_class_review_later_promotion_candidate_approval_after_patch.md` — **Phase 4** promotion after patch（**10** candidates · gate PASS）
- `plans/cninfo_c_class_company_snapshot_architecture_plan.md` — **Phase 4** Company Snapshot 架构计划（**18** 模块）
- `outputs/validation/cninfo_c_class_company_snapshot_field_mapping.csv` — **Phase 4** snapshot 字段映射（**120** 行）
- `plans/cninfo_c_class_snapshot_source_priority_rules.md` — snapshot 多源优先级规则
- `plans/cninfo_c_class_snapshot_conflict_resolution.md` — snapshot 冲突消解规则
- `plans/cninfo_c_class_snapshot_quality_model.md` — snapshot 质量模型
- `outputs/validation/cninfo_c_class_company_snapshot_planning_summary.md` — snapshot planning 摘要
- `lab/build_cninfo_c_class_company_snapshot.py` — **Phase 4** Company Snapshot Builder（离线只读 PoC）
- `outputs/snapshot/cninfo_c_class/company_snapshot_demo/688750.json` — snapshot demo 产物
- `outputs/validation/cninfo_c_class_snapshot_builder_demo_summary.md` — builder demo 摘要
- `plans/cninfo_c_class_snapshot_smoke_plan.md` — 10 家 smoke 规划
- `lab/eval_companies_c_class_snapshot_smoke_10.yaml` — **Phase 4** snapshot smoke 10 家样本
- `lab/run_cninfo_c_class_snapshot_smoke_10.py` — **Phase 4** snapshot smoke 10 家 batch runner（离线）
- `outputs/snapshot/cninfo_c_class/smoke/` — snapshot smoke 10 家产物（**10** JSON）
- `outputs/validation/cninfo_c_class_snapshot_smoke_10_report.csv` — smoke 10 质量报告
- `outputs/validation/cninfo_c_class_snapshot_smoke_10_summary.md` — smoke 10 摘要（gate **PASS_WITH_CAVEAT**）
- `plans/cninfo_c_class_snapshot_full_batch_plan.md` — **Phase 4** 863 家 snapshot full batch 执行规划
- `lab/build_cninfo_c_class_snapshot_batch.py` — **Phase 4** snapshot batch runner（`--dry-run` · `--harvest-root` · `--output-dir` · `--approve-phase2-smoke-188-snapshot` · `--approve-phase3-success-snapshot-build`）
- `lab/test_cninfo_c_class_snapshot_batch_runner.py` — batch runner 测试（**5/5 PASS**）
- `outputs/snapshot/cninfo_c_class/full/quality/company_snapshot_status.csv` — batch status 框架（863 pending）
- `outputs/snapshot/cninfo_c_class/full/quality/company_snapshot_error.csv` — batch error 框架
- `outputs/validation/cninfo_c_class_snapshot_batch_dryrun_report.csv` — dry-run 报告（863 行）
- `outputs/validation/cninfo_c_class_snapshot_batch_dryrun_summary.md` — dry-run 摘要（gate **PASS_WITH_CAVEAT**）
- `outputs/validation/cninfo_c_class_snapshot_batch_runner_test_summary.md` — runner 测试摘要（**5/5 PASS**）
- `plans/cninfo_c_class_snapshot_full_execution_approval_checklist.md` — **Phase 4** full batch 执行前审核清单（gate **READY_FOR_APPROVAL**）
- `lab/review_cninfo_c_class_snapshot_full_quality.py` — **Phase 4** full snapshot QA review（离线只读）
- `lab/test_cninfo_c_class_snapshot_full_quality_review.py` — QA review 测试（**5/5 PASS**）
- `outputs/snapshot/cninfo_c_class/full/` — **863** 家 full snapshot JSON
- `outputs/validation/cninfo_c_class_snapshot_full_completeness_report.csv` — snapshot 完整性报告
- `outputs/validation/cninfo_c_class_snapshot_full_module_coverage.csv` — 18 模块覆盖率
- `outputs/validation/cninfo_c_class_snapshot_full_field_coverage.csv` — 字段覆盖率
- `outputs/validation/cninfo_c_class_snapshot_full_quality_flags.csv` — QA flags
- `outputs/validation/cninfo_c_class_snapshot_full_quality_summary.md` — full snapshot QA 摘要
- `outputs/validation/cninfo_c_class_snapshot_full_quality_review_test_summary.md` — QA review 测试摘要
- `plans/cninfo_c_class_full_market_universe_registry_plan.md` — **Phase 4** 全市场 company_registry 架构规划
- `outputs/validation/cninfo_c_class_full_market_universe_design.md` — **Phase 4** 863 vs 全市场 universe 设计
- `plans/cninfo_c_class_bse_expansion_strategy.md` — **Phase 4** BSE 扩展策略（920 / legacy 分轨）
- `plans/cninfo_c_class_hold_company_policy.md` — **Phase 4** hold 公司侧轨政策
- `plans/cninfo_c_class_full_market_harvest_architecture.md` — **Phase 4** 全市场 Harvest→Snapshot→QA 架构
- `plans/cninfo_c_class_full_market_expansion_readiness_review.md` — **Phase 4** 全市场扩展就绪度评估（§7cr · gate **PASS_WITH_CAVEAT**）
- `lab/reconcile_cninfo_c_class_full_market_universe.py` — **Phase 4** 全市场 universe 离线对账脚本（§7ct · dry-run）
- `lab/test_cninfo_c_class_full_market_universe_reconciliation.py` — **Phase 4** 对账测试（6/6 PASS）
- `outputs/validation/cninfo_c_class_full_market_universe_reconciliation_result.csv` — **Phase 4** 对账结果（6124 行）
- `plans/cninfo_c_class_registry_candidate_refresh_plan.md` — **Phase 4** registry candidate refresh 规划（§7cu）
- `lab/refresh_cninfo_c_class_company_registry_candidate.py` — **Phase 4** registry candidate refresh 脚本（§7cv · dry-run / --write）
- `lab/test_cninfo_c_class_company_registry_candidate_refresh.py` — **Phase 4** refresh 测试（8/8 PASS）
- `outputs/validation/cninfo_c_class_company_registry_candidate_refreshed.csv` — **Phase 4** refreshed candidate（6124 行 · validation artifact）
- `plans/cninfo_c_class_phase2_expansion_smoke_plan.md` — **Phase 4** Phase 2 expansion smoke 规划（§7cw）
- `plans/cninfo_c_class_phase2_smoke_universe_output_design.md` — **Phase 4** smoke universe 未来产物设计
- `plans/cninfo_c_class_phase2_expansion_smoke_execution_checklist.md` — **Phase 4** smoke 未来执行检查清单
- `outputs/validation/cninfo_c_class_phase2_expansion_smoke_candidate_matrix.csv` — **Phase 4** smoke 候选矩阵
- `lab/select_cninfo_c_class_phase2_smoke_universe.py` — **Phase 4** Phase 2 smoke 200 选股脚本（§7cx）
- `lab/test_cninfo_c_class_phase2_smoke_universe_selection.py` — **Phase 4** smoke 选股测试（8/8 PASS）
- `lab/eval_companies_c_class_phase2_smoke_200.yaml` — **Phase 4** smoke 200 universe（200 家）
- `outputs/validation/cninfo_c_class_phase2_smoke_200_selection_matrix.csv` — **Phase 4** smoke 选股矩阵
- `plans/cninfo_c_class_phase2_smoke_200_harvest_dryrun_plan.md` — **Phase 4** smoke 200 harvest dry-run 规划（§7cy）
- `plans/cninfo_c_class_phase2_smoke_200_harvest_command_checklist.md` — **Phase 4** harvest 命令检查清单
- `outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_expected_case_matrix.csv` — **Phase 4** harvest 预期 case 矩阵
- `outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_dryrun_report.csv` — **Phase 4** smoke 200 harvest dry-run 报告（2000 行 matrix）
- `outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_dryrun_summary.md` — **Phase 4** dry-run 摘要
- `outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_dryrun_validation_summary.md` — **Phase 4** dry-run validation 摘要
- `outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_dryrun_qa_summary.md` — **Phase 4** dry-run QA 摘要（§7cz · gate **PASS**）
- `plans/cninfo_c_class_phase2_smoke_200_live_harvest_approval_plan.md` — **Phase 4** live harvest 批准规划（§7da）
- `plans/cninfo_c_class_phase2_smoke_200_live_harvest_command_draft.md` — **Phase 4** live harvest 命令草案（**NOT APPROVED**）
- `outputs/validation/cninfo_c_class_phase2_smoke_200_live_harvest_approval_checklist.md` — **Phase 4** live harvest 批准检查清单
- `outputs/validation/cninfo_c_class_phase2_smoke_200_live_harvest_approval_summary.md` — **Phase 4** live harvest 批准摘要
- `lab/review_cninfo_c_class_phase2_smoke_200_live_harvest_qa.py` — **Phase 4** Phase 2 live harvest 离线 QA review（§7dc）
- `outputs/validation/cninfo_c_class_phase2_smoke_200_live_harvest_report.csv` — **Phase 4** live harvest 报告（2000 行）
- `outputs/validation/cninfo_c_class_phase2_smoke_200_live_harvest_summary.md` — **Phase 4** live harvest 摘要（generic 复制 + note）
- `outputs/validation/cninfo_c_class_phase2_smoke_200_live_harvest_qa_report.csv` — **Phase 4** live harvest QA 明细
- `outputs/validation/cninfo_c_class_phase2_smoke_200_live_harvest_company_failure_summary.csv` — **Phase 4** 公司级失败摘要
- `outputs/validation/cninfo_c_class_phase2_smoke_200_live_harvest_source_summary.csv` — **Phase 4** 源级摘要
- `outputs/validation/cninfo_c_class_phase2_smoke_200_live_harvest_qa_summary.md` — **Phase 4** live harvest QA 摘要（§7dc · gate **PASS_WITH_CAVEAT**）
- `outputs/validation/cninfo_c_class_phase2_smoke_200_output_isolation_check.md` — **Phase 4** output 隔离检查
- `plans/cninfo_c_class_phase2_smoke_188_snapshot_dryrun_plan.md` — **Phase 4** Phase 2 smoke 188 snapshot dry-run 规划（§7de）
- `plans/cninfo_c_class_phase2_smoke_188_snapshot_command_checklist.md` — **Phase 4** snapshot 命令检查清单
- `outputs/validation/cninfo_c_class_phase2_smoke_188_snapshot_subset_design.csv` — **Phase 4** 188 子集设计（200 行 · 188 include）
- `outputs/validation/cninfo_c_class_phase2_smoke_188_snapshot_dryrun_review_checklist.md` — **Phase 4** snapshot dry-run 审查清单
- `outputs/validation/cninfo_c_class_phase2_smoke_188_snapshot_planning_summary.md` — **Phase 4** snapshot 规划摘要（§7de · gate **DESIGN_COMPLETE**）
- `lab/eval_companies_c_class_phase2_smoke_188_snapshot.yaml` — **Phase 4** snapshot 188 universe YAML
- `lab/test_cninfo_c_class_phase2_smoke_188_snapshot_builder_extension.py` — **Phase 4** snapshot builder 扩展测试（§7df · **9/9 PASS**）
- `outputs/validation/cninfo_c_class_phase2_smoke_188_snapshot_builder_extension_summary.md` — **Phase 4** builder 扩展摘要（§7df · gate **PASS**）
- `outputs/validation/cninfo_c_class_phase2_smoke_188_snapshot_dryrun_report.csv` — **Phase 4** snapshot dry-run 报告（188 行）
- `outputs/validation/cninfo_c_class_phase2_smoke_188_snapshot_dryrun_summary.md` — **Phase 4** snapshot dry-run 摘要
- `outputs/snapshot/cninfo_c_class/phase2_smoke_188/` — **Phase 4** Phase 2 smoke 188 snapshot 输出（§7dg · **188** JSON）
- `outputs/validation/cninfo_c_class_phase2_smoke_188_snapshot_build_report.csv` — **Phase 4** snapshot build 报告（§7dg）
- `outputs/validation/cninfo_c_class_phase2_smoke_188_snapshot_build_summary.md` — **Phase 4** snapshot build 摘要
- `outputs/validation/cninfo_c_class_phase2_smoke_188_snapshot_build_qa_summary.md` — **Phase 4** snapshot build QA 摘要（gate **PASS_WITH_CAVEAT**）
- `lab/review_cninfo_c_class_phase2_smoke_188_snapshot_quality.py` — **Phase 4** Phase 2 smoke 188 snapshot QA review 脚本（§7dh）
- `lab/test_cninfo_c_class_phase2_smoke_188_snapshot_quality_review.py` — **Phase 4** snapshot QA review 测试（§7dh · **5/5 PASS**）
- `outputs/validation/cninfo_c_class_phase2_smoke_188_snapshot_completeness_report.csv` — **Phase 4** snapshot 完整性报告
- `outputs/validation/cninfo_c_class_phase2_smoke_188_snapshot_module_coverage.csv` — **Phase 4** snapshot 模块覆盖
- `outputs/validation/cninfo_c_class_phase2_smoke_188_snapshot_quality_flags.csv` — **Phase 4** snapshot 质量标记
- `outputs/validation/cninfo_c_class_phase2_smoke_188_snapshot_qa_summary.md` — **Phase 4** snapshot QA 摘要（§7dh · gate **PASS_WITH_CAVEAT**）
- `plans/cninfo_c_class_phase2_smoke_closure_review.md` — **Phase 4** Phase 2 smoke closure review（§7di · gate **PASS_WITH_CAVEAT**）
- `outputs/validation/cninfo_c_class_phase2_smoke_closure_metrics.csv` — **Phase 4** Phase 2 closure 指标
- `outputs/validation/cninfo_c_class_phase2_smoke_excluded_company_caveat_ledger.csv` — **Phase 4** 12 家排除公司 caveat 台账
- `outputs/validation/cninfo_c_class_phase3_batch_readiness_summary.md` — **Phase 4** Phase 3 batch 规划就绪摘要（`READY_FOR_PLANNING`）
- `plans/cninfo_c_class_phase3_batch_500_expansion_plan.md` — **Phase 4** Phase 3 batch 500 扩源规划（§7dj · gate **DESIGN_COMPLETE**）
- `outputs/validation/cninfo_c_class_phase3_batch_500_candidate_matrix.csv` — **Phase 4** Phase 3 候选矩阵
- `plans/cninfo_c_class_phase3_batch_500_output_design.md` — **Phase 4** Phase 3 产物路径设计
- `plans/cninfo_c_class_phase3_batch_500_execution_checklist.md` — **Phase 4** Phase 3 执行检查清单
- `outputs/validation/cninfo_c_class_phase3_batch_500_planning_summary.md` — **Phase 4** Phase 3 batch 500 规划摘要
- `lab/select_cninfo_c_class_phase3_batch_500_universe.py` — **Phase 4** Phase 3 batch 500 选股脚本（§7dk）
- `lab/test_cninfo_c_class_phase3_batch_500_universe_selection.py` — **Phase 4** batch 500 选股测试（§7dk · **12/12 PASS**）
- `lab/eval_companies_c_class_phase3_batch_500_001.yaml` — **Phase 4** batch 500 universe YAML（**500** 家）
- `outputs/validation/cninfo_c_class_phase3_batch_500_001_selection_matrix.csv` — **Phase 4** batch 500 选股矩阵
- `outputs/validation/cninfo_c_class_phase3_batch_500_001_selection_summary.md` — **Phase 4** batch 500 选股摘要（gate **PASS**）
- `plans/cninfo_c_class_phase3_batch_500_001_harvest_dryrun_plan.md` — **Phase 4** Phase 3 batch 500 harvest dry-run 规划（§7dl · **READY_FOR_DRYRUN**）
- `outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_expected_case_matrix.csv` — **Phase 4** harvest 预期 case 矩阵（**5000** rows）
- `plans/cninfo_c_class_phase3_batch_500_001_harvest_command_checklist.md` — **Phase 4** harvest 命令检查清单
- `outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_dryrun_review_checklist.md` — **Phase 4** dry-run 审查清单
- `outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_dryrun_planning_summary.md` — **Phase 4** dry-run 规划摘要
- `outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_dryrun_report.csv` — **Phase 4** dry-run 报告（§7dm · **5000** rows）
- `outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_dryrun_summary.md` — **Phase 4** dry-run 摘要
- `outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_dryrun_validation_summary.md` — **Phase 4** dry-run validation 摘要（gate **PASS**）
- `outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_dryrun_qa_summary.md` — **Phase 4** dry-run QA 摘要（§7dm · execution gate **PASS**）
- `lab/test_cninfo_c_class_phase3_batch_500_harvest_approval.py` — **Phase 4** Phase 3 approval 扩展测试（§7dn · **10/10 PASS**）
- `plans/cninfo_c_class_phase3_batch_500_001_live_harvest_approval_plan.md` — **Phase 4** Phase 3 live approval 计划（§7dn · gate **`READY_FOR_APPROVAL`**）
- `outputs/validation/cninfo_c_class_phase3_batch_500_001_live_harvest_approval_checklist.md` — **Phase 4** live approval 检查清单
- `plans/cninfo_c_class_phase3_batch_500_001_live_harvest_command_draft.md` — **Phase 4** live 命令草稿（**NOT APPROVED YET**）
- `outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_approval_extension_summary.md` — **Phase 4** approval 扩展摘要（§7dn）
- `lab/triage_cninfo_c_class_phase3_batch_500_failure_identity.py` — **Phase 4** failure identity 分诊（§7dp）
- `outputs/validation/cninfo_c_class_phase3_batch_500_failure_identity_caveat_ledger.csv` — **Phase 4** identity caveat 台账（**9** 家）
- `outputs/validation/cninfo_c_class_phase3_batch_500_failure_identity_caveat_summary.md` — **Phase 4** identity 分诊摘要
- `lab/plan_cninfo_c_class_phase3_batch_500_success_snapshot.py` — **Phase 4** success-subset snapshot 规划脚本（§7dpo）
- `outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_subset_design.csv` — **Phase 4** snapshot subset design（**491** / **9**）
- `plans/cninfo_c_class_phase3_batch_500_success_snapshot_plan.md` — **Phase 4** success-subset snapshot 规划（§7dpo）
- `plans/cninfo_c_class_phase3_batch_500_success_snapshot_execution_checklist.md` — **Phase 4** snapshot 执行检查清单
- `outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_planning_summary.md` — **Phase 4** snapshot 规划摘要（§7dpo · gate **`DESIGN_COMPLETE`**）
- `plans/cninfo_c_class_phase3_batch_500_success_snapshot_dryrun_plan.md` — **Phase 4** success-subset snapshot dry-run 规划（§7dpr）
- `plans/cninfo_c_class_phase3_batch_500_success_snapshot_dryrun_checklist.md` — **Phase 4** dry-run 检查清单
- `outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_dryrun_validation_design.md` — **Phase 4** dry-run validation 设计
- `outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_dryrun_planning_summary.md` — **Phase 4** dry-run 规划摘要（gate **`READY_FOR_DRYRUN`**）
- `lab/eval_companies_c_class_phase3_batch_500_success_snapshot_491.yaml` — **Phase 4** snapshot universe YAML（**491** 家）
- `lab/generate_cninfo_c_class_phase3_batch_500_success_snapshot_universe_yaml.py` — **Phase 4** YAML 生成脚本
- `outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_dryrun_report.csv` — **Phase 4** dry-run 报告（**491** rows）
- `outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_dryrun_summary.md` — **Phase 4** dry-run 摘要
- `outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_build_approval_checklist.md` — **Phase 4** snapshot build 审批清单（§7dps · gate **`READY_FOR_APPROVAL`**）
- `plans/cninfo_c_class_phase3_batch_500_success_snapshot_build_command_draft.md` — **Phase 4** build 命令草稿（**NOT APPROVED YET**）
- `outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_build_expected_qa.md` — **Phase 4** build 预期 QA
- `outputs/validation/cninfo_c_class_phase3_success_snapshot_approval_extension_summary.md` — **Phase 4** snapshot approval extension 摘要（§7dpt · test **11/11 PASS**）
- `lab/test_cninfo_c_class_phase3_success_snapshot_approval.py` — **Phase 4** snapshot approval 测试（**11/11 PASS**）
- `lab/review_cninfo_c_class_phase3_batch_500_success_snapshot_quality.py` — **Phase 4** Phase 3 success-subset snapshot QA reviewer（§7dpv）
- `lab/test_cninfo_c_class_phase3_batch_500_success_snapshot_quality_review.py` — **Phase 4** snapshot QA 测试（**6/6 PASS**）
- `outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_completeness_report.csv` — **Phase 4** snapshot 完整性报告
- `outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_module_coverage.csv` — **Phase 4** 模块覆盖率报告
- `outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_quality_flags.csv` — **Phase 4** 质量 flag 报告
- `outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_qa_summary.md` — **Phase 4** snapshot QA 摘要（gate **`PASS_WITH_CAVEAT`**）
- `plans/cninfo_c_class_phase3_batch_500_closure_review.md` — **Phase 4** Phase 3 batch 500 closure review（§7dpw · gate **`PASS_WITH_CAVEAT`**）
- `outputs/validation/cninfo_c_class_phase3_batch_500_closure_metrics.csv` — **Phase 4** Phase 3 closure 指标
- `outputs/validation/cninfo_c_class_phase3_batch_500_closure_summary.md` — **Phase 4** Phase 3 closure 摘要
- `plans/cninfo_c_class_phase3_next_step_recommendation.md` — **Phase 4** Phase 3 下一步建议
- `plans/cninfo_c_class_phase35_batch_planning.md` — **Phase 4** Phase 3.5 batch 规划（§7dpx · gate **`READY_FOR_REVIEW`**）
- `plans/cninfo_c_class_phase35_harvest_dryrun_plan.md` — **Phase 4** Phase 3.5 harvest dry-run 规划（**NOT APPROVED**）
- `outputs/validation/cninfo_c_class_phase35_candidate_universe_design.csv` — **Phase 4** Phase 3.5 候选 universe 设计
- `outputs/validation/cninfo_c_class_phase35_batch_universe_draft.csv` — **Phase 4** Phase 3.5 universe draft（**500**）
- `outputs/validation/cninfo_c_class_phase35_batch_approval_checklist.md` — **Phase 4** Phase 3.5 审批清单
- `outputs/validation/cninfo_c_class_phase35_batch_planning_summary.md` — **Phase 4** Phase 3.5 规划摘要
- `lab/eval_companies_c_class_phase35_batch_500_001.yaml` — **Phase 4** Phase 3.5 batch 500 harvest YAML（**500**）
- `outputs/validation/cninfo_c_class_phase35_harvest_dryrun_report.csv` — **Phase 4** Phase 3.5 harvest dry-run 报告
- `outputs/validation/cninfo_c_class_phase35_harvest_dryrun_summary.md` — **Phase 4** Phase 3.5 harvest dry-run 摘要
- `outputs/validation/cninfo_c_class_phase35_harvest_approval_extension_summary.md` — **Phase 4** Phase 3.5 approval extension 摘要
- `plans/cninfo_c_class_phase35_live_harvest_command_draft.md` — **Phase 4** Phase 3.5 live harvest 命令草稿（**NOT APPROVED**）
- `lab/test_cninfo_c_class_phase35_harvest_approval.py` — **Phase 4** Phase 3.5 harvest approval 测试（**11/11 PASS**）
- `lab/select_cninfo_c_class_phase35_batch_universe.py` — **Phase 4** Phase 3.5 universe 选股 / YAML 生成脚本
- `plans/cninfo_c_class_phase35_harvest_qa_review.md` — **Phase 4** Phase 3.5 harvest QA review
- `outputs/validation/cninfo_c_class_phase35_failed_company_triage_ledger.csv` — **Phase 4** Phase 3.5 failed 分诊（**6**）
- `outputs/validation/cninfo_c_class_phase35_partial_company_qa_ledger.csv` — **Phase 4** Phase 3.5 partial QA（**75**）
- `outputs/validation/cninfo_c_class_phase35_empty_but_valid_reconciliation.csv` — **Phase 4** empty_but_valid 对账
- `outputs/validation/cninfo_c_class_phase35_http_error_analysis.csv` — **Phase 4** http_error 分析
- `outputs/validation/cninfo_c_class_phase35_success_subset_design.csv` — **Phase 4** success subset 设计（**463**）
- `outputs/validation/cninfo_c_class_phase35_snapshot_holdout_ledger.csv` — **Phase 4** snapshot holdout（**37**）
- `outputs/validation/cninfo_c_class_phase35_harvest_qa_summary.md` — **Phase 4** Phase 3.5 harvest QA 摘要
- `lab/review_cninfo_c_class_phase35_harvest_qa.py` — **Phase 4** Phase 3.5 harvest QA 脚本（离线）
- `plans/cninfo_c_class_phase35_isolated_resume_plan.md` — **Phase 4** Phase 3.5 isolated resume 规划
- `outputs/validation/cninfo_c_class_phase35_isolated_resume_universe.csv` — **Phase 4** resume universe（**29**）
- `plans/cninfo_c_class_phase35_hold_for_review_decision_note.md` — **Phase 4** hold_for_review 决策（**8** 排除）
- `outputs/validation/cninfo_c_class_phase35_isolated_resume_approval_checklist.md` — **Phase 4** resume 审批清单（**NOT APPROVED**）
- `plans/cninfo_c_class_phase35_isolated_resume_command_draft.md` — **Phase 4** resume 命令草稿（**NOT APPROVED**）
- `plans/cninfo_c_class_phase35_isolated_resume_runner_extension_design.md` — **Phase 4** resume runner 扩展设计
- `outputs/validation/cninfo_c_class_phase35_isolated_resume_planning_summary.md` — **Phase 4** resume 规划摘要
- `lab/test_cninfo_c_class_phase35_isolated_resume_runner.py` — **Phase 4** isolated resume runner 测试（**27/27 PASS**）
- `outputs/validation/cninfo_c_class_phase35_isolated_resume_runner_extension_summary.md` — **Phase 4** resume runner 扩展摘要（gate **`READY_FOR_APPROVAL`**）
- `outputs/harvest/cninfo_c_class/phase35_batch_500_001_resume/reports/cninfo_c_class_phase35_isolated_resume_dryrun_report.csv` — **Phase 4** isolated resume dry-run 报告（**29**）
- `outputs/harvest/cninfo_c_class/phase35_batch_500_001_resume/reports/cninfo_c_class_phase35_isolated_resume_dryrun_summary.md` — **Phase 4** isolated resume dry-run 摘要
- `lab/review_cninfo_c_class_phase35_isolated_resume_qa.py` — **Phase 4** isolated resume QA 脚本（离线）
- `outputs/validation/cninfo_c_class_phase35_isolated_resume_qa_summary.md` — **Phase 4** isolated resume QA 摘要
- `outputs/validation/cninfo_c_class_phase35_isolated_resume_case_triage.csv` — **Phase 4** resume case triage（**29**）
- `outputs/validation/cninfo_c_class_phase35_resume_merge_planning.md` — **Phase 4** resume merge 规划（planning only）
- `outputs/validation/cninfo_c_class_phase35_updated_success_holdout_plan.csv` — **Phase 4** 更新 success/holdout 规划（**491** + **9**）
- `lab/plan_cninfo_c_class_phase35_expanded_success_subset_snapshot.py` — **Phase 4** expanded snapshot 规划脚本（离线）
- `outputs/validation/cninfo_c_class_phase35_expanded_success_subset_snapshot_plan.md` — **Phase 4** expanded snapshot 规划
- `outputs/validation/cninfo_c_class_phase35_expanded_success_subset_universe.csv` — **Phase 4** expanded snapshot universe（**491**）
- `outputs/validation/cninfo_c_class_phase35_snapshot_merge_manifest_design.csv` — **Phase 4** snapshot merge manifest 设计
- `outputs/validation/cninfo_c_class_phase35_expanded_snapshot_holdout_ledger.csv` — **Phase 4** expanded holdout（**9**）
- `outputs/validation/cninfo_c_class_phase35_expanded_snapshot_approval_checklist.md` — **Phase 4** expanded snapshot 审批清单（**NOT APPROVED**）
- `outputs/validation/cninfo_c_class_phase35_expanded_snapshot_planning_summary.md` — **Phase 4** expanded snapshot 规划摘要
- `plans/cninfo_c_class_phase35_expanded_snapshot_build_command_draft.md` — **Phase 4** expanded snapshot build 命令草稿（**NOT APPROVED**）
- `lab/eval_companies_c_class_phase35_expanded_success_snapshot_491.yaml` — **Phase 4** expanded snapshot universe YAML（**491**）
- `lab/test_cninfo_c_class_phase35_expanded_snapshot_builder.py` — **Phase 4** expanded snapshot builder 测试（**17/17 PASS** · 含 cleanup 硬化）
- `outputs/validation/cninfo_c_class_phase35_expanded_snapshot_builder_extension_summary.md` — **Phase 4** expanded snapshot builder 扩展摘要（gate **`READY_FOR_APPROVAL`**）
- `outputs/validation/cninfo_c_class_phase35_expanded_snapshot_dryrun_report.csv` — **Phase 4** expanded snapshot dry-run 报告（**491**）
- `outputs/validation/cninfo_c_class_phase35_expanded_snapshot_dryrun_summary.md` — **Phase 4** expanded snapshot dry-run 摘要
- `outputs/validation/cninfo_c_class_phase35_expanded_snapshot_build_report.csv` — **Phase 4** expanded snapshot build 报告（**491**）
- `outputs/validation/cninfo_c_class_phase35_expanded_snapshot_build_summary.md` — **Phase 4** expanded snapshot build 摘要（gate **`PASS_WITH_CAVEAT`**）
- `outputs/snapshot/cninfo_c_class/phase35_batch_500_001_expanded_success_491/` — **Phase 4** expanded snapshot 输出根（**491** JSON）
- `lab/review_cninfo_c_class_phase35_expanded_snapshot_quality.py` — **Phase 4** expanded snapshot QA 脚本（离线）
- `lab/test_cninfo_c_class_phase35_expanded_snapshot_quality_review.py` — **Phase 4** expanded snapshot QA 测试（**10/10 PASS**）
- `outputs/validation/cninfo_c_class_phase35_expanded_snapshot_qa_summary.md` — **Phase 4** expanded snapshot QA 摘要（gate **`PASS_WITH_CAVEAT`**）
- `outputs/validation/cninfo_c_class_phase35_expanded_snapshot_qa_metrics.csv` — **Phase 4** expanded snapshot QA 指标
- `outputs/validation/cninfo_c_class_phase35_expanded_snapshot_qa_case_ledger.csv` — **Phase 4** expanded snapshot QA case ledger（**491**）
- `outputs/validation/cninfo_c_class_phase35_expanded_snapshot_qa_holdout_confirmation.csv` — **Phase 4** holdout 排除确认（**9**）
- `lab/review_cninfo_c_class_phase35_expanded_snapshot_closure.py` — **Phase 4** expanded snapshot closure 脚本（离线）
- `plans/cninfo_c_class_phase35_expanded_snapshot_closure_review.md` — **Phase 4** expanded snapshot closure review
- `outputs/validation/cninfo_c_class_phase35_expanded_snapshot_closure_summary.md` — **Phase 4** closure 摘要（gate **`PASS_WITH_CAVEAT`**）
- `outputs/validation/cninfo_c_class_phase35_expanded_snapshot_closure_metrics.csv` — **Phase 4** closure 指标
- `outputs/validation/cninfo_c_class_phase35_expanded_snapshot_final_caveat_ledger.csv` — **Phase 4** final caveat ledger
- `outputs/validation/cninfo_c_class_phase35_expanded_snapshot_post_closure_next_step_recommendation.md` — **Phase 4** post-closure 下一步建议
- `lab/review_cninfo_c_class_phase35_expanded_snapshot_commit_boundary.py` — **Phase 4** commit boundary 脚本（离线）
- `plans/cninfo_c_class_phase35_expanded_snapshot_commit_boundary_review.md` — **Phase 4** commit boundary review
- `outputs/validation/cninfo_c_class_phase35_expanded_snapshot_final_artifact_inventory.csv` — **Phase 4** artifact inventory
- `outputs/validation/cninfo_c_class_phase35_expanded_snapshot_commit_caveat_ledger.csv` — **Phase 4** commit caveat ledger
- `outputs/validation/cninfo_c_class_phase35_expanded_snapshot_safe_to_commit_list.md` — **Phase 4** safe-to-commit list
- `outputs/validation/cninfo_c_class_phase35_expanded_snapshot_commit_boundary_summary.md` — **Phase 4** boundary summary（gate **`READY_FOR_COMMIT_REVIEW`**）
- `lab/cninfo_c_class_erad_cleanup_guard.py` — **Era D** C 类 cleanup / audit 写入保护工具
- `lab/test_cninfo_c_class_erad_cleanup_hardening.py` — **Era D** cleanup 硬化回归（**7/7 PASS**）
- `outputs/validation/cninfo_c_class_erad_cleanup_hardening_summary.md` — **Era D** Slice-C-EraD-01 硬化摘要（gate **`PASS_OFFLINE`**）
- `lab/run_cninfo_c_class_harvest_resume_audit.py` — **Era D** 863 harvest resume 审计 runner（dry-run only）
- `lab/test_cninfo_c_class_erad_harvest_resume_audit.py` — **Era D** harvest resume 审计测试（**7/7 PASS**）
- `outputs/validation/cninfo_c_class_erad_harvest_resume_audit/` — **Era D** Slice-C-EraD-02 审计报告根
- `outputs/validation/cninfo_c_class_erad_harvest_resume_audit_summary.md` — **Era D** Slice-C-EraD-02 审计摘要（gate **`PASS_OFFLINE`**）
- `plans/cninfo_c_class_erad_snapshot_rebuild_readiness_plan.md` — **Era D** Slice-C-EraD-03 snapshot rebuild readiness 规划
- `outputs/validation/cninfo_c_class_erad_snapshot_rebuild_readiness_checklist.md` — **Era D** rebuild readiness 批准清单（**NOT APPROVED**）
- `outputs/validation/cninfo_c_class_erad_snapshot_rebuild_candidate_matrix.csv` — **Era D** rebuild 候选 cohort 矩阵
- `outputs/validation/cninfo_c_class_erad_snapshot_rebuild_readiness_summary.md` — **Era D** Slice-C-EraD-03 规划摘要（gate **`READY_FOR_APPROVAL`**）
- `outputs/validation/cninfo_c_class_erad_snapshot_rebuild_next_step_recommendation.md` — **Era D** rebuild 下一步建议（**Option A HOLD**）
- `plans/cninfo_c_class_erad_option_a_hold_signoff.md` — **Era D** Option A HOLD 人批 signoff
- `outputs/validation/cninfo_c_class_erad_option_a_hold_ledger.csv` — **Era D** HOLD cohort 决策 ledger
- `outputs/validation/cninfo_c_class_erad_needs_review_58_triage_ledger.csv` — **Era D** 58 needs_review 分诊 ledger
- `outputs/validation/cninfo_c_class_erad_needs_review_58_triage_summary.md` — **Era D** 58 分诊摘要（gate **`PASS_OFFLINE`**）
- `outputs/validation/cninfo_c_class_erad_needs_review_58_next_step_recommendation.md` — **Era D** 58 分诊下一步
- `outputs/validation/cninfo_c_class_erad_c_line_continue_summary.md` — **Era D** C-line 继续摘要（**Era D 未结束**）
- `lab/run_cninfo_c_class_erad_status_fix_8_scan.py` — **Era D** 8 家 status-fix 离线扫描（validation-root writes only）
- `outputs/validation/cninfo_c_class_erad_status_fix_8/` — **Era D** status-fix-8 报告根
- `outputs/validation/cninfo_c_class_erad_status_fix_8_summary.md` — **Era D** status-fix-8 摘要（gate **`PASS_OFFLINE`** · **8/8**）
- `lab/run_cninfo_c_class_erad_status_fix_8_apply.py` — **Era D** status-fix-8 生产 CSV 安全 apply
- `outputs/validation/cninfo_c_class_erad_status_fix_8_apply/` — **Era D** status-fix-8 apply 报告根
- `outputs/validation/cninfo_c_class_erad_status_fix_8_apply_summary.md` — **Era D** apply 摘要（gate **`PASS_WITH_CAVEAT`**）
- `lab/run_cninfo_c_class_erad_partial6_human_review_scan.py` — **Era D** partial-6 离线 human-review 扫描
- `outputs/validation/cninfo_c_class_erad_partial6_human_review/` — **Era D** partial-6 报告根
- `outputs/validation/cninfo_c_class_erad_partial6_human_review_summary.md` — **Era D** partial-6 摘要（gate **`PASS_OFFLINE`** · needs_live_resume **0/6**）
- `lab/test_cninfo_c_class_harvest_output_root_isolation.py` — **Phase 4** output-root 隔离测试（§7db · **8/8 PASS**）
- `outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_output_root_extension_summary.md` — **Phase 4** runner 扩展摘要（§7db · gate **PASS**）
- `outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_output_root_dryrun_report.csv` — **Phase 4** output-root dry-run 报告
- `outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_output_root_dryrun_summary.md` — **Phase 4** output-root dry-run 摘要
- `outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_output_root_dryrun_validation_summary.md` — **Phase 4** output-root dry-run validation 摘要
- `plans/cninfo_c_class_registry_candidate_refresh_execution_plan.md` — **Phase 4** refresh 未来执行计划（§7cu）
- `outputs/validation/cninfo_c_class_registry_candidate_refresh_action_matrix.csv` — **Phase 4** refresh action 矩阵
- `outputs/validation/cninfo_c_class_registry_candidate_refresh_planning_summary.md` — **Phase 4** refresh 规划摘要
- `plans/cninfo_c_class_full_market_universe_reconciliation_plan.md` — **Phase 4** 全市场 universe 对账设计（§7cs）
- `plans/cninfo_c_class_full_market_phased_execution_plan.md` — **Phase 4** 全市场分阶段执行计划（§7cs）
- `outputs/validation/cninfo_c_class_full_market_universe_reconciliation_matrix.csv` — **Phase 4** 全市场对账矩阵
- `outputs/validation/cninfo_c_class_full_market_readiness_matrix.csv` — **Phase 4** 全市场就绪矩阵（规划阶段）
- `outputs/validation/cninfo_c_class_full_market_expansion_readiness_matrix.csv` — **Phase 4** 全市场扩展就绪矩阵（§7cr）
- `outputs/validation/cninfo_c_class_full_market_expansion_readiness_summary.md` — **Phase 4** 全市场扩展就绪度摘要
- `outputs/validation/cninfo_c_class_full_market_expansion_planning_summary.md` — **Phase 4** 全市场扩展规划摘要
- `outputs/validation/cninfo_c_class_field_inventory_promotion_summary.md` — **Phase 4** 字段升格摘要（**10** promoted · normalized_core=**74**）
- `outputs/validation/cninfo_c_class_field_inventory_promotion_check.csv` — **Phase 4** 升格核对表
- `outputs/validation/cninfo_c_class_final_field_catalog.csv` — **Phase 4** 最终字段目录（**120** 字段 · inventory 未改）
- `outputs/validation/cninfo_c_class_field_freeze_summary.md` — **Phase 4** Field Freeze 摘要
- `plans/cninfo_c_class_field_freeze_v1.md` — **Phase 4** 字段冻结说明 v1
- `outputs/validation/cninfo_c_class_company_profile_coverage_matrix.csv` — **Phase 4** 公司画像覆盖矩阵
- `outputs/validation/cninfo_c_class_raw_only_field_policy_review.md` — **Phase 4** raw_only 25 字段政策复判
- `outputs/validation/cninfo_c_class_review_later_promotion_candidate_approval.md` — **Phase 4** promotion candidate approval（**9** approved · gate PASS）
- `outputs/validation/cninfo_c_class_review_later_field_reclassification.md` — **Phase 4** review_later 31 字段复判报告
- `plans/cninfo_c_class_qa_review_queue_closure_plan.md` — **Phase 4** QA review queue 关闭计划（72 flags · P0=6 / P1=12 / P2=54）
- `outputs/validation/cninfo_c_class_qa_review_queue_closure_summary.md` — **Phase 4** QA queue closure classification 摘要（**gate PASS**）
- `plans/cninfo_c_class_dividend_history_mapping.md` — **Phase 4** dividend_history 字段映射（≠ financing）
- `config/cninfo_dividend_history_mapper.yaml` — dividend_history mapper 配置（normalized_core=9）
- `plans/cninfo_c_class_stable_200_live_pass_decision.md` — **Phase 4** stable 200 rerun LIVE_PASS 决策
- `lab/debug_cninfo_c_class_12_six_fail_endpoints.py` — **Phase 4** 十二家 endpoint debug 脚本（仅 12 家 CNINFO）
- `plans/cninfo_c_class_source_status_decision.md` — **Phase 4** C 类 10 源阶段性状态判断（scale 验证收口）
- `plans/cninfo_c_class_universe_split_and_sample_cleaning_plan.md` — **Phase 4** C 类 universe split + 1000-like 清洗规则
- `plans/cninfo_c_class_scale_smoke_200_plan.md` — **Phase 4** C 类 200-company scale smoke 计划（active 过滤 · gate · 不直接跑 live）
- `plans/cninfo_c_class_p1_yaml_backfill_decision.md` — P1 candidate YAML 回填 / 暂缓决策（**YAML 未改**）
- `plans/cninfo_c_class_basic_profile_field_mapping_draft.md` — getCompanyIntroduction → basic profile 字段映射草案
- `plans/cninfo_c_class_f10_source_discovery_design.md` — **Phase 4** C 类 F10 / company profile source discovery 设计草案
- `plans/cninfo_c_class_profile_data_model_draft.md` — C 类 profile snapshot 逻辑数据模型
- `plans/cninfo_c_vs_b_vs_d_boundary.md` — C 类与 B / D 类边界
- `plans/cninfo_a_class_report_metadata_architecture_plan.md` — **Phase 0** A 类定期报告元数据层架构计划（report_document + PDF lineage · 不下载 PDF）
- `plans/cninfo_a_class_source_discovery_plan.md` — **Phase 0** A 类 source discovery 离线策略
- `outputs/validation/cninfo_a_class_readiness_matrix.csv` — A 类 Phase 1 readiness 矩阵（**6** 组件）
- `outputs/validation/cninfo_a_class_initial_planning_summary.md` — A 类规划摘要（gate **DESIGN_STARTED**）
- `outputs/validation/cninfo_a_class_phase1_minimum_fields.csv` — A 类 Phase 1 最小字段目录（**40** 字段）
- `plans/cninfo_a_class_phase1_schema_freeze_review.md` — **Phase 1** A 类 schema freeze 评审（gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_a_class_phase1_field_decision_matrix.csv` — A 类 Phase 1 字段决策矩阵（**40** 行）
- `outputs/validation/cninfo_a_class_phase1_schema_freeze_review_summary.md` — freeze review 摘要
- `fixtures/a_class/phase1/` — A 类 Phase1 离线 fixture 骨架（**3** 文件 · 合成占位符）
- `outputs/validation/cninfo_a_class_phase1_schema_freeze_approval_checklist.md` — A 类 Phase 1 freeze 人工批准清单
- `outputs/validation/cninfo_a_class_phase1_schema_freeze_approval_summary.md` — A 类 Phase 1 freeze 批准摘要
- `outputs/validation/cninfo_a_class_phase1_freeze_v1_field_catalog.csv` — A 类 Phase 1 freeze v1 字段目录（**40** 行 · required=**22**）
- `config/cninfo_a_class_source_registry_draft.yaml` — A 类 registry draft（**3** sources · design-only）
- `lab/lint_cninfo_a_class_freeze_v1.py` — A 类 freeze v1 implementation lint（**14/14 PASS**）
- `lab/lint_cninfo_a_class_phase1_freeze_v1.py` — A 类 Phase1 fixture skeleton lint（**10/10 PASS**）
- `outputs/validation/cninfo_a_class_phase1_freeze_v1_lint_summary.md` — lint 摘要
- `outputs/validation/cninfo_a_class_phase1_freeze_v1_implementation_summary.md` — freeze v1 implementation 摘要（gate **PASS_OFFLINE**）
- `fixtures/a_class/phase1/ready_cases/` — A 类 Phase1 ready-case fixtures（**AC001–AC005**）
- `lab/run_cninfo_a_class_phase1_ready_case_benchmark.py` — A 类 ready-case benchmark 离线 runner（**5/5 PASS**）
- `lab/test_cninfo_a_class_phase1_ready_case_benchmark.py` — benchmark 测试（**11/11 PASS**）
- `outputs/validation/cninfo_a_class_phase1_ready_case_benchmark.csv` — ready-case benchmark 结果
- `outputs/validation/cninfo_a_class_phase1_ready_case_benchmark_summary.md` — benchmark 摘要（gate **READY_FOR_REVIEW**）
- `outputs/validation/cninfo_a_class_phase1_tiny_live_metadata_approval_checklist.md` — A 类 tiny live metadata 批准清单
- `outputs/validation/cninfo_a_class_phase1_tiny_live_metadata_universe.csv` — A 类 tiny live universe（**5** 家 · ALM001–ALM005）
- `plans/cninfo_a_class_phase1_tiny_live_metadata_command_draft.md` — A 类 tiny live 命令草案（**NOT APPROVED**）
- `outputs/validation/cninfo_a_class_phase1_tiny_live_metadata_approval_summary.md` — A 类 tiny live 批准摘要（gate **READY_FOR_APPROVAL**）
- `lab/run_cninfo_a_class_tiny_live_metadata_validation.py` — A 类 tiny live metadata runner（dry-run default · **9/9 PASS**）
- `lab/test_cninfo_a_class_tiny_live_metadata_validation_runner.py` — runner 测试（**9/9 PASS**）
- `outputs/validation/cninfo_a_class_tiny_live_metadata/reports/` — dry-run 报告与摘要
- `outputs/validation/cninfo_a_class_tiny_live_metadata_fix_review.md` — A 类 tiny live caveat 修复评审
- `outputs/validation/cninfo_a_class_phase1_tiny_live_metadata_universe_v2_draft.csv` — universe v2 draft（ALM003 修正）
- `lab/test_cninfo_a_class_tiny_live_metadata_matching_logic.py` — matching logic 测试（**10/10 PASS**）
- `outputs/validation/cninfo_a_class_tiny_live_metadata/reports/a_class_tiny_live_metadata_v2_dryrun_report.csv` — v2 dry-run 报告
- `outputs/validation/cninfo_a_class_tiny_live_metadata_fix_summary.md` — fix 摘要（gate **READY_FOR_RERUN_APPROVAL**）
- `outputs/validation/cninfo_a_class_tiny_live_metadata_v2_rerun_review.md` — v2 rerun 评审
- `plans/cninfo_a_class_phase1_tiny_live_metadata_v2_closure_review.md` — Phase 1 tiny live v2 收口评审
- `outputs/validation/cninfo_a_class_phase1_tiny_live_metadata_v2_closure_metrics.csv` — v2 closure 指标
- `outputs/validation/cninfo_a_class_phase1_tiny_live_metadata_v2_closure_summary.md` — v2 closure 摘要（gate **PASS_WITH_CAVEAT**）
- `plans/cninfo_a_class_phase1_boundary_signoff.md` — A 类 Phase 1 边界 signoff（gate **PASS_WITH_CAVEAT**）
- `outputs/validation/cninfo_a_class_phase1_boundary_metrics.csv` — Phase 1 边界指标
- `outputs/validation/cninfo_a_class_phase1_boundary_summary.md` — Phase 1 边界摘要
- `plans/cninfo_a_class_phase2_metadata_expansion_plan.md` — A 类 Phase 2 20-company metadata expansion 规划
- `outputs/validation/cninfo_a_class_phase2_candidate_universe_design.csv` — Phase 2 candidate universe 设计（12 bucket）
- `outputs/validation/cninfo_a_class_phase2_metadata_universe_draft.csv` — Phase 2 universe draft（**20** 家 · A2M001–A2M020）
- `plans/cninfo_a_class_phase2_metadata_command_draft.md` — Phase 2 命令草稿（**NOT APPROVED**）
- `outputs/validation/cninfo_a_class_phase2_metadata_approval_checklist.md` — Phase 2 批准检查清单
- `outputs/validation/cninfo_a_class_phase2_metadata_approval_summary.md` — Phase 2 批准摘要（gate **READY_FOR_APPROVAL**）
- `lab/run_cninfo_a_class_phase2_metadata_expansion.py` — Phase 2 metadata expansion runner
- `lab/test_cninfo_a_class_phase2_metadata_expansion_runner.py` — Phase 2 runner 测试（**16/16 PASS**）
- `outputs/validation/cninfo_a_class_phase2_metadata_runner_extension_summary.md` — Phase 2 runner extension 摘要
- `outputs/validation/cninfo_a_class_phase2_metadata_expansion/reports/a_class_phase2_metadata_dryrun_report.csv` — Phase 2 dry-run 报告
- `outputs/validation/cninfo_a_class_phase2_metadata_expansion/reports/a_class_phase2_metadata_report.csv` — Phase 2 live 执行报告（**12/20 correct**）
- `outputs/validation/cninfo_a_class_phase2_metadata_expansion/reports/a_class_phase2_metadata_summary.md` — Phase 2 live 执行摘要
- `outputs/validation/cninfo_a_class_phase2_metadata_expansion/reports/a_class_phase2_metadata_quality_report.csv` — Phase 2 live 质量报告
- `outputs/validation/cninfo_a_class_phase2_failed_cases_review.md` — Phase 2 失败 case 评审
- `outputs/validation/cninfo_a_class_phase2_failed_retry_universe.csv` — isolated retry universe（**8** 家）
- `plans/cninfo_a_class_phase2_failed_retry_command_draft.md` — failed retry 命令草稿（**NOT APPROVED**）
- `outputs/validation/cninfo_a_class_phase2_failed_retry_approval_checklist.md` — failed retry 批准检查清单
- `outputs/validation/cninfo_a_class_phase2_failed_retry_approval_summary.md` — failed retry 批准摘要
- `lab/test_cninfo_a_class_phase2_failed_retry_runner.py` — failed retry runner 测试（**12/12 PASS**）
- `outputs/validation/cninfo_a_class_phase2_metadata_retry/reports/a_class_phase2_failed_retry_dryrun_report.csv` — failed retry dry-run 报告
- `outputs/validation/cninfo_a_class_phase2_metadata_retry/reports/a_class_phase2_failed_retry_report.csv` — failed retry live 执行报告（**0/8 correct**）
- `outputs/validation/cninfo_a_class_phase2_metadata_retry/reports/a_class_phase2_failed_retry_summary.md` — failed retry live 摘要
- `outputs/validation/cninfo_a_class_phase2_metadata_retry/reports/a_class_phase2_failed_retry_quality_report.csv` — failed retry 质量报告
- `plans/cninfo_a_class_phase2_metadata_merge_closure_review.md` — Phase 2 merge closure 评审（gate **PASS_WITH_CAVEAT_NETWORK_UNRESOLVED**）
- `outputs/validation/cninfo_a_class_phase2_metadata_merged_result.csv` — Phase 2 merged result（**12 accepted** · **8 unresolved**）
- `outputs/validation/cninfo_a_class_phase2_unresolved_network_failure_ledger.csv` — unresolved network failure 台账（**8** 行）
- `outputs/validation/cninfo_a_class_phase2_metadata_closure_metrics.csv` — Phase 2 closure 指标
- `outputs/validation/cninfo_a_class_phase2_metadata_closure_summary.md` — Phase 2 closure 摘要
- `plans/cninfo_a_class_phase2_network_recovery_retry_recommendation.md` — network recovery retry 建议（Option A/B/C）
- `plans/cninfo_a_class_phase2_network_recovery_retry_v2_plan.md` — network recovery retry v2 规划（**8 case** · **NOT APPROVED**）
- `outputs/validation/cninfo_a_class_phase2_network_recovery_retry_v2_universe.csv` — retry v2 universe（**8** 行）
- `outputs/validation/cninfo_a_class_phase2_network_recovery_retry_v2_approval_checklist.md` — retry v2 批准检查清单（**NOT_APPROVED**）
- `plans/cninfo_a_class_phase2_network_recovery_retry_v2_command_draft.md` — retry v2 命令草稿（**NOT APPROVED**）
- `plans/cninfo_a_class_phase2_network_recovery_retry_v2_runner_extension_plan.md` — retry v2 runner extension 规划
- `outputs/validation/cninfo_a_class_phase2_network_recovery_retry_v2_planning_summary.md` — retry v2 规划摘要（gate **READY_FOR_APPROVAL**）
- `lab/test_cninfo_a_class_phase2_network_recovery_retry_v2_runner.py` — retry v2 runner 测试（**18/18 PASS**）
- `outputs/validation/cninfo_a_class_phase2_network_recovery_retry_v2_runner_extension_summary.md` — retry v2 runner extension 摘要（gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_a_class_phase2_metadata_retry_v2/reports/a_class_phase2_retry_v2_dryrun_report.csv` — retry v2 dry-run 报告（**8/8**）
- `outputs/validation/cninfo_a_class_phase2_metadata_retry_v2/reports/a_class_phase2_retry_v2_report.csv` — retry v2 live 报告（**0/8 acceptable**）
- `outputs/validation/cninfo_a_class_phase2_metadata_retry_v2/reports/a_class_phase2_retry_v2_summary.md` — retry v2 live 摘要（execution gate **FAIL_REVIEW_REQUIRED**）
- `outputs/validation/cninfo_a_class_phase2_metadata_retry_v2/reports/a_class_phase2_retry_v2_quality_report.csv` — retry v2 quality 报告
- `plans/cninfo_a_class_phase2_retry_v2_closure_review.md` — retry v2 merge closure 评审（gate **PASS_WITH_CAVEAT_NETWORK_UNRESOLVED**）
- `outputs/validation/cninfo_a_class_phase2_unresolved_network_failure_ledger_v2.csv` — unresolved network failure 台账 v2（**8** 行）
- `outputs/validation/cninfo_a_class_phase2_metadata_merged_result_v2.csv` — merged effective result v2（**12 accepted** · **8 unresolved**）
- `outputs/validation/cninfo_a_class_phase2_retry_v2_closure_metrics.csv` — retry v2 closure 指标
- `outputs/validation/cninfo_a_class_phase2_retry_v2_closure_summary.md` — retry v2 closure 摘要
- `plans/cninfo_a_class_phase2_post_retry_v2_next_step_recommendation.md` — post retry_v2 路径建议（Option B before A）
- `plans/cninfo_a_class_phase2_cninfo_reachability_precheck_plan.md` — CNINFO reachability precheck 规划（**NOT APPROVED**）
- `outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck_candidates.csv` — precheck 候选（**3** 行 · unresolved 8 子集）
- `outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck_approval_checklist.md` — precheck 批准检查清单（**NOT_APPROVED**）
- `plans/cninfo_a_class_phase2_cninfo_reachability_precheck_command_draft.md` — precheck 命令草稿（**NOT APPROVED**）
- `plans/cninfo_a_class_phase2_cninfo_reachability_precheck_runner_design.md` — precheck runner 设计（**未实现 live**）
- `outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck_planning_summary.md` — precheck 规划摘要（gate **READY_FOR_APPROVAL**）
- `lab/run_cninfo_a_class_phase2_cninfo_reachability_precheck.py` — precheck runner
- `lab/test_cninfo_a_class_phase2_cninfo_reachability_precheck_runner.py` — precheck runner 测试（**23/23 PASS**）
- `outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck_runner_summary.md` — precheck runner 摘要（runner gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck/reports/a_class_phase2_cninfo_reachability_precheck_dryrun_report.csv` — precheck dry-run 报告（**3/3**）
- `outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck/reports/a_class_phase2_cninfo_reachability_precheck_dryrun_summary.md` — precheck dry-run 摘要
- `outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck/reports/a_class_phase2_cninfo_reachability_precheck_report.csv` — precheck live 报告（**2/3 orgId resolved**）
- `outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck/reports/a_class_phase2_cninfo_reachability_precheck_summary.md` — precheck live 摘要（execution gate **PASS_WITH_CAVEAT**）
- `outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck/reports/a_class_phase2_cninfo_reachability_precheck_quality_report.csv` — precheck quality 报告
- `plans/cninfo_a_class_phase2_retry_v3_isolated_plan.md` — retry v3 isolated 规划（**NOT APPROVED**）
- `outputs/validation/cninfo_a_class_phase2_retry_v3_universe.csv` — retry v3 universe（**8** 行）
- `outputs/validation/cninfo_a_class_phase2_retry_v3_approval_checklist.md` — retry v3 批准检查清单（**NOT_APPROVED**）
- `plans/cninfo_a_class_phase2_retry_v3_command_draft.md` — retry v3 命令草稿（**NOT APPROVED**）
- `plans/cninfo_a_class_phase2_retry_v3_runner_extension_design.md` — retry v3 runner 扩展设计（**已实现**）
- `outputs/validation/cninfo_a_class_phase2_retry_v3_runner_extension_summary.md` — retry v3 runner 扩展摘要（gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_a_class_phase2_metadata_retry_v3/reports/` — retry v3 dry-run 报告（**8/8 planned_ok** · CNINFO **0**）
- `lab/test_cninfo_a_class_phase2_retry_v3_runner.py` — retry v3 runner 测试（**23/23 PASS**）
- `lab/test_cninfo_a_class_phase2_retry_v3_live_path.py` — retry v3 live-path 测试（**25/25 PASS** · mock CNINFO）
- `outputs/validation/cninfo_a_class_phase2_metadata_merged_result_v3.csv` — Phase 2 merged effective result v3（**20/20**）
- `outputs/validation/cninfo_a_class_phase2_retry_v3_recovered_case_ledger.csv` — retry v3 recovered ledger（**8** case）
- `outputs/validation/cninfo_a_class_phase2_retry_v3_final_closure_metrics.csv` — final closure metrics
- `outputs/validation/cninfo_a_class_phase2_retry_v3_final_closure_summary.md` — final closure summary（gate **PASS_WITH_CAVEAT**）
- `plans/cninfo_a_class_phase2_retry_v3_merge_closure_review.md` — retry v3 merge closure review
- `plans/cninfo_a_class_phase2_final_commit_boundary_review.md` — Phase 2 commit boundary review
- `outputs/validation/cninfo_a_class_phase2_final_artifact_inventory.csv` — final artifact inventory
- `outputs/validation/cninfo_a_class_phase2_final_caveat_ledger.csv` — final caveat ledger
- `outputs/validation/cninfo_a_class_phase2_safe_to_commit_list.md` — safe-to-commit list
- `outputs/validation/cninfo_a_class_phase2_commit_boundary_summary.md` — commit boundary summary（gate **READY_FOR_COMMIT_REVIEW** · commit **`cad5ed1`** · review gate **READY_FOR_HUMAN_DECISION**）
- `plans/cninfo_a_class_phase3_50_company_expansion_plan.md` — Phase 3 50-company expansion plan
- `outputs/validation/cninfo_a_class_phase3_50_company_universe_draft.csv` — Phase 3 universe draft（**50** · A3M001–A3M050）
- `outputs/validation/cninfo_a_class_phase3_50_company_approval_checklist.md` — Phase 3 approval checklist（**APPROVED** · live executed）
- `plans/cninfo_a_class_phase3_50_company_command_draft.md` — Phase 3 command draft（live executed）
- `plans/cninfo_a_class_phase3_50_company_runner_extension_design.md` — Phase 3 runner extension design（design only）
- `outputs/validation/cninfo_a_class_phase3_50_company_planning_summary.md` — Phase 3 planning summary（gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_a_class_phase3_50_company_runner_extension_summary.md` — Phase 3 runner extension summary（gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_a_class_phase3_50_company_expansion/reports/a_class_phase3_50_company_dryrun_report.csv` — Phase 3 dry-run report（**50/50**）
- `lab/test_cninfo_a_class_phase3_50_company_runner.py` — Phase 3 runner tests（**26/26 PASS**）
- `outputs/validation/cninfo_a_class_phase3_50_company_live_path_summary.md` — Phase 3 live path summary（gate **READY_FOR_APPROVAL**）
- `lab/test_cninfo_a_class_phase3_50_company_live_path.py` — Phase 3 live-path tests（**28/28 PASS**）
- `outputs/validation/cninfo_a_class_phase3_50_company_expansion/reports/a_class_phase3_50_company_expansion_report.csv` — Phase 3 live report（**49/50 acceptable** · CNINFO **104**）
- `outputs/validation/cninfo_a_class_phase3_50_company_expansion/reports/a_class_phase3_50_company_expansion_summary.md` — Phase 3 live summary
- `outputs/validation/cninfo_a_class_phase3_50_company_expansion/reports/a_class_phase3_50_company_expansion_quality_report.csv` — Phase 3 live quality report
- `outputs/validation/cninfo_a_class_phase3_50_company_expansion/raw_metadata/` — Phase 3 raw_metadata JSON × **50**
- `plans/cninfo_a_class_phase3_50_company_merge_closure_review.md` — Phase 3 merge closure review（gate **PASS_WITH_CAVEAT**）
- `outputs/validation/cninfo_a_class_phase3_50_company_effective_merged_result.csv` — Phase 3 effective merged result（**49/50**）
- `outputs/validation/cninfo_a_class_phase3_50_company_unresolved_case_ledger.csv` — Phase 3 unresolved ledger（**1** · A3M017）
- `outputs/validation/cninfo_a_class_phase3_50_company_closure_metrics.csv` — Phase 3 closure metrics
- `outputs/validation/cninfo_a_class_phase3_50_company_closure_summary.md` — Phase 3 closure summary
- `outputs/validation/cninfo_a_class_phase3_50_company_post_closure_next_step_recommendation.md` — Phase 3 post-closure recommendation
- `plans/cninfo_a_class_phase3_50_company_final_commit_boundary_review.md` — Phase 3 commit boundary review（gate **READY_FOR_COMMIT_REVIEW**）
- `outputs/validation/cninfo_a_class_phase3_50_company_final_artifact_inventory.csv` — Phase 3 artifact inventory（**80 yes / 9 no**）
- `outputs/validation/cninfo_a_class_phase3_50_company_final_caveat_ledger.csv` — Phase 3 final caveat ledger
- `outputs/validation/cninfo_a_class_phase3_50_company_safe_to_commit_list.md` — Phase 3 safe-to-commit list
- `outputs/validation/cninfo_a_class_phase3_50_company_commit_boundary_summary.md` — Phase 3 commit boundary summary
- `plans/cninfo_a_class_phase3_a3m017_isolated_retry_plan.md` — A3M017 isolated retry plan（gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_a_class_phase3_a3m017_isolated_retry_universe.csv` — A3M017 retry universe（**1** row）
- `outputs/validation/cninfo_a_class_phase3_a3m017_isolated_retry_approval_checklist.md` — A3M017 retry approval checklist（**NOT APPROVED**）
- `plans/cninfo_a_class_phase3_a3m017_isolated_retry_command_draft.md` — A3M017 retry command draft（**NOT APPROVED**）
- `outputs/validation/cninfo_a_class_phase3_a3m017_isolated_retry_planning_summary.md` — A3M017 retry planning summary
- `outputs/validation/cninfo_a_class_phase3_a3m017_isolated_retry_next_step_recommendation.md` — A3M017 retry next-step recommendation
- `plans/cninfo_a_class_erad_scale_200_plan.md` — **Era D** A-class ~200 expansion plan
- `outputs/validation/cninfo_a_class_erad_scale_200_universe_draft.csv` — Era D universe（**200** = **50+150**）
- `outputs/validation/cninfo_a_class_erad_scale_200_approval_checklist.md` — Era D approval checklist（**NOT APPROVED live**）
- `plans/cninfo_a_class_erad_scale_200_command_draft.md` — Era D command draft
- `outputs/validation/cninfo_a_class_erad_scale_200_planning_summary.md` — Era D planning summary
- `outputs/validation/cninfo_a_class_erad_scale_200_runner_extension_summary.md` — Era D runner extension summary（**27/27 PASS** · **200/200 planned_ok**）
- `lab/test_cninfo_a_class_erad_scale_200_runner.py` — Era D runner tests
- `outputs/validation/cninfo_a_class_erad_scale_200/reports/a_class_erad_scale_200_dryrun_report.csv` — Era D dry-run report
- `outputs/validation/cninfo_a_class_erad_scale_200/reports/a_class_erad_scale_200_dryrun_summary.md` — Era D dry-run summary
- `outputs/validation/cninfo_a_class_erad_scale_200_live_path_summary.md` — Era D live path summary（**26/26 PASS** · mock CNINFO **0**）
- `lab/test_cninfo_a_class_erad_scale_200_live_path.py` — Era D live path tests
- `outputs/validation/cninfo_a_class_erad_scale_200_failed_case_triage_ledger.csv` — Era D failed-case triage ledger（**8** rows）
- `outputs/validation/cninfo_a_class_erad_scale_200_failed_case_triage_summary.md` — Era D triage summary（gate **`PASS_OFFLINE`**）
- `outputs/validation/cninfo_a_class_erad_scale_200_isolated_retry_universe_draft.csv` — Era D isolated retry universe（**7** cases）
- `plans/cninfo_a_class_erad_scale_200_isolated_retry_plan.md` — Era D isolated retry plan
- `plans/cninfo_a_class_erad_scale_200_isolated_retry_command_draft.md` — Era D isolated retry command draft（**NOT APPROVED live**）
- `outputs/validation/cninfo_a_class_erad_scale_200_isolated_retry_approval_checklist.md` — Era D retry approval checklist
- `outputs/validation/cninfo_a_class_erad_scale_200_failed_case_triage_next_step_recommendation.md` — Era D triage next-step
- `outputs/validation/cninfo_a_class_erad_scale_200_isolated_retry_runner_extension_summary.md` — Era D isolated retry runner summary（**21/21 PASS** · **7/7 planned_ok**）
- `lab/test_cninfo_a_class_erad_scale_200_isolated_retry_runner.py` — Era D isolated retry runner tests
- `outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/reports/a_class_erad_scale_200_failed_retry_dryrun_report.csv` — Era D failed-retry dry-run report
- `outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/reports/a_class_erad_scale_200_failed_retry_dryrun_summary.md` — Era D failed-retry dry-run summary
- `outputs/validation/cninfo_a_class_erad_scale_200_isolated_retry_live_path_summary.md` — Era D isolated retry live path summary（**18/18 PASS** · mock CNINFO **0**）
- `lab/test_cninfo_a_class_erad_scale_200_isolated_retry_live_path.py` — Era D isolated retry live path tests
- `outputs/validation/cninfo_a_class_phase2_retry_v3_planning_summary.md` — retry v3 规划摘要（gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_d_class_phase1_schema_freeze_approval_checklist.md` — Phase 1 schema freeze 人工批准检查清单
- `outputs/validation/cninfo_d_class_phase1_schema_freeze_approval_summary.md` — Phase 1 批准摘要（gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_d_class_phase1_freeze_v1_field_catalog.csv` — Phase 1 freeze v1 字段目录（**79** 行 · required=**49**）
- `outputs/validation/cninfo_d_class_phase1_freeze_v1_implementation_summary.md` — freeze v1 implementation 摘要（gate **PASS_OFFLINE**）
- `outputs/validation/cninfo_d_class_phase1_freeze_v1_lint_summary.md` — freeze v1 lint 摘要（**12/12 PASS**）
- `plans/cninfo_d_class_phase1_freeze_v1_implementation_plan.md` — signoff 后 offline implementation 计划（**已离线执行**）
- `plans/cninfo_d_class_event_quality_policy.md` — D 类 event retrieval/quality/lineage 口径
- `plans/cninfo_d_class_phase1_schema_freeze_review.md` — **Phase 1** D 类市场行为 schema freeze 评审（7 组件 · gate **READY_FOR_APPROVAL**）
- `plans/cninfo_d_class_event_object_schema.md` — D 类 `market_event` 信封与 timeline 对象设计
- `outputs/validation/cninfo_d_class_phase1_field_decision_matrix.csv` — Phase 1 字段决策矩阵（**79** 行）
- `outputs/validation/cninfo_d_class_phase1_schema_freeze_summary.md` — Phase 1 freeze 摘要
- `outputs/validation/cninfo_d_class_phase1_schema_lint_summary.md` — Phase 1 离线 lint（**10/10 PASS**）
- `fixtures/d_class/phase1/` — Phase 1 合成 schema 示例 fixture（**10** 文件：3 示例 + **DC001–DC007**）
- `lab/lint_cninfo_d_class_phase1_schema.py` — Phase 1 schema 离线 lint（无 CNINFO）
- `lab/lint_cninfo_d_class_phase1_freeze_v1.py` — Phase 1 freeze v1 离线 lint（**12/12 PASS** · 无 CNINFO）
- `lab/run_cninfo_d_class_phase1_ready_case_benchmark.py` — Phase 1 ready-case benchmark 离线 runner（**7/7 PASS** · 无 CNINFO）
- `lab/test_cninfo_d_class_phase1_ready_case_benchmark.py` — ready-case benchmark 测试（**8/8 PASS**）
- `outputs/validation/cninfo_d_class_phase1_ready_case_benchmark.csv` — ready-case benchmark 结果（**DC001–DC007**）
- `outputs/validation/cninfo_d_class_phase1_ready_case_benchmark_summary.md` — benchmark 摘要（gate **READY_FOR_REVIEW**）
- `outputs/validation/cninfo_d_class_phase1_tiny_live_approval_checklist.md` — Phase 1 tiny live 批准检查清单
- `outputs/validation/cninfo_d_class_phase1_tiny_live_universe.csv` — tiny live universe（**7** 家 · DLC001–DLC007）
- `outputs/validation/cninfo_d_class_phase1_tiny_live_approval_summary.md` — tiny live 批准摘要（gate **READY_FOR_APPROVAL**）
- `plans/cninfo_d_class_phase1_tiny_live_command_draft.md` — tiny live 命令草案（**NOT APPROVED**）
- `lab/run_cninfo_d_class_tiny_live_validation.py` — D-class tiny live runner（dry-run default · **0 CNINFO**）
- `lab/test_cninfo_d_class_tiny_live_validation_runner.py` — runner 测试（**10/10 PASS**）
- `outputs/validation/cninfo_d_class_tiny_live_runner_extension_summary.md` — runner extension 摘要（gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_d_class_tiny_live_validation/reports/d_class_tiny_live_dryrun_report.csv` — dry-run 报告（**7** cases）
- `outputs/validation/cninfo_d_class_tiny_live_validation/reports/d_class_tiny_live_dryrun_summary.md` — dry-run 摘要
- `outputs/validation/cninfo_d_class_tiny_live_validation/reports/d_class_tiny_live_report.csv` — tiny live 执行报告（**7** cases）
- `outputs/validation/cninfo_d_class_tiny_live_validation/reports/d_class_tiny_live_summary.md` — tiny live 执行摘要（gate **PASS_WITH_CAVEAT**）
- `outputs/validation/cninfo_d_class_tiny_live_validation/reports/d_class_tiny_live_quality_report.csv` — tiny live 质量报告
- `plans/cninfo_d_class_phase1_tiny_live_closure_review.md` — Phase 1 tiny live 收口评审
- `outputs/validation/cninfo_d_class_phase1_tiny_live_closure_metrics.csv` — tiny live 收口指标
- `plans/cninfo_d_class_phase1_expectation_calibration_note.md` — DLC003/DLC006 预期校准决策记录
- `outputs/validation/cninfo_d_class_phase1_tiny_live_closure_summary.md` — tiny live 收口摘要（gate **PASS_WITH_CAVEAT**）
- `plans/cninfo_d_class_dlc003_dlc006_calibration_review.md` — DLC003/DLC006 详细校准评审
- `outputs/validation/cninfo_d_class_dlc003_dlc006_calibration_decision_matrix.csv` — 校准决策矩阵（6 行 · 3 选项 × 2 cases）
- `outputs/validation/cninfo_d_class_phase1_tiny_live_universe_v2_draft.csv` — tiny live universe v2 草案（**2** placeholders）
- `plans/cninfo_d_class_tiny_live_v2_rerun_planning_note.md` — v2 rerun 规划（**NOT APPROVED**）
- `outputs/validation/cninfo_d_class_dlc003_dlc006_calibration_summary.md` — 校准决策包摘要（gate **READY_FOR_HUMAN_DECISION**）
- `plans/cninfo_d_class_phase1_boundary_signoff.md` — Phase 1 边界 signoff
- `outputs/validation/cninfo_d_class_phase1_boundary_metrics.csv` — Phase 1 边界指标
- `outputs/validation/cninfo_d_class_phase1_boundary_summary.md` — Phase 1 边界摘要（gate **PASS_WITH_CAVEAT**）
- `plans/cninfo_d_class_dlc003_dlc006_bounded_probe_extension_design.md` — DLC003/DLC006 有界 probe 扩展设计（Option B）
- `outputs/validation/cninfo_d_class_dlc003_dlc006_bounded_probe_matrix.csv` — 有界 probe 矩阵
- `plans/cninfo_d_class_tiny_live_v2_bounded_probe_command_draft.md` — v2 bounded probe 未来命令草案（**NOT APPROVED**）
- `plans/cninfo_d_class_tiny_live_v2_runner_modification_plan.md` — v2 runner 修改计划（未实现）
- `outputs/validation/cninfo_d_class_tiny_live_v2_bounded_probe_approval_checklist.md` — v2 bounded probe 批准清单
- `outputs/validation/cninfo_d_class_tiny_live_v2_bounded_probe_design_summary.md` — v2 bounded probe 设计摘要（gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_d_class_tiny_live_v2_bounded_probe_runner_extension_summary.md` — v2 runner 扩展摘要（tests **14/14**）
- `outputs/validation/cninfo_d_class_tiny_live_validation_v2/reports/d_class_tiny_live_v2_bounded_probe_report.csv` — v2 bounded probe 执行报告（CNINFO **40**）
- `outputs/validation/cninfo_d_class_tiny_live_validation_v2/reports/d_class_tiny_live_v2_bounded_probe_summary.md` — v2 执行摘要（gate **PASS_WITH_CAVEAT**）
- `plans/cninfo_d_class_tiny_live_v2_bounded_probe_closure_review.md` — v2 bounded probe 收口评审
- `outputs/validation/cninfo_d_class_dlc003_dlc006_v1_v2_evidence_matrix.csv` — DLC003/DLC006 v1-v2 证据矩阵
- `outputs/validation/cninfo_d_class_dlc003_dlc006_final_calibration_decision_summary.md` — 最终校准决策摘要
- `outputs/validation/cninfo_d_class_phase1_tiny_live_universe_calibration_proposal.csv` — universe 校准提案（**apply_now=false**）
- `outputs/validation/cninfo_d_class_tiny_live_v2_bounded_probe_closure_summary.md` — v2 收口摘要（closure gate **PASS_WITH_CAVEAT**）
- `outputs/validation/cninfo_d_class_dlc003_dlc006_calibration_human_signoff.md` — DLC003/DLC006 人工 signoff 记录
- `outputs/validation/cninfo_d_class_phase1_tiny_live_universe_calibrated.csv` — 校准后 tiny-live universe（DLC003/DLC006 → empty_but_valid）
- `outputs/validation/cninfo_d_class_dlc003_dlc006_calibration_application_summary.md` — 校准应用摘要（gate **HUMAN_SIGNED_OFF_WITH_CAVEAT**）
- `plans/cninfo_d_class_known_event_replacement_case_planning_note.md` — Option C 初始规划注记
- `plans/cninfo_d_class_known_event_replacement_case_plan.md` — Option C 完整规划
- `outputs/validation/cninfo_d_class_known_event_replacement_candidate_template.csv` — replacement 候选模板
- `outputs/validation/cninfo_d_class_tiny_live_replacement_universe_filled.csv` — replacement filled universe（DLC003R **688671** · DLC006R **301259**）
- `outputs/validation/cninfo_d_class_known_event_replacement_validation_approval_summary.md` — replacement validation approval 摘要（gate **READY_FOR_APPROVAL**）
- `plans/cninfo_d_class_known_event_replacement_runner_extension_design.md` — replacement runner 扩展设计
- `outputs/validation/cninfo_d_class_known_event_replacement_runner_extension_summary.md` — replacement runner 扩展摘要（gate **READY_FOR_APPROVAL** · tests **20/20**）
- `outputs/validation/cninfo_d_class_known_event_replacement_live_failure_review_summary.md` — replacement live failure review 摘要（gate **READY_FOR_HUMAN_DECISION**）
- `plans/cninfo_d_class_known_event_replacement_live_failure_review.md` — replacement live failure 完整评审
- `outputs/validation/cninfo_d_class_known_event_replacement_evidence_reconciliation_matrix.csv` — 证据 vs live 对账矩阵
- `plans/cninfo_d_class_known_event_targeted_probe_option_design.md` — targeted probe 选项设计（**NOT APPROVED**）
- `plans/cninfo_d_class_known_event_targeted_probe_plan.md` — targeted probe 完整规划（gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_d_class_known_event_targeted_probe_universe_draft.csv` — targeted probe universe draft（**2 rows** · DLC003R-T01 · DLC006R-T01）
- `outputs/validation/cninfo_d_class_known_event_targeted_probe_approval_checklist.md` — targeted probe 批准清单（**NOT APPROVED**）
- `plans/cninfo_d_class_known_event_targeted_probe_command_draft.md` — targeted probe 未来命令草案（**NOT APPROVED** · **Do not execute**）
- `plans/cninfo_d_class_known_event_targeted_probe_runner_extension_design.md` — targeted probe runner 扩展设计（**未实现**）
- `outputs/validation/cninfo_d_class_known_event_targeted_probe_planning_summary.md` — targeted probe 规划摘要（planning gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_d_class_known_event_targeted_probe_runner_extension_summary.md` — targeted probe runner 扩展摘要（extension gate **READY_FOR_APPROVAL** · tests **27/27** · dry-run **2/2**）
- `outputs/validation/cninfo_d_class_known_event_targeted_probe_live_implementation_summary.md` — targeted probe live 实现摘要（live implementation gate **READY_FOR_APPROVAL** · live-path tests **29/29**）
- `plans/cninfo_d_class_known_event_targeted_probe_closure_review.md` — targeted probe closure 评审（closure gate **READY_FOR_HUMAN_DECISION**）
- `outputs/validation/cninfo_d_class_known_event_targeted_probe_closure_summary.md` — targeted probe closure 摘要
- `outputs/validation/cninfo_d_class_known_event_targeted_probe_effective_result_ledger.csv` — targeted probe 有效结果台账（**2 rows**）
- `outputs/validation/cninfo_d_class_dlc006r_targeted_probe_failure_review_ledger.csv` — DLC006R-T01 failure review 台账
- `outputs/validation/cninfo_d_class_known_event_targeted_probe_closure_metrics.csv` — targeted probe closure 指标
- `plans/cninfo_d_class_dlc003r_positive_structured_evidence_note.md` — DLC003R 正向结构化证据注记
- `plans/cninfo_d_class_dlc006r_human_decision_package.md` — DLC006R 人工决策包
- `plans/cninfo_d_class_dlc006r_human_decision_record.md` — DLC006R 人工决策记录（**Option A + Option C**）
- `plans/cninfo_d_class_dlc006r_disclosure_evidence_reconciliation_note.md` — DLC006R 披露证据谱系注记
- `outputs/validation/cninfo_d_class_known_event_replacement_final_effective_status_ledger.csv` — replacement 最终有效状态台账
- `outputs/validation/cninfo_d_class_known_event_replacement_final_closure_summary.md` — replacement 最终收口摘要（gate **PASS_WITH_CAVEAT**）
- `outputs/validation/cninfo_d_class_known_event_replacement_final_closure_metrics.csv` — replacement 最终收口指标
- `plans/cninfo_d_class_known_event_replacement_boundary_review.md` — replacement 最终边界评审（gate **READY_FOR_COMMIT_REVIEW**）
- `outputs/validation/cninfo_d_class_known_event_replacement_final_artifact_inventory.csv` — replacement 最终 artifact 清单
- `outputs/validation/cninfo_d_class_known_event_replacement_final_caveat_ledger.csv` — replacement 最终 caveat 台账
- `outputs/validation/cninfo_d_class_known_event_replacement_safe_to_commit_list.md` — replacement safe-to-commit 清单
- `outputs/validation/cninfo_d_class_known_event_replacement_boundary_summary.md` — replacement 边界评审摘要
- `outputs/validation/cninfo_d_class_known_event_replacement_push_status.md` — replacement push 状态摘要（commit **`389cd9c`** on **`origin/main`**）
- `plans/cninfo_d_class_next_component_planning.md` — next component 离线规划（gate **READY_FOR_HUMAN_DECISION**）
- `outputs/validation/cninfo_d_class_next_component_candidate_matrix.csv` — next component 候选矩阵（**7** 组件）
- `outputs/validation/cninfo_d_class_next_component_recommendation.md` — next component 推荐（**margin_trading**）
- `outputs/validation/cninfo_d_class_next_component_planning_summary.md` — next component 规划摘要
- `plans/cninfo_d_class_margin_trading_first_slice_plan.md` — margin_trading 第一切片规划（gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_d_class_margin_trading_first_slice_universe_draft.csv` — margin_trading 第一切片 universe（**5** 行）
- `outputs/validation/cninfo_d_class_margin_trading_first_slice_approval_checklist.md` — margin_trading 第一切片批准清单
- `plans/cninfo_d_class_margin_trading_first_slice_command_draft.md` — margin_trading 第一切片命令草案（**NOT APPROVED**）
- `outputs/validation/cninfo_d_class_margin_trading_first_slice_approval_summary.md` — margin_trading 第一切片批准包摘要
- `outputs/validation/cninfo_d_class_margin_trading_first_slice_runner_extension_summary.md` — margin_trading runner 扩展摘要（dry-run **5/5** · tests **21/21**）
- `outputs/validation/cninfo_d_class_margin_trading_first_slice_live_path_summary.md` — margin_trading live path 离线实现摘要（tests **19/19** · **NOT APPROVED live**）
- `lab/test_cninfo_d_class_margin_trading_first_slice_runner.py` — margin_trading first-slice runner 测试（**21/21**）
- `lab/test_cninfo_d_class_margin_trading_first_slice_live_path.py` — margin_trading first-slice live-path 测试（**19/19** · mock only）
- `plans/cninfo_d_class_margin_trading_first_slice_closure_review.md` — margin_trading first-slice closure 评审（closure gate **PASS_WITH_CAVEAT**）
- `outputs/validation/cninfo_d_class_margin_trading_first_slice_closure_summary.md` — margin_trading first-slice closure 摘要
- `outputs/validation/cninfo_d_class_margin_trading_first_slice_closure_metrics.csv` — margin_trading first-slice closure 指标
- `outputs/validation/cninfo_d_class_margin_trading_first_slice_effective_result.csv` — margin_trading first-slice effective result（**5 rows**）
- `outputs/validation/cninfo_d_class_margin_trading_first_slice_final_caveat_ledger.csv` — margin_trading first-slice caveat 台账
- `outputs/validation/cninfo_d_class_margin_trading_first_slice_post_closure_next_step_recommendation.md` — margin_trading post-closure 下一步建议
- `plans/cninfo_d_class_margin_trading_first_slice_commit_boundary_review.md` — margin_trading first-slice commit boundary 评审（gate **READY_FOR_COMMIT_REVIEW**）
- `outputs/validation/cninfo_d_class_margin_trading_first_slice_commit_boundary_summary.md` — margin_trading commit boundary 摘要
- `outputs/validation/cninfo_d_class_margin_trading_first_slice_final_artifact_inventory.csv` — margin_trading artifact 清单（**34 yes / 15 no**）
- `outputs/validation/cninfo_d_class_margin_trading_first_slice_commit_caveat_ledger.csv` — margin_trading commit caveat 台账
- `outputs/validation/cninfo_d_class_margin_trading_first_slice_safe_to_commit_list.md` — margin_trading safe-to-commit 清单
- `plans/cninfo_d_class_disclosure_schedule_first_slice_closure_review.md` — disclosure_schedule first-slice closure（commit **`d37ce0a`**）
- `outputs/validation/cninfo_d_class_disclosure_schedule_first_slice_commit_review_summary.md` — disclosure_schedule post-commit 摘要
- `plans/cninfo_d_class_erad_next_component_planning.md` — Era D 下一组件规划（primary **`block_trade`**）
- `outputs/validation/cninfo_d_class_erad_next_component_candidate_matrix.csv` — Era D 候选矩阵
- `outputs/validation/cninfo_d_class_erad_next_component_recommendation.md` — Era D 推荐
- `outputs/validation/cninfo_d_class_erad_next_component_planning_summary.md` — Era D 规划摘要
- `plans/cninfo_d_class_block_trade_first_slice_plan.md` — block_trade 第一切片规划（gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_d_class_block_trade_first_slice_universe_draft.csv` — block_trade universe（**5** 行 · DBT001–DBT005）
- `outputs/validation/cninfo_d_class_block_trade_first_slice_approval_checklist.md` — block_trade 批准清单（**NOT APPROVED**）
- `plans/cninfo_d_class_block_trade_first_slice_command_draft.md` — block_trade 命令草案（**NOT APPROVED**）
- `outputs/validation/cninfo_d_class_block_trade_first_slice_approval_summary.md` — block_trade 批准包摘要
- `lab/test_cninfo_d_class_block_trade_first_slice_runner.py` — block_trade runner 测试（**19/19**）
- `lab/test_cninfo_d_class_block_trade_first_slice_live_path.py` — block_trade live-path 测试（**18/18** · mock only）
- `outputs/validation/cninfo_d_class_block_trade_first_slice_runner_extension_summary.md` — runner 扩展摘要（dry-run **5/5**）
- `outputs/validation/cninfo_d_class_block_trade_first_slice_live_path_summary.md` — live-path 摘要（mock **18/18**）
- `outputs/validation/cninfo_d_class_block_trade_first_slice_isolated_live_validation_summary.md` — isolated live 摘要（CNINFO **5** · **4/5**）
- `outputs/validation/cninfo_d_class_block_trade_first_slice_closure_summary.md` — closure 摘要（gate **`PASS_WITH_CAVEAT`**）
- `outputs/validation/cninfo_d_class_block_trade_first_slice_closure_decision.md` — closure 决策
- `outputs/validation/cninfo_d_class_block_trade_first_slice_unresolved_case_ledger.csv` — unresolved ledger（DBT002）
- `outputs/validation/cninfo_d_class_block_trade_first_slice_post_closure_next_step_recommendation.md` — post-closure 建议
- `outputs/validation/cninfo_d_class_block_trade_first_slice_commit_boundary_summary.md` — commit boundary 摘要（gate **`READY_FOR_COMMIT_REVIEW`**）
- `outputs/validation/cninfo_d_class_block_trade_first_slice_safe_to_commit_list.md` — safe-to-commit（**~27** paths）
- `outputs/validation/cninfo_d_class_block_trade_first_slice_do_not_commit_list.md` — do-not-commit 清单
- `outputs/validation/cninfo_d_class_block_trade_first_slice_commit_message_draft.md` — commit message 草案
- `outputs/validation/cninfo_d_class_block_trade_first_slice_commit_status.md` — explicit-path commit 状态（**`a12298b`** · **无 push**）
- `outputs/validation/cninfo_d_class_block_trade_first_slice/reports/d_class_block_trade_first_slice_live_report.csv` — live 报告
- `outputs/validation/cninfo_d_class_block_trade_first_slice/reports/d_class_block_trade_first_slice_dryrun_report.csv` — dry-run 报告
- `outputs/validation/cninfo_d_class_block_trade_first_slice/reports/d_class_block_trade_first_slice_dryrun_summary.md` — dry-run 摘要
- `lab/test_cninfo_d_class_known_event_targeted_probe_runner.py` — targeted probe runner 测试（**27/27**）
- `lab/test_cninfo_d_class_known_event_targeted_probe_live_path.py` — targeted probe live-path 测试（**29/29** · mock only）
- `lab/test_cninfo_d_class_known_event_replacement_live_path.py` — replacement live-path 测试（**22/22**）
- `plans/cninfo_d_class_known_event_replacement_validation_command_draft.md` — 未来 validation 命令草案（**NOT APPROVED**）
- `outputs/validation/cninfo_d_class_known_event_replacement_approval_checklist.md` — replacement 批准清单
- `outputs/validation/cninfo_d_class_known_event_replacement_planning_summary.md` — replacement 规划摘要（gate **READY_FOR_HUMAN_CANDIDATES**）
- `plans/cninfo_d_class_known_event_candidate_intake_instructions.md` — 候选 intake 说明
- `outputs/validation/cninfo_d_class_known_event_candidate_intake_schema.csv` — intake 校验 schema
- `lab/validate_cninfo_d_class_known_event_candidates.py` — 候选 intake 离线校验脚本
- `outputs/validation/cninfo_d_class_known_event_candidate_validation_report.csv` — intake 校验报告
- `outputs/validation/cninfo_d_class_known_event_candidate_validation_summary.md` — intake 校验摘要
- `outputs/validation/cninfo_d_class_known_event_candidate_intake_summary.md` — intake 完成摘要（gate **HUMAN_CANDIDATE_VALIDATED**）
- `plans/cninfo_d_class_market_data_architecture_plan.md` — **Phase 0** D 类市场行为结构化数据层架构计划（event/metric timeline · 非 company profile）
- `plans/cninfo_d_class_source_discovery_plan.md` — **Phase 0** D 类 7 源 source discovery 离线策略
- `outputs/validation/cninfo_d_class_readiness_matrix.csv` — D 类 Phase 0 readiness 矩阵（**12** 组件 · gate **DESIGN_STARTED**）
- `outputs/validation/cninfo_d_class_initial_planning_summary.md` — D 类规划摘要
- `plans/cninfo_b_class_announcement_metadata_architecture_plan.md` — **Phase 0** B 类公告元数据层架构计划（metadata + PDF URL lineage · 不下载 PDF）
- `plans/cninfo_b_class_source_discovery_plan.md` — **Phase 0** B 类 source discovery 离线策略
- `outputs/validation/cninfo_b_class_readiness_matrix.csv` — B 类 Phase 1 readiness 矩阵
- `outputs/validation/cninfo_b_class_initial_planning_summary.md` — B 类规划摘要（gate **DESIGN_STARTED**）
- `outputs/validation/cninfo_b_class_existing_artifact_inventory.csv` — A/B 既有产物离线盘点（**72** 条）
- `outputs/validation/cninfo_b_class_existing_artifact_inventory_summary.md` — 盘点摘要（gate **PASS**）
- `outputs/validation/cninfo_b_class_endpoint_candidate_table.csv` — **Phase 0/1** endpoint 候选表（**7** 条 · live **not_run**）
- `outputs/validation/cninfo_b_class_phase1_minimum_fields.csv` — Phase 1 最小字段目录（**46** 字段）
- `plans/cninfo_b_class_phase1_schema_freeze_review.md` — Phase 1 schema freeze 评审（gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_b_class_phase1_schema_freeze_review_summary.md` — freeze review 摘要
- `outputs/validation/cninfo_b_class_source_registry_alignment_report.csv` — registry 与 endpoint 对齐报告
- `outputs/validation/cninfo_b_class_phase1_schema_freeze_manual_review_checklist.md` — Phase 1 人工评审清单
- `outputs/validation/cninfo_b_class_phase1_field_decision_matrix.csv` — Phase 1 字段决策矩阵（草案）
- `outputs/validation/cninfo_b_class_phase1_endpoint_decision_matrix.csv` — Phase 1 endpoint 决策矩阵（草案）
- `plans/cninfo_b_class_phase1_schema_freeze_approval_draft.md` — Phase 1 freeze 批准/signoff 记录
- `outputs/validation/cninfo_b_class_phase1_schema_freeze_signoff_summary.md` — signoff 摘要（gate **READY_FOR_IMPLEMENTATION**）
- `plans/cninfo_b_class_phase1_freeze_v1_implementation_plan.md` — freeze v1 实施计划
- `outputs/validation/cninfo_b_class_phase1_freeze_v1_field_catalog.csv` — freeze v1 字段目录（**15** required）
- `outputs/validation/cninfo_b_class_phase1_freeze_v1_endpoint_catalog.csv` — freeze v1 endpoint 目录
- `fixtures/b_class/phase1/` — Phase1 离线 fixture 骨架（**3** 文件）
- `lab/lint_cninfo_b_class_phase1_freeze_v1.py` — Phase1 freeze v1 离线 lint（**9/9 PASS**）
- `outputs/validation/cninfo_b_class_phase1_freeze_v1_lint_summary.md` — lint 摘要
- `outputs/validation/cninfo_b_class_phase1_ready_case_benchmark.csv` — ready-case benchmark（**RC001–RC005**）
- `outputs/validation/cninfo_b_class_phase1_ready_case_benchmark_summary.md` — benchmark 摘要（gate **READY_FOR_REVIEW**）
- `lab/run_cninfo_b_class_phase1_ready_case_benchmark.py` — ready-case benchmark 离线 runner（**5/5 PASS**）
- `outputs/validation/cninfo_b_class_phase1_ready_case_benchmark_execution_report.csv` — benchmark 离线执行报告
- `outputs/validation/cninfo_b_class_phase1_ready_case_benchmark_execution_summary.md` — benchmark 离线执行摘要（execution gate **PASS_OFFLINE**）
- `outputs/validation/cninfo_b_class_phase1_tiny_live_validation_approval_checklist.md` — tiny live 最终批准检查清单
- `outputs/validation/cninfo_b_class_phase1_tiny_live_validation_universe.csv` — tiny live universe（**5** 家 · TLC001–TLC005）
- `plans/cninfo_b_class_phase1_tiny_live_validation_command_draft.md` — tiny live 命令草案（**NOT APPROVED**）
- `lab/run_cninfo_b_class_tiny_live_validation.py` — tiny live metadata runner（dry-run default · **11/11 tests**）
- `lab/test_cninfo_b_class_tiny_live_validation_runner.py` — runner 测试（无 CNINFO）
- `outputs/validation/cninfo_b_class_tiny_live_validation_runner_extension_summary.md` — runner 扩展摘要（gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_b_class_tiny_live_validation_summary.md` — tiny live 执行摘要（gate **PASS_WITH_CAVEAT**）
- `outputs/validation/cninfo_b_class_tiny_live_validation_report.csv` — tiny live 报告
- `outputs/validation/cninfo_b_class_tlc002_failure_analysis.md` — TLC002 失败离线分析
- `plans/cninfo_b_class_tlc002_isolated_retry_plan.md` — TLC002 isolated retry 计划
- `outputs/validation/cninfo_b_class_tlc002_retry_checklist.md` — TLC002 retry 检查清单
- `plans/cninfo_b_class_tlc002_retry_command_draft.md` — TLC002 retry 命令草案（**NOT APPROVED**）
- `lab/run_cninfo_b_class_tlc002_retry.py` — TLC002 isolated retry runner（dry-run default · **10/10 tests**）
- `lab/test_cninfo_b_class_tlc002_retry_runner.py` — TLC002 retry runner 测试
- `outputs/validation/cninfo_b_class_tlc002_retry_execution_checklist.md` — TLC002 retry 执行清单
- `plans/cninfo_b_class_phase2_expansion_plan.md` — Phase 2 expansion 规划
- `outputs/validation/cninfo_b_class_phase2_candidate_universe_design.csv` — Phase 2 候选 universe bucket 设计
- `outputs/validation/cninfo_b_class_phase2_expansion_universe_draft.csv` — Phase 2 20 家公司 universe draft
- `plans/cninfo_b_class_phase2_expansion_command_draft.md` — Phase 2 expansion 命令草案（**NOT APPROVED**）
- `outputs/validation/cninfo_b_class_phase2_expansion_approval_checklist.md` — Phase 2 expansion 批准检查清单
- `outputs/validation/cninfo_b_class_phase2_expansion_approval_summary.md` — Phase 2 expansion 批准摘要（gate **READY_FOR_APPROVAL**）
- `lab/run_cninfo_b_class_phase2_expansion_validation.py` — Phase 2 expansion runner（dry-run default · **12/12 tests**）
- `lab/test_cninfo_b_class_phase2_expansion_runner.py` — Phase 2 expansion runner 测试
- `outputs/validation/cninfo_b_class_phase2_expansion_runner_extension_summary.md` — Phase 2 runner 扩展摘要（runner gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_b_class_phase2_expansion_closure_metrics.csv` — Phase 2 收口指标（**20/20 acceptable**）
- `outputs/validation/cninfo_b_class_phase2_expansion_closure_summary.md` — Phase 2 收口摘要（closure gate **PASS_WITH_CAVEAT**）
- `plans/cninfo_b_class_phase2_expansion_closure_review.md` — Phase 2 收口评审
- `plans/cninfo_b_class_phase25_expansion_plan.md` — Phase 2.5 expansion 规划（**50** 家）
- `outputs/validation/cninfo_b_class_phase25_candidate_universe_design.csv` — Phase 2.5 候选 universe bucket 设计
- `outputs/validation/cninfo_b_class_phase25_expansion_universe_draft.csv` — Phase 2.5 50 家公司 universe draft
- `plans/cninfo_b_class_phase25_expansion_command_draft.md` — Phase 2.5 expansion 命令草案（**NOT APPROVED**）
- `outputs/validation/cninfo_b_class_phase25_expansion_approval_checklist.md` — Phase 2.5 expansion 批准检查清单
- `outputs/validation/cninfo_b_class_phase25_expansion_approval_summary.md` — Phase 2.5 expansion 批准摘要（gate **READY_FOR_APPROVAL**）
- `lab/run_cninfo_b_class_phase25_expansion_validation.py` — Phase 2.5 / Phase 3 / **Era D ~200** expansion runner（dry-run default · Phase 2.5 **15/15** · Era D **15/15** tests）
- `lab/test_cninfo_b_class_phase25_expansion_runner.py` — Phase 2.5 expansion runner 测试
- `outputs/validation/cninfo_b_class_phase25_expansion_runner_extension_summary.md` — Phase 2.5 runner 扩展摘要（runner gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_b_class_phase25_expansion/reports/b_class_phase25_expansion_dryrun_report.csv` — Phase 2.5 dry-run 报告（**50/50 planned_ok**）
- `outputs/validation/cninfo_b_class_phase25_expansion/reports/b_class_phase25_expansion_dryrun_summary.md` — Phase 2.5 dry-run 摘要（CNINFO **0**）
- `outputs/validation/cninfo_b_class_phase25_expansion/reports/b_class_phase25_expansion_report.csv` — Phase 2.5 live 执行报告（**45/50 acceptable**）
- `outputs/validation/cninfo_b_class_phase25_expansion/reports/b_class_phase25_expansion_summary.md` — Phase 2.5 live 执行摘要（execution gate **PASS_WITH_CAVEAT**）
- `outputs/validation/cninfo_b_class_phase25_expansion/reports/b_class_phase25_expansion_quality_report.csv` — Phase 2.5 quality 报告
- `plans/cninfo_b_class_phase25_expansion_closure_review.md` — Phase 2.5 收口评审
- `outputs/validation/cninfo_b_class_phase25_failed_case_triage.csv` — Phase 2.5 失败 case 分类（**5** 例）
- `plans/cninfo_b_class_phase25_failed_retry_planning_note.md` — Phase 2.5 isolated retry 规划（**NOT APPROVED**）
- `outputs/validation/cninfo_b_class_phase25_expansion_closure_metrics.csv` — Phase 2.5 收口指标（**45/50 acceptable**）
- `outputs/validation/cninfo_b_class_phase25_expansion_closure_summary.md` — Phase 2.5 收口摘要（closure gate **PASS_WITH_CAVEAT**）
- `plans/cninfo_b_class_phase25_next_step_recommendation.md` — Phase 2.5 下一步建议
- `outputs/validation/cninfo_b_class_phase25_failed_retry_universe.csv` — Phase 2.5 失败 case retry universe（**5** 家）
- `plans/cninfo_b_class_phase25_failed_retry_command_draft.md` — Phase 2.5 failed retry 命令草案（**NOT APPROVED**）
- `outputs/validation/cninfo_b_class_phase25_failed_retry_approval_checklist.md` — Phase 2.5 failed retry 批准检查清单
- `outputs/validation/cninfo_b_class_phase25_failed_retry_approval_summary.md` — Phase 2.5 failed retry 批准摘要
- `outputs/validation/cninfo_b_class_phase25_failed_retry_package_summary.md` — Phase 2.5 failed retry 包摘要（package gate **READY_FOR_APPROVAL**）
- `lab/test_cninfo_b_class_phase25_failed_retry_runner.py` — Phase 2.5 failed retry runner 测试（**14/14 PASS**）
- `outputs/validation/cninfo_b_class_phase25_failed_retry/reports/b_class_phase25_failed_retry_dryrun_report.csv` — Phase 2.5 failed retry dry-run 报告
- `outputs/validation/cninfo_b_class_phase25_failed_retry/reports/b_class_phase25_failed_retry_report.csv` — Phase 2.5 failed retry live 报告（**5/5 found**）
- `outputs/validation/cninfo_b_class_phase25_failed_retry/reports/b_class_phase25_failed_retry_summary.md` — Phase 2.5 failed retry 执行摘要（execution gate **PASS_WITH_CAVEAT**）
- `outputs/validation/cninfo_b_class_phase25_failed_retry/reports/b_class_phase25_failed_retry_quality_report.csv` — Phase 2.5 failed retry quality 报告
- `plans/cninfo_b_class_phase25_failed_retry_closure_review.md` — Phase 2.5 failed retry 收口评审
- `outputs/validation/cninfo_b_class_phase25_effective_merged_result.csv` — Phase 2.5 合并有效结果（**50/50**）
- `outputs/validation/cninfo_b_class_phase25_failed_retry_closure_metrics.csv` — Phase 2.5 failed retry 收口指标
- `outputs/validation/cninfo_b_class_phase25_failed_retry_closure_summary.md` — Phase 2.5 failed retry 收口摘要（closure gate **PASS_WITH_CAVEAT**）
- `plans/cninfo_b_class_phase25_post_retry_next_step_recommendation.md` — Phase 2.5 post-retry 下一步建议
- `plans/cninfo_b_class_phase3_100_expansion_plan.md` — Phase 3 100-company expansion 规划（**离线 only** · **NOT APPROVED**）
- `outputs/validation/cninfo_b_class_phase3_100_candidate_universe_design.csv` — Phase 3 候选 universe bucket 设计
- `outputs/validation/cninfo_b_class_phase3_100_universe_draft.csv` — Phase 3 100 家公司 universe draft（B3E001–B3E100）
- `plans/cninfo_b_class_phase3_100_command_draft.md` — Phase 3 expansion 命令草案（**NOT APPROVED**）
- `outputs/validation/cninfo_b_class_phase3_100_approval_checklist.md` — Phase 3 expansion 批准检查清单
- `outputs/validation/cninfo_b_class_phase3_100_planning_summary.md` — Phase 3 planning 摘要（planning gate **READY_FOR_APPROVAL**）
- `lab/test_cninfo_b_class_phase3_100_runner.py` — Phase 3 100-company runner 测试（**20/20 PASS**）
- `outputs/validation/cninfo_b_class_phase3_100_runner_extension_summary.md` — Phase 3 runner 扩展摘要（runner gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_b_class_phase3_100_expansion/reports/b_class_phase3_100_dryrun_report.csv` — Phase 3 dry-run 报告（**100/100 planned_ok**）
- `outputs/validation/cninfo_b_class_phase3_100_expansion/reports/b_class_phase3_100_dryrun_summary.md` — Phase 3 dry-run 摘要（CNINFO **0**）
- `outputs/validation/cninfo_b_class_phase3_100_expansion/reports/b_class_phase3_100_report.csv` — Phase 3 live 执行报告（**1/100 acceptable**）
- `outputs/validation/cninfo_b_class_phase3_100_expansion/reports/b_class_phase3_100_summary.md` — Phase 3 live 执行摘要（execution gate **FAIL_REVIEW_REQUIRED**）
- `outputs/validation/cninfo_b_class_phase3_100_expansion/reports/b_class_phase3_100_quality_report.csv` — Phase 3 quality 报告
- `plans/cninfo_b_class_phase3_100_failed_case_triage_review.md` — Phase 3 失败 case 分类评审（triage gate **READY_FOR_REVIEW**）
- `outputs/validation/cninfo_b_class_phase3_100_failed_case_triage.csv` — Phase 3 失败 case 分类（**99** 例）
- `outputs/validation/cninfo_b_class_phase3_100_success_hold_ledger.csv` — Phase 3 成功 case 保留台账（B3E087 · rerun **no**）
- `outputs/validation/cninfo_b_class_phase3_100_failed_retry_universe.csv` — Phase 3 isolated retry universe（**99** 家）
- `outputs/validation/cninfo_b_class_phase3_100_failed_retry/reports/b_class_phase3_100_failed_retry_dryrun_report.csv` — Phase 3 failed retry dry-run report（**99/99 planned_ok**）
- `outputs/validation/cninfo_b_class_phase3_100_failed_retry/reports/b_class_phase3_100_failed_retry_dryrun_summary.md` — Phase 3 failed retry dry-run summary
- `outputs/validation/cninfo_b_class_phase3_100_failed_retry_runner_extension_summary.md` — Phase 3 failed retry runner extension summary（runner extension gate **READY_FOR_APPROVAL**）
- `lab/test_cninfo_b_class_phase3_100_failed_retry_live_path.py` — Phase 3 failed retry live-path tests（**24/24 PASS** · mock only）
- `outputs/validation/cninfo_b_class_phase3_100_failed_retry_closure_summary.md` — Phase 3 failed retry closure summary（closure gate **PASS_WITH_CAVEAT_NETWORK_UNRESOLVED**）
- `outputs/validation/cninfo_b_class_phase3_100_effective_merged_result.csv` — Phase 3 effective merged result（**9/100 accepted** · **91 unresolved**）
- `plans/cninfo_b_class_phase3_100_failed_retry_closure_review.md` — Phase 3 failed retry closure review
- `plans/cninfo_b_class_phase3_100_ep002_reachability_precheck_plan.md` — Phase 3 EP002 reachability precheck 规划（**NOT APPROVED**）
- `outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck_candidates.csv` — EP002 precheck 候选（**8** 例）
- `outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck_planning_summary.md` — EP002 precheck 规划摘要（planning gate **READY_FOR_APPROVAL**）
- `lab/run_cninfo_b_class_phase3_100_ep002_reachability_precheck.py` — Phase 3 EP002 reachability precheck runner
- `lab/test_cninfo_b_class_phase3_100_ep002_reachability_precheck_runner.py` — EP002 precheck runner 测试（**26/26 PASS**）
- `outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck_runner_summary.md` — EP002 precheck runner 摘要（runner gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck/reports/b_class_phase3_100_ep002_reachability_precheck_dryrun_report.csv` — EP002 precheck dry-run 报告（**8/8 planned_ok**）
- `outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck/reports/b_class_phase3_100_ep002_reachability_precheck_dryrun_summary.md` — EP002 precheck dry-run 摘要（CNINFO **0**）
- `outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck/reports/b_class_phase3_100_ep002_reachability_precheck_report.csv` — EP002 precheck live 报告（**8/8 orgId resolved**）
- `outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck/reports/b_class_phase3_100_ep002_reachability_precheck_summary.md` — EP002 precheck live 摘要（execution gate **PASS_WITH_CAVEAT**）
- `outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck/reports/b_class_phase3_100_ep002_reachability_precheck_quality_report.csv` — EP002 precheck quality 报告（CNINFO **8** · PDF **0**）
- `plans/cninfo_b_class_phase3_100_retry_v2_isolated_plan.md` — Phase 3 retry_v2 isolated 规划（**NOT APPROVED**）
- `outputs/validation/cninfo_b_class_phase3_100_retry_v2_universe.csv` — retry_v2 universe（**91** 例 · B3R2_001–B3R2_091）
- `outputs/validation/cninfo_b_class_phase3_100_retry_v2_approval_checklist.md` — retry_v2 批准检查清单
- `plans/cninfo_b_class_phase3_100_retry_v2_command_draft.md` — retry_v2 命令草案（**NOT APPROVED**）
- `plans/cninfo_b_class_phase3_100_retry_v2_runner_extension_design.md` — retry_v2 runner extension 设计（design only）
- `outputs/validation/cninfo_b_class_phase3_100_retry_v2_planning_summary.md` — retry_v2 规划摘要（planning gate **READY_FOR_APPROVAL**）
- `lab/test_cninfo_b_class_phase3_100_retry_v2_runner.py` — retry_v2 runner 测试（**26/26 PASS**）
- `outputs/validation/cninfo_b_class_phase3_100_retry_v2_runner_extension_summary.md` — retry_v2 runner extension 摘要（runner extension gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_b_class_phase3_100_retry_v2/reports/b_class_phase3_100_retry_v2_dryrun_report.csv` — retry_v2 dry-run 报告（**91/91 planned_ok**）
- `outputs/validation/cninfo_b_class_phase3_100_retry_v2/reports/b_class_phase3_100_retry_v2_dryrun_summary.md` — retry_v2 dry-run 摘要（CNINFO **0**）
- `lab/test_cninfo_b_class_phase3_100_retry_v2_live_path.py` — retry_v2 live-path 测试（**24/24 PASS** · mock only）
- `outputs/validation/cninfo_b_class_phase3_100_retry_v2_live_path_summary.md` — retry_v2 live path 实现摘要（live path gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_b_class_phase3_100_retry_v2/reports/b_class_phase3_100_retry_v2_report.csv` — retry_v2 live 报告（**91/91 acceptable**）
- `outputs/validation/cninfo_b_class_phase3_100_retry_v2/reports/b_class_phase3_100_retry_v2_summary.md` — retry_v2 live 摘要（execution gate **PASS_WITH_CAVEAT** · CNINFO **182**）
- `outputs/validation/cninfo_b_class_phase3_100_retry_v2/reports/b_class_phase3_100_retry_v2_quality_report.csv` — retry_v2 quality 报告（PDF **0**）
- `plans/cninfo_b_class_phase3_100_retry_v2_merge_closure_review.md` — retry_v2 merge closure 评审（closure gate **PASS_WITH_CAVEAT**）
- `outputs/validation/cninfo_b_class_phase3_100_effective_merged_result_v2.csv` — Phase 3 effective merged result v2（**100/100 accepted**）
- `outputs/validation/cninfo_b_class_phase3_100_retry_v2_recovered_case_ledger.csv` — retry_v2 recovered ledger（**91** 例）
- `outputs/validation/cninfo_b_class_phase3_100_retry_v2_closure_metrics.csv` — retry_v2 closure 指标
- `outputs/validation/cninfo_b_class_phase3_100_retry_v2_closure_summary.md` — retry_v2 closure 摘要
- `plans/cninfo_b_class_phase3_100_post_retry_v2_next_step_recommendation.md` — post retry_v2 路径建议
- `plans/cninfo_b_class_phase3_100_final_commit_boundary_review.md` — Phase 3 final commit boundary 评审（gate **READY_FOR_COMMIT_REVIEW**）
- `outputs/validation/cninfo_b_class_phase3_100_final_artifact_inventory.csv` — Phase 3 artifact inventory（**763 yes · 12 no**）
- `outputs/validation/cninfo_b_class_phase3_100_final_caveat_ledger.csv` — Phase 3 final caveat ledger
- `outputs/validation/cninfo_b_class_phase3_100_safe_to_commit_list.md` — Phase 3 safe-to-commit list
- `outputs/validation/cninfo_b_class_phase3_100_commit_boundary_summary.md` — Phase 3 commit boundary summary
- **Phase 3 commit** — **`f3f6077`** · **578 files**
- `outputs/validation/cninfo_b_class_phase3_100_retry_v2_test_cleanup_hardening_summary.md` — test cleanup hardening
- `outputs/validation/cninfo_b_class_phase3_100_retry_v2_missing_artifact_recovery_summary.md` — recovery live **185/185**
- `outputs/validation/cninfo_b_class_phase3_100_retry_v2_supplemental_commit_path_list.csv` — supplemental path list
- **Era D B-class ~200 expansion** — `plans/cninfo_b_class_erad_scale_200_plan.md` · universe [cninfo_b_class_erad_scale_200_universe_draft.csv](outputs/validation/cninfo_b_class_erad_scale_200_universe_draft.csv)（**200** = **100 retained** + **100 new**）· [runner extension summary](outputs/validation/cninfo_b_class_erad_scale_200_runner_extension_summary.md) · live **198/200** · CNINFO **397**
- **Era D B-class ~200 explicit-path commit** — **`e738fa9`** · **30 files** · [commit status](outputs/validation/cninfo_b_class_erad_scale_200_commit_status.md)（gate **`PASS_WITH_CAVEAT`** · **NOT pushed** · bulk raw_metadata/quality excluded）
- `lab/test_cninfo_b_class_erad_scale_200_runner.py` — Era D ~200 runner 测试（**15/15 PASS** · CNINFO **0**）
- `lab/test_cninfo_b_class_erad_scale_200_live_path.py` — Era D ~200 live-path 测试（**17/17 PASS** · mock CNINFO **0**）
- `plans/cninfo_b_class_erad_scale_200_commit_boundary_review.md` — Era D commit boundary review
- `outputs/validation/cninfo_b_class_erad_scale_200_commit_boundary_summary.md` — boundary summary
- `outputs/validation/cninfo_b_class_erad_scale_200_safe_to_commit_list.md` — explicit-path safe list（**30** paths committed）
- `outputs/validation/cninfo_b_class_erad_scale_200_do_not_commit_list.md` — bulk raw_metadata/quality excluded（local-only）
- `outputs/validation/cninfo_b_class_erad_scale_200_unresolved_case_ledger.csv` — unresolved ledger（BD2E090 · BD2E092）
- `outputs/validation/cninfo_b_class_erad_scale_200/reports/b_class_erad_scale_200_report.csv` — Era D live 报告（**198/200 acceptable** · CNINFO **397**）
- `plans/cninfo_b_class_erad_scale_200_command_draft.md` — Era D 命令草案
- `outputs/validation/cninfo_b_class_erad_scale_200_approval_checklist.md` — Era D 批准检查清单（commit complete · **NOT pushed**）
- `plans/cninfo_b_class_phase3_100_post_commit_inventory_gap_review.md` — Phase 3 post-commit inventory gap review（gate **`READY_FOR_HUMAN_DECISION`** · primary **Option A**）
- `outputs/validation/cninfo_b_class_phase3_100_post_commit_missing_artifact_ledger.csv` — missing artifact ledger（**185** paths）
- `outputs/validation/cninfo_b_class_phase3_100_post_commit_gap_metrics.csv` — gap metrics
- `outputs/validation/cninfo_b_class_phase3_100_post_commit_gap_summary.md` — gap summary
- `outputs/validation/cninfo_b_class_phase3_100_post_commit_next_step_recommendation.md` — next-step recommendation
- `outputs/validation/cninfo_b_class_phase3_100_failed_retry/reports/b_class_phase3_100_failed_retry_summary.md` — Phase 3 failed retry live summary（execution gate **FAIL_REVIEW_REQUIRED**）
- `outputs/validation/cninfo_b_class_phase3_100_failed_retry/reports/b_class_phase3_100_failed_retry_quality_report.csv` — Phase 3 failed retry quality report
- `plans/cninfo_b_class_phase3_100_failed_retry_plan.md` — Phase 3 failed retry 规划（**NOT APPROVED**）
- `plans/cninfo_b_class_phase3_100_failed_retry_command_draft.md` — Phase 3 failed retry 命令草案
- `outputs/validation/cninfo_b_class_phase3_100_failed_retry_approval_checklist.md` — Phase 3 failed retry 批准检查清单
- `outputs/validation/cninfo_b_class_phase3_100_failed_retry_planning_summary.md` — Phase 3 failed retry 规划摘要（retry planning gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_b_class_phase2_expansion/reports/b_class_phase2_expansion_summary.md` — Phase 2 live 执行摘要（execution gate **PASS_WITH_CAVEAT**）
- `outputs/validation/cninfo_b_class_phase2_expansion/reports/b_class_phase2_expansion_quality_report.csv` — Phase 2 quality 报告
- `plans/cninfo_b_class_phase1_tiny_live_closure_review.md` — Phase 1 tiny live 收口评审
- `outputs/validation/cninfo_b_class_phase1_tiny_live_final_metrics.csv` — tiny live 最终指标（**5/5 resolved**）
- `outputs/validation/cninfo_b_class_phase1_tiny_live_closure_summary.md` — tiny live 收口摘要（closure gate **PASS_WITH_CAVEAT**）
- `fixtures/b_class/phase1/ready_cases/` — RC003/RC004/RC005 离线 fixture
- `plans/cninfo_b_class_phase1_live_validation_approval_plan.md` — live validation 批准计划（gate **READY_FOR_APPROVAL**）
- `outputs/validation/cninfo_b_class_phase1_live_validation_checklist.md` — live validation 检查清单
- `outputs/validation/cninfo_b_class_phase1_freeze_v1_implementation_summary.md` — implementation 摘要（gate **PASS_OFFLINE**）
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
- `plans/eraD_execution_plan.md` — Era D 本地稳定扩规模执行计划（四线并行 · 不入库）
- `plans/company_portrait_ontology_plan.md` — **横切** 公司画像 18 模块 ontology 映射总说明
- `plans/company_portrait_local_layout.md` — portrait 本地目录与 evidence 指针约定
- `outputs/validation/company_portrait_module_index.csv` — 画像模块 M01–M18
- `outputs/validation/company_portrait_field_catalog_v0.csv` — 画像字段 catalog v0（**715** 字段）
- `outputs/validation/company_portrait_coverage_matrix_v0.csv` — 画像覆盖矩阵 v0
- `outputs/validation/company_portrait_coverage_summary.md` — 按模块覆盖率汇总
- `outputs/validation/company_portrait_pilot_fill_summary.md` — 试点 000009 填充摘要
- `schemas/portrait/fact_record.schema.json` — 画像事实层 schema
- `schemas/portrait/evidence_ref.schema.json` — 画像证据指针 schema
- `outputs/portrait/companies/<code>/` — 画像试点产出（facts.jsonl · evidence_index.jsonl · coverage.json）
- `lab/build_company_portrait_ontology.py` — docx → catalog + coverage（offline）
- `lab/fill_company_portrait_pilot.py` — C normalized → portrait 试点回填（offline · 只读）
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
4. **Phase 4 C 类**见 [registry lint](outputs/validation/cninfo_c_class_registry_lint_summary.md) / [fixture validation](outputs/validation/cninfo_c_class_profile_schema_validation_summary.md) / [active 30 smoke summary](outputs/validation/cninfo_c_class_scale_smoke_30_active_summary.md) / [candidates YAML](config/cninfo_c_class_source_candidates.yaml)。
5. **C 类** · **Era D** [local retention summary](outputs/validation/cninfo_c_class_erad_local_retention_summary.md) · gate **`PASS_OFFLINE`** · C-line **continues** · 下一步 **post-fix8 harvest audit 重跑** 或 **hold**。
6. **A 类 Report Metadata Phase 0 规划已启动**（[planning summary](outputs/validation/cninfo_a_class_initial_planning_summary.md) · **无 CNINFO · 无 PDF**）。
7. **A 类 Phase 1 freeze v1 已离线实现**（[implementation summary](outputs/validation/cninfo_a_class_phase1_freeze_v1_implementation_summary.md) · gate **`PASS_OFFLINE`**）。
8. **A 类 ready-case benchmark 已完成**（[benchmark summary](outputs/validation/cninfo_a_class_phase1_ready_case_benchmark_summary.md) · **5/5 PASS** · gate **`READY_FOR_REVIEW`** · **无 CNINFO**）。
9. **A 类 tiny live metadata approval package 已准备**（[approval summary](outputs/validation/cninfo_a_class_phase1_tiny_live_metadata_approval_summary.md) · gate **`READY_FOR_APPROVAL`** · **无 A-class live** · **无 PDF**）。
10. **A 类 tiny live metadata validation 已执行**（[live summary](outputs/validation/cninfo_a_class_tiny_live_metadata/reports/a_class_tiny_live_metadata_summary.md) · **5/5 found** · gate **`PASS_WITH_CAVEAT`** · **无 PDF** · **无 verified**）。
11. **A 类 tiny live metadata v2 rerun 已执行**（[v2 rerun review](outputs/validation/cninfo_a_class_tiny_live_metadata_v2_rerun_review.md) · **5/5 correct** · gate **`PASS_WITH_CAVEAT`** · **无 PDF** · **无 verified**）。
12. **A 类 Phase 1 tiny live metadata v2 closure 已完成**（[closure summary](outputs/validation/cninfo_a_class_phase1_tiny_live_metadata_v2_closure_summary.md) · closure gate **`PASS_WITH_CAVEAT`** · **无 CNINFO**）。
13. **A 类 Phase 1 boundary 已收口**（[boundary summary](outputs/validation/cninfo_a_class_phase1_boundary_summary.md) · `a_class_phase1_boundary_gate = PASS_WITH_CAVEAT`** · **不是 verified**）。
14. **A 类 Phase 2 20-company metadata expansion 规划包已准备**（[approval summary](outputs/validation/cninfo_a_class_phase2_metadata_approval_summary.md) · universe **20** · planning gate **`READY_FOR_APPROVAL`** · **无 CNINFO** · **无 live**）。
15. **A 类 Phase 2 metadata expansion runner 已离线准备**（[extension summary](outputs/validation/cninfo_a_class_phase2_metadata_runner_extension_summary.md) · dry-run **20/20** · test **16/16 PASS** · runner gate **`READY_FOR_APPROVAL`** · CNINFO **0**）。
16. **A 类 Phase 2 20-company live metadata validation 已执行**（[live summary](outputs/validation/cninfo_a_class_phase2_metadata_expansion/reports/a_class_phase2_metadata_summary.md) · **12/20 correct** · wrong_report_type **0** · execution gate **`FAIL_REVIEW_REQUIRED`** · CNINFO **28** · **无 PDF** · **不是 verified**）。
17. **A 类 Phase 2 failed-case isolated retry 批准包已准备**（[retry approval summary](outputs/validation/cninfo_a_class_phase2_failed_retry_approval_summary.md) · retry **8** · test **12/12 PASS** · planning gate **`READY_FOR_APPROVAL`** · CNINFO **0** · **无 live**）。
18. **A 类 Phase 2 failed-case isolated retry 已执行**（[retry summary](outputs/validation/cninfo_a_class_phase2_metadata_retry/reports/a_class_phase2_failed_retry_summary.md) · **0/8 correct** · orgId network_error · retry gate **`FAIL_REVIEW_REQUIRED`** · CNINFO **0** · **无 PDF** · **不是 verified**）。
19. **A 类 Phase 2 retry_v2 merge closure 更新已完成**（[closure summary](outputs/validation/cninfo_a_class_phase2_retry_v2_closure_summary.md) · **12 effective accepted** · **8 effective unresolved** · retry_v2 closure gate **`PASS_WITH_CAVEAT_NETWORK_UNRESOLVED`** · CNINFO **0** · **不是 verified**）。
20. **A 类 Phase 2 CNINFO reachability precheck 规划包已准备**（[planning summary](outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck_planning_summary.md) · candidates **3** · cap **≤6** · planning gate **`READY_FOR_APPROVAL`** · CNINFO **0** · **NOT APPROVED**）。
21. **A 类 Phase 2 CNINFO reachability precheck runner 与 dry-run 已准备**（[runner summary](outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck_runner_summary.md) · **3/3 planned_ok** · test **23/23 PASS** · runner gate **`READY_FOR_APPROVAL`** · CNINFO **0** · **NOT APPROVED live**）。
22. **A 类 Phase 2 CNINFO reachability precheck live 已执行**（[live summary](outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck/reports/a_class_phase2_cninfo_reachability_precheck_summary.md) · **2/3 orgId resolved** · CNINFO **2** · execution gate **`PASS_WITH_CAVEAT`** · PDF **0** · **不是 verified**）。
28. **A 类 Phase 2 final commit boundary review 已完成**（[boundary summary](outputs/validation/cninfo_a_class_phase2_commit_boundary_summary.md) · gate **`READY_FOR_COMMIT_REVIEW`** · CNINFO **0** · **不是 verified**）。
29. **A 类 Phase 2 commit 已完成**（commit **`cad5ed1`** · **80 files** · explicit-path only · gate **`a_class_phase2_commit_review_gate = READY_FOR_HUMAN_DECISION`** · CNINFO **0** · **无 push** · **不是 verified**）。
30. **A 类 Phase 3 50-company expansion planning package 已离线准备**（[planning summary](outputs/validation/cninfo_a_class_phase3_50_company_planning_summary.md) · universe **50** · overlap **0/0** · gate **`READY_FOR_APPROVAL`** · CNINFO **0** · **NOT APPROVED** · **不是 verified**）。
31. **A 类 Phase 3 runner extension + dry-run 已离线准备**（[runner extension summary](outputs/validation/cninfo_a_class_phase3_50_company_runner_extension_summary.md) · **50/50 planned_ok** · test **26/26 PASS** · gate **`READY_FOR_APPROVAL`** · CNINFO **0** · **NOT APPROVED live** · **不是 verified**）。
32. **A 类 Phase 3 live path 已离线实现**（[live path summary](outputs/validation/cninfo_a_class_phase3_50_company_live_path_summary.md) · test **28/28 PASS** · gate **`READY_FOR_APPROVAL`** · mock CNINFO **0** · **不是 verified**）。
33. **A 类 Phase 3 50-company isolated live 已执行**（[expansion summary](outputs/validation/cninfo_a_class_phase3_50_company_expansion/reports/a_class_phase3_50_company_expansion_summary.md) · **49/50 acceptable** · CNINFO **104** · execution gate **`PASS_WITH_CAVEAT`** · **不是 verified**）。
34. **A 类 Phase 3 50-company merge closure 已完成**（[closure summary](outputs/validation/cninfo_a_class_phase3_50_company_closure_summary.md) · **49/50 effective** · A3M017 unresolved · closure gate **`PASS_WITH_CAVEAT`** · CNINFO **0** · **不是 verified**）。
35. **A 类 Phase 3 50-company final commit boundary review 已完成**（[boundary summary](outputs/validation/cninfo_a_class_phase3_50_company_commit_boundary_summary.md) · **80 yes / 9 no** · boundary gate **`READY_FOR_COMMIT_REVIEW`** · A3M017 caveat retained · **不是 verified**）。
36. **A 类 Phase 3 explicit-path commit 已完成**（commit **`bbc15c3`** · **77 files** · test **54/54 PASS** · review gate **`READY_FOR_HUMAN_DECISION`** · **无 push** · **不是 verified**）· A3M017 caveat retained。
37. **A 类 Phase 3 A3M017 isolated retry planning package 已离线准备**（[planning summary](outputs/validation/cninfo_a_class_phase3_a3m017_isolated_retry_planning_summary.md) · universe **1** · planning gate **`READY_FOR_APPROVAL`** · CNINFO **0** · **NOT APPROVED live** · **不是 verified**）。
38. **A 类 Era D ~200 metadata expansion 规划包已准备**（[planning summary](outputs/validation/cninfo_a_class_erad_scale_200_planning_summary.md) · **200** = **50+150** · planning gate **`READY_FOR_APPROVAL`** · CNINFO **0** · **不是 verified**）。
39. **A 类 Era D ~200 runner extension + dry-run 已完成**（[runner extension summary](outputs/validation/cninfo_a_class_erad_scale_200_runner_extension_summary.md) · **200/200 planned_ok** · tests **27/27 PASS** · runner gate **`READY_FOR_APPROVAL`** · live **NOT APPROVED** · CNINFO **0** · **不是 verified**）。
40. **A 类 Era D ~200 live path 已离线实现**（[live path summary](outputs/validation/cninfo_a_class_erad_scale_200_live_path_summary.md) · live-path tests **26/26 PASS** · live path gate **`READY_FOR_APPROVAL`** · mock CNINFO **0** · **不是 verified**）。
41. **A 类 Era D ~200 isolated live 已执行**（[execution summary](outputs/validation/cninfo_a_class_erad_scale_200_execution_summary.md) · **192/200 acceptable** · CNINFO **423** · execution gate **`PASS_WITH_CAVEAT`** · **8 not_found** · **不是 verified**）。
42. **A 类 Era D ~200 failed-case triage + isolated retry planning 已完成**（[triage summary](outputs/validation/cninfo_a_class_erad_scale_200_failed_case_triage_summary.md) · **7 retry / 1 defer** · triage gate **`PASS_OFFLINE`** · retry planning gate **`READY_FOR_APPROVAL`** · CNINFO **0** · **不是 verified**）。
43. **A 类 Era D ~200 isolated retry runner extension + dry-run 已完成**（[runner extension summary](outputs/validation/cninfo_a_class_erad_scale_200_isolated_retry_runner_extension_summary.md) · **7/7 planned_ok** · tests **21/21 PASS** · runner gate **`READY_FOR_APPROVAL`** · CNINFO **0** · **NOT APPROVED live** · **不是 verified**）。
44. **A 类 Era D ~200 isolated retry live path 已离线实现**（[live path summary](outputs/validation/cninfo_a_class_erad_scale_200_isolated_retry_live_path_summary.md) · live-path tests **18/18 PASS** · live path gate **`READY_FOR_APPROVAL`** · mock CNINFO **0** · **无 live 执行** · **不是 verified**）。
8. **B 类 Phase 1 tiny live 收口完成**（[closure summary](outputs/validation/cninfo_b_class_phase1_tiny_live_closure_summary.md) · **5/5 resolved** · **无 verified**）。
9. **B 类 Phase 2 expansion 批准包已准备**（[approval summary](outputs/validation/cninfo_b_class_phase2_expansion_approval_summary.md) · universe draft **20** · gate **`READY_FOR_APPROVAL`** · **无 B-class live**）。
10. **B 类 Phase 2 expansion runner 已离线准备**（[extension summary](outputs/validation/cninfo_b_class_phase2_expansion_runner_extension_summary.md) · dry-run **20/20** · test **12/12 PASS** · **无 CNINFO**）。
11. **B 类 Phase 2 expansion live 已执行**（[execution summary](outputs/validation/cninfo_b_class_phase2_expansion/reports/b_class_phase2_expansion_summary.md) · **20/20 found** · CNINFO **40** · gate **`PASS_WITH_CAVEAT`** · **无 PDF** · **无 verified**）。
12. **B 类 Phase 2 expansion 收口完成**（[closure summary](outputs/validation/cninfo_b_class_phase2_expansion_closure_summary.md) · **20/20 acceptable** · closure gate **`PASS_WITH_CAVEAT`** · **无 verified**）。
13. **B 类 Phase 2.5 50-company expansion 批准包已准备**（[approval summary](outputs/validation/cninfo_b_class_phase25_expansion_approval_summary.md) · universe **50** · overlap **0/0** · gate **`READY_FOR_APPROVAL`** · **无 B-class live**）。
14. **B 类 Phase 2.5 expansion runner 已离线准备**（[extension summary](outputs/validation/cninfo_b_class_phase25_expansion_runner_extension_summary.md) · dry-run **50/50** · test **15/15 PASS** · **无 CNINFO** · **无 live**）。
15. **B 类 Phase 2.5 50-company live metadata validation 已执行**（[execution summary](outputs/validation/cninfo_b_class_phase25_expansion/reports/b_class_phase25_expansion_summary.md) · **45/50 acceptable** · CNINFO **93** · gate **`PASS_WITH_CAVEAT`** · **无 PDF** · **无 verified**）。
16. **B 类 Phase 2.5 expansion 收口完成**（[closure summary](outputs/validation/cninfo_b_class_phase25_expansion_closure_summary.md) · **5 network_error triaged** · closure gate **`PASS_WITH_CAVEAT`** · **无 verified**）。
17. **B 类 Phase 2.5 failed-case isolated retry 批准包已准备**（[package summary](outputs/validation/cninfo_b_class_phase25_failed_retry_package_summary.md) · retry **5** · dry-run **5/5** · test **14/14 PASS** · gate **`READY_FOR_APPROVAL`** · **无 CNINFO** · **无 live**）。
18. **B 类 Phase 2.5 failed-case isolated retry 已执行**（[retry summary](outputs/validation/cninfo_b_class_phase25_failed_retry/reports/b_class_phase25_failed_retry_summary.md) · **5/5 found** · CNINFO **10** · gate **`PASS_WITH_CAVEAT`** · **无 PDF** · **无 verified**）。
19. **B 类 Phase 2.5 failed retry 收口完成**（[closure summary](outputs/validation/cninfo_b_class_phase25_failed_retry_closure_summary.md) · **50/50 effective** · closure gate **`PASS_WITH_CAVEAT`** · **无 verified**）。
9. **D 类 Phase 0 市场行为层规划**见 [architecture plan](plans/cninfo_d_class_market_data_architecture_plan.md) / [discovery plan](plans/cninfo_d_class_source_discovery_plan.md) / [readiness matrix](outputs/validation/cninfo_d_class_readiness_matrix.csv)（**无 D-class live**）。
10. **D 类 Phase 1 schema freeze review 已准备**（[freeze review](plans/cninfo_d_class_phase1_schema_freeze_review.md) · lint **10/10** · gate **`READY_FOR_APPROVAL`** · **无 D-class live**）。
11. **D 类 Phase 1 schema freeze approval package 已准备**（[approval summary](outputs/validation/cninfo_d_class_phase1_schema_freeze_approval_summary.md) · **未 signoff** · **无 D-class live**）。
12. **D 类 Phase 1 freeze v1 已离线落地**（[implementation summary](outputs/validation/cninfo_d_class_phase1_freeze_v1_implementation_summary.md) · lint **12/12** · gate **`PASS_OFFLINE`** · **无 D-class live**）。
13. **D 类 Phase 1 ready-case benchmark 已离线执行**（[benchmark summary](outputs/validation/cninfo_d_class_phase1_ready_case_benchmark_summary.md) · **7/7 PASS** · tests **8/8** · gate **`READY_FOR_REVIEW`** · **无 D-class live**）。
14. **D 类 Phase 1 tiny live 批准包已准备**（[approval summary](outputs/validation/cninfo_d_class_phase1_tiny_live_approval_summary.md) · universe **7** · gate **`READY_FOR_APPROVAL`** · **无 D-class live**）。
15. **D 类 tiny live runner 已离线准备**（[extension summary](outputs/validation/cninfo_d_class_tiny_live_runner_extension_summary.md) · dry-run **7/7** · tests **10/10** · gate **`READY_FOR_APPROVAL`**）。
16. **D 类 tiny live validation 已执行**（[live summary](outputs/validation/cninfo_d_class_tiny_live_validation/reports/d_class_tiny_live_summary.md) · **5/7 acceptable** · execution gate **`PASS_WITH_CAVEAT`** · **不是 verified**）。
17. **D 类 Phase 1 tiny live 已收口**（[closure summary](outputs/validation/cninfo_d_class_phase1_tiny_live_closure_summary.md) · closure gate **`PASS_WITH_CAVEAT`** · **无 rerun**）。
18. **D 类 DLC003/DLC006 校准决策包已准备**（[calibration summary](outputs/validation/cninfo_d_class_dlc003_dlc006_calibration_summary.md) · gate **`READY_FOR_HUMAN_DECISION`** · v2 rerun **NOT APPROVED**）。
19. **D 类 Phase 1 边界已收口**（[boundary summary](outputs/validation/cninfo_d_class_phase1_boundary_summary.md) · boundary gate **`PASS_WITH_CAVEAT`** · **不是 verified**）。
20. **D 类 DLC003/DLC006 有界 probe 扩展设计已准备**（[design summary](outputs/validation/cninfo_d_class_tiny_live_v2_bounded_probe_design_summary.md) · design gate **`READY_FOR_APPROVAL`** · v2 **NOT APPROVED**）。
21. **D 类 tiny live v2 bounded probe runner 已离线准备**（[runner extension summary](outputs/validation/cninfo_d_class_tiny_live_v2_bounded_probe_runner_extension_summary.md) · tests **14/14** · runner gate **`READY_FOR_APPROVAL`**）。
22. **D 类 tiny live v2 bounded probe 已执行**（[v2 summary](outputs/validation/cninfo_d_class_tiny_live_validation_v2/reports/d_class_tiny_live_v2_bounded_probe_summary.md) · CNINFO **40** · execution gate **`PASS_WITH_CAVEAT`** · **不是 verified**）。
23. **D 类 v2 bounded probe 已收口**（[closure summary](outputs/validation/cninfo_d_class_tiny_live_v2_bounded_probe_closure_summary.md) · closure gate **`PASS_WITH_CAVEAT`** · final calibration **`READY_FOR_HUMAN_SIGNOFF`**）。
24. **D 类 DLC003/DLC006 校准人工 signoff 已完成**（[human signoff](outputs/validation/cninfo_d_class_dlc003_dlc006_calibration_human_signoff.md) · [calibrated universe](outputs/validation/cninfo_d_class_phase1_tiny_live_universe_calibrated.csv) · gate **`HUMAN_SIGNED_OFF_WITH_CAVEAT`** · **不是 verified**）。
25. **D 类 known event replacement 规划已准备**（[planning summary](outputs/validation/cninfo_d_class_known_event_replacement_planning_summary.md) · gate **`READY_FOR_HUMAN_CANDIDATES`** · **NOT APPROVED**）。
26. **D 类 known event candidate intake 已校验通过**（[intake summary](outputs/validation/cninfo_d_class_known_event_candidate_intake_summary.md) · [validation summary](outputs/validation/cninfo_d_class_known_event_candidate_validation_summary.md) · DLC003R **688671** · DLC006R **301259** · intake gate **`HUMAN_CANDIDATE_VALIDATED`** · **不是 verified**）。
27. **D 类 known-event replacement validation approval package 已准备**（[approval summary](outputs/validation/cninfo_d_class_known_event_replacement_validation_approval_summary.md) · [filled universe](outputs/validation/cninfo_d_class_tiny_live_replacement_universe_filled.csv) · package gate **`READY_FOR_APPROVAL`** · **NOT APPROVED**）。
28. **D 类 known-event replacement runner 扩展已准备**（[extension summary](outputs/validation/cninfo_d_class_known_event_replacement_runner_extension_summary.md) · dry-run **7/7** · tests **20/20** · extension gate **`READY_FOR_APPROVAL`**）。
29. **D 类 known-event replacement live 探针路径已实现**（[live implementation summary](outputs/validation/cninfo_d_class_known_event_replacement_live_implementation_summary.md) · live-path tests **22/22** · live implementation gate **`READY_FOR_APPROVAL`**）。
30. **D 类 known-event replacement isolated live 已执行**（[live summary](outputs/validation/cninfo_d_class_known_event_replacement_validation/reports/d_class_known_event_replacement_live_summary.md) · CNINFO **40** · execution gate **`FAIL_REVIEW_REQUIRED`** · **不是 verified**）。
31. **D 类 known-event replacement live failure review 已完成**（[review summary](outputs/validation/cninfo_d_class_known_event_replacement_live_failure_review_summary.md) · **2/2 failed** · failure review gate **`READY_FOR_HUMAN_DECISION`** · targeted probe Option A 推荐规划优先）。
32. **D 类 known-event targeted probe planning package 已准备**（[planning summary](outputs/validation/cninfo_d_class_known_event_targeted_probe_planning_summary.md) · universe **2** · cap **≤24** · planning gate **`READY_FOR_APPROVAL`** · **NOT APPROVED** · **无 CNINFO** · **无 live** · **无实现**）。
33. **D 类 known-event targeted probe runner 扩展与 dry-run 已准备**（[extension summary](outputs/validation/cninfo_d_class_known_event_targeted_probe_runner_extension_summary.md) · dry-run **2/2** · planned **24** · tests **27/27** · extension gate **`READY_FOR_APPROVAL`** · **无 live**）。
34. **D 类 known-event targeted probe live 路径已实现**（[live implementation summary](outputs/validation/cninfo_d_class_known_event_targeted_probe_live_implementation_summary.md) · live-path tests **29/29** · live implementation gate **`READY_FOR_APPROVAL`** · **无真实 CNINFO**）。
35. **D 类 known-event targeted probe isolated live 已执行**（[live summary](outputs/validation/cninfo_d_class_known_event_targeted_probe/reports/d_class_known_event_targeted_probe_live_summary.md) · CNINFO **13** · DLC003R-T01 **found/1** · DLC006R-T01 **empty_but_valid/0** · execution gate **`FAIL_REVIEW_REQUIRED`** · **不是 verified**）。
36. **D 类 known-event targeted probe closure 与 DLC006R failure review 已完成**（[closure summary](outputs/validation/cninfo_d_class_known_event_targeted_probe_closure_summary.md) · closure gate **`READY_FOR_HUMAN_DECISION`** · **无 CNINFO** · **无 rerun**）。
37. **D 类 known-event replacement 最终收口已完成**（[final closure summary](outputs/validation/cninfo_d_class_known_event_replacement_final_closure_summary.md) · DLC006R **Option A+C** · final closure gate **`PASS_WITH_CAVEAT`** · **不是 verified**）。
38. **D 类 known-event replacement boundary review 已完成**（[boundary summary](outputs/validation/cninfo_d_class_known_event_replacement_boundary_summary.md) · [safe-to-commit list](outputs/validation/cninfo_d_class_known_event_replacement_safe_to_commit_list.md) · boundary gate **`READY_FOR_COMMIT_REVIEW`** · commit **`389cd9c`**）。
39. **D 类 known-event replacement commit 已推送**（commit **`389cd9c`** · on **`origin/main`** · [push status](outputs/validation/cninfo_d_class_known_event_replacement_push_status.md) · push gate **`READY_FOR_HUMAN_DECISION`** · final closure gate **`PASS_WITH_CAVEAT`** · **不是 verified**）。
40. **D 类 next component planning package 已准备**（[planning summary](outputs/validation/cninfo_d_class_next_component_planning_summary.md) · primary **`margin_trading`** · planning gate **`READY_FOR_HUMAN_DECISION`** · **NOT_APPROVED live** · **无 CNINFO**）。
41. **D 类 margin_trading first-slice approval package 已准备**（[approval summary](outputs/validation/cninfo_d_class_margin_trading_first_slice_approval_summary.md) · universe **5** · cap **≤20** · approval gate **`READY_FOR_APPROVAL`** · **NOT APPROVED** · **无 live**）。
42. **D 类 margin_trading first-slice runner 扩展与 dry-run 已准备**（[extension summary](outputs/validation/cninfo_d_class_margin_trading_first_slice_runner_extension_summary.md) · dry-run **5/5** · planned **20** · tests **21/21** · extension gate **`READY_FOR_APPROVAL`** · **无 live**）。
43. **D 类 margin_trading first-slice live path 已离线实现**（[live-path summary](outputs/validation/cninfo_d_class_margin_trading_first_slice_live_path_summary.md) · tests **40/40** · live-path gate **`READY_FOR_APPROVAL`**）。
44. **D 类 margin_trading first-slice isolated live 已执行**（[live summary](outputs/validation/cninfo_d_class_margin_trading_first_slice/reports/d_class_margin_trading_first_slice_live_summary.md) · CNINFO **5** · acceptable **5/5** · execution gate **`PASS_WITH_CAVEAT`** · **不是 verified** · **无 commit**）。
45. **D 类 margin_trading first-slice closure review 已完成**（[closure summary](outputs/validation/cninfo_d_class_margin_trading_first_slice_closure_summary.md) · effective **5/5** · unresolved **0** · closure gate **`PASS_WITH_CAVEAT`** · CNINFO **0** · **无 commit**）。
46. **D 类 margin_trading first-slice commit boundary review 已完成**（[boundary summary](outputs/validation/cninfo_d_class_margin_trading_first_slice_commit_boundary_summary.md) · should_commit **34/15** · boundary gate **`READY_FOR_COMMIT_REVIEW`**）。
47. **D 类 margin_trading first-slice commit 已完成**（commit **`116f875`** · explicit-path **34** artifacts · tests **40/40** · commit review gate **`READY_FOR_HUMAN_DECISION`** · **不是 verified** · **无 push**）。
48. **D 类 disclosure_schedule first-slice explicit-path commit 已完成**（commit **`d37ce0a`** · **31** artifacts · **5/5** · DDS004 caveat retained · gate **`PASS_WITH_CAVEAT`** · **无 push**）。
49. **D 类进入 Era D next-component planning 已完成**（[planning summary](outputs/validation/cninfo_d_class_erad_next_component_planning_summary.md) · primary **`block_trade`** · runner-up **`restricted_shares_unlock`** · gate **`READY_FOR_APPROVAL`** · CNINFO **0**）。
50. **D 类 block_trade first-slice approval package 已准备**（[approval summary](outputs/validation/cninfo_d_class_block_trade_first_slice_approval_summary.md) · universe **5** · cap **≤20** · approval gate **`READY_FOR_APPROVAL`** · **NOT APPROVED** · **无 live**）。
51. **D 类 block_trade first-slice runner 扩展与 dry-run 已准备**（[extension summary](outputs/validation/cninfo_d_class_block_trade_first_slice_runner_extension_summary.md) · dry-run **5/5** · tests **19/19** · extension gate **`READY_FOR_APPROVAL`** · **无 live**）。
52. **D 类 block_trade first-slice live path 已离线实现**（[live-path summary](outputs/validation/cninfo_d_class_block_trade_first_slice_live_path_summary.md) · tests **18/18** · mock only）。
53. **D 类 block_trade first-slice isolated live 已执行**（[isolated live summary](outputs/validation/cninfo_d_class_block_trade_first_slice_isolated_live_validation_summary.md) · CNINFO **5** · acceptable **4/5** · execution gate **`PASS_WITH_CAVEAT`** · caveat DBT002 · **无 commit**）。
54. **D 类 block_trade first-slice closure review 已完成**（[closure summary](outputs/validation/cninfo_d_class_block_trade_first_slice_closure_summary.md) · **4/5** · sparse-day **5/5** · closure gate **`PASS_WITH_CAVEAT`** · CNINFO **0** · **无 commit**）。
55. **D 类 block_trade first-slice commit boundary review 已完成**（[boundary summary](outputs/validation/cninfo_d_class_block_trade_first_slice_commit_boundary_summary.md) · safe **~27** · boundary gate **`READY_FOR_COMMIT_REVIEW`** · CNINFO **0**）。
56. **D 类 block_trade first-slice explicit-path commit 已完成**（commit **`a12298b`** · **24 files** · [commit status](outputs/validation/cninfo_d_class_block_trade_first_slice_commit_status.md) · gate **`PASS_WITH_CAVEAT`** · DBT002 caveat retained · **无 push**）。
12. **每完成一个 Phase**：更新分层表状态 + `outputs/validation/` 留 summary；不做数据库接入。
