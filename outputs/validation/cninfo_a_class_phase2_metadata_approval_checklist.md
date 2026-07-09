# CNINFO A 类 Phase 2 Metadata Expansion — 批准检查清单

_生成时间：2026-07-09_

> **性质：** Phase 2 metadata expansion 人工批准检查清单；**无 CNINFO** · **无 live** · **NOT APPROVED**

---

## Phase 1 前置条件

- [ ] **Phase 1 boundary reviewed**
  - `a_class_phase1_boundary_gate = PASS_WITH_CAVEAT`
  - boundary commit `2f1f342` 已 review
  - [boundary signoff](../../plans/cninfo_a_class_phase1_boundary_signoff.md) 已读

- [ ] **Phase 1 v2 matching policy reviewed**
  - `match_title_for_report_type()` report-type 专用过滤
  - `ENGLISH_TITLE_REJECT` 已启用
  - matching tests **10/10 PASS**
  - v2 rerun **5/5** · wrong_report_type=**0**

---

## Phase 2 Universe 审阅

- [ ] **20-company universe reviewed**
  - [universe draft](cninfo_a_class_phase2_metadata_universe_draft.csv)（A2M001–A2M020）
  - 全部活跃上市 · 非 ST / *ST · 非退市 · 非 BSE legacy
  - 无 manual identity review case
  - phase1_overlap=**0**（避开 ALM001–ALM005 公司代码）

- [ ] **report-type mix reviewed**
  - annual_report：**8**
  - semi_annual_report：**4**
  - quarterly_report_q1：**4**
  - quarterly_report_q3：**4**

- [ ] **candidate universe design reviewed**
  - [candidate design](cninfo_a_class_phase2_candidate_universe_design.csv)（12 bucket）

---

## 输出与安全

- [ ] **output root isolated**
  - 专用根：`outputs/validation/cninfo_a_class_phase2_metadata_expansion/`
  - 不写入 Phase 1 根 `cninfo_a_class_tiny_live_metadata/`
  - 不写入 `outputs/harvest/` · `outputs/snapshot/`

- [ ] **no PDF download**
  - `DOWNLOAD_PDF = False`（runner 硬编码）

- [ ] **no PDF parse**
  - `PARSE_PDF = False`

- [ ] **no DB**
  - `WRITE_DB = False`

- [ ] **no MinIO**
  - `WRITE_MINIO = False`

- [ ] **no RAG**
  - `ENABLE_RAG = False`

---

## 批准与执行

- [ ] **explicit user approval required**
  - flag：`--approve-a-class-phase2-metadata-expansion`
  - **当前状态：NOT APPROVED**

- [ ] **runner extension required**
  - Phase 2 runner **未实现**（本回合仅规划）
  - dry-run + live 测试 **未执行**

- [ ] **schema freeze v1 unchanged**
  - 不修改 field catalog · registry draft

- [ ] **no verified / production_ready / testing_stable_sample**
  - 不写 verified
  - 不标 production_ready
  - 不升级 testing_stable_sample

---

## 签核

| 项 | 签核人 | 日期 | 备注 |
|----|--------|------|------|
| Phase 1 boundary | | | |
| v2 matching policy | | | |
| 20-company universe | | | |
| report-type mix | | | |
| output isolation | | | |
| explicit approval | | | **待批准** |

---

**Gate：** `a_class_phase2_metadata_planning_gate = READY_FOR_APPROVAL`

**不是 PASS。** **不是 live_ready。**
