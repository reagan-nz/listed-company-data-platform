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
41. ~~C 类 P2 executive_profile 人工 DevTools probe~~ → **3/3 endpoint_found**（§7l）
42. ~~C 类 P2 share_capital + shareholders 人工 DevTools probe~~ → **P2-A 12/12 endpoint_found**（§7m）
43. ~~C 类 P2-A YAML backfill decision 起草~~ → **已完成**（§7n）
44. ~~C 类 P2-A YAML backfill v1 + registry lint~~ → **已完成**（§7o）
45. ~~C 类 P2-A live validation v1~~ → **LIVE_PASS**（§7p）
46. ~~C 类 executive_profile mapper draft + fixture schema validation~~ → **已完成**（§7q）
47. ~~C 类 share_capital_profile mapper draft + fixture schema validation~~ → **已完成**（§7r）
48. ~~C 类 shareholder_profile mapper draft + fixture schema validation~~ → **已完成**（§7s）
49. ~~C 类 P2-A mapper completion summary~~ → **已完成**（§7t）
50. ~~C 类 status consolidation summary~~ → **已完成**（§7u）
51. ~~C 类 P2-B probe plan + records 初始化~~ → **已完成**（§7v）
52. ~~C 类 P2-B dividend_financing manual probe~~ → **3/3 endpoint_found**（§7w）
53. ~~C 类 P2-B contact_profile 600000 probe~~ → **derived**（§7x）
54. ~~C 类 P2-B contact_profile 3/3 derived~~ → **已完成**（§7y）
55. ~~C 类 P2-B business_scope 3/3 derived~~ → **已完成**（§7z）
56. ~~C 类 P2-B industry_profile derived recheck~~ → **3/3 derived**（§7aa）
57. ~~C 类 P2-B source decision table~~ → **已完成**（§7ab）
58. ~~30-company smoke（含退市）~~ → **LIVE_PARTIAL**（§7ac）
59. ~~30-company smoke（active-only）~~ → **完成**（§7ad · [active summary](../outputs/validation/cninfo_c_class_scale_smoke_30_active_summary.md)）
60. dividend_history YAML backfill → **GO（仅决策 · 暂不执行）**（§7ad）
61. 扩至 200 家 → **CONDITIONAL YES**（§7ad · [200 plan](cninfo_c_class_scale_smoke_200_plan.md)）
62. ~~active 200 样本派生 + dry-run checkpoint~~ → **PASS**（§7ae）
63. ~~shareholder / security 口径文档化~~ → **完成**（§7af）
64. ~~200 live smoke~~ → **LIVE_PARTIAL**（§7ag）
65. ~~BSE failure diagnosis~~ → **完成**（§7ag）
66. ~~universe split + sample cleaning~~ → **完成**（§7ah）
67. ~~non-BSE 1000-like 离线派生 + dry-run~~ → **完成**（§7ai）
68. ~~non-BSE 1000-like live~~ → **完成**（§7aj · LIVE_PARTIAL）
69. ~~targeted retry 样本 + dry-run~~ → **完成**（§7ak）
70. ~~partial-fail targeted retry live~~ → **完成**（§7al · LIVE_PARTIAL）
71. ~~C-class source status decision~~ → **完成**（§7am）
72. ~~stable 200 non-BSE 样本 + dry-run~~ → **完成**（§7an）
73. ~~stable 200 live~~ → **完成**（§7ao · LIVE_PARTIAL）
74. ~~stable 200 post-live diagnosis~~ → **完成**（§7ao）
75. ~~stable 200 二次清洗~~ → **暂停**（§7ap · 人工审计 overturn）
76. ~~12 six-fail endpoint/parser debug~~ → **完成**（§7aq）
77. ~~runner 退避/重试 + orgId fallback~~ → **完成**（§7ar）
78. ~~12 家 retry 样本 + dry-run~~ → **完成**（§7ar）
79. ~~12 家 targeted retry live~~ → **LIVE_PASS**（§7as）
80. ~~stable 200 rerun（新版 runner）~~ → **LIVE_PASS**（§7at）
81. ~~stable 200 live pass decision~~ → **完成**（§7at）
82. ~~889 non-BSE rerun plan + dry-run~~ → **完成**（§7au）
83. ~~889 non-BSE rerun live~~ → **LIVE_PARTIAL**（§7av）
84. ~~post-889 diagnosis~~ → **完成**（§7av）
85. ~~partial-fail targeted retry 设计~~ → **完成**（§7aw）
86. ~~26 家 all6 hold 标注~~ → **完成**（§7aw）
87. ~~partial-fail targeted retry live~~ → **LIVE_PARTIAL**（§7ax）
88. ~~post-retry decision~~ → **完成**（§7ax）
89. ~~C-class field inventory~~ → **完成**（§7ay）
90. ~~C-class harvest planning~~ → **完成**（§7az）
91. ~~harvest runner dry-run~~ → **PASS**（§7ba）
92. ~~dividend_history mapper spec~~ → **完成**（§7bb）
93. ~~dividend_history mapper 代码~~ → **完成**（§7bc · fixture 5/5）
94. ~~harvest runner dry-run validation~~ → **PASS**（§7bd）
95. ~~harvest live runner smoke~~ → **PASS**（§7be · limit=10）
96. ~~863 full harvest approval plan~~ → **完成**（§7bf）
97. ~~harvest runner 安全控制~~ → **完成**（§7bg · safety test 5/5）
98. 863 full harvest 执行 → **PENDING_APPROVAL**（`full_harvest_gate`）
99. dividend_history YAML registry → **GO（decision only）** · **不执行 backfill**
100. BSE legacy targeted probe（8 家）→ **待启动**
101. **暂不全量 harvest live、暂不入库**

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

**下一步：** ~~人工 DevTools probe `c_p2_executive_600000`~~ → 见 §7l。

---

## 7l. Phase 4 C 类 P2 Executive Profile Probe（2026-07-06）

| 项 | 结果 |
|----|------|
| Source | `cninfo_executive_profile` |
| Probe matrix | 600000 / 300001 / 688001 |
| probe_status | **3/3 `endpoint_found`** |
| Endpoint | `GET https://www.cninfo.com.cn/data20/companyOverview/getCompanyExecutives?scode={company_code}` |
| records_path | `data.records` |
| row_count | 19 / 17 / 13 |
| Probe records | [c_class_p2_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p2_probe_records.yaml) |

**共享字段：** F002V, F010V, F012V, F017V, F009V, F005N, F012N, SEQID, F001V（见 probe record `candidate_field_mapping`）。

**红线：** **无 verified**；**无 testing_stable_sample**；**无 candidate YAML backfill**（本轮）；不入库；未保存 Cookie/SID/Authorization。

**下一步：** 起草 executive_profile YAML backfill decision；或继续 P2 probe `cninfo_share_capital_profile`。

---

## 7m. Phase 4 C 类 P2-A Probe Complete（2026-07-06）

| source_id | endpoint_found | Endpoint | row_count (600000/300001/688001) |
|-----------|----------------|----------|----------------------------------|
| `cninfo_executive_profile` | **3/3** | `GET .../getCompanyExecutives?scode=` | 19 / 17 / 13 |
| `cninfo_share_capital_profile` | **3/3** | `GET .../getStockStructure?scode=` | 5 / 5 / 5 |
| `cninfo_top_shareholders_profile` | **3/3** | `GET .../getTopTenStockholders?scode=` | 50 / 50 / 50 |
| `cninfo_top_float_shareholders_profile` | **3/3** | `GET .../getTopTenCirculatingStockholders?scode=` | 50 / 50 / 50 |

**合计：** **12/12 `endpoint_found`**。records_path 均为 `data.records`。无 blocked / login / captcha / schema_unexpected。

**红线：** **无 verified**；**无 testing_stable_sample**；**无 candidate YAML backfill**（本轮）；不入库。

**下一步：** ~~起草 P2-A YAML backfill decision~~ → 见 §7n；应用 P2-A YAML backfill v1。

---

## 7n. Phase 4 C 类 P2-A YAML Backfill Decision（2026-07-06）

| 文档 | 内容 |
|------|------|
| [cninfo_c_class_p2a_yaml_backfill_decision.md](cninfo_c_class_p2a_yaml_backfill_decision.md) | P2-A 四源 YAML 回填决策 |

**决策：** 四个 P2-A source **允许**后续 YAML backfill → `recommended_status: testing`，`verified: false`。

| source_id | decision | max_status |
|-----------|----------|------------|
| `cninfo_executive_profile` | allow_yaml_backfill | testing |
| `cninfo_share_capital_profile` | allow_yaml_backfill | testing |
| `cninfo_top_shareholders_profile` | allow_yaml_backfill | testing |
| `cninfo_top_float_shareholders_profile` | allow_yaml_backfill | testing |

**本轮：** decision **已执行** → [cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml) P2-A backfill v1；registry lint **PASS**。

**红线：** **无 verified**；**无 testing_stable_sample**；不入库。

**下一步：** P2-A YAML backfill v1 → ~~registry lint~~ → 见 §7o；P2-A live validation。

---

## 7o. Phase 4 C 类 P2-A YAML Backfill v1（2026-07-06）

| 项 | 结果 |
|----|------|
| Candidate YAML | [cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml) |
| Backfilled sources | executive · share_capital · top_shareholders · top_float_shareholders |
| `recommended_status` | **testing**（四源） |
| `verified` | **false**（全部） |
| Registry lint | **PASS**（14 rules · fail=0） |
| Testing sources total | **6/10**（P1 basic + security + P2-A 四源） |

| source_id | endpoint |
|-----------|----------|
| `cninfo_executive_profile` | `GET .../getCompanyExecutives?scode=` |
| `cninfo_share_capital_profile` | `GET .../getStockStructure?scode=` |
| `cninfo_top_shareholders_profile` | `GET .../getTopTenStockholders?scode=` |
| `cninfo_top_float_shareholders_profile` | `GET .../getTopTenCirculatingStockholders?scode=` |

**红线：** **无 verified**；**无 testing_stable_sample**；不入库；无 live request（本轮）。

**下一步：** ~~P2-A live validation~~ → 见 §7p；P2-A mapper drafts。

---

## 7p. Phase 4 C 类 P2-A Live Validation v1（2026-07-06）

| 脚本 / 输出 | 内容 |
|------|------|
| [validate_cninfo_c_class_p2a_live_sources.py](../lab/validate_cninfo_c_class_p2a_live_sources.py) | 3 家 × 4 源 · 默认 `--dry-run` · `--live` 最多 12 请求 |
| [cninfo_c_class_p2a_live_source_validation_summary.md](../outputs/validation/cninfo_c_class_p2a_live_source_validation_summary.md) | **LIVE_PASS 12/12** |

| source_id | endpoint_found | case pass |
|-----------|----------------|-----------|
| `cninfo_executive_profile` | **3/3** | **3/3** |
| `cninfo_share_capital_profile` | **3/3** | **3/3** |
| `cninfo_top_shareholders_profile` | **3/3** | **3/3** |
| `cninfo_top_float_shareholders_profile` | **3/3** | **3/3** |

**Dry-run：** 12 skipped。**Live：** no blocked / schema_unexpected / http_error。

**Shape note：** required field check uses **key presence** on `records[0]`; null values on optional/candidate fields (e.g. executive `F005N`) do not fail.

**红线：** sources 仍 **testing**；**无 verified**；**无 testing_stable_sample**；不入库。

**下一步：** P2-A mapper drafts 全部完成（§7q–§7s）；completion summary **done**（§7t）。

---

## 7q. Phase 4 C 类 Executive Profile Mapper Draft（2026-07-06）

| 脚本 / 输出 | 内容 |
|------|------|
| [cninfo_c_class_mappers.py](../lab/cninfo_c_class_mappers.py) | `map_company_executive_profile()` — getCompanyExecutives row → `c_executive_profile` |
| [seed_cninfo_c_class_executive_profile_fixtures.py](../lab/seed_cninfo_c_class_executive_profile_fixtures.py) | 内置 6 行（600000×2 · 300001×2 · 688001×2） |
| [executive_profile_fixtures.jsonl](../fixtures/c_class/executive_profile/executive_profile_fixtures.jsonl) | **6** 条 mapped fixture |
| [validate_cninfo_c_class_executive_profile_schema.py](../lab/validate_cninfo_c_class_executive_profile_schema.py) | schema 校验 |
| [cninfo_c_class_executive_profile_schema_validation_summary.md](../outputs/validation/cninfo_c_class_executive_profile_schema_validation_summary.md) | **6/6 PASS** |

**映射：** F002V→person_name, F009V→position, F010V→gender_candidate, F012V→birth_year_candidate, F017V→education_candidate；F005N/F012N/SEQID/F001V 留在 raw_record_json。

**红线：** `source_status=testing`；**无 verified**；不入库；schema 未修改。

**下一步：** share_capital_profile **done**（§7r）；shareholder_profile mapper draft next。

---

## 7r. Phase 4 C 类 Share Capital Profile Mapper Draft（2026-07-06）

| 脚本 / 输出 | 内容 |
|------|------|
| [cninfo_c_class_mappers.py](../lab/cninfo_c_class_mappers.py) | `map_company_share_capital_profile()` — getStockStructure row → `c_share_capital_profile` |
| [seed_cninfo_c_class_share_capital_profile_fixtures.py](../lab/seed_cninfo_c_class_share_capital_profile_fixtures.py) | 内置 6 行（600000×2 · 300001×2 · 688001×2） |
| [share_capital_profile_fixtures.jsonl](../fixtures/c_class/share_capital_profile/share_capital_profile_fixtures.jsonl) | **6** 条 mapped fixture |
| [validate_cninfo_c_class_share_capital_profile_schema.py](../lab/validate_cninfo_c_class_share_capital_profile_schema.py) | schema 校验 |
| [cninfo_c_class_share_capital_profile_schema_validation_summary.md](../outputs/validation/cninfo_c_class_share_capital_profile_schema_validation_summary.md) | **6/6 PASS** |

**映射：** VARYDATE→report_date, F021N→total_share_capital, F022N→float_share_capital, F023N→restricted_share_capital；F002V/F024N/F028N/F003N 留在 raw_record_json。

**红线：** `source_status=testing`；**无 verified**；不入库；schema 未修改。

**下一步：** shareholder_profile **done**（§7s）；P2-A completion summary **done**（§7t）。

---

## 7s. Phase 4 C 类 Shareholder Profile Mapper Draft（2026-07-06）

| 脚本 / 输出 | 内容 |
|------|------|
| [cninfo_c_class_mappers.py](../lab/cninfo_c_class_mappers.py) | `map_company_shareholder_profile()` — getTopTenStockholders / getTopTenCirculatingStockholders row → `c_shareholder_profile` |
| [seed_cninfo_c_class_shareholder_profile_fixtures.py](../lab/seed_cninfo_c_class_shareholder_profile_fixtures.py) | 内置 12 行（600000/300001/688001 × top_shareholder×2 + top_float_shareholder×2） |
| [shareholder_profile_fixtures.jsonl](../fixtures/c_class/shareholder_profile/shareholder_profile_fixtures.jsonl) | **12** 条 mapped fixture |
| [validate_cninfo_c_class_shareholder_profile_schema.py](../lab/validate_cninfo_c_class_shareholder_profile_schema.py) | schema 校验 |
| [cninfo_c_class_shareholder_profile_schema_validation_summary.md](../outputs/validation/cninfo_c_class_shareholder_profile_schema_validation_summary.md) | **12/12 PASS** |

**映射：** F001D→report_period, F002V→shareholder_name, F003N→holding_shares, F004N→holding_ratio, F005N→rank, F006V→shareholder_type_candidate；F007V 留在 raw_record_json。

**shareholder_scope：** `top_shareholder`（cninfo_top_shareholders_profile）· `top_float_shareholder`（cninfo_top_float_shareholders_profile）

**红线：** `source_status=testing`；**无 verified**；不入库；schema 未修改。

**下一步：** P2-A mapper stage **closed**（§7t）；consolidation **done**（§7u）；P2-B probe planning next。

---

## 7t. Phase 4 C 类 P2-A Mapper Completion Summary（2026-07-06）

| 文档 | 内容 |
|------|------|
| [cninfo_c_class_p2a_mapper_completion_summary.md](cninfo_c_class_p2a_mapper_completion_summary.md) | P2-A 四源完整链路收口汇总 |

**覆盖：** executive 6/6 · share_capital 6/6 · shareholder 12/12 schema PASS；live validation 12/12 LIVE_PASS。

**红线：** 全部 `testing`；**无 verified**；**无 testing_stable_sample**；不入库。

**下一步：** P2-B decision table **done**（§7ab）；30-company smoke test next。

---

## 7u. Phase 4 C 类 Status Consolidation Summary（2026-07-06）

| 文档 | 内容 |
|------|------|
| [cninfo_c_class_status_consolidation_summary.md](cninfo_c_class_status_consolidation_summary.md) | C 类 10 源 P1 + P2-A 状态总表 |

**Rollup:** **6 testing** · **4 candidate** · **0 verified** · **29 mapper fixtures 29/29 PASS**

**下一步：** P2-B decision table **done**（§7ab）；30-company smoke test next。

---

## 7v. Phase 4 C 类 P2-B Probe Plan Initialized（2026-07-06）

| 文档 / 记录 | 内容 |
|-------------|------|
| [cninfo_c_class_p2b_probe_plan.md](cninfo_c_class_p2b_probe_plan.md) | P2-B scope · derived vs independent rules · completion criteria |
| [cninfo_c_class_p2b_probe_checklist.md](cninfo_c_class_p2b_probe_checklist.md) | 人工 DevTools 清单 |
| [c_class_p2b_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p2b_probe_records.yaml) | **12** records · `manual_probe_pending` |

**P2-B sources：** dividend_financing · contact · business_scope · industry — **12/12 complete**

**红线：** 无 CNINFO 请求（初始化轮）· 无 YAML backfill · **无 verified** · 不入库

**下一步：** P2-B decision table **done**（§7ab）；30-company smoke test next。

---

## 7w. Phase 4 C 类 P2-B Dividend Financing Probe Complete（2026-07-06）

| 项 | 结果 |
|----|------|
| source_id | `cninfo_dividend_financing_profile` |
| probe_status | **3/3** `endpoint_found` |
| Endpoint | `GET .../getCompanyHisDividend?scode=` |
| records_path | `data.records` |
| row_count | 600000 **25** · 300001 **16** · 688001 **6** |

**Caveat：** historical dividend records only; broader financing/allotment **not confirmed**.

**红线：** 无 YAML backfill · **无 verified** · 不入库

**下一步：** P2-B decision table **done**（§7ab）；30-company smoke test next。

---

**下一步：** P2-B decision table **done**（§7ab）；30-company smoke test next。

---

**下一步：** P2-B decision table **done**（§7ab）；30-company smoke test next。

---

**下一步：** P2-B source decision table **done**（§7ab）；30-company smoke test next。

---

## 7ab. Phase 4 C 类 P2-B Source Decision Table（2026-07-06）

| 文档 | 内容 |
|------|------|
| [cninfo_c_class_p2b_source_decision_table.md](cninfo_c_class_p2b_source_decision_table.md) | P2-B 四源阶段性决策表 |

**Rollup:**

| source | decision_type | next action |
|--------|---------------|-------------|
| `cninfo_dividend_financing_profile` | `direct_endpoint_candidate` | allow_yaml_backfill_decision → 30-company smoke test |
| `cninfo_company_contact_profile` | `derived_candidate_from_basic_profile` | no_separate_fetch |
| `cninfo_company_business_scope` | `derived_candidate_from_basic_profile` | no_separate_fetch |
| `cninfo_company_industry_profile` | `derived_candidate_from_basic_profile` | no_separate_fetch |

**P2-B probe discovery：** **closed & frozen** for this stage（**不再新增端点探测 / 不再新增 consolidation·completion 类 summary 文档**）。

**红线：** 无 YAML 执行 · **无 verified** · 无 DB

**下一步：** 30-company scalability smoke test — especially `basic_profile` + historical dividend (`getCompanyHisDividend`).

---

## 7ac. Phase 4 C 类 30-Company Scale Smoke Test（2026-07-06）

| 项 | 内容 |
|----|------|
| 脚本 | `lab/validate_cninfo_c_class_scale_smoke.py` |
| 样本 | `lab/eval_companies_c_class_smoke_30.yaml`（从 `eval_companies_200` 派生 · 30 家分层） |
| 主判定 source | basic · dividend · P2-A 四源（executive / share_capital / top_shareholders / top_float） |
| 观察维度 | security（`secType=szshe` 跨板块风险单列） |
| derived 三源 | contact / business_scope / industry — 仅随 basic `basicInformation` fill_rate 统计，不单独请求 |
| 指标升级 | fill_rate · non_empty_rate · reachability% · 板块分组 · valid-empty（dividend）· blocked/429 |
| 输出 | [cninfo_c_class_scale_smoke_30_report.csv](../outputs/validation/cninfo_c_class_scale_smoke_30_report.csv) · [summary](../outputs/validation/cninfo_c_class_scale_smoke_30_summary.md) |

**Live 结果（2026-07-06）：** `LIVE_PARTIAL` — 210 cases · pass=159 · fail=21 · blocked/429=0

| source | reachability | non_empty% | valid_empty | 备注 |
|--------|--------------|------------|-------------|------|
| basic | 27/30 (90%) | 90% | — | 关键字段 fill_rate 100%（endpoint_found 子集） |
| dividend | 27/30 (90%) | 83.3% | 2 | valid-empty 语义正常 |
| P2-A 四源 | 83–90% | 83–90% | — | 3 家退市 HTTP 500 拖累 |
| security（观察） | 30/30 (100%) | — | — | 不绑定主判定 |

**失败归因：**
- **3 家退市标的**（600647 退市同达 · 600002 齐鲁退市 · 002473 圣莱退）→ HTTP 500 / `9240002`，占 fail 18/21
- **3 例 empty_but_valid**（688797 臻宝科技 top 股东 · 920186 中科仪 top 流通股东）→ 新股/数据空，非 blocked

**derived fill_rate（basic 子集）：** contact 8 字段 100%；business_scope F017V 88.9%；industry F044V 92.6%

**Gate — dividend YAML backfill：** **NO-GO**（reachability 90% < 95%；error 10% 因退市样本；建议剔除退市后复测，backfill 时窄化命名为 `dividend_history`）

**Gate — 扩至 200 家：** **CONDITIONAL**（活跃上市子集表现良好；需：①样本剔除退市 ②明确 empty 股东西源口径 ③security secType 跨板块映射待修后再扩）

**红线：** 无 verified · 无 testing_stable_sample · 无 DB · dividend YAML backfill **暂缓**

---

## 7ad. Phase 4 C 类 Active-Only 30 Live Smoke Complete（2026-07-06）

| 项 | 内容 |
|----|------|
| 确认方式 | 输出文件完整性（`cninfo_c_class_scale_smoke_30_active_report.csv` · 210 live cases · 30×7 · 210/210 http_status） |
| 样本 | [eval_companies_c_class_smoke_30_active.yaml](../lab/eval_companies_c_class_smoke_30_active.yaml)（剔除 600647 / 600002 / 002473） |
| 输出 | [active report](../outputs/validation/cninfo_c_class_scale_smoke_30_active_report.csv) · [active summary](../outputs/validation/cninfo_c_class_scale_smoke_30_active_summary.md) |
| 200 计划 | [cninfo_c_class_scale_smoke_200_plan.md](cninfo_c_class_scale_smoke_200_plan.md) |

**Live 结果：** `LIVE_PARTIAL`（主判定语义）— pass=177 · observe_pass=30 · fail=3 · **blocked/429=0**

| source | reachability | 备注 |
|--------|--------------|------|
| basic_profile | **100%** | non_empty 100% · 关键字段 fill_rate 100% |
| dividend | **100%** | valid_empty=2 · 日期类 fill_rate 85.7% |
| executive | **100%** | |
| share_capital | **100%** | |
| top_shareholders | 96.7% | 1× empty_but_valid（688797） |
| top_float | 93.3% | 2× empty_but_valid（688797 · 920186） |
| security（观察） | 100% | observe-only · 不绑定主判定 |

**derived（经 basic fill_rate，无单独请求）：** contact 8 字段 100% · business_scope F015V/F016V 100% · industry F032V/MARKET 100%

**3 fail 均为股东源 `empty_but_valid_response`（HTTP 200），非 network/schema failure。**

**Gate — dividend_history YAML backfill：** **GO（仅决策）** — reachability 100% · valid_empty 可解释；**caveat：historical dividend only**；窄化命名 `dividend_history`；**本轮不执行 backfill**。

**Gate — enter_200：** **CONDITIONAL YES** — dry-run checkpoint **PASS**（§7ae）；口径 **done**（§7af）；**200 live 等待人工明确批准**。

**红线：** 无 verified · 无 testing_stable_sample · 无 DB · 无 YAML backfill

**下一步：** BSE-920 targeted probe · 样本清洗（839729 重复等）· 非 BSE 1000-like planning — **不全量重跑**

---

## 7ag. Phase 4 C 类 195 Active Live + BSE Diagnosis（2026-07-06）

| 项 | 结果 |
|----|------|
| live | **LIVE_PARTIAL** — 195 cos · 1365 cases · pass=1101 · fail=69 · blocked=4 · 429=0 |
| summary | [cninfo_c_class_scale_smoke_200_active_summary.md](../outputs/validation/cninfo_c_class_scale_smoke_200_active_summary.md) |
| failure cases | [cninfo_c_class_scale_smoke_200_failure_cases.csv](../outputs/validation/cninfo_c_class_scale_smoke_200_failure_cases.csv) |
| BSE diagnosis | [cninfo_c_class_scale_smoke_200_bse_diagnosis.md](../outputs/validation/cninfo_c_class_scale_smoke_200_bse_diagnosis.md) |

**非 BSE（175 家）：** 主判定 pass **~97%** · chinext 100% · 失败主要为 3 家 ST/异常 + 臻宝科技股东 empty

**BSE（20 家）：** 主判定 pass **59%** — **83/87 前缀 8 家 6/6 HTTP 500（9240002）**；**92 前缀 11/12 全过**；920186 仅 top_float empty

**样本问题：** `839729`/`920729` 永顺生物同 orgid 重复

**Gate — dividend backfill：** non-BSE **GO（决策）** · mixed universe **HOLD** · **不执行**

**Gate — BSE：** **从主 scale gate 拆出**；legacy 83/87 标记 `legacy_code_incompatible`；需 **BSE targeted probe**（非 195 重跑）

**下一步：** universe split **done**（§7ah）；non-BSE 1000-like 离线派生 **done**（§7ai）；**live 待批准**

---

## 7ai. Phase 4 C 类 Non-BSE 1000-like Candidate + Dry-Run（2026-07-06）

| 项 | 内容 |
|----|------|
| 母本 | `lab/eval_companies_1000.yaml`（**1020**） |
| 候选 | `lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml`（**889**） |
| 清洗规则 | 与 §7ah / [universe split plan](cninfo_c_class_universe_split_and_sample_cleaning_plan.md) 一致 |
| dry-run | `python lab/validate_cninfo_c_class_scale_smoke.py --dry-run --sample-file lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml` |
| 结果 | **DRY_RUN_ONLY** · cases=**6223** skipped · **0 CNINFO** |
| 报告 | [cninfo_c_class_smoke_1000_non_bse_dryrun_summary.md](../outputs/validation/cninfo_c_class_smoke_1000_non_bse_dryrun_summary.md) |

| board | count |
|-------|-------|
| sse_main | 292 |
| szse_main | 239 |
| chinext | 233 |
| star | 125 |

| exclusion_reason | count |
|------------------|-------|
| board_bse | 106 |
| name_suffix_tui | 15 |
| name_delisted_cn | 7 |
| abnormal_review_explicit | 3 |

**Planned live:** 889 × 7 = **6223**（6 主判定 + security observe-only）；derived 三源无单独请求。

**红线：** 本轮 **无 live** · **无 CNINFO** · **无 YAML backfill** · **无 DB** · **无 verified**

**建议：** ~~等待人工批准后跑 non-BSE 1000-like `--live`~~ → **已完成**（§7aj）

---

## 7aj. Phase 4 C 类 889 Non-BSE Live + Post-889 Diagnosis（2026-07-07）

| 项 | 内容 |
|----|------|
| Live | **889** 家 · **6223** cases · **LIVE_PARTIAL** |
| 主判定 | pass=**5064** fail=**270** · blocked=**14** · 429=**0** |
| security | observe_pass=**889** |
| Live 报告 | [live_report.csv](../outputs/validation/cninfo_c_class_smoke_1000_non_bse_live_report.csv) · [live_summary.md](../outputs/validation/cninfo_c_class_smoke_1000_non_bse_live_summary.md) |
| Diagnosis | [failure_cases.csv](../outputs/validation/cninfo_c_class_smoke_1000_non_bse_failure_cases.csv) · [diagnosis.md](../outputs/validation/cninfo_c_class_smoke_1000_non_bse_diagnosis.md) |

**结论：** fail 主要由 **26 家 6/6 全失败** + **empty_but_valid 计 fail**；**非系统性退化**。dividend **GO（决策）**；top_float **source_partial**；security **observe-only**。

**下一步：** partial-fail targeted retry **live 待批准**（§7ak）；样本清洗 26 家 6/6

---

## 7ak. Phase 4 C 类 Failed-Company Targeted Retry Prep（2026-07-07）

| 项 | 内容 |
|----|------|
| 889 full rerun | **不推荐** |
| 失败公司 | **88** 家（至少 1 主源 fail） |
| six-fail hold | **26** 家 · `lab/eval_companies_c_class_retry_889_six_fail_hold.yaml` · `sample_quality_or_status_review` |
| partial retry | **62** 家 · `lab/eval_companies_c_class_retry_889_partial_fail_retry.yaml` |
| 全量失败索引 | `lab/eval_companies_c_class_retry_889_failed_companies.yaml` |
| dry-run | **DRY_RUN_ONLY** · **62** × 7 = **434** cases |
| 报告 | [dryrun_summary.md](../outputs/validation/cninfo_c_class_retry_889_partial_fail_dryrun_summary.md) |

**Runner 修正：** 股东源 `empty_but_valid_response` → `case_result=pass`；计入 reachable；**source_partial**（non_empty 单独统计）

**红线：** 本轮 **无 live** · **无 CNINFO** · **无 YAML** · **无 DB**

**建议：** ~~等待人工批准后~~ → **已完成**（§7al）

---

## 7al. Phase 4 C 类 62 Partial-Fail Targeted Retry Live（2026-07-07）

| 项 | 内容 |
|----|------|
| 样本 | `lab/eval_companies_c_class_retry_889_partial_fail_retry.yaml`（**62**） |
| Live | **434** cases · **LIVE_PARTIAL** |
| 主判定 | pass=**300** fail=**72** · blocked=**0** · 429=**0** |
| security | observe **62/62** |
| 报告 | [live_summary.md](../outputs/validation/cninfo_c_class_retry_889_partial_fail_live_summary.md) |

**困难样本 reachability：** basic **66.1%** · executive **67.7%** · share_capital **59.7%** · dividend **96.8%**

---

## 7an. Phase 4 C 类 Stable 200 Non-BSE Sample + Dry-Run（2026-07-07）

| 项 | 内容 |
|----|------|
| 计划 | [cninfo_c_class_stable_200_sample_plan.md](cninfo_c_class_stable_200_sample_plan.md) |
| 样本 | `lab/eval_companies_c_class_stable_200_non_bse.yaml`（**200**） |
| 母本 | 889 candidate；剔除 **26** six_fail_hold |
| board | sse **66** · szse **54** · chinext **52** · star **28** |
| dry-run | **DRY_RUN_ONLY** · **1400** cases |
| 报告 | [dryrun_summary.md](../outputs/validation/cninfo_c_class_stable_200_dryrun_summary.md) |

**建议：** ~~等待人工批准后 stable 200 `--live`~~ → **已完成**（§7ao）

---

## 7ao. Phase 4 C 类 Stable 200 Live + Post-Live Diagnosis（2026-07-07）

| 项 | 内容 |
|----|------|
| Live | **200** · **1400** · **LIVE_PARTIAL** |
| 主判定 | pass=**1069** fail=**131** · blocked/429/http_error=**0** |
| 报告 | [live_summary.md](../outputs/validation/cninfo_c_class_stable_200_live_summary.md) · [diagnosis.md](../outputs/validation/cninfo_c_class_stable_200_diagnosis.md) |

**结论：** fail = **schema_unexpected（114）** + **empty_but_valid（17）**；**12 家 6/6**；dividend **90%**；YAML → **HOLD**。

**注：** §7ao 中「样本二次清洗 / 剔除 12 家」建议已被 §7ap 人工审计 **overturn**。

---

## 7ap. Phase 4 C 类 Stable 200 十二家 6/6 Fail 人工审计 + Endpoint Debug 转向（2026-07-07）

| 项 | 内容 |
|----|------|
| 审计对象 | stable 200 live 中 **12 家 6/6 主源失败** |
| 人工审计表 | [cninfo_c_class_stable_200_manual_audit_12_companies.csv](../outputs/validation/cninfo_c_class_stable_200_manual_audit_12_companies.csv) |
| 审计计划 | [cninfo_c_class_manual_audit_12_six_fail_companies.md](cninfo_c_class_manual_audit_12_six_fail_companies.md) |
| endpoint debug 计划 | [cninfo_c_class_12_six_fail_endpoint_debug_plan.md](cninfo_c_class_12_six_fail_endpoint_debug_plan.md) |

### 人工结论（12/12）

| 字段 | 值 |
|------|-----|
| `manual_cninfo_search_found` | **yes** |
| `manual_f10_page_exists` | **yes** |
| `manual_basic_profile_visible` | **yes** |
| `manual_judgment` | **`endpoint_parameter_issue_or_parser_issue`** |

**不剔除 12 家：** 网页端均有结构化公司介绍；剔除会造成 stable sample **过拟合**；当前失败不应解释为公司无效。

### 最可能根因

- runner endpoint 与网页真实数据源不一致（`scode-only` vs `stockCode` + `orgId`）
- parser 硬编码 `data.records`；实际响应可能为 **response_shape_mismatch**
- 类别候选：`endpoint_parameter_issue` · `parser_schema_assumption_issue` · `current_endpoint_not_web_source`

### 状态变更

| 项 | 状态 |
|----|------|
| stable 200 v2 清洗 | **PAUSED** |
| 12 家进入 hold | **否** |
| 根因调查 | sample cleaning → **endpoint/parser debug** |
| dividend YAML backfill | **HOLD** |
| verified / testing_stable_sample | **不写** |

### 下一步产出（待批准后执行 · 本轮不创建）

- `outputs/validation/cninfo_c_class_12_six_fail_endpoint_debug_cases.csv`
- `outputs/validation/cninfo_c_class_12_six_fail_endpoint_debug_summary.md`

**红线：** 本轮 **无 live** · **无 CNINFO 程序请求** · **无 stable 200 v2** · **无剔除** · **无 YAML** · **无 DB** · **无 verified**

---

## 7aq. Phase 4 C 类 12 Six-Fail Endpoint Debug 执行完成（2026-07-07）

| 项 | 内容 |
|----|------|
| 脚本 | `lab/debug_cninfo_c_class_12_six_fail_endpoints.py` |
| cases | [cninfo_c_class_12_six_fail_endpoint_debug_cases.csv](../outputs/validation/cninfo_c_class_12_six_fail_endpoint_debug_cases.csv) |
| summary | [cninfo_c_class_12_six_fail_endpoint_debug_summary.md](../outputs/validation/cninfo_c_class_12_six_fail_endpoint_debug_summary.md) |
| 范围 | **12 家** · **84** CNINFO 请求（6 runner + 1 orgId basic 变体 / 家） |

### 结论摘要

| 项 | 结果 |
|----|------|
| debug basic 可达 | **11/12** |
| live fail → debug pass | **11/12** |
| 最主要 category | **`needs_more_check`**（11）+ **`endpoint_parameter_issue`**（1 · 600203） |
| endpoint 路径 | **正确** — `getCompanyIntroduction` 等 data20 路径可用 |
| orgId query | **600203** 需 `scode+orgId`；其余 scode-only 通常足够 |
| 批量 live 429/90001 | **主因候选** — JSON 业务码非 HTTP 429；1400 连跑节流 |
| sample_quality_issue | **否** |
| stable 200 v2 | **继续暂停** |

**下一步：** ~~runner 退避~~ → **完成**（§7ar）；**12 家 targeted retry live 待批准**。

---

## 7ar. Phase 4 C 类 Runner Backoff Patch + 12 Six-Fail Retry Dry-Run（2026-07-07）

| 项 | 内容 |
|----|------|
| Runner | `lab/validate_cninfo_c_class_scale_smoke.py` |
| 样本 | `lab/eval_companies_c_class_retry_stable_200_six_fail_12.yaml`（**12**） |
| dry-run | **DRY_RUN_ONLY** · **84** cases（12 × 7） |
| 报告 | [dryrun_summary.md](../outputs/validation/cninfo_c_class_retry_stable_200_six_fail_12_dryrun_summary.md) |

### Runner 变更

| 能力 | 说明 |
|------|------|
| `cninfo_throttled_business_code` | JSON `429`/`90001` 或限流文案；不再直接判 `schema_unexpected` |
| 退避重试（live） | 2s → 5s → 10s，最多 3 次 |
| live 基础节流 | 请求间隔 **0.5s** |
| orgId fallback | data20 endpoint：`scode+orgId` 单次 fallback（600203 已知案例） |
| report 字段 | `retry_count` · `final_retrieval_status` · `first_result_code` · `final_result_code` · `used_orgid_variant` |

**下一步：** ~~889 rerun planning~~ → **完成**（§7au）；**889 live 待批准**。

---

## 7as. Phase 4 C 类 12 Six-Fail Retry Live（2026-07-07）

| 项 | 内容 |
|----|------|
| 样本 | `lab/eval_companies_c_class_retry_stable_200_six_fail_12.yaml`（**12**） |
| Live | **LIVE_PASS** · pass=**72** · observe_pass=**12** · fail=**0** |
| 报告 | [live_summary.md](../outputs/validation/cninfo_c_class_retry_stable_200_six_fail_12_live_summary.md) |

六主源 **12/12** reachable；验证 backoff + orgId fallback 有效（含 600203）。

---

## 7at. Phase 4 C 类 Stable 200 Rerun LIVE_PASS + Decision（2026-07-07）

| 项 | 内容 |
|----|------|
| 决策文档 | [cninfo_c_class_stable_200_live_pass_decision.md](cninfo_c_class_stable_200_live_pass_decision.md) |
| stable 200 rerun | **LIVE_PASS** · 200 · 1400 · pass=**1200** fail=**0** |
| 12 retry | **LIVE_PASS** · 12 · 84 · pass=72 observe_pass=12 |
| 报告 | [stable_200_live_summary.md](../outputs/validation/cninfo_c_class_stable_200_live_summary.md) |

### 决策摘要

- 前次 LIVE_PARTIAL 主因：**runner 业务码限流处理不足**（非 sample_quality · 非 parser 主因）
- **12 家 six-fail 不清洗**
- **stable 200 v2 取消**
- non-BSE main：**CONDITIONAL YES** · ready for **889 rerun planning**
- dividend_history：**GO（决策 only）** · **不执行 YAML**

**下一步：** ~~889 rerun plan~~ → **完成**（§7au）。

---

## 7au. Phase 4 C 类 889 Non-BSE Rerun Plan + Dry-Run（2026-07-07）

| 项 | 内容 |
|----|------|
| 计划 | [cninfo_c_class_889_non_bse_rerun_plan.md](cninfo_c_class_889_non_bse_rerun_plan.md) |
| 样本 | `lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml`（**889**） |
| dry-run | **DRY_RUN_ONLY** · **6223** cases |
| 报告 | [rerun_dryrun_summary.md](../outputs/validation/cninfo_c_class_889_non_bse_rerun_dryrun_summary.md) |

**board：** sse_main **292** · szse_main **239** · chinext **233** · star **125**

**preflight：** 无 BSE · 无 abnormal_review · 无退市名；**000765/001267** duplicate orgid 共存（监测项）

**下一步：** ~~harvest runner 安全控制~~ → **完成**（§7bg）；**full_harvest_gate = PENDING_APPROVAL**。

---

## 7bg. Phase 4 C 类 Harvest Runner 安全控制（2026-07-07）

| 项 | 内容 |
|----|------|
| runner | `lab/harvest_cninfo_c_class.py` |
| 测试 | `lab/test_cninfo_c_class_harvest_runner_safety.py` · **5/5 PASS** |
| 报告 | [harvest_runner_safety_test_summary.md](../outputs/validation/cninfo_c_class_harvest_runner_safety_test_summary.md) |
| run_status | `outputs/harvest/cninfo_c_class/quality/run_status.json` |

### 新增参数

| 参数 | 说明 |
|------|------|
| `--approve-full-harvest` | 863 full harvest 显式人工批准（无 `--limit` 时必需） |
| `--resume` | 续跑框架：跳过 `harvest_status=complete` 公司 |
| `--limit N` | smoke 模式（保留，无需 approve） |

### 安全机制

- `--live` 无 `--limit` 且无 `--approve-full-harvest` → `FULL_HARVEST_APPROVAL_REQUIRED` · exit≠0
- `pre_live_harvest_validation`：company_count · hold_overlap · approve · output dir · run_status
- `resume_skip_count` / `resume_pending_count` 输出

### Gate

| Gate | 状态 |
|------|------|
| harvest_smoke_gate | **PASS** |
| safety_controls | **PASS**（5/5） |
| full_harvest_gate | **PENDING_APPROVAL** |

---

## 7bf. Phase 4 C 类 Full Harvest 863 Approval Plan（2026-07-07）

| 项 | 内容 |
|----|------|
| 计划 | [cninfo_c_class_full_harvest_863_execution_plan.md](cninfo_c_class_full_harvest_863_execution_plan.md) |
| universe | **863**（889 − 26 hold） |
| planned HTTP | **6041**（863 × 7） |
| smoke 前置 | **PASS**（§7be） |

### Gate 状态

| Gate | 状态 |
|------|------|
| harvest_smoke_gate | **PASS** |
| full_harvest_gate | **PENDING_APPROVAL** |

### 结论摘要

- 执行计划已冻结：scope · command · output · safety · failure · resume · completion
- runner `--limit` 安全锁仍在；批准后解除或加 `--approve-full-harvest`
- **resume 逻辑规划完成 · 代码待批准后实现**
- **本轮不执行 full harvest** · **no verified** · **no DB**

---

## 7be. Phase 4 C 类 Harvest Live Runner Smoke（2026-07-07）

| 项 | 内容 |
|----|------|
| runner | `lab/harvest_cninfo_c_class.py` · `--live --limit 10` |
| sample | `lab/eval_companies_c_class_harvest_863_non_bse.yaml`（取前 **10** 家） |
| smoke 报告 | [harvest_smoke_summary.md](../outputs/validation/cninfo_c_class_harvest_smoke_summary.md) |
| smoke CSV | [harvest_smoke_report.csv](../outputs/validation/cninfo_c_class_harvest_smoke_report.csv) |
| 产物 | `outputs/harvest/cninfo_c_class/{raw,normalized,quality}/` |

### 验收结果

| check | result |
|-------|--------|
| companies | **10** |
| HTTP requests | **70** |
| success | **100** |
| empty_but_valid | **2** |
| blocked / http_error | **0** / **0** |
| raw files | **70** |
| normalized files | **100** |
| dividend_history 解析 | **10/10 PASS** |
| quality summary | **PASS** |
| **harvest_smoke_gate** | **PASS** |

### 结论摘要

- live runner 已实现（复用 throttle backoff · orgId fallback · empty_but_valid · mappers）
- **无 --limit 禁止 live**（防 863 误跑）
- **863 full harvest 未执行**
- **下一步：smoke 评审 → 人工批准 → 863 full harvest**
- **no verified** · **no DB** · **no MinIO**

---

## 7bd. Phase 4 C 类 Harvest Runner Dry-Run Validation（2026-07-07）

| 项 | 内容 |
|----|------|
| runner | `lab/harvest_cninfo_c_class.py` |
| sample | `lab/eval_companies_c_class_harvest_863_non_bse.yaml`（**863**） |
| validation | [harvest_dryrun_validation_summary.md](../outputs/validation/cninfo_c_class_harvest_dryrun_validation_summary.md) |
| matrix CSV | [harvest_dryrun_report.csv](../outputs/validation/cninfo_c_class_harvest_dryrun_report.csv) |

### 验收结果

| check | result |
|-------|--------|
| preflight | **PASS** — company_count=**863** · hold_overlap=**0** · planned_http_cases=**6041** |
| source_matrix | **PASS** — direct **6** · derived **3** · observe **1** |
| mapper_wiring | **PASS** — basic · executive · share_capital · shareholder(top+float) · dividend_history |
| output_paths | **PASS** — raw / normalized / quality planned（无真实写入） |
| CNINFO requests | **0** |
| raw writes | **0** |
| normalized writes | **0** |

### 结论摘要

- mapper 接入后完整 dry-run 流程 **PASS**
- **harvest_dryrun_validation_gate = PASS**
- **下一步：人工批准 → harvest live**
- **无 CNINFO** · **无 harvest 执行** · **no verified**

---

## 7bc. Phase 4 C 类 dividend_history Mapper 代码实现（2026-07-07）

| 项 | 内容 |
|----|------|
| mapper | `lab/cninfo_c_class_mappers.py` · `map_dividend_history()` · `parse_dividend_f007v()` |
| harvest 入口 | `lab/harvest_cninfo_c_class.py`（import `map_dividend_history`） |
| 配置 | [cninfo_dividend_history_mapper.yaml](../config/cninfo_dividend_history_mapper.yaml) |
| fixture test | `lab/test_cninfo_c_class_dividend_history_mapper.py` · **5/5 PASS** |
| 报告 | [dividend_history_mapper_test_summary.md](../outputs/validation/cninfo_c_class_dividend_history_mapper_test_summary.md) |
| fixtures | `fixtures/c_class/dividend_history/dividend_history_mapper_fixtures.json` |

### 结论摘要

- raw F001V/F007V/F018D/F020D/F023D → normalized **9** normalized_core 字段已映射
- F007V 解析器支持：纯现金 · 现金+送股 · 现金+转增 · 空记录 · 不可解析文本
- `dividend_parse_status`：`parsed` / `partial` / `needs_review` / `empty_but_valid`
- harvest dry-run 复跑 **PASS**（863 · CNINFO=0）
- **下一步：harvest runner dry-run 验收 → 人工批准 → harvest live**
- **无 CNINFO** · **无 harvest 执行** · **no verified**

---

## 7bb. Phase 4 C 类 dividend_history Mapper（2026-07-07）

| 项 | 内容 |
|----|------|
| 配置 | [cninfo_dividend_history_mapper.yaml](../config/cninfo_dividend_history_mapper.yaml) |
| 文档 | [cninfo_c_class_dividend_history_mapping.md](cninfo_c_class_dividend_history_mapping.md) |
| logical_name | **dividend_history**（≠ financing） |
| normalized_core | **9** · review_later **8** · raw_only **4** |

### 结论摘要

- raw F001V/F007V/F018D/F020D/F023D → normalized 映射 **已冻结**
- **harvest live 字段阻塞已解除**
- ~~`map_dividend_history()` 代码实现~~ → **完成**（§7bc）
- harvest live 仍 **待人工批准**
- **无 CNINFO** · **无 harvest 执行** · **no verified**

---

## 7ba. Phase 4 C 类 Harvest Runner Dry-Run（2026-07-07）

| 项 | 内容 |
|----|------|
| runner | `lab/harvest_cninfo_c_class.py` |
| sample | `lab/eval_companies_c_class_harvest_863_non_bse.yaml`（**863**） |
| dry-run | **DRY_RUN_ONLY** · matrix **8630** · HTTP planned **6041** |
| 报告 | [harvest_dryrun_summary.md](../outputs/validation/cninfo_c_class_harvest_dryrun_summary.md) |

### 结论摘要

- preflight **PASS**（863 · hold overlap=0）
- **CNINFO requests = 0** · raw/normalized writes = 0
- direct **6** · derived **3** · observe **1**
- **harvest_dryrun_gate = PASS** · **live pending approval**

---

## 7az. Phase 4 C 类 Harvest Plan（2026-07-07）

| 项 | 内容 |
|----|------|
| 计划 | [cninfo_c_class_harvest_plan.md](cninfo_c_class_harvest_plan.md) |
| universe | **863** = 889 non-BSE − **26** all6 hold |
| 输出三层 | raw · normalized · quality |
| planned live cases | **6041**（863 × 7） |
| 未来 runner | `lab/harvest_cninfo_c_class.py`（**未实现**） |

### 结论摘要

- **planning only** — 不请求 CNINFO · 不 harvest live · 不入库
- direct **6** + derived **3** + observe **1**
- field mapping：normalized_core **64** · review_later **31** · raw_only **25**
- **live gate = PENDING_RUNNER_DRYRUN**
- **下一步：** harvest runner dry-run → 人工批准 → harvest live

---

## 7ay. Phase 4 C 类 Field Inventory（2026-07-07）

| 项 | 内容 |
|----|------|
| 文档 | [cninfo_c_class_field_inventory.md](cninfo_c_class_field_inventory.md) |
| CSV | [cninfo_c_class_field_inventory.csv](../outputs/validation/cninfo_c_class_field_inventory.csv) |
| 字段总数 | **120** |
| normalized_core | **64** (`include=yes`) |
| review_later | **31** (`include=review`) |
| raw_only | **25** (`include=no`) |

### 结论摘要

- **不是** discovery / harvest / live；为 raw + normalized harvest **准备字段清单**
- **10** source 分节（basic · 3 derived · executive · share_capital · 2 shareholder · dividend_history · security observe）
- caveat：share_capital **source_partial** · executive **caveat** · top_float **source_partial** · security **observe-only** · dividend **≠ financing**
- **harvest planning 允许启动**；**harvest live 未启动**

---

## 7ax. Phase 4 C 类 889 Partial-Fail Retry Live + Post-Retry Decision（2026-07-07）

| 项 | 内容 |
|----|------|
| Live | **LIVE_PARTIAL** · **41** · **287** · pass=**237** fail=**9** |
| 报告 | [partial_fail_retry_live_summary.md](../outputs/validation/cninfo_c_class_889_rerun_partial_fail_retry_live_summary.md) |
| post-retry decision | [cninfo_c_class_889_post_retry_decision.md](cninfo_c_class_889_post_retry_decision.md) |

### 结论摘要

- targeted retry **已完成**（非 pending approval）
- blocked=**0** · 429=**0** · http_error=**0** → **runner/pacing 排除**
- 残留 fail：**share_capital 8** · **executive 1** · 均为 `empty_but_valid_response`
- **26 家 all6 hold** 继续 hold_no_retry · **889 不重跑**
- **share_capital** → source_partial · **executive** → caveat
- **harvest** → **可进入 planning**（summary 保留 26 hold + share_capital caveat）
- dividend_history YAML → **GO（决策 only）** · **不执行**

---

## 7aw. Phase 4 C 类 889 Rerun Partial-Fail Retry Plan + Dry-Run（2026-07-07）

| 项 | 内容 |
|----|------|
| 计划 | [cninfo_c_class_889_rerun_retry_plan.md](cninfo_c_class_889_rerun_retry_plan.md) |
| all6 hold | `lab/eval_companies_c_class_889_rerun_all6_hold.yaml`（**26** · hold_no_retry） |
| partial-fail retry | `lab/eval_companies_c_class_889_rerun_partial_fail_retry.yaml`（**41**） |
| dry-run | **DRY_RUN_ONLY** · **287** cases · preflight **PASS** |
| 报告 | [partial_fail_retry_dryrun_summary.md](../outputs/validation/cninfo_c_class_889_rerun_partial_fail_retry_dryrun_summary.md) |

### 结论摘要

- **26 家 all6** → sample_quality_or_status_review · **不 retry**
- **41 家 partial-fail** → targeted retry 候选 · high=**4** · medium=**37**
- **board（partial）：** chinext **36** · star **2** · szse_main **2** · sse_main **1**
- **本轮不重跑 889** · **harvest 暂停** · **runner pacing 暂不调**
- **下一步：** **等待人工批准** partial-fail `--live`

---

## 7av. Phase 4 C 类 889 Non-BSE Rerun Live + Post-Diagnosis（2026-07-07）

| 项 | 内容 |
|----|------|
| Live | **LIVE_PARTIAL** · 889 · 6223 · pass=**5119** fail=**215** |
| 报告 | [live_summary.md](../outputs/validation/cninfo_c_class_889_non_bse_rerun_live_summary.md) |
| diagnosis | [cninfo_c_class_889_non_bse_rerun_diagnosis.md](../outputs/validation/cninfo_c_class_889_non_bse_rerun_diagnosis.md) |
| failure cases | [cninfo_c_class_889_non_bse_rerun_failure_cases.csv](../outputs/validation/cninfo_c_class_889_non_bse_rerun_failure_cases.csv) |

### 结论摘要

- fail 主因：**http_error 142**（HTTP 500/`9240002`）+ **empty_but_valid 52**（executive/share）
- **26 家新 6/6** · hold 候选 · **非** stable 200 十二家
- chinext executive/share 偏弱 = **合法空 records**
- backoff/orgId **有效**（throttled fail 仅 1）
- **建议：** ~**41** 家 partial-fail targeted retry · **暂停 harvest**

---

## 7am. Phase 4 C 类 Source Status Decision（2026-07-07）

| 项 | 内容 |
|----|------|
| 文档 | [cninfo_c_class_source_status_decision.md](cninfo_c_class_source_status_decision.md) |
| non-BSE | **CONDITIONAL YES** |
| dividend_history | **proceed_testing** · YAML **GO（决策 only）** |
| source_partial | top_float · share_capital |
| observe_only | security |
| derived | contact · business_scope · industry |

**阶段：** scale smoke → **source status consolidation**

---

## 7ah. Phase 4 C 类 Universe Split + Sample Cleaning（2026-07-06）

| 项 | 内容 |
|----|------|
| 计划 | [cninfo_c_class_universe_split_and_sample_cleaning_plan.md](cninfo_c_class_universe_split_and_sample_cleaning_plan.md) |
| 母本 | `eval_companies_c_class_smoke_200_active.yaml`（195） |

| universe | 数量 | 派生文件 | 下一阶段 |
|----------|------|----------|----------|
| `non_bse_active` | **172** | `lab/eval_companies_c_class_smoke_195_non_bse_active.yaml` | 1000-like planning 主宇宙 |
| `bse_920_active` | **12** | `lab/eval_companies_c_class_smoke_195_bse_920_active.yaml` | BSE 子 gate |
| `bse_legacy_83_87_hold` | **8** | `lab/eval_companies_c_class_smoke_195_bse_legacy_hold.yaml` | HOLD · targeted probe |
| `abnormal_review` | **3** | `lab/eval_companies_c_class_smoke_195_abnormal_review.yaml` | 不进入主 gate |

**策略：** 主 gate **不再**混算 BSE legacy；**非 blind 1000**；non-BSE mainline 与 BSE legacy side-track **分离**

**dividend_history backfill：** non-BSE **GO（决策）** · mixed **HOLD** · **不执行 YAML**

**红线：** 无 live · 无 CNINFO · 无 verified · 无 DB

---

## 7af. Phase 4 C 类 200 Live 前口径 + Dry-Run Checkpoint（2026-07-06）

| 项 | 状态 |
|----|------|
| 权威文档 | [cninfo_c_class_scale_smoke_200_plan.md](cninfo_c_class_scale_smoke_200_plan.md) §0 · §6 · §7 |
| dry-run checkpoint | **PASS** — 195 companies · 1365 cases · `DRY_RUN_ONLY` · **0 CNINFO 请求** |
| planned live | **1365** requests |

### Shareholder `empty_but_valid` policy（摘要）

适用：`cninfo_top_shareholders_profile` · `cninfo_top_float_shareholders_profile`。

当 HTTP 200 · code=200 · `data.resultCode=200` · `data.records` 为 list 且 **length=0** → `retrieval_status: empty_but_valid_response`。

- 不计 blocked / http_error / schema_unexpected；不直接代表 endpoint 不可用
- 单独统计；按 board（及可选 company_age）观察集中度
- 主 gate：**区分 endpoint_reachable 与 non_empty**
- review 阈值：全样本 **>15%** · 单板块 **>30%** → board-specific review

### `security_profile` observe-only policy（摘要）

- 200 live **仍请求** marketOverview（观察）
- **不绑定**主 go/no-go（`secType=szshe` 跨板块未充分验证）
- summary **单独展示**；`observe_pass` 不计入主判定 pass/fail

### 红线

无 verified · 无 testing_stable_sample · 无 DB · 无 YAML backfill · **不跑 live 直至人工批准**

---

## 7ae. Phase 4 C 类 Active 200 Sample + Dry-Run（2026-07-06）

| 项 | 内容 |
|----|------|
| 母本 | `lab/eval_companies_200.yaml`（200 家） |
| 派生样本 | [eval_companies_c_class_smoke_200_active.yaml](../lab/eval_companies_c_class_smoke_200_active.yaml) |
| active 数量 | **195**（剔除 5 家，未联网补样本） |
| dry-run | [summary](../outputs/validation/cninfo_c_class_scale_smoke_200_active_summary.md) · **DRY_RUN_ONLY** · 1365 cases · 无 CNINFO 请求 |
| planned live | **1365** = 195 × 7 sources |

**剔除（5）：** 600896 退市海医 · 600002 齐鲁退市 · 600647 退市同达 · 002473 圣莱退 · 000760 斯太退

**板块（active）：** sse_main 57 · szse_main 48 · chinext 45 · star 25 · bse 20

**红线：** 本轮 **无 live** · 无 YAML backfill · 无 verified · 无 DB

---

## 7aa. Phase 4 C 类 P2-B Industry Profile Derived Recheck Complete（2026-07-06）

| 项 | 结果 |
|----|------|
| source_id | `cninfo_company_industry_profile` |
| probe_status | **3/3** `derived_candidate_from_basic_profile` |
| independent endpoint | **None observed**（600000 · 300001 · 688001） |
| derived_from | `cninfo_company_basic_profile` · `getCompanyIntroduction` · `data.records[0].basicInformation[0]` |

**Fields：** F032V → industry_candidate · MARKET → market_candidate · F044V → listing_board_or_industry_candidate

**Caveat：** 仅公司概况 industry-like 字段；**不是**完整外部行业分类体系

**P2-B rollup：** **12/12** probe complete（1 endpoint source + 3 derived sources）

**红线：** 无 YAML backfill · **无 verified** · 无 DB

**下一步：** P2-B decision table **done**（§7ab）；30-company smoke test next。

---

## 7z. Phase 4 C 类 P2-B Business Scope Probe Complete（2026-07-06）

| 项 | 结果 |
|----|------|
| source_id | `cninfo_company_business_scope` |
| probe_status | **3/3** `derived_candidate_from_basic_profile` |
| independent endpoint | **None observed**（600000 · 300001 · 688001） |
| derived_from | `cninfo_company_basic_profile` · `getCompanyIntroduction` · `data.records[0].basicInformation[0]` |

**Fields：** F015V → main_business · F016V → business_scope · F017V → company_history_or_introduction

**红线：** 无 YAML backfill · source 仍 **candidate** · **无 verified** · 无 DB · 无 CNINFO 请求

**下一步：** P2-B decision table **done**（§7ab）；30-company smoke test next。

---

## 7y. Phase 4 C 类 P2-B Contact Profile Probe Complete（2026-07-06）

| 项 | 结果 |
|----|------|
| source_id | `cninfo_company_contact_profile` |
| probe_status | **3/3** `derived_candidate_from_basic_profile` |
| independent endpoint | **None observed**（600000 · 300001 · 688001） |
| derived_from | `cninfo_company_basic_profile` · `getCompanyIntroduction` · `data.records[0].basicInformation[0]` |

**Contact fields：** F004V · F005V · F006V · F011V · F012V · F013V · F014V · F018V → address · contact · board_secretary_candidate

**红线：** 无 YAML backfill · source 仍 **candidate** · **无 verified** · 不入库

**下一步：** P2-B decision table **done**（§7ab）；30-company smoke test next。

---

## 7x. Phase 4 C 类 P2-B Contact Profile 600000 Probe（2026-07-06）

| 项 | 结果 |
|----|------|
| probe_id | `c_p2b_contact_600000` |
| probe_status | `derived_candidate_from_basic_profile` |
| independent endpoint | **None observed** |
| derived_from | `cninfo_company_basic_profile` · `getCompanyIntroduction` · `data.records[0].basicInformation[0]` |

**Contact fields（via basicInformation）：** F004V–F018V → registered_address · office_address · postal_code · website · email · phone · fax · board_secretary_candidate

**红线：** 无 YAML backfill · **无 verified** · 不入库

**下一步：** P2-B decision table **done**（§7ab）；30-company smoke test next.

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
当前 Phase：C 类 **Harvest Runner 安全控制完成**（§7bg）；**full_harvest_gate = PENDING_APPROVAL**；**BSE legacy** HOLD。
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
