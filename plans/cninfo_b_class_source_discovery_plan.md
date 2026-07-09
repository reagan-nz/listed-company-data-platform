# CNINFO B 类 Source Discovery 计划

_最后更新：2026-07-09_

> **性质：** 规划 only；本轮 **不调用 CNINFO**、不 live、不 harvest、不下载 PDF。  
> **前置：** [cninfo_b_class_announcement_metadata_architecture_plan.md](cninfo_b_class_announcement_metadata_architecture_plan.md) · [cninfo_b_class_source_registry_design.md](cninfo_b_class_source_registry_design.md)  
> **并行约束：** C-class Phase 3 live harvest 运行中也不启动 B-class live；不读写在跑输出根。

---

## Candidate Sources

以下为 B-class 未来可能使用的 CNINFO 公告 / 文档来源类型（概念层，**未在本轮 live 验证**）：

| 候选源类型 | 说明 | 既有线索 |
|------------|------|----------|
| **company announcement list** | 按公司 + 时间窗检索公告列表 | `hisAnnouncement/query`；见 A-class / B-class registry |
| **periodic report announcement** | 年报 / 半年报 / 季报全文公告 | A-class Phase 1；`cninfo_periodic_report_pdf` |
| **non-periodic announcement** | 董事会决议、股东大会、业绩预告等事件公告 | `cninfo_general_announcement_pdf`；category routing |
| **PDF attachment URL** | 公告响应中的 `adjunctUrl` → 静态 PDF 链接 | registry `url_field: adjunctUrl` |
| **announcement category index** | 官方公告类别码 / 栏目标签 | `cninfo_announcement_categories.yaml`；`cninfo_announcement_retrieval_strategies.yaml` |

### Registry 中已登记的 4 个 B-class source（草案）

| source_id | source_category | query_endpoint 状态 |
|-----------|-----------------|---------------------|
| `cninfo_periodic_report_pdf` | periodic_report_pdf | 已记录 `hisAnnouncement/query`（继承 A-class） |
| `cninfo_general_announcement_pdf` | announcement_pdf | 已记录 `hisAnnouncement/query`（candidate） |
| `cninfo_inquiry_reply_pdf` | inquiry_reply_pdf | endpoint **null**（待 probe） |
| `cninfo_meeting_notice_pdf` | meeting_notice_pdf | endpoint **null**（待 probe） |

### 相关但非 B-class 主线的 adjacent 源

- `topSearch/query`：orgId 发现辅助（A/B live 脚本共用）
- `disclosure/list/notice` UI 页：Referer / 人工 probe 参考
- Era B `probe_cninfo.py` / `extract_annual_report.py`：历史 PDF 下载解析链路，**冻结**，不作为当前 B-class 执行路径

---

## Discovery Strategy

未来 source discovery 严格按以下顺序推进；**本轮仅完成 Step 1–2 的离线盘点**。

### Step 1. Inspect existing A-class report retrieval artifacts

离线检查以下产物，提取 endpoint、参数模板、title filter、orgId 规则：

| 产物 | 路径 | 目的 |
|------|------|------|
| Phase 1 最终总结 | [cninfo_report_phase1_final_summary.md](../outputs/validation/cninfo_report_phase1_final_summary.md) | A-class coverage 口径与有效 found 定义 |
| Coverage 脚本 | [lab/validate_cninfo_report_coverage.py](../lab/validate_cninfo_report_coverage.py) | `hisAnnouncement/query` 参数、title exclusion、period match |
| Identity mapping | [lab/build_cninfo_report_p1_identity_mapping.py](../lab/build_cninfo_report_p1_identity_mapping.py) | `company_code` ↔ `org_id` 映射 |
| P1 coverage CSV | `outputs/validation/cninfo_report_p1_coverage_validation.csv` | 已知成功案例与失败模式 |
| A→B registry 继承 | [config/cninfo_b_class_source_registry_draft.yaml](../config/cninfo_b_class_source_registry_draft.yaml) | `cninfo_periodic_report_pdf` 字段映射 |

**本轮状态：** 已完成离线阅读与 inventory 归档（见 [cninfo_b_class_existing_artifact_inventory_summary.md](../outputs/validation/cninfo_b_class_existing_artifact_inventory_summary.md)）。

### Step 2. Inspect existing B-class candidate notes / scripts

离线检查 B-class corpus、schema、routing、retrieval validation 既有草案：

| 类别 | 代表路径 |
|------|----------|
| Corpus / document model | `plans/cninfo_b_class_corpus_design.md`、`plans/cninfo_b_class_document_model_draft.md` |
| Registry / categories | `config/cninfo_b_class_source_registry_draft.yaml`、`config/cninfo_announcement_categories.yaml` |
| Routing / validation | `lab/validate_cninfo_b_class_category_routing.py`、`plans/cninfo_b_class_validation_design.md` |
| Fixtures / schema | `fixtures/b_class/`、`schemas/b_class/` |
| Retrieval v1 证据 | `outputs/validation/cninfo_b_class_corpus_retrieval_live_summary.md`（5 ready · 5/5 PASS） |

**本轮状态：** 已完成 inventory；确认 B-class 已有 design-only + tiny live metadata v1，但**未形成全市场 metadata harvest 批准**。

### Step 3. Define endpoint candidates

基于 Step 1–2，整理 endpoint candidate 表（**设计表，不 live 验证**）：

| endpoint_candidate | method | 用途 | 当前状态 |
|------------------|--------|------|----------|
| `https://www.cninfo.com.cn/new/hisAnnouncement/query` | POST | 公司公告列表 + PDF metadata | A-class 已用；B-class registry 已登记 |
| `https://www.cninfo.com.cn/new/information/topSearch/query` | POST | orgId 辅助检索 | B-class live v1 脚本已引用 |
| `disclosure/list/notice` UI | GET | 类别浏览 / Referer | 仅页面线索，未 freeze |
| category-specific browse API | TBD | 按官方类别索引拉公告 | **未定义** |

输出物（后续 Step）：`outputs/validation/cninfo_b_class_endpoint_candidate_table.csv`（**尚未创建；不在本轮范围**）。

### Step 4. Run tiny offline / sample review

在 explicit live approval 之前，仅允许：

- 阅读既有 fixture / ready-case / live v1 报告；
- 离线 lint / schema validation / routing benchmark；
- 人工对照 title → category 路由结果；
- 设计 dedup、rate-limit、quality flag 口径。

**禁止：** 新 CNINFO 请求、扩大 live case 数、PDF 下载。

### Step 5. Only later request live approval

只有满足以下条件后，才进入 controlled live metadata：

1. `b_class_existing_artifact_inventory_gate = PASS`
2. readiness matrix 中 P0 项（endpoint discovery、schema、lineage、taxonomy）达到 `design_complete` 或 `ready_for_tiny_sample`
3. C-class Phase 3 live harvest 完成且不与 B-class live 抢带宽
4. 用户显式批准 B-class tiny live metadata

---

## Reuse vs Gap（Discovery 视角）

### 可直接复用

- A-class `hisAnnouncement/query` 参数与 title exclusion 逻辑
- B-class registry YAML 四源草稿
- `cninfo_announcement_categories.yaml` + title routing benchmark（16 PASS）
- document / raw_file JSON Schema + 33/20/13 条 fixture
- corpus retrieval ready-case 机制与 5-case live v1 报告
- `utils/fetcher.py` 礼貌请求模式（未来 live 时参考）

### 仍缺失

- 全量 announcement metadata schema **未 freeze** 到 Phase 1 最小字段 CSV
- `cninfo_inquiry_reply_pdf` / `cninfo_meeting_notice_pdf` endpoint **未独立验证**
- PDF URL lineage **未在全市场样本上测试**
- category taxonomy 与官方 CNINFO category code **未完全对齐**
- dedup policy / rate-limit policy **未实现**
- company universe linkage 仍依赖 A-class / C-class 各自 YAML，**未统一 B-class harvest universe**

---

## Gate

```text
b_class_source_discovery_gate = OFFLINE_INVENTORY_COMPLETE
```

下一轮建议任务：**生成 endpoint candidate 表 + announcement metadata schema freeze v1**（仍 offline，不 live）。
