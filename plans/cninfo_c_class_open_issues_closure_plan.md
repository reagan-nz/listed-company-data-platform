# CNINFO C-Class Open Issues & Closure Plan（Era C Phase 4）

_生成时间：2026-07-08_

> **性质：** harvest milestone 已完成后的**问题梳理与收口计划**。**不是**新 harvest · **不是** DB/RAG · **不写 verified** · **不升级 testing_stable_sample**。
>
> **本轮：** 仅文档规划；**无 CNINFO** · **无 live** · **无 raw/normalized 修改**。

---

## 1. Current Status

### Harvest milestone

**C-class harvest milestone completed.**

863 non-BSE full harvest 已落地：

| 指标 | 结果 |
|------|------|
| harvest_full_gate | **PASS_WITH_RESUME** |
| raw total | **6041** / 6041 |
| normalized total | **8630** / 8630 |
| completed companies | **863** / 863 |
| blocked | **0** |
| http_error | **0** |
| hold_overlap | **0** |

QA 与 parser patch 后：

| 指标 | 结果 |
|------|------|
| QA conclusion | **PASS_WITH_CAVEAT** |
| QA flags | **72**（post-triage，原 137） |
| dividend needs_review 事件 | **12**（原 80） |
| triage conclusion | **PASS_WITH_CAVEAT_REVIEW_QUEUE_READY** |

### Overall completion

**C-class is NOT fully completed.**

当前阶段状态：

```
HARVEST_COMPLETED_QA_ONGOING
```

含义：

- **Harvest 执行线已收口**（863 磁盘产物 + gate PASS_WITH_RESUME）。
- **质量收口、字段政策、universe 侧轨、产品规则尚未关闭**。
- **禁止**将本阶段标记为 verified 或 testing_stable_sample。

---

## 2. Completed Milestones

以下里程碑**已完成**（证据链见 `outputs/validation/` · `outputs/harvest/cninfo_c_class/` · `plans/`）：

| # | 里程碑 | 关键产物 / gate |
|---|--------|-----------------|
| 1 | **Source validation** | 30/195/889/stable200 scale smoke · P2-A live PASS · [source status decision](cninfo_c_class_source_status_decision.md) |
| 2 | **Field inventory** | [field inventory](cninfo_c_class_field_inventory.md) · CSV **120** 字段 · 64/31/25 三分法 |
| 3 | **Harvest plan** | [harvest plan](cninfo_c_class_harvest_plan.md) · [863 execution plan](cninfo_c_class_full_harvest_863_execution_plan.md) |
| 4 | **Mapper implementation** | `lab/cninfo_c_class_mappers.py` · 6 direct + derived · dividend mapper **10/10** fixture |
| 5 | **863 full harvest** | `harvest_full_gate = PASS_WITH_RESUME` · raw 6041 · normalized 8630 |
| 6 | **QA review** | [qa review](outputs/validation/cninfo_c_class_full_harvest_qa_review.md) · **PASS_WITH_CAVEAT** |
| 7 | **Dividend parser patch** | `parse_dividend_f007v()` · `10股派X元（含税）` 变体 · fixture **10/10** |
| 8 | **Offline remap** | [remap summary](outputs/validation/cninfo_c_class_dividend_history_remap_summary.md) · needs_review **80→12** |
| 9 | **QA triage** | [flag triage](outputs/validation/cninfo_c_class_full_harvest_qa_flag_triage.md) · **PASS_WITH_CAVEAT_REVIEW_QUEUE_READY** |

**已完成里程碑数：9**

---

## 3. Open Issues

共 **9** 类开放问题（A–I）。**未关闭前，C-class 不算整体完成。**

### A. QA review queue

**状态：OPEN · P0**

Post-triage 剩余 **72** flags（[qa_flags.csv](../outputs/validation/cninfo_c_class_full_harvest_qa_flags.csv)）：

| 类别 | 数量 | 说明 |
|------|------|------|
| dividend_parse（P1） | **12** 公司 / **12** 事件 | 长尾 `needs_review` F007V |
| missing_normalized_core（P0） | **6** 公司 / **12** 字段行 | industry/contact nullable 缺口 |
| source_caveat（P2） | **54** 条 / **28** 公司 | `empty_but_valid` on partial/caveat sources |

**未决：** 每条 flag 需 **关闭（resolved）** 或 **显式接受（accepted_caveat）** 并记录理由。

**禁止：** 因 queue 未处理而宣称 C-class 完成。

---

### B. review_later fields

**状态：OPEN · P1**

[field inventory](../outputs/validation/cninfo_c_class_field_inventory.csv) 中 `include_in_normalized_snapshot=review`：**31** 字段。

代表问题：

- 语义不稳（如 `index_or_plate_labels` / F044V）
- mapper 未覆盖或仅 raw 保留
- schema 槽位待确认

**未决：** 逐字段复判 → `yes`（升入 core）· `no`（raw_only）· `drop`（弃用）· `defer`（延期并记录）。

---

### C. raw_only fields

**状态：OPEN · P1**

`include_in_normalized_snapshot=no`：**25** 字段。

含：

- security observe 相关 raw 保留（14）
- basic/executive/shareholder 等待定 raw 列

**未决：** 最终政策——永久 raw_only · 升 review · 或明确永不进 snapshot。

---

### D. company_snapshot

**状态：OPEN · P2 · not designed**

[profile data model draft](cninfo_c_class_profile_data_model_draft.md) 仅为逻辑草案；**无**：

- 聚合 `company_snapshot` schema 定稿
- 863 家 snapshot 离线生成规范
- C-class 10 源 → 单公司视图的字段合并规则

**未决：** snapshot 设计属于 **P2**，在 QA queue 关闭后进行。

---

### E. security_observe

**状态：OPEN · P3**

`cninfo_company_security_profile`：**observe_only**。

- 863 harvest 已写 raw + normalized observe 文件
- **不进入**主 company snapshot gate
- listing_status / is_st 等字段在 inventory 中为 review_later / raw_only

**未决：** 是否长期 observe · 是否升格为 caveat 主源 · 是否仅作审计旁路。

---

### F. hold universe

**状态：OPEN · P4**

[26 all6 hold](../lab/eval_companies_c_class_889_rerun_all6_hold.yaml) 自 863 harvest universe **排除**。

- `hold_overlap = 0`（已验证）
- 26 家 **6/6 主源全失败** · `sample_quality_or_status_review`

**未决：** 永久 hold · 人工清洗后重试 · 移出 C-class 母本 · 单独 abnormal 子 universe。

---

### G. BSE / abnormal side-track

**状态：OPEN · P4**

当前 863 harvest = **non-BSE only**。未覆盖：

| 侧轨 | 规模 | 状态 |
|------|------|------|
| BSE 920 | 12（195 active 子集） | 独立 child universe · 未并入 863 gate |
| BSE 83/87 legacy | 8 | **HOLD** · scode HTTP 500 |
| abnormal_review | 3+ | 样本质量审查 |

**未决：** 侧轨文档化 + 是否单独立项；**不**与 863 主 gate 混判。

---

### H. registry backfill

**状态：OPEN · P5 · not approved**

- P1/P2-A YAML backfill：**决策 only**，**未执行**
- dividend_history YAML：**GO（决策 only）** · **不执行**
- `config/cninfo_c_class_source_candidates.yaml` 仍有 4 源 `candidate`

**未决：** 是否批准 YAML 执行 · 哪些源升级 `testing` · 与 harvest 产物关系。

**红线：** 本计划阶段 **不执行** YAML backfill。

---

### I. product quality rules

**状态：OPEN · P1（与 B/C 并行文档化）**

Harvest / QA 已有技术 gate，但**产品层展示规则未定型**：

| 规则域 | 当前事实 | 未文档化 |
|--------|----------|----------|
| `empty_but_valid` | 计 reachability · 不计 http_error | 下游 UI/报表如何展示 |
| `source_partial` | share_capital / top_float 允许空表 | 主 snapshot 是否标注 partial-risk |
| `needs_review` | dividend 事件级标记 | 何时阻断 vs 仅黄标 |
| `observe_only` | security 旁路 | 是否对消费者可见 |

**未决：** 一份 **quality display policy** 文档（非 verified · 非 DB）。

---

## 4. Closure Order

推荐收口顺序（**禁止跳步**）：

| 优先级 | 工作包 | 内容 | 依赖 |
|--------|--------|------|------|
| **P0** | **QA review queue closure** | 72 flags → resolved / accepted_caveat；产出 closure log | harvest 完成 |
| **P1** | **review_later / raw_only 复判** | 31 + 25 字段政策定稿；更新 inventory CSV | P0 进展或并行只读复判 |
| **P1** | **product quality rules** | empty_but_valid · source_partial · needs_review 展示规则 | 与 P1 字段政策对齐 |
| **P2** | **company_snapshot planning** | schema draft · 聚合规则 · 离线生成规范（无 DB） | P0 queue 关闭或接受 |
| **P3** | **security observe decision** | 长期 observe vs 升格 caveat | P2 草案输入 |
| **P4** | **hold / BSE / abnormal** | 26 hold + BSE 侧轨文档与 universe 决策 | 不阻塞 863 主结论 |
| **P5** | **registry backfill planning** | YAML 执行批准矩阵（仍不执行） | 字段政策 P1 完成 |

**显式禁止的跳步：**

- P0 未完成 → **不做** company_snapshot 实现
- 任何阶段 → **不做** DB / MinIO / RAG
- 任何阶段 → **不执行** registry YAML backfill
- 任何阶段 → **不写** verified · **不升** testing_stable_sample

---

## 5. Acceptance Criteria

C-class **真正做完**（`C_CLASS_PHASE4_CLOSED`）需满足：

| # | 验收项 | 标准 |
|---|--------|------|
| 1 | QA review queue | **72** flags 全部 closed 或 explicit accepted · 有 closure 记录 |
| 2 | review_later | **31** 字段逐条 resolved（yes/no/defer + 理由） |
| 3 | raw_only | **25** 字段最终政策文档化 |
| 4 | company_snapshot | schema **drafted** · 聚合规则 **documented**（不要求 DB 入库） |
| 5 | quality rules | product display policy **documented** |
| 6 | hold / side-track | 26 hold + BSE/abnormal **documented** with decision |
| 7 | registry backfill | approve / defer / reject **decision ready**（仍可不执行） |
| 8 | security | observe 长期策略 **documented** |
| 9 | 红线 | **no verified** · **no testing_stable_sample** · **no DB/MinIO/RAG** |

**当前对照：** 9 项中 **0** 项 fully closed → **C-class NOT completed**。

---

## 6. Next Immediate Task

**下一步只做：QA review queue closure planning**

具体交付（规划 only · 本轮不执行 live）：

1. 起草 `plans/cninfo_c_class_qa_review_queue_closure_plan.md`（或等价 checklist）
2. 按 P0/P1/P2 分层，为 **72** flags 定义 closure 动作模板：
   - `resolved`（人工确认源端 nullable / parser 长尾）
   - `accepted_caveat`（source_partial / empty_but_valid 政策内接受）
   - `defer`（需外部信息 · 记录原因）
3. 产出目标：`qa_flags_closure_log.csv` 结构定义（**不要求本轮填完**）

**明确不做：**

- company_snapshot 设计与实现
- DB / MinIO / RAG
- registry YAML backfill 执行
- 新 harvest live / CNINFO 请求
- raw / normalized 数据修改

---

## 7. 红线确认

- 未请求 CNINFO
- 未重跑 harvest live
- 未修改 raw / normalized 数据
- 未写 verified
- 未升级 testing_stable_sample
- 未入库 / MinIO / RAG
- 未执行 YAML backfill
- 未修改 B / D / Phase1

---

## 8. 参考文档

| 文档 | 用途 |
|------|------|
| [cninfo_c_class_full_harvest_qa_review.md](../outputs/validation/cninfo_c_class_full_harvest_qa_review.md) | QA 总览 |
| [cninfo_c_class_full_harvest_qa_flags.csv](../outputs/validation/cninfo_c_class_full_harvest_qa_flags.csv) | 72 flags |
| [cninfo_c_class_full_harvest_qa_flag_triage.md](../outputs/validation/cninfo_c_class_full_harvest_qa_flag_triage.md) | 分层 triage |
| [cninfo_c_class_field_inventory.md](cninfo_c_class_field_inventory.md) | 31 review + 25 raw_only |
| [cninfo_c_class_source_status_decision.md](cninfo_c_class_source_status_decision.md) | source_partial / observe 政策 |
| [cninfo_c_class_profile_data_model_draft.md](cninfo_c_class_profile_data_model_draft.md) | snapshot 草案（未完成） |
