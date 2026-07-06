# CNINFO B 类 Registry Lint 设计

_最后更新：2026-07-05_

> **脚本：** `lab/lint_cninfo_b_class_registry.py`  
> **Registry YAML：** [config/cninfo_b_class_source_registry_draft.yaml](../config/cninfo_b_class_source_registry_draft.yaml)  
> **Category routing：** [config/cninfo_announcement_categories.yaml](../config/cninfo_announcement_categories.yaml)  
> **JSON Schema：** [schemas/b_class/](../schemas/b_class/)

---

## 1. 目的

B 类 document corpus 已具备 registry YAML、category routing YAML、8 个 JSON Schema、33 条 document / 20 条 raw_file / 33 条 parse_run dry-run fixture。

**Registry lint** 在 **本地、离线、无 CNINFO 请求** 前提下，检查四者 **内部一致性**，避免：

- `route_to.source_id` 与 registry 脱节；
- `verified` 误写入；
- non-periodic source 被误升级为 `testing_stable_sample`；
- fixture `source_id` / enum 与 schema 不一致；
- D 类 `source_id` 混入 B 类配置。

Lint **不**代表 CNINFO coverage；**不**下载/解析 PDF；**不写 verified**。

---

## 2. Lint 输入

| 输入 | 路径 | 用途 |
|------|------|------|
| B 类 registry | `config/cninfo_b_class_source_registry_draft.yaml` | source 定义、status、exclusion patterns |
| Category routing | `config/cninfo_announcement_categories.yaml` | route_to、exclusion、registry_status |
| JSON Schema | `schemas/b_class/*.schema.json` | document_type / status enum |
| Document fixtures | `fixtures/b_class/document/*.jsonl` | source_id、source_confidence |
| Raw file fixtures | `fixtures/b_class/raw_file/*.jsonl` | source_url、download_status |
| Parse run fixtures | `fixtures/b_class/parse_run/*.jsonl` | parse_status dry-run |

**不读取：** CNINFO API、数据库、Phase 1 CSV（只读 fixture 派生结果）。

---

## 3. Lint 规则（R001–R023）

| rule_id | severity | 检查 |
|---------|----------|------|
| R001 | FAIL | `sources[].source_id` 唯一 |
| R002 | FAIL | `source_layer` 必须为 `document_corpus` |
| R003 | FAIL | 禁止 `verified: true`、`recommended_status: verified`、enum 含 `verified` |
| R004 | FAIL | `source_category` 仅允许 7 类 B 类 corpus category |
| R005 | FAIL | 必填：`source_id`, `source_name`, `source_layer`, `source_category`, `document_type_candidates`, `status.recommended_status`, `status.verified` |
| R006 | FAIL | `recommended_status` 仅允许 candidate/testing/testing_stable_sample/partial/blocked/deprecated |
| R007 | FAIL/WARN | `cninfo_periodic_report_pdf` 须为 `testing_stable_sample`；其他 non-periodic 须为 `candidate` |
| R008 | FAIL | category `route_to.source_id` 须存在于 registry |
| R009 | FAIL | category YAML 顶层 `verified` 须为 `false` |
| R010 | INFO | `category_code: null` 允许；非 null 仅 INFO |
| R011 | FAIL | `periodic_report` exclusion_patterns 须含 7 项核心短语 |
| R012 | WARN | inquiry/meeting/general 三 source 应为 `candidate` |
| R013 | FAIL | 8 个 `schemas/b_class/*.schema.json` 文件存在 |
| R014 | FAIL | document fixture `source_id` 须在 registry |
| R015 | FAIL | periodic fixture 可 `testing_stable_sample`；non-periodic 须 `candidate` |
| R016 | FAIL | raw_file 行 `source_url` 非空；空 jsonl 文件允许 |
| R017 | FAIL | parse_run：periodic→`not_started`，non-periodic→`skipped` |
| R018 | FAIL | registry/category/fixture 不得含 D 类 source_id |
| R019 | FAIL | `document_type` 属于 `b_document` enum |
| R020 | FAIL | `retrieval_status` 属于 `b_document` enum |
| R021 | FAIL | `classification_status` 属于 `b_document` enum |
| R022 | FAIL | `download_status` 属于 `b_raw_file` enum |
| R023 | FAIL | `parse_status` 属于 `b_document_parse_run` enum |

---

## 4. 输出

| 输出 | 路径 |
|------|------|
| CSV | `outputs/validation/cninfo_b_class_registry_lint_report.csv` |
| Summary MD | `outputs/validation/cninfo_b_class_registry_lint_summary.md` |

CSV 列：`rule_id`, `severity`, `target`, `status`, `message`, `suggested_fix`

**退出码：** 有 FAIL → 1；`--strict` 且有 WARN → 1；否则 0。

---

## 5. 与 D 类 lint 的区别

| 维度 | D 类 lint | B 类 lint |
|------|-----------|-----------|
| 主对象 | fixed-table API source | document_corpus PDF source |
| 交叉配置 | `cninfo_table_sources.yaml` | `cninfo_announcement_categories.yaml` |
| Fixture | `fixtures/d_class/` | `fixtures/b_class/` |
| 状态重点 | `testing_stable_sample` ×10 | periodic=stable，non-periodic=candidate |
| Schema 目录 | `schemas/d_class/` | `schemas/b_class/` |

---

## 6. 质量边界

- Lint **PASS** 不代表 CNINFO retrieval coverage%。
- 不代表 PDF 已下载或已解析。
- 不代表 source **verified**（全项目禁止写 verified）。
- offline title fixture 的 `retrieval_status=found` 仅表示 benchmark 路由，非 Phase 1 式 found。

---

## 7. 下一步

1. Corpus retrieval validation 小样本设计。
2. Known-document benchmark 替换为真实 CNINFO 样本（补 `pdf_url`）。
3. Probe 官方 `category_code` 填入 YAML。
4. 允许小样本请求后更新 raw_file / parse_run 状态。

---

## 参考

| 文档 | 路径 |
|------|------|
| B registry 设计 | [cninfo_b_class_source_registry_design.md](cninfo_b_class_source_registry_design.md) |
| Category routing | [cninfo_b_class_category_routing_rules.md](cninfo_b_class_category_routing_rules.md) |
| D 类 lint 先例 | [cninfo_d_class_registry_lint_design.md](cninfo_d_class_registry_lint_design.md) |
