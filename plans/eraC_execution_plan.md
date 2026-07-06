# Era C 执行计划（A–F 分层验证 · Composer 可执行）

_最后更新：2026-07-05_

> **权威分类与验证口径：** [cninfo_data_source_layered_inventory.md](cninfo_data_source_layered_inventory.md)  
> **仓库导航：** [PROJECT_MAP.md](../PROJECT_MAP.md) · **当前进展：** [CURRENT_STATUS.md](../CURRENT_STATUS.md)
>
> **只在 Era C 范围内改动**；**不要同时展开所有 Phase**；红线见第 1 节。

---

## 0. Era C 完成定义（三层 + A–F 分层）

1. **穷尽式收集**：CNINFO 可见栏目/入口清单（A–F 分层表已覆盖官网观察版，可持续补漏）。
2. **分类**：每项归入 A–F 之一；A = 类年报 PDF 流，B–F = 非类年报路径。
3. **分层验证**：每层用**各自口径**验证完毕，状态回填分层表。

> A 类最终结论见 [cninfo_report_phase1_final_summary.md](../outputs/validation/cninfo_report_phase1_final_summary.md)（**testing/usable candidate**，不写 verified）。

---

## 1. 红线

- 不接 PostgreSQL / MinIO / MongoDB；不下载/解析 PDF 正文。
- 不绕过登录/验证码/付费/权限；请求间 sleep；不用 BrowserUser。
- `recommended_status` 只用 `candidate`/`testing`/`partial`/`blocked`/`unknown`（D 类）；A 类可用 `testing/usable candidate`；**不写 `verified`**。
- 不碰 Era A / Era B 代码；联网脚本本地手动跑。

---

## 2. Phase 路线图（严格顺序，一次只做一个 Phase）

| Phase | 内容 | 状态 | 主要产出 |
|---|---|---|---|
| **0** | 固化 A–F 分层表 + 统一验证口径 | **已完成** | [cninfo_data_source_layered_inventory.md](cninfo_data_source_layered_inventory.md) |
| **1** | A 类：per-company coverage%（P0→P1 + title filter + quality audit） | **已收口** | [cninfo_report_phase1_final_summary.md](../outputs/validation/cninfo_report_phase1_final_summary.md) |
| **2** | D 类：10 源 discovery + UI + 稳定性 | **已收口** | [phase2_final_summary](../outputs/validation/cninfo_table_sources_phase2_current_final_summary.md) |
| **2b** | D 类：registry / schema / status model 设计 | **草案完成** | [registry](cninfo_d_class_source_registry_design.md) · [schema](cninfo_d_class_schema_draft.md) · [status](cninfo_d_class_ingestion_status_model.md) |
| **2c** | D 类：source → schema 映射审查 | **已完成** | [mapping_review](cninfo_d_class_source_to_schema_mapping_review.md) |
| **2d** | D 类：registry YAML draft（10 源） | **草案完成** | [cninfo_d_class_source_registry_draft.yaml](../config/cninfo_d_class_source_registry_draft.yaml) |
| **2e** | D 类：JSON Schema draft（10 逻辑表） | **草案完成** | [schemas/d_class/](../schemas/d_class/) |
| **3** | B 类：corpus + live metadata v1 | **已打通** | [B live summary](../outputs/validation/cninfo_b_class_corpus_retrieval_live_summary.md) |
| **4** | C 类 F10 / company profile 设计 | **basic_profile mapper** | [mapper summary](../outputs/validation/cninfo_c_class_basic_profile_mapper_summary.md) |
| **4b** | E 类可达性三态；F 类暂缓 | 待 C probe 后 | reachability summary |

---

## 3. Phase 0 — 已完成

- 新建 [cninfo_data_source_layered_inventory.md](cninfo_data_source_layered_inventory.md)：A–F 清单 + 每类分母/分子/成功指标。
- 更新 PROJECT_MAP、CURRENT_STATUS、本文件。
- 明确：旧 `368/780` 行计数**不能**作为 A 类最终 coverage 结论。

---

## 4. Phase 1 — 已收口（A 类 report retrieval）

### 结果摘要

| 项 | 数值 |
|----|------|
| P1 effective coverage | **749/796 = 94.10%** |
| 二轮 audit found pass | **97.5%**（39/40） |
| **recommended_status** | **testing / usable candidate** |
| BSE residual | later improvement（不阻塞 Phase 2） |

### 主要产出

- `lab/validate_cninfo_report_coverage.py`
- `outputs/validation/cninfo_report_p1_coverage_validation{.csv,_summary.md}`
- [cninfo_report_phase1_final_summary.md](../outputs/validation/cninfo_report_phase1_final_summary.md)
- 两轮 quality audit results

**不写 verified；不写 full-market stable。**

---

## 5. Phase 2 — 已收口（D 类固定表格，10 源）

### 结果摘要

| 项 | 数值 |
|----|------|
| 已验证 source | **10**（P1 五 + P2 五） |
| testing_stable_sample | **10** |
| blocked | **0** |
| schema_changed | **0** |
| candidate 待探测 | **2**（ipo_query、szse_calendar） |
| **verified** | **0**（不写） |

**testing_stable_sample 列表：**

- **P1：** disclosure_schedule、restricted_shares_unlock、block_trade、margin_trading、abnormal_trading
- **P2：** equity_pledge、shareholder_change、executive_shareholding、fund_industry_allocation、shareholder_data

**总总结：** [cninfo_table_sources_phase2_current_final_summary.md](../outputs/validation/cninfo_table_sources_phase2_current_final_summary.md)

### 已完成任务

1. ✅ 探测计划、配置、验证脚本（含 multidate / priority2 stability）
2. ✅ DevTools endpoint discovery（P1 五 + P2 五 source）
3. ✅ 各 source 独立 `--source-id` 小样本 live 验证
4. ✅ P1/P2 consolidated 总结 + **Phase 2 总总结**
5. ✅ 字段语义表 + UI 对照（P1 28 confirmed；P2 51 confirmed 行）
6. ✅ P1 多日期稳定性（15 cases，5/5 stable）
7. ✅ P2 多参数稳定性（15 cases，5/5 stable）

### 下一步（Phase 2 延续 / Phase 3）

1. ~~Phase 2 当前批次~~ → **已收口**
2. ~~D 类 registry / schema / status model 设计草案~~ → **已完成**（§5c）
3. ~~Source → Schema 映射审查~~ → **已完成**（§5d）
4. ~~Registry YAML draft（10 源）~~ → **已完成**（§5e）
5. ~~JSON Schema draft（10 逻辑表）~~ → **已完成**（§5f）
6. ~~registry lint / schema validation plan 设计~~ → **已完成**（§5g）
7. ~~fixtures + mapper + schema validation v1~~ → **已完成**（§5h）
8. ~~B 类 corpus / document model / B-D 边界设计~~ → **已完成**（§6a）
9. ~~B 类 document_corpus source registry~~ → **已完成**（§6b）
10. ~~B 类 validation 口径 + category routing~~ → **已完成**（§6c）
11. ~~B 类 offline title routing 脚本 + benchmark~~ → **已完成**（§6d）
12. ~~Phase 1 found → B 类 document metadata fixtures~~ → **已完成**（§6e）
13. ~~B 类 document JSON Schema + fixture validation~~ → **已完成**（§6f）
14. ~~B 类 raw_file fixture seed + schema validation~~ → **已完成**（§6g）
15. ~~B 类 parser / chunker / parse quality 设计~~ → **已完成**（§6h）
16. ~~B 类 non-periodic document fixture seed + schema validation~~ → **已完成**（§6i）
17. ~~B 类 parse_run dry-run fixture + schema validation~~ → **已完成**（§6j）
18. ~~B 类 registry lint~~ → **已完成**（§6k）
19. ~~B 类 corpus retrieval validation 小样本设计~~ → **已完成**（§6l）
20. ~~B 类 retrieval ready-case 机制 + selector~~ → **已完成**（§6m）
21. ~~B 类 ready-case intake 模板 + 审核 checklist~~ → **已完成**（§6n）
22. ~~B 类 corpus retrieval 脚本骨架（dry-run）~~ → **已完成**（§6o）
23. ~~第一批真实 known-document 草稿填入 placeholder case（3 条）~~ → **已完成**（§6p）
24. ~~人工 checklist review → 3 条改 ready → selector → dry-run 复跑~~ → **已完成**（§6q）
25. ~~B 类 corpus retrieval live metadata v1~~ → **已完成**（§6r）
26. ~~补第 4 条 ready（board_resolution）+ periodic_guard 草稿~~ → **已完成**（§6s）
27. ~~periodic_guard_002 补 date 窗 → ready → guard live audit~~ → **已完成**（§6t）
28. 更多 category-sample / periodic_guard_001 live（暂缓）
29. ~~C 类 F10 / company profile source discovery 设计草案~~ → **已完成**（§7）
30. ~~C 类 company profile JSON Schema draft（6 schema）~~ → **已完成**（§7a）
31. ~~C 类 registry lint + known-company fixture schema validation~~ → **已完成**（§7b）
32. ~~C 类 DevTools probe plan + checklist + record template~~ → **已完成**（§7c）
33. ~~C 类 P1 probe record 文件（3 source × 3 company）~~ → **已完成**（§7d）
34. 人工 DevTools probe P1 → 填写 probe records → **已完成**（basic 2/3 + security 3/3）
35. ~~C 类 P1 probe review + YAML 回填决策 + field mapping draft~~ → **已完成**（§7f）
36. ~~C 类 P1 YAML backfill v1 + registry lint~~ → **已完成**（§7g）
37. ~~C 类 live validation v1 + 600000 预期对齐~~ → **LIVE_PASS**（§7h）
38. ~~C 类 basic_profile mapper draft + fixture schema validation~~ → **已完成**（§7i）
39. ~~C 类 security_profile mapper draft + fixture schema validation~~ → **已完成**（§7j）
40. ~~C 类 P2 DevTools probe plan + records 初始化~~ → **已完成**（§7k）
41. 人工 DevTools probe P2：`cninfo_executive_profile` @ 600000 首发
42. 可选：probe 官方 category code（B 类）
43. **暂不全量抓取、暂不入库**

**不要与 Phase 3 B 类并行抢主线时分散验证资源。**

---

## 5c. Phase 3 D 类设计草案（2026-07-05）

| 文档 | 内容 |
|------|------|
| [cninfo_d_class_source_registry_design.md](cninfo_d_class_source_registry_design.md) | source 分层、registry 字段、supported_modes、示例 |
| [cninfo_d_class_schema_draft.md](cninfo_d_class_schema_draft.md) | 9 逻辑表、source→schema 映射 |
| [cninfo_d_class_ingestion_status_model.md](cninfo_d_class_ingestion_status_model.md) | source/fetch/field/stability 状态与流转 |

**性质：** 设计草案；不入库、不写 migration、不写 verified。

---

## 5d. Phase 3 D 类映射审查（2026-07-05）

| 文档 | 内容 |
|------|------|
| [cninfo_d_class_source_to_schema_mapping_review.md](cninfo_d_class_source_to_schema_mapping_review.md) | 10 源 target 表、标准列 vs raw_only、confidence、缺口 |

**结论摘要：** 6 源 high / 3 源 medium；建议逻辑层新增 `d_event_party_detail`；`d_source_query_mode` 暂不必单独建表。

---

## 5e. Phase 3 Registry YAML Draft（2026-07-05）

| 文档 | 内容 |
|------|------|
| [cninfo_d_class_source_registry_draft.yaml](../config/cninfo_d_class_source_registry_draft.yaml) | 10 源 machine-readable registry（design_only） |
| [cninfo_d_class_source_registry_draft_notes.md](cninfo_d_class_source_registry_draft_notes.md) | YAML 说明、分层、supported_modes、caveat |

**覆盖：** 10/10 testing_stable_sample source；`verified: false` 全源；`raw_record_required: true` 全源。

---

## 5f. Phase 3 JSON Schema Draft（2026-07-05）

| 文档 | 内容 |
|------|------|
| [schemas/d_class/](../schemas/d_class/) | 10 个逻辑表 JSON Schema（draft-07） |
| [cninfo_d_class_json_schema_draft_notes.md](cninfo_d_class_json_schema_draft_notes.md) | Schema 说明、required 原则、registry 映射 |

**版本：** JSON Schema **draft-07**；业务 record 均要求 `raw_record_json` + `raw_record_hash`（field_semantics / registry 除外部分）。

---

## 5g. Phase 3 Registry Lint & Schema Validation Plan（2026-07-05）

| 文档 / 脚本 | 内容 |
|------|------|
| [cninfo_d_class_registry_lint_design.md](cninfo_d_class_registry_lint_design.md) | 23 条离线 lint 规则（R001–R023）；FAIL/WARN/INFO 分级 |
| [cninfo_d_class_schema_validation_plan.md](cninfo_d_class_schema_validation_plan.md) | registry / transformed record / raw snapshot 三类校验路线图 |
| [lab/lint_cninfo_d_class_registry.py](../lab/lint_cninfo_d_class_registry.py) | 本地 YAML + schema 文件一致性检查；`--registry` / `--schemas-dir` / `--strict` |

**当前结果：** 对 `cninfo_d_class_source_registry_draft.yaml` 跑 lint → **PASS**（10 源；17 条 INFO 为字段跨组提示，无 FAIL/WARN）。

**不做：** 不请求 CNINFO、不入库、不写 migration、不把 `testing_stable_sample` 升级为 `verified`。

---

## 5h. Phase 3 Fixture Schema Validation v1（2026-07-05）

| 文档 / 脚本 / 数据 | 内容 |
|------|------|
| [fixtures/d_class/](../fixtures/d_class/) | 11 个 `sample_raw.json`（10 源；shareholder_change inc/desc 各一） |
| [lab/cninfo_d_class_mappers.py](../lab/cninfo_d_class_mappers.py) | raw → 逻辑 record 最小 mapper 草案 |
| [lab/validate_cninfo_d_class_schema.py](../lab/validate_cninfo_d_class_schema.py) | jsonschema 离线校验；输出 CSV + MD |
| [cninfo_d_class_schema_validation_summary.md](../outputs/validation/cninfo_d_class_schema_validation_summary.md) | 汇总报告 |

**当前结果：** 11 fixture **PASS**；生成 **22** 条 logical record + 11 条 raw snapshot；**0** fail。

**Deferred：** `abnormal_trading` detail[] → `d_event_party_detail`；`block_trade` optional metric_daily ETL。

---

## 5b. Phase 2 分源索引（归档）

| 批次 | 总结文档 |
|------|----------|
| Priority-1 | [cninfo_table_sources_priority1_summary.md](../outputs/validation/cninfo_table_sources_priority1_summary.md) |
| Priority-1 稳定性 | [cninfo_table_sources_multidate_stability_summary.md](../outputs/validation/cninfo_table_sources_multidate_stability_summary.md) |
| Priority-2 | [cninfo_table_sources_priority2_current_summary.md](../outputs/validation/cninfo_table_sources_priority2_current_summary.md) |
| Priority-2 稳定性 | [cninfo_table_sources_priority2_stability_summary.md](../outputs/validation/cninfo_table_sources_priority2_stability_summary.md) |

---

---

## 6a. Phase 3 B 类 Corpus 设计草案（2026-07-05）

| 文档 | 内容 |
|------|------|
| [cninfo_b_class_corpus_design.md](cninfo_b_class_corpus_design.md) | B 类 corpus 职责、对象层级、document_type、status、与 A/D 关系、RAG 用途 |
| [cninfo_b_class_document_model_draft.md](cninfo_b_class_document_model_draft.md) | raw_file / document / section / chunk / citation / parse_run / event_document_link |
| [cninfo_b_vs_d_class_boundary.md](cninfo_b_vs_d_class_boundary.md) | B 类文档 vs D 类表格、反模式、连接键、架构建议 |

**性质：** 设计草案；**不**下载 PDF、**不**解析、**不**接库、**不写 verified**。

**与 A 类：** Phase 1 retrieval 结果（`pdf_url`、title、report_period）作为 B 类 `document` metadata seed。

**与 D 类：** 结构化 event/metric 留在 `schemas/d_class/`；B 类通过 `event_document_link` 引用证据 PDF。

**下一步（脚本阶段，非本批）：**
1. 补 B 类官方 `category` 码到 `cninfo_announcement_categories.yaml`。
2. 改造 `validate_cninfo_announcement_categories.py`：corpus + known-event 口径。

---

## 6b. Phase 3 B 类 Document Corpus Registry（2026-07-05）

| 文档 / 配置 | 内容 |
|------|------|
| [cninfo_b_class_source_registry_design.md](cninfo_b_class_source_registry_design.md) | `source_layer=document_corpus`、核心字段、与 D 类区别、validation 口径 |
| [config/cninfo_b_class_source_registry_draft.yaml](../config/cninfo_b_class_source_registry_draft.yaml) | 4 个初始 B 类 source YAML |
| [cninfo_b_class_source_registry_draft_notes.md](cninfo_b_class_source_registry_draft_notes.md) | YAML 说明、Phase 1 继承、title 分类原则 |

**初始 source（4）：**

| source_id | recommended_status | Phase 1 继承 |
|-----------|-------------------|----------------|
| `cninfo_periodic_report_pdf` | `testing_stable_sample` | 是（749/796） |
| `cninfo_general_announcement_pdf` | `candidate` | 否 |
| `cninfo_inquiry_reply_pdf` | `candidate` | 否（title 从 exclusion 转正向） |
| `cninfo_meeting_notice_pdf` | `candidate` | 否（title 从 exclusion 转正向） |

**与 D 类：** 独立 YAML；禁止混用 `records_path` / `target_logical_table`。

---

## 6c. Phase 3 B 类 Validation & Category Routing（2026-07-05）

| 文档 / 配置 | 内容 |
|------|------|
| [cninfo_b_class_validation_design.md](cninfo_b_class_validation_design.md) | 三种 validation 口径；废弃错误 success rate |
| [cninfo_b_class_category_routing_rules.md](cninfo_b_class_category_routing_rules.md) | Title 路由优先级；10 条示例 |
| [config/cninfo_announcement_categories.yaml](../config/cninfo_announcement_categories.yaml) | 4 路由组 + `legacy_category_key_map` |

**Validation 口径：**

| 方法 | 适用 category | source |
|------|---------------|--------|
| expected_period | `periodic_report` | `cninfo_periodic_report_pdf`（继承 P1 749/796） |
| known_document | `inquiry_reply`, `meeting_notice` | candidate sources |
| category_sample | `general_announcement` | `cninfo_general_announcement_pdf` |

**注意：** `category_code: null` — 官方 CNINFO category 码尚未锁定；`validate_cninfo_announcement_categories.py` **待迁移**。

---

## 6d. Phase 3 B 类 Offline Title Routing Validation（2026-07-05）

| 文档 / 脚本 / 输出 | 内容 |
|------|------|
| [lab/validate_cninfo_b_class_category_routing.py](../lab/validate_cninfo_b_class_category_routing.py) | 离线 title → route_to / document_type（无 CNINFO 请求） |
| [fixtures/b_class/known_documents/known_document_benchmark.yaml](../fixtures/b_class/known_documents/known_document_benchmark.yaml) | 16 条 offline benchmark |
| [cninfo_b_class_category_routing_summary.md](../outputs/validation/cninfo_b_class_category_routing_summary.md) | 汇总 |

**当前结果：** 16/16 route_match + document_type_match **PASS**；4/4 periodic false-positive guard 未误入 `cninfo_periodic_report_pdf`。

**未改：** `validate_cninfo_announcement_categories.py`（旧 14 类格式保留）。

---

## 6e. Phase 3 B 类 Document Metadata Seed（2026-07-05）

| 文档 / 脚本 / 输出 | 内容 |
|------|------|
| [lab/seed_cninfo_b_class_document_fixtures.py](../lab/seed_cninfo_b_class_document_fixtures.py) | Phase 1 `found=yes` → B 类 document metadata JSONL（无 CNINFO、无 PDF） |
| [periodic_report_document_fixtures.jsonl](../fixtures/b_class/document/periodic_report_document_fixtures.jsonl) | 20 条 periodic report metadata fixture |
| [cninfo_b_class_document_seed_report.csv](../outputs/validation/cninfo_b_class_document_seed_report.csv) | 逐条 seed 状态 |
| [cninfo_b_class_document_seed_summary.md](../outputs/validation/cninfo_b_class_document_seed_summary.md) | 汇总 |

**输入：** `cninfo_report_p1_coverage_validation.csv` + `cninfo_report_p1_identity_mapping.csv`（只读）。

**抽样：** 四类 periodic report 各 ≤5 条，总数 20；按 `company_code` 排序确定性抽样。

**当前结果：** 20 seeded / 0 skipped；`annual_report`×5、`semi_annual_report`×5、`quarterly_report_q1`×5、`quarterly_report_q3`×5。

**未改：** Phase 1 CSV / scripts；D 类 registry/schema/fixtures；`database/schema`。

---

## 6f. Phase 3 B 类 JSON Schema + Document Fixture Validation（2026-07-05）

| 文档 / 脚本 / 输出 | 内容 |
|------|------|
| [schemas/b_class/](../schemas/b_class/) | 8 个 B 类 logical record JSON Schema（draft-07） |
| [cninfo_b_class_json_schema_draft_notes.md](cninfo_b_class_json_schema_draft_notes.md) | Schema 覆盖、required 原则、与 registry/D 类区别 |
| [lab/validate_cninfo_b_class_document_schema.py](../lab/validate_cninfo_b_class_document_schema.py) | 离线校验 `b_document` vs periodic report JSONL |
| [cninfo_b_class_document_schema_validation_summary.md](../outputs/validation/cninfo_b_class_document_schema_validation_summary.md) | 汇总 |

**当前结果：** 20/20 **PASS**；`annual_report`×5、`semi_annual_report`×5、`quarterly_report_q1`×5、`quarterly_report_q3`×5。

**未校验（待 fixture）：** version、section、chunk、citation、parse_run、event_document_link。

**未改：** Phase 1 CSV/scripts；D 类 registry/schema/fixtures；现有 B 类 document fixture 原始文件；`database/schema`。

---

## 6g. Phase 3 B 类 Raw File Fixture Seed + Schema Validation（2026-07-05）

| 文档 / 脚本 / 输出 | 内容 |
|------|------|
| [lab/seed_cninfo_b_class_raw_file_fixtures.py](../lab/seed_cninfo_b_class_raw_file_fixtures.py) | document `pdf_url` → `b_raw_file` metadata JSONL |
| [periodic_report_raw_file_fixtures.jsonl](../fixtures/b_class/raw_file/periodic_report_raw_file_fixtures.jsonl) | 20 条 raw_file metadata（`download_status=not_started`） |
| [lab/validate_cninfo_b_class_raw_file_schema.py](../lab/validate_cninfo_b_class_raw_file_schema.py) | 离线 schema 校验 |
| [cninfo_b_class_raw_file_schema_validation_summary.md](../outputs/validation/cninfo_b_class_raw_file_schema_validation_summary.md) | 汇总 |

**派生规则：** `raw_file_id=raw_file_<document_id>`；`sha256`/`file_size`/`storage_uri`/`fetch_time` 均为 `null`。

**当前结果：** 20 documents → 20 raw_file seeded / 0 skipped；schema **20/20 PASS**。

**Schema 微调：** `b_raw_file.schema.json` 增加 `document_id`、`created_from`；nullable 字段支持 `null`。

---

## 6h. Phase 3 B 类 Parser / Chunker / Parse Quality 设计（2026-07-05）

| 文档 | 内容 |
|------|------|
| [cninfo_b_class_parser_chunker_plan.md](cninfo_b_class_parser_chunker_plan.md) | raw_file → parse_run → section → chunk → citation 流水线 |
| [cninfo_b_class_chunking_strategy.md](cninfo_b_class_chunking_strategy.md) | RAG chunk 粒度、size、metadata、validation |
| [cninfo_b_class_parse_quality_model.md](cninfo_b_class_parse_quality_model.md) | quality dimensions、flags、confidence、failure handling |

**性质：** 仅设计；不下载/解析 PDF、不跑 OCR、不生成 chunk/embedding、不写 verified。

**当前状态：** 20 条 document + raw_file metadata fixture 就绪；`download_status=not_started`；parse 链路待实施。

---

## 6i. Phase 3 B 类 Non-periodic Document Fixture Seed（2026-07-05）

| 文档 / 脚本 / 输出 | 内容 |
|------|------|
| [lab/seed_cninfo_b_class_non_periodic_document_fixtures.py](../lab/seed_cninfo_b_class_non_periodic_document_fixtures.py) | known-document benchmark → non-periodic document JSONL |
| [non_periodic_document_fixtures.jsonl](../fixtures/b_class/document/non_periodic_document_fixtures.jsonl) | 13 条 title-only metadata |
| [non_periodic_raw_file_fixtures.jsonl](../fixtures/b_class/raw_file/non_periodic_raw_file_fixtures.jsonl) | 空（无 pdf_url） |
| [lab/validate_cninfo_b_class_non_periodic_document_schema.py](../lab/validate_cninfo_b_class_non_periodic_document_schema.py) | schema 校验 + summary |
| [cninfo_b_class_non_periodic_document_schema_validation_summary.md](../outputs/validation/cninfo_b_class_non_periodic_document_schema_validation_summary.md) | 汇总 |

**输入：** `known_document_benchmark.yaml`（16 条）；跳过 3 条 periodic_report。

**当前结果：** 13 seeded / 3 skipped_periodic；schema **13/13 PASS**；`raw_file_seeded=0`。

**按 source_id：** `cninfo_inquiry_reply_pdf`×3 · `cninfo_meeting_notice_pdf`×3 · `cninfo_general_announcement_pdf`×7。

**`source_confidence=candidate`**；未升级为 `testing_stable_sample`。

**Schema 微调：** `b_document.schema.json` 可选字段支持 `null`（periodic 20 条回归仍 PASS）。

---

## 6j. Phase 3 B 类 Parse Run Dry-run Fixture + Schema Validation（2026-07-05）

| 文档 / 脚本 / 输出 | 内容 |
|------|------|
| [lab/seed_cninfo_b_class_parse_run_dry_run_fixtures.py](../lab/seed_cninfo_b_class_parse_run_dry_run_fixtures.py) | 33 document → parse_run dry-run JSONL |
| [document_parse_run_dry_run_fixtures.jsonl](../fixtures/b_class/parse_run/document_parse_run_dry_run_fixtures.jsonl) | `not_started`×20 + `skipped`×13 |
| [lab/validate_cninfo_b_class_parse_run_schema.py](../lab/validate_cninfo_b_class_parse_run_schema.py) | schema 校验 + summary |
| [cninfo_b_class_parse_run_schema_validation_summary.md](../outputs/validation/cninfo_b_class_parse_run_schema_validation_summary.md) | 汇总 |

**规则：** periodic → `not_started` + `raw_file_id`；non-periodic → `skipped` + `raw_file_id=null`；`parser_name=dry_run_no_parser`。

**当前结果：** 33/33 schema **PASS**；parser 未执行；PDF 未下载。

**Schema 微调：** `b_document_parse_run.schema.json` 增加 `raw_file_id`、`created_from`、`notes`；nullable `page_count`/`text_length`/`error_message`/`created_at`。

---

## 6k. Phase 3 B 类 Registry Lint（2026-07-05）

| 文档 / 脚本 / 输出 | 内容 |
|------|------|
| [cninfo_b_class_registry_lint_design.md](cninfo_b_class_registry_lint_design.md) | R001–R023 规则设计 |
| [lab/lint_cninfo_b_class_registry.py](../lab/lint_cninfo_b_class_registry.py) | registry + category + schema + fixture 一致性 lint |
| [cninfo_b_class_registry_lint_summary.md](../outputs/validation/cninfo_b_class_registry_lint_summary.md) | 汇总 |

**检查范围：** 4 B 类 source · category route_to · 8 schema 文件 · 33 document / 20 raw_file / 33 parse_run fixture。

**当前结果：** **23 rules PASS**；fail=0 warn=0；`verified` 全 false；non-periodic source 均为 `candidate`。

---

## 6l. Phase 3 B 类 Corpus Retrieval Validation 小样本设计（2026-07-05）

| 文档 / Fixture | 内容 |
|------|------|
| [cninfo_b_class_corpus_retrieval_validation_design.md](cninfo_b_class_corpus_retrieval_validation_design.md) | expected-period / known-document / category-sample 三口径 |
| [cninfo_b_class_retrieval_validation_next_steps.md](cninfo_b_class_retrieval_validation_next_steps.md) | live validation 前置与原则 |
| [known_document_retrieval_cases.yaml](../fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml) | 12 条 known-document case（**design_only**） |
| [category_sample_cases.yaml](../fixtures/b_class/retrieval_validation/category_sample_cases.yaml) | 9 条 category-sample case（**design_only**） |

**覆盖：** inquiry_reply×3 · regulatory_inquiry×3 · meeting_notice×2 · IR×2 · board×1 · shareholder×1 · general/inquiry/meeting samples · periodic false-positive guard×2。

**性质：** 不请求 CNINFO；`company_code`/`date_*` 多为 null placeholder；candidate **不升级**；不写 verified。

**未实现：** `lab/validate_cninfo_b_class_corpus_retrieval.py`（待真实样本就绪）。

---

## 6m. Phase 3 B 类 Retrieval Ready-Case 机制（2026-07-05）

| 文档 / 脚本 / 输出 | 内容 |
|------|------|
| [cninfo_b_class_retrieval_ready_case_rules.md](cninfo_b_class_retrieval_ready_case_rules.md) | `case_status` placeholder/ready/retired + required 字段 |
| [lab/select_cninfo_b_class_retrieval_ready_cases.py](../lab/select_cninfo_b_class_retrieval_ready_cases.py) | 离线 ready-case 筛选（无 CNINFO） |
| [cninfo_b_class_retrieval_ready_case_summary.md](../outputs/validation/cninfo_b_class_retrieval_ready_case_summary.md) | 汇总 |

**YAML 增强：** 21 条 case 均增 `case_status: placeholder`；无伪造 ready case。

**当前结果：** total=21 · placeholder=21 · ready=**0** · invalid_ready=0 · **NO_READY_CASES**。

**未来 live 脚本：** 仅消费 `ready_status=ready` 的 case。

---

## 6n. Phase 3 B 类 Ready-Case Intake 与审核清单（2026-07-05）

| 文档 / Fixture | 内容 |
|------|------|
| [cninfo_b_class_ready_case_intake_template.md](cninfo_b_class_ready_case_intake_template.md) | known-document / category-sample 填写模板 |
| [cninfo_b_class_ready_case_review_checklist.md](cninfo_b_class_ready_case_review_checklist.md) | 人工审核 checklist + selector 前置要求 |
| [ready_case_examples_do_not_run.yaml](../fixtures/b_class/retrieval_validation/ready_case_examples_do_not_run.yaml) | 4 条 **example_only** 结构参考（不参与 selector） |

**性质：** 不请求 CNINFO；21 条生产 case 仍为 `placeholder`；无伪造 ready。

---

## 6o. Phase 3 B 类 Corpus Retrieval Script Skeleton（2026-07-05）

| 文档 / 脚本 / 输出 | 内容 |
|------|------|
| [lab/validate_cninfo_b_class_corpus_retrieval.py](../lab/validate_cninfo_b_class_corpus_retrieval.py) | dry-run 骨架；默认不请求 CNINFO |
| [cninfo_b_class_corpus_retrieval_script_skeleton_notes.md](cninfo_b_class_corpus_retrieval_script_skeleton_notes.md) | skeleton / live 边界说明 |
| [cninfo_b_class_corpus_retrieval_dry_run_summary.md](../outputs/validation/cninfo_b_class_corpus_retrieval_dry_run_summary.md) | 汇总 |

**当前结果：** total=21 · ready=0 · invalid_ready=0 · query_executed=0 · **NO_READY_CASES**。

**`--no-dry-run`：** 拒绝执行（live mode not implemented）。

---

## 6p. Phase 3 B 类 Known-Document 真实样本草稿填入（2026-07-05）

| Fixture / 输出 | 内容 |
|------|------|
| [known_document_retrieval_cases.yaml](../fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml) | 3 条优先真实 CNINFO 样本候选字段已填入 |
| [cninfo_b_class_retrieval_ready_case_summary.md](../outputs/validation/cninfo_b_class_retrieval_ready_case_summary.md) | selector 复跑汇总 |
| [cninfo_b_class_corpus_retrieval_dry_run_summary.md](../outputs/validation/cninfo_b_class_corpus_retrieval_dry_run_summary.md) | dry-run 复跑汇总 |

**已填入 case（仍为 `case_status: placeholder`）：**

| case_id | company | document_type | 路由验证目标 |
|---------|---------|---------------|--------------|
| `inquiry_known_003` | 300165 天瑞仪器 | `inquiry_reply` | 年报问询函回复 → `cninfo_inquiry_reply_pdf`（非 annual_report） |
| `regulatory_known_002` | 002499 *ST科林 | `regulatory_inquiry` | 收到关注函 → `cninfo_inquiry_reply_pdf`（非 inquiry_reply） |
| `meeting_known_001` | 002480 新筑股份 | `meeting_notice` | 业绩说明会公告 → `cninfo_meeting_notice_pdf` |

**本轮红线（均已遵守）：**

1. 已填入 3 条真实样本候选字段
2. **所有 case_status 仍为 `placeholder`**（21/21）
3. **没有请求 CNINFO**
4. **没有下载 PDF**
5. **没有解析 PDF**
6. **没有写 verified**
7. selector 复跑：**total=21 · placeholder=21 · ready=0 · invalid_ready=0 · NO_READY_CASES**
8. dry-run 复跑：**ready_cases=0 · query_executed=0 · NO_READY_CASES**；全部 case 仍为 `skipped_placeholder`

**下一步：** 按 [review checklist](cninfo_b_class_ready_case_review_checklist.md) 人工审核上述 3 条；审核通过后再改 `case_status: ready`，然后复跑 selector 与 dry-run。

---

## 6q. Phase 3 B 类 Ready Case 人工审核通过（2026-07-05）

| Fixture / 输出 | 内容 |
|------|------|
| [known_document_retrieval_cases.yaml](../fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml) | 3 条 case `case_status` 改为 `ready` |
| [cninfo_b_class_retrieval_ready_case_summary.md](../outputs/validation/cninfo_b_class_retrieval_ready_case_summary.md) | selector：**PASS** |
| [cninfo_b_class_corpus_retrieval_dry_run_summary.md](../outputs/validation/cninfo_b_class_corpus_retrieval_dry_run_summary.md) | dry-run：**DRY_RUN_PASS** |

**Checklist 审核结论（3/3 通过）：**

| case_id | company | document_type | 日期窗 | 路由 |
|---------|---------|---------------|--------|------|
| `inquiry_known_003` | 300165 天瑞仪器 | `inquiry_reply` | 7 天 | `cninfo_inquiry_reply_pdf` |
| `regulatory_known_002` | 002499 *ST科林 | `regulatory_inquiry` | 5 天 | `cninfo_inquiry_reply_pdf` |
| `meeting_known_001` | 002480 新筑股份 | `meeting_notice` | 3 天 | `cninfo_meeting_notice_pdf` |

**验证结果：**

| 脚本 | 结果 |
|------|------|
| selector | total=21 · placeholder=18 · **ready=3** · invalid_ready=0 · **PASS** |
| dry-run | ready_cases=3 · query_executed=0 · **DRY_RUN_PASS** · 3 条 `would_query=true` |

**红线（均已遵守）：** 未请求 CNINFO · 未下载/解析 PDF · 未写 verified · 未升级 source status · 未改 `category_sample_cases.yaml`。

**下一步：** 评审是否在 `validate_cninfo_b_class_corpus_retrieval.py` 实现 live **metadata** request（`hisAnnouncement/query`）；仍不下载 PDF、不写 verified。

---

## 6r. Phase 3 B 类 Corpus Retrieval Live Metadata v1（2026-07-05）

| 脚本 / 输出 | 内容 |
|------|------|
| [lab/validate_cninfo_b_class_corpus_retrieval.py](../lab/validate_cninfo_b_class_corpus_retrieval.py) | `--live-metadata`：仅 ready known-document；默认仍为 dry-run |
| [cninfo_b_class_corpus_retrieval_live_report.csv](../outputs/validation/cninfo_b_class_corpus_retrieval_live_report.csv) | 3 条 live 明细 |
| [cninfo_b_class_corpus_retrieval_live_summary.md](../outputs/validation/cninfo_b_class_corpus_retrieval_live_summary.md) | **LIVE_PASS** |

**实现要点：**

- 显式 `--live-metadata` 才请求 CNINFO；`invalid_ready>0` 或 `ready=0` 时拒绝 live
- 沿用 Phase 1 `hisAnnouncement/query` + topSearch orgId；每条 case ≤2 次 query + sleep
- 标题匹配剥离 CNINFO `<em>` 高亮标签
- 离线 `route_title` 校验 `expected_route_to` / `expected_document_type`
- **不下载 PDF**；不写 verified；不升级 source status

**结果（3/3 pass）：**

| case_id | matched_date | pdf_url | classification | case_result |
|---------|--------------|---------|----------------|-------------|
| `inquiry_known_003` | 2024-05-27 | available | classified_correctly | pass |
| `regulatory_known_002` | 2023-01-31 | available | classified_correctly | pass |
| `meeting_known_001` | 2025-05-08 | available | classified_correctly | pass |

`query_executed=3` · placeholder / category-sample **未请求**。

**下一步：** 补更多 ready case；category-sample live 暂缓；仍不下载 PDF。

---

## 6s. Phase 3 B 类 Ready Case #4–5 扩充（2026-07-05）

| Case | 状态 | 说明 |
|------|------|------|
| `board_resolution_known_001` | **ready** | 威孚高科 000581；`cninfo_general_announcement_pdf` / `board_resolution` |
| `periodic_guard_002` | **placeholder** | 字段草稿已补；`date_start`/`date_end` 仍 null，**未 ready** |

**board_resolution 标题校正：** 建议的「第十一届董事会第六次会议决议公告」在 CNINFO 检索未命中；实际 2025-04-17 公告标题为 **「董事会决议公告」**，已按 checklist 核对后写入 `title_pattern`。

**验证结果：**

| 脚本 | 结果 |
|------|------|
| selector | total=21 · ready=**4** · placeholder=17 · invalid_ready=0 · **PASS** |
| dry-run | ready=4 · query_executed=0 · **DRY_RUN_PASS** |
| live metadata | query_executed=**4** · pass=**4** · **LIVE_PASS** |

**红线：** PDF 未下载/解析 · 未写 verified · 未升级 source status · `periodic_guard_002` 与 17 条 placeholder **未请求**。

---

## 6t. Phase 3 B 类 periodic_guard_002 False-Positive Guard Live Audit（2026-07-05）

| Case / 输出 | 内容 |
|------|------|
| `periodic_guard_002` | category-sample guard；**ready** |
| date window | **2025-03-27 ~ 2025-04-02**（7 天；来源 Phase 1 年报摘要披露季） |
| [live report](../outputs/validation/cninfo_b_class_corpus_retrieval_live_report.csv) | guard pass |

**脚本扩展：** `validate_cninfo_b_class_corpus_retrieval.py` 新增 `process_live_guard_case`；仅 `periodic_guard_*` ready case 做全市场 metadata 查询 + route guard；其他 category-sample live 仍 deferred。

**Guard 结果：**

| 指标 | 值 |
|------|------|
| matched_title | `2024年年度报告摘要`（示例） |
| predicted_route_to | `cninfo_general_announcement_pdf` |
| predicted_document_type | `announcement` |
| 误入 periodic_report | **0** / 29 条摘要标题 |
| case_result | **pass** |

**总体验证（含 4 known-document）：** ready=5 · query_executed=5 · pass=5 · **LIVE_PASS**

---

## 6. Phase 3 — B 类事件公告验证（设计后实施）

1. ~~B 类 validation 口径 + category routing 配置~~ → **已完成**（§6c）。
2. 改造 `validate_cninfo_announcement_categories.py`：corpus 口径 + known-document / category-sample；**禁止**随机公司 success rate 作主指标。
3. 后续：官方 `category` 码 probe 后填入 YAML（当前 `category_code: null`）。

---

## 7. Phase 4 — C 类 F10 / Company Profile（设计启动 · 2026-07-05）

| 文档 / 配置 | 内容 |
|------|------|
| [cninfo_c_class_f10_source_discovery_design.md](cninfo_c_class_f10_source_discovery_design.md) | C 类 source discovery 方法、验证口径、状态机 |
| [cninfo_c_class_profile_data_model_draft.md](cninfo_c_class_profile_data_model_draft.md) | `company_profile_snapshot` 及子 profile 逻辑模型 |
| [cninfo_c_vs_b_vs_d_boundary.md](cninfo_c_vs_b_vs_d_boundary.md) | C 与 B / D 边界（画像 vs 文档 vs 表格行） |
| [cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml) | **10** 候选源；`recommended_status: candidate`；`endpoint: null` |

**C 类定位：** company profile snapshot / F10 / Wiki profile base；**不是** B 类 document corpus，**不是** D 类 fixed-table event。

**初始候选 source（10）：** basic · industry · business_scope · executive · share_capital · top_shareholders · top_float_shareholders · dividend_financing · contact · security。

**红线：** 不入库 · 不写 migration · 不写 verified · 不做全市场 F10 抓取 · 不下载/解析 PDF。

**下一步：** 见 §7g — live validation（600000 / 300001 / 688001）→ mapper 草案。

---

## 7a. Phase 4 C 类 Company Profile JSON Schema Draft（2026-07-05）

| 文档 / Schema | 内容 |
|------|------|
| [schemas/c_class/](../schemas/c_class/) | **6** 个 logical record JSON Schema（draft-07） |
| [cninfo_c_class_json_schema_draft_notes.md](cninfo_c_class_json_schema_draft_notes.md) | 覆盖范围、required 原则、B/D 区别 |

**Schema 列表：**

| 文件 | 逻辑对象 |
|------|----------|
| `c_company_profile_snapshot.schema.json` | 顶层 profile snapshot |
| `c_company_basic_profile.schema.json` | 基本资料 |
| `c_executive_profile.schema.json` | 高管 / 董事名单 |
| `c_share_capital_profile.schema.json` | 股本结构 |
| `c_shareholder_profile.schema.json` | 十大股东 / 流通股东 |
| `c_profile_raw_snapshot.schema.json` | 抓取层 raw JSON |

**原则：** `source_status` 最高 `testing_stable_sample`；**无 verified**；`raw_record_json` 必留；endpoint 未 probe 前非 required。

---

## 7b. Phase 4 C 类 Registry Lint + Offline Fixture Schema Validation（2026-07-05）

| 文档 / 脚本 / 输出 | 内容 |
|------|------|
| [cninfo_c_class_registry_lint_design.md](cninfo_c_class_registry_lint_design.md) | R001–R012 规则设计 |
| [lab/lint_cninfo_c_class_registry.py](../lab/lint_cninfo_c_class_registry.py) | candidate YAML + schema 一致性 lint |
| [cninfo_c_class_registry_lint_summary.md](../outputs/validation/cninfo_c_class_registry_lint_summary.md) | lint 汇总 |
| [known_company_profile_fixtures.jsonl](../fixtures/c_class/known_company_profile_fixtures.jsonl) | **12** 条 offline known-company fixture（600000 / 300001 / 688001） |
| [lab/validate_cninfo_c_class_profile_schema.py](../lab/validate_cninfo_c_class_profile_schema.py) | jsonschema 离线校验；输出 CSV + MD |
| [cninfo_c_class_profile_schema_validation_summary.md](../outputs/validation/cninfo_c_class_profile_schema_validation_summary.md) | fixture validation 汇总 |

**Lint 当前结果：** **12 rules PASS**；fail=0 warn=0 info=4；10 source 全 `candidate`；endpoint 全 null（INFO，不 FAIL）。

**Fixture 当前结果：** **12/12 PASS**；覆盖 6 schema × 3 公司（每公司 snapshot + basic + raw；600000 另含 executive / share_capital / shareholder 各 1 条）。

**性质：** offline shape test；**不请求 CNINFO**；不 probe endpoint；**不写 verified**；不代表 source 可用。

**未改：** Phase 1 CSV/scripts；B/D registry/schema/fixtures/live reports；`database/schema`。

**下一步：** 按 [probe plan](cninfo_c_class_devtools_probe_plan.md) 执行 P1 DevTools probe → 填写 probe record → 审查后回填 YAML `endpoint`。

---

## 7c. Phase 4 C 类 DevTools Probe Plan + Checklist（2026-07-05）

| 文档 / 模板 | 内容 |
|------|------|
| [cninfo_c_class_devtools_probe_plan.md](cninfo_c_class_devtools_probe_plan.md) | endpoint discovery 方法、P1–P3 优先级、记录字段、probe_status、回填规则 |
| [cninfo_c_class_probe_checklist.md](cninfo_c_class_probe_checklist.md) | probe 前 / DevTools / response / 回填前检查清单 |
| [c_class_probe_record_template.yaml](../fixtures/c_class/probe/c_class_probe_record_template.yaml) | `template_only` probe record 结构示例 |

**Probe 范围：** known companies **600000 / 300001 / 688001**；每 source **1–3 家**。

**P1 优先：** `cninfo_company_basic_profile` · `cninfo_company_security_profile` · `cninfo_company_industry_profile`。

**性质：** 仅设计准备；**未请求 CNINFO**；**未回填 endpoint**；`recommended_status` 仍为 `candidate`；**不写 verified**。

**未改：** `config/cninfo_c_class_source_candidates.yaml` 的 endpoint/status；Phase 1 / B / D 类文件。

**下一步：** 见 §7f — probe review 完成；待 YAML 回填。

---

## 7d. Phase 4 C 类 P1 Probe Records（2026-07-05 · 已填写）

| 文档 / 数据 | 内容 |
|------|------|
| [c_class_p1_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p1_probe_records.yaml) | P1 三源 × 三公司 = **9** 条 `probe_records` |
| [cninfo_c_class_p1_probe_execution_notes.md](cninfo_c_class_p1_probe_execution_notes.md) | 执行顺序、填写字段、`endpoint_found` 判定 |

**当前 probe 结果：** basic **2/3** endpoint_found + **1/3** empty；security **3/3** endpoint_found；industry **3/3** needs_more_probe（derived 字段已观察）；`getHeadStripData` annex 已记录。

**未改：** `config/cninfo_c_class_source_candidates.yaml` endpoint/status。

---

## 7f. Phase 4 C 类 P1 Probe Review + YAML Backfill Decision（2026-07-06）

| 文档 | 内容 |
|------|------|
| [cninfo_c_class_p1_probe_review.md](cninfo_c_class_p1_probe_review.md) | P1 probe 结果审查 |
| [cninfo_c_class_p1_yaml_backfill_decision.md](cninfo_c_class_p1_yaml_backfill_decision.md) | 建议回填 basic + security；industry 暂缓；annex 不回填 |
| [cninfo_c_class_basic_profile_field_mapping_draft.md](cninfo_c_class_basic_profile_field_mapping_draft.md) | getCompanyIntroduction 字段映射草案 |

**回填决策摘要：**

| source_id | 建议 |
|-----------|------|
| `cninfo_company_basic_profile` | **回填** getCompanyIntroduction（最多 `testing`） |
| `cninfo_company_security_profile` | **回填** marketOverview（最多 `testing`） |
| `cninfo_company_industry_profile` | **暂缓**；`derived_from` basic |
| `getHeadStripData` | **不回填**独立 source |

**性质：** 决策草案；~~candidate YAML 尚未修改~~ → **P1 backfill v1 已完成**（§7g）。

**下一步：** C 类 live validation script（3 家 known company）。

---

## 7g. Phase 4 C 类 P1 YAML Backfill v1（2026-07-06）

| 变更 | 内容 |
|------|------|
| [cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml) | P1 endpoint 回填 |
| [cninfo_c_class_registry_lint_summary.md](../outputs/validation/cninfo_c_class_registry_lint_summary.md) | lint 复跑 **PASS**（14 rules） |

**回填摘要：**

| source_id | recommended_status | endpoint | 备注 |
|-----------|-------------------|----------|------|
| `cninfo_company_basic_profile` | **testing** | getCompanyIntroduction | 2/3 found + 1 empty |
| `cninfo_company_security_profile` | **testing** | marketOverview + `annex_endpoints` getHeadStripData | 3/3 found |
| `cninfo_company_industry_profile` | **candidate** | null | `derived_from_candidate` → basic |
| 其余 7 源 | **candidate** | null | 未变 |

**红线遵守：** `verified: false` 全库；无 `testing_stable_sample`；getHeadStripData **仅** annex，非独立 source；不入库。

**Lint：** `lab/lint_cninfo_c_class_registry.py` 扩展 R005/R006/R013/R014；**fail=0**。

**下一步：** basic_profile mapper 草案；复核 600000 empty 态变化。

---

## 7h. Phase 4 C 类 Live Source Validation v1（2026-07-06）

| 脚本 / 输出 | 内容 |
|------|------|
| [validate_cninfo_c_class_live_sources.py](../lab/validate_cninfo_c_class_live_sources.py) | `--dry-run` 默认；`--live` 验证 basic + security（3 家 × 2 源 = 6 请求） |
| [cninfo_c_class_live_source_validation_summary.md](../outputs/validation/cninfo_c_class_live_source_validation_summary.md) | 汇总 |

**Live 结果（2026-07-06，预期对齐后复跑）：**

| source | case pass | retrieval |
|--------|-----------|-----------|
| `cninfo_company_security_profile` | **3/3** | 3/3 endpoint_found |
| `cninfo_company_basic_profile` | **3/3** | 3/3 endpoint_found |

**结果：** **LIVE_PASS**（6/6 cases）。600000 `expected_basic_result` 已从 `empty_but_valid_response` 调整为 `endpoint_found`；DevTools 空态保留于 probe `historical_observations` 与 YAML `known_caveats`。无 blocked / schema_unexpected。

**红线：** sources 仍 **testing**；**无 verified**；**无 testing_stable_sample**；不入库；仅 3 家样本。

**下一步：** ~~security_profile mapper~~ → 见 §7j；或 P2 probe。

---

## 7i. Phase 4 C 类 Basic Profile Mapper Draft（2026-07-06）

| 脚本 / 输出 | 内容 |
|------|------|
| [cninfo_c_class_mappers.py](../lab/cninfo_c_class_mappers.py) | `map_company_basic_profile()` — getCompanyIntroduction → `c_company_basic_profile` |
| [seed_cninfo_c_class_basic_profile_fixtures.py](../lab/seed_cninfo_c_class_basic_profile_fixtures.py) | 内置 300001 / 688001 简化 raw → JSONL |
| [basic_profile_fixtures.jsonl](../fixtures/c_class/basic_profile/basic_profile_fixtures.jsonl) | **2** 条 mapped fixture |
| [validate_cninfo_c_class_basic_profile_schema.py](../lab/validate_cninfo_c_class_basic_profile_schema.py) | schema 校验 |
| [cninfo_c_class_basic_profile_mapper_summary.md](../outputs/validation/cninfo_c_class_basic_profile_mapper_summary.md) | mapper 汇总 |
| [cninfo_c_class_basic_profile_schema_validation_summary.md](../outputs/validation/cninfo_c_class_basic_profile_schema_validation_summary.md) | **2/2 PASS** |

**样本：** 300001 特锐德、688001 华兴源创（非空 embedded raw）；600000 无完整 raw body，未纳入 fixture。

**红线：** `source_status=testing`；**无 verified**；不入库；未修改 schema。

**下一步：** ~~security_profile mapper~~ → 见 §7j。

---

## 7j. Phase 4 C 类 Security Profile Mapper Draft（2026-07-06）

| 脚本 / 输出 | 内容 |
|------|------|
| [cninfo_c_class_mappers.py](../lab/cninfo_c_class_mappers.py) | `map_company_security_profile()` — marketOverview → `c_company_security_profile` |
| [c_company_security_profile.schema.json](../schemas/c_class/c_company_security_profile.schema.json) | **新增** security profile 逻辑 schema（draft-07） |
| [seed_cninfo_c_class_security_profile_fixtures.py](../lab/seed_cninfo_c_class_security_profile_fixtures.py) | 内置 600000 / 300001 / 688001 marketOverview raw → JSONL |
| [security_profile_fixtures.jsonl](../fixtures/c_class/security_profile/security_profile_fixtures.jsonl) | **3** 条 mapped fixture |
| [validate_cninfo_c_class_security_profile_schema.py](../lab/validate_cninfo_c_class_security_profile_schema.py) | schema 校验 |
| [cninfo_c_class_security_profile_mapper_summary.md](../outputs/validation/cninfo_c_class_security_profile_mapper_summary.md) | mapper 汇总 |
| [cninfo_c_class_security_profile_schema_validation_summary.md](../outputs/validation/cninfo_c_class_security_profile_schema_validation_summary.md) | **3/3 PASS** |

**样本：** 600000 浦发银行、300001 特锐德、688001 华兴源创（embedded marketOverview root；9 字段）。

**字段：** secCode/secName/secType/tradingStatus/age/finance/delisted/sshk/szhk → schema 对应列；`exchange` 由 company_code 前缀推断（candidate）。

**红线：** `source_status=testing`；**无 verified**；不入库；未升级 `testing_stable_sample`；新增 schema 为最小 lineage + marketOverview 字段闭包。

**下一步：** getHeadStripData annex 映射；P2 DevTools probe。

---

## 7k. Phase 4 C 类 P2 DevTools Probe Plan Initialized（2026-07-06）

| 文档 / 产出 | 内容 |
|------|------|
| [cninfo_c_class_p2_probe_plan.md](cninfo_c_class_p2_probe_plan.md) | P2 scope：executive / share_capital / top_shareholders / top_float_shareholders |
| [cninfo_c_class_p2_probe_checklist.md](cninfo_c_class_p2_probe_checklist.md) | 人工 probe 前/中/后检查；YAML backfill 准入条件 |
| [c_class_p2_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p2_probe_records.yaml) | **12** 条（4 source × 3 company），全部 `manual_probe_pending` |

**P2 优先 source：** `cninfo_executive_profile`、`cninfo_share_capital_profile`、`cninfo_top_shareholders_profile`、`cninfo_top_float_shareholders_profile`。

**暂缓：** dividend_financing、contact、business_scope、getHeadStripData annex。

**Known companies：** 600000 / 300001 / 688001（与 P1 相同）。

**红线：** 本轮 **0** CNINFO 请求；**无 verified**；**无 testing_stable_sample**；不入库；不修改 candidate YAML。

**下一步：** 人工 DevTools probe **`c_p2_executive_600000`**（高管/董监高 tab）→ 填写 probe record → 按 checklist 判定 status。

---

## 7e. Phase 4 — E / F（C probe 后再做）

- **E**：可达性三态脚本（公开 / 需登录 / 需权限），不采数据。
- **F**：仅记可达性，暂缓。

---

## 8. 便宜模型通用开场

```
这是 CNINFO Era C 项目。先读：
- PROJECT_MAP.md
- plans/cninfo_data_source_layered_inventory.md
- plans/eraC_execution_plan.md
当前 Phase：C 类 **P1 mapper 完成** + **P2 probe plan 已初始化**（12 pending）；下一步人工 probe `cninfo_executive_profile` @ 600000。只做该 Phase，不要同时展开其他 Phase。
红线见 eraC_execution_plan 第 1 节。recommended_status 不写 verified。
我要做的是：<具体任务>
```

---

## 9. 旧任务清单（已 supersede，仅供参考）

- ~~Phase 1 coverage 重算~~ → **已完成**
- ~~任务 0 穷尽收集 → 已并入 A–F 分层表~~
- ~~任务 A 完成 → 旧脚本保留为 deprecated 参考~~

---

## 10. 额度作战（怎么挺到月底）

- 7/2–7/16：主用账号2，省着花；账号1 剩量只救火。
- 7/16 账号1 刷新：7/16–7/27 优先账号1。
- 7/27 账号2 刷新：7/27–7/31 用新账号2。
- **便宜模型干 80%**（写脚本、写文档）；**高级模型只干 Phase 规划/复盘/卡死**。
