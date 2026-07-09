# CNINFO B 类 Existing Artifact Inventory Summary

_生成时间：2026-07-09_

> **性质：** 离线盘点快照；未执行任何 CNINFO 请求、live、harvest、crawler、PDF 下载或解析。  
> **明细表：** [cninfo_b_class_existing_artifact_inventory.csv](cninfo_b_class_existing_artifact_inventory.csv)

---

## Search Scope

本轮仅做**离线文件名与轻量文本内容检查**，搜索范围如下：

| 目录 | 检查内容 |
|------|----------|
| `plans/` | A-class / B-class / boundary / validation 设计文档 |
| `config/` | registry YAML、announcement categories、retrieval strategies |
| `schemas/b_class/` | B-class JSON Schema draft |
| `fixtures/b_class/` | document / raw_file / parse_run / retrieval_validation fixtures |
| `lab/` | A-class coverage、B-class validation、shared announcement utilities |
| `outputs/validation/` | A-class Phase1 总结、B-class validation summaries（**排除** `outputs/harvest/cninfo_c_class/phase3_batch_500_001/`） |

搜索关键词：`announcement`、`notice`、`disclosure`、`report`、`pdf`、`document`、`annual`、`periodic`、`cninfo`、`A-class`、`B-class`。

**未执行：** 任何 collection 脚本、live metadata 重跑、PDF 下载/解析。

---

## Existing Relevant Artifacts

盘点 CSV 共 **72** 条 artifact 记录；其中 **relevance=high** 共 **28** 条。

### A-class report retrieval

| 产物 | 价值 |
|------|------|
| `lab/validate_cninfo_report_coverage.py` | A-class 主脚本；`hisAnnouncement/query` 参数、title exclusion、period match |
| `outputs/validation/cninfo_report_phase1_final_summary.md` | Phase1 收口：749/796 = 94.10%，testing usable candidate |
| `outputs/validation/cninfo_report_p1_coverage_validation.csv` | per-company coverage 明细 |
| `lab/build_cninfo_report_p1_identity_mapping.py` | `company_code` ↔ `org_id` 映射 |
| `lab/validate_cninfo_report_announcements.py` | 旧策略探测（deprecated 参考） |

### B-class announcement / document candidate

| 产物 | 价值 |
|------|------|
| `config/cninfo_b_class_source_registry_draft.yaml` | 4 个 B-class source；`adjunctUrl` 字段映射 |
| `plans/cninfo_b_class_corpus_design.md` | corpus 职责与 document_type |
| `plans/cninfo_b_class_document_model_draft.md` | raw_file / document / version 逻辑模型 |
| `schemas/b_class/` | 8 个 JSON Schema draft-07 |
| `fixtures/b_class/document/*.jsonl` | 20+13 条 metadata fixture |
| `lab/validate_cninfo_b_class_corpus_retrieval.py` | dry-run + live metadata v1（5/5 PASS 历史证据） |
| `outputs/validation/cninfo_b_class_corpus_retrieval_live_summary.md` | tiny live metadata v1 报告 |
| **本轮新增** `plans/cninfo_b_class_announcement_metadata_architecture_plan.md` | Phase0 架构收敛入口 |
| **本轮新增** `plans/cninfo_b_class_source_discovery_plan.md` | 离线 source discovery 五步策略 |

### shared CNINFO utilities

| 产物 | 价值 |
|------|------|
| `utils/fetcher.py` | 礼貌 HTTP 请求原型 |
| `lab/validate_cninfo_pdf_metadata.py` | PDF URL / hash 规则验证（不下载正文） |
| `lab/validate_cninfo_latest_announcements.py` | 最新公告列表栏目验证 |
| `config/cninfo_announcement_retrieval_strategies.yaml` | 关键词检索策略 |
| `lab/probe_cninfo.py` / `lab/extract_annual_report.py` | Era B 冻结链路；**不作为当前 B-class 执行路径** |

### quality / validation utilities

| 产物 | 价值 |
|------|------|
| `lab/validate_cninfo_b_class_category_routing.py` | 16 benchmark PASS |
| `lab/lint_cninfo_b_class_registry.py` | 23 rules PASS |
| `outputs/validation/cninfo_b_class_*_schema_validation_summary.md` | document/raw_file/non-periodic/parse_run schema PASS |
| `outputs/validation/cninfo_b_class_readiness_matrix.csv` | 本轮新增 12-component readiness |
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | 5 ready + guard case |

---

## Endpoint Hints

以下 endpoint / source 名称来自既有 registry、脚本注释与计划文档，**本轮未 live 验证**：

| 名称 | URL / 线索 | 来源 |
|------|------------|------|
| `hisAnnouncement/query` | `https://www.cninfo.com.cn/new/hisAnnouncement/query` | A-class + B-class registry + corpus retrieval script |
| `topSearch/query` | `https://www.cninfo.com.cn/new/information/topSearch/query` | B-class corpus retrieval script orgId 辅助 |
| `disclosure/list/notice` | UI page / Referer | registry `page_url` for periodic_report_pdf |
| `cninfo_periodic_report_pdf` | source_id | registry YAML |
| `cninfo_general_announcement_pdf` | source_id | registry YAML |
| `cninfo_inquiry_reply_pdf` | source_id | registry YAML；endpoint **null** |
| `cninfo_meeting_notice_pdf` | source_id | registry YAML；endpoint **null** |
| `adjunctUrl` | PDF URL 字段 | registry `url_field` |
| `announcementId` | 公告 ID 字段 | registry `document_id_field` |
| `announcementTitle` | 标题字段 | registry `title_field` |
| `announcementTime` | 披露日字段 | registry `announcement_date_field` |

---

## Reuse Opportunities

| 机会 | 说明 |
|------|------|
| **company universe YAML** | A-class P1 identity mapping + C-class eval YAML 可提供 `company_code` / `org_id`；B-class 尚未有独立 harvest universe |
| **CNINFO request helper** | `validate_cninfo_report_coverage.py` 与 `validate_cninfo_b_class_corpus_retrieval.py` 已共享 AJAX headers / sleep；`utils/fetcher.py` 可作未来统一封装参考 |
| **quality report pattern** | C-class harvest QA CSV + summary 模式可复用到 B-class metadata harvest QA |
| **PDF URL lineage pattern** | registry `adjunctUrl` + `b_raw_file.schema.json` + periodic raw_file fixtures 已形成 URL 登记骨架 |
| **source registry pattern** | `cninfo_b_class_source_registry_draft.yaml` 四源草稿 + lint 23 rules 可直接延续 |
| **title routing** | `cninfo_announcement_categories.yaml` + 16 routing benchmarks 可支撑 non-periodic 分类 |
| **ready-case mechanism** | known_document_retrieval_cases.yaml + selector + checklist 可控制 tiny live 范围 |

---

## Gaps

| 缺口 | 状态 |
|------|------|
| announcement schema not frozen | 有 JSON Schema draft 与 architecture minimum fields，但缺 Phase1 freeze CSV |
| source endpoint not validated | inquiry/meeting 两源 endpoint 仍为 null；category browse API 未定义 |
| PDF URL lineage not tested | fixture 级有；全市场 / 扩大样本未测 |
| category taxonomy not defined | routing draft 存在；官方 CNINFO category code 未完全对齐 |
| dedup policy not implemented | 仅假设 `announcement_id` 唯一 |
| rate limit policy not implemented | registry 默认 sleep 0.6s；无并发/退避执行器 |
| unified B-class harvest universe | 缺失 |
| endpoint candidate table | 尚未生成 CSV |
| B-class metadata harvest QA runner | 缺失 |

---

## Gate

```text
b_class_existing_artifact_inventory_gate = PASS
```

---

## Parallel Safety

- C-class status remains: **`SNAPSHOT_GENERATED_QA_REVIEW`**
- `outputs/harvest/cninfo_c_class/phase3_batch_500_001/`：**未读取、未写入**
- No B-class live execution in this round

---

## Recommended Next B-class Task

离线生成：

1. `outputs/validation/cninfo_b_class_endpoint_candidate_table.csv`
2. `outputs/validation/cninfo_b_class_phase1_minimum_fields.csv`

并对照 `config/cninfo_b_class_source_registry_draft.yaml` 做 schema freeze v1 review。**仍不 live。**
