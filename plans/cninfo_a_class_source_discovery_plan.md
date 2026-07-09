# CNINFO A 类 Source Discovery 计划

_最后更新：2026-07-09_

> **性质：** 规划 only；本轮 **不调用 CNINFO**、不 live、不 harvest、不下载 PDF。  
> **前置：** [cninfo_a_class_report_metadata_architecture_plan.md](cninfo_a_class_report_metadata_architecture_plan.md) · [cninfo_report_phase1_final_summary.md](../outputs/validation/cninfo_report_phase1_final_summary.md)  
> **并行约束：** C-class Phase 3 live harvest 运行中也不启动 A-class live；不读写在跑输出根；不修改 B-class / C-class 输出。

---

## Discovery Overview

A-class source discovery 目标：为 **annual / semi-annual / quarterly** 三类定期报告，离线梳理可检索 metadata 的 CNINFO 入口与字段预期。

本轮仅完成 **离线盘点与设计表**；所有 endpoint 的 live 重验 deferred 到显式批准后的 Phase 2。

---

## Candidate Source 1: Periodic Report PDF

| 项 | 内容 |
|----|------|
| **说明** | 通过公告检索接口获取定期报告全文 PDF 的 metadata 与 `adjunctUrl` |
| **endpoint candidate** | `POST https://www.cninfo.com.cn/new/hisAnnouncement/query` |
| **辅助 endpoint** | `POST https://www.cninfo.com.cn/new/information/topSearch/query`（orgId 解析） |
| **expected fields** | `announcementId`、`announcementTitle`、`announcementTime`、`adjunctUrl`、`secCode`、`secName`、`orgId` |
| **confidence** | **high** — A-class Phase 1 已验证 749/796 = 94.10% effective coverage |
| **risks** | SZSE 创业板 Q1/Q3 `empty_response` 残留；BSE 部分公司 orgId 映射缺口；title 误匹配摘要版需 exclusion |
| **validation plan** | 继承 `lab/validate_cninfo_report_coverage.py` 逻辑；Phase 2 tiny live 复用 P1 40 家 audit 子集；对照 `cninfo_report_p1_coverage_validation.csv` 做 offline fixture seed |

**既有线索：**

- [lab/validate_cninfo_report_coverage.py](../lab/validate_cninfo_report_coverage.py)
- [cninfo_report_phase1_final_summary.md](../outputs/validation/cninfo_report_phase1_final_summary.md)
- [config/cninfo_b_class_source_registry_draft.yaml](../config/cninfo_b_class_source_registry_draft.yaml) `cninfo_periodic_report_pdf`（A→B 继承登记）

---

## Candidate Source 2: Annual Report Metadata

| 项 | 内容 |
|----|------|
| **说明** | 年报（`annual_report`）专用 metadata 检索；title filter + report_period 匹配 |
| **endpoint candidate** | `POST https://www.cninfo.com.cn/new/hisAnnouncement/query`（`category=category_ndbg_szsh` 或等价 category 参数） |
| **expected fields** | `report_type=annual_report`、`report_period`（年末如 `YYYY-12-31`）、`announcement_title`（含「年度报告」）、`pdf_url` |
| **confidence** | **high** — P1 annual_report coverage 100%（mapped 子集） |
| **risks** | 摘要版 / 英文版 / 修订版标题干扰；需 title exclusion 规则 |
| **validation plan** | offline：从 P1 CSV 筛选 `report_type=annual_report` 行做 fixture；Phase 2：3 家 known-company（600000 / 300001 / 688001）tiny live 对照 |

**title exclusion 参考：** `validate_cninfo_report_coverage.py` 中 `TITLE_EXCLUSION_PATTERNS`（摘要、英文版、提示性公告等）。

---

## Candidate Source 3: Semi-Annual Report Metadata

| 项 | 内容 |
|----|------|
| **说明** | 半年报（`semi_annual_report`）专用 metadata 检索 |
| **endpoint candidate** | `POST https://www.cninfo.com.cn/new/hisAnnouncement/query`（`category=category_bndbg_szsh` 或等价） |
| **expected fields** | `report_type=semi_annual_report`、`report_period`（如 `YYYY-06-30`）、`announcement_title`（含「半年度报告」）、`pdf_url` |
| **confidence** | **high** — P1 semi_annual_report coverage 100%（mapped 子集） |
| **risks** | 与年报 category fallback 逻辑交叉；中期报告标题变体 |
| **validation plan** | offline：P1 CSV `semi_annual_report` 子集 fixture；Phase 2 tiny live 复用同一 3 家矩阵 |

---

## Candidate Source 4: Quarterly Report Metadata

| 项 | 内容 |
|----|------|
| **说明** | 一季报（`quarterly_report_q1`）与三季报（`quarterly_report_q3`）metadata 检索 |
| **endpoint candidate** | `POST https://www.cninfo.com.cn/new/hisAnnouncement/query`（`category=category_yjdbg_szsh` / `category_sjdbg_szsh`；存在 category fallback 逻辑） |
| **expected fields** | `report_type`（q1/q3）、`report_period`（`YYYY-03-31` / `YYYY-09-30`）、`announcement_title`、`pdf_url` |
| **confidence** | **medium** — P1 Q1 86.67%、Q3 90.00%；SZSE 创业板仍有缺口 |
| **risks** | `empty_response` 高发板块；category 参数因交易所而异；季报标题「第一季度报告」vs「一季度报告」变体 |
| **validation plan** | offline：按 exchange 分层统计 P1 失败模式；Phase 2 tiny live 优先覆盖 SZSE 创业板 known-fail case；不扩大 live 规模直到 Q1/Q3 规则 freeze |

**category fallback：** 见 `validate_cninfo_report_coverage.py` 中 quarterly category 回退逻辑（文档化，本轮不执行）。

---

## Candidate Source 5: Report Announcement Lineage

| 项 | 内容 |
|----|------|
| **说明** | 公告检索响应 → `report_document` + `document_lineage` 的谱系登记；含 `source_endpoint`、`retrieval_time`、`raw_hash` |
| **endpoint candidate** | 同 Source 1（`hisAnnouncement/query`）；lineage 为**响应处理层**而非独立 API |
| **expected fields** | `source_endpoint`、`retrieval_time`、`raw_hash`（响应 JSON hash）、`adjunct_url`（原始）、`pdf_url`（归一化）、`lineage_status`、`storage_status=not_attempted` |
| **confidence** | **medium** — registry 与 B-class `raw_file` schema 有草案；A-class 专用 lineage 对象**未 freeze** |
| **risks** | `adjunctUrl` 相对路径需 host 拼接；同一 `announcementId` 多次检索 hash 变化；无 PDF 下载则无法验证 `file_hash` |
| **validation plan** | Phase 0：定义 `document_lineage` 字段与 version 语义（本计划已完成）；Phase 1：离线 fixture 登记 lineage 字段；Phase 2：tiny live 对比 `raw_hash` 稳定性（同 announcement 隔日重查） |

**与 B-class 关系：** B-class `pdf_reference` / `raw_file` 逻辑可参考，但 A-class lineage 绑定 `report_type` + `report_period`，不混入非定期公告。

---

## Discovery Strategy

未来 source discovery 严格按以下顺序推进；**本轮仅完成 Step 1–3 的离线设计**。

### Step 1. Inspect existing A-class Phase 1 artifacts

| 产物 | 路径 | 目的 |
|------|------|------|
| Phase 1 最终总结 | [cninfo_report_phase1_final_summary.md](../outputs/validation/cninfo_report_phase1_final_summary.md) | coverage 口径与 effective found 定义 |
| Coverage 脚本 | [lab/validate_cninfo_report_coverage.py](../lab/validate_cninfo_report_coverage.py) | endpoint、title exclusion、period match |
| Identity mapping | [lab/build_cninfo_report_p1_identity_mapping.py](../lab/build_cninfo_report_p1_identity_mapping.py) | `company_code` ↔ `org_id` |
| P1 coverage CSV | `outputs/validation/cninfo_report_p1_coverage_validation.csv` | 成功案例与失败模式 |
| PDF metadata 脚本 | [lab/validate_cninfo_pdf_metadata.py](../lab/validate_cninfo_pdf_metadata.py) | URL/hash 规则参考（不下载正文） |

**本轮状态：** 离线阅读完成；作为 5 个候选源的 confidence 依据。

### Step 2. Define A-class object → field mapping

将 5 个候选源映射到 `report_document` / `report_period_snapshot` / `document_lineage` 三对象。

输出物：[cninfo_a_class_phase1_minimum_fields.csv](../outputs/validation/cninfo_a_class_phase1_minimum_fields.csv)

**本轮状态：** 已完成。

### Step 3. Assess readiness per component

输出物：[cninfo_a_class_readiness_matrix.csv](../outputs/validation/cninfo_a_class_readiness_matrix.csv)

**本轮状态：** 已完成。

### Step 4. Offline fixture seed（下一轮）

在 explicit live approval 之前，仅允许：

- 从 P1 CSV 派生 offline `report_document` fixture；
- 人工对照 title → report_type → report_period 解析；
- 离线 lint / schema validation 设计。

**禁止：** 新 CNINFO 请求、PDF 下载、修改 C/B-class 输出。

### Step 5. Request live approval（更晚）

只有满足以下条件后，才进入 controlled live metadata：

1. `a_class_initial_planning_gate = DESIGN_STARTED` 且 schema freeze review 通过
2. readiness matrix 中 P0 项达到 `design_complete` 或 `ready_for_tiny_sample`
3. C-class Phase 3 live harvest 完成且不与 A-class live 抢带宽
4. 用户显式批准 A-class tiny live metadata

---

## Reuse vs Gap

### 可直接复用

- A-class Phase 1 `hisAnnouncement/query` 参数与 title exclusion
- `company_code` ↔ `org_id` identity mapping
- P1 coverage CSV 与 audit 子集（40 家二轮 audit 97.5%）
- B-class registry 中 `cninfo_periodic_report_pdf` 字段映射草案
- `utils/fetcher.py` 礼貌请求模式（未来 live 时参考）

### 仍缺失

- A-class 专用 `report_document` JSON Schema **未 freeze**
- `report_period_snapshot` 读模型 **未实现**
- `document_lineage` 全市场样本测试 **未做**
- A-class harvest universe **未与 C-class registry 统一**
- dedup policy（`announcement_id` vs `document_id`）**未实现**
- `available_sections` 依赖未来 parser，**明确 deferred**

---

## Gate

```text
a_class_source_discovery_gate = OFFLINE_DESIGN_COMPLETE
```

下一轮建议任务：**A-class Phase 1 schema freeze review + offline fixture 骨架**（仍 offline，不 live）。
