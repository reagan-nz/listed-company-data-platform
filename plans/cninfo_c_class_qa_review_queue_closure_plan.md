# CNINFO C-Class QA Review Queue Closure Plan（Era C Phase 4）

_生成时间：2026-07-08_

> **性质：** QA review queue 的**关闭计划与分类判断**。**不是** harvest 重跑 · **不是** parser 修改 · **不是** re-map · **不写 verified**。
>
> **本轮：** 仅规划与离线分类；**无 CNINFO** · **无 live** · **无 raw/normalized 修改**。

---

## 1. Current QA Queue Status

| 项 | 值 |
|----|-----|
| QA queue total | **72** |
| C-class status | **`HARVEST_COMPLETED_QA_ONGOING`** |
| QA conclusion | **PASS_WITH_CAVEAT** |
| Triage conclusion | **PASS_WITH_CAVEAT_REVIEW_QUEUE_READY** |
| harvest_full_gate | **PASS_WITH_RESUME** |

**说明：** harvest milestone 已完成；72 条 QA flag 均已在本计划中分配 `recommended_action` 与 `closure_action`，但**尚未执行 closure classification 落账**（下一步）。C-class **未整体完成**。

**分类产物：** [cninfo_c_class_qa_review_queue_closure_plan.csv](../outputs/validation/cninfo_c_class_qa_review_queue_closure_plan.csv)（72 rows）

---

## 2. Queue Breakdown

| Tier | 类别 | 公司数 | flag 行数 | 严重度 |
|------|------|--------|-----------|--------|
| **P0** | missing_normalized_core | **6** | **6**（含 **12** 个字段缺口） | medium |
| **P1** | dividend_parse needs_review | **12** | **12** | medium |
| **P2** | source_caveat / empty_but_valid | **28** | **54** | low |

### P2 按 source 子类

| 子类 | flag 数 | source_status |
|------|---------|---------------|
| executive empty_but_valid | **9** | `proceed_testing_with_caveat` |
| share_capital empty_but_valid | **10** | `source_partial` |
| top_shareholders empty_but_valid | **16** | `proceed_testing_with_caveat` |
| top_float empty_but_valid | **19** | `source_partial` |

---

## 3. P0 Missing Normalized Core Review Plan

共 **6** 家公司、**12** 个 normalized_core 字段缺口。均已离线核对 `raw/basic_profile/*.json` 与 `field_fill_rate.csv`。**本轮不修，仅判断。**

| company_code | company_name | 缺口字段 | source | 根因判断 | 建议 closure |
|--------------|--------------|----------|--------|----------|--------------|
| 002710 | 慈铭体检 | F032V, F044V | cninfo_company_industry_profile（derived） | **basic source missing** — basic raw `F032V=null`, `F044V=null`；`MARKET` 有值 | `close_as_accepted_nullable_gap` |
| 601206 | 海尔施 | F032V, F044V | cninfo_company_industry_profile（derived） | **basic source missing** — 同上 | `close_as_accepted_nullable_gap` |
| 688235 | 百济神州 | F018V, F016V | contact / business_scope（derived） | **basic source missing** — `F018V=null`, `F016V=null`；`F015V`/`F017V` 有值 | `close_as_accepted_nullable_gap` |
| 688688 | 蚂蚁集团 | F032V, F044V | cninfo_company_industry_profile（derived） | **basic source missing** — `F032V=null`, `F044V=null` | `close_as_accepted_nullable_gap` |
| 688795 | 摩尔线程 | F014V, F044V | contact / industry（derived） | **basic source missing** — `F014V=null`, `F044V=null` | `close_as_accepted_nullable_gap` |
| 688809 | 强一股份 | F014V, F044V | contact / industry（derived） | **basic source missing** — `F014V=null`, `F044V=null` | `close_as_accepted_nullable_gap` |

### P0 判断汇总

| 判断类型 | 数量 | 说明 |
|----------|------|------|
| nullable derived field | **12/12** | 字段来自 basic derived mapper；源端 JSON 显式 null |
| basic source missing | **12/12** | CNINFO basic 未返回对应 F 字段 |
| mapper issue | **0** | mapper 已正确传播 null，非逻辑错误 |
| data repair needed | **0** | raw 文件完整、`retrieval_status=endpoint_found`，无需重 harvest |

**注意：** 002710 / 601206 / 688688 同时存在 P2 `empty_but_valid`（股东/股本端点空响应），与 P0 缺口**机制不同**——P0 是 basic 字段 null，P2 是独立端点空表。

---

## 4. P1 Dividend Needs Review Plan

剩余 **12** 条事件级 `needs_review`（12 家公司各 1 条）。`dividend_parse_status=partial`（公司级）含上述事件。

| # | company | period | F007V raw | parse_status | 建议 review_action | closure_action |
|---|---------|--------|-----------|--------------|-------------------|----------------|
| 1 | 000011 深物业A | 1995年报 | `10送1派1.00元` | needs_review | **accept_as_long_tail_manual_review** | close_as_manual_review_queue |
| 2 | 000655 金岭矿业 | 1995年报 | `94和95未分配利润均结转至上市后分配` | needs_review | **mark_as_no_distribution** | close_as_manual_review_queue |
| 3 | 000905 厦门港务 | 2006三季报 | `10转增8 股` | needs_review | **accept_as_long_tail_manual_review** | close_as_manual_review_queue |
| 4 | 002019 亿帆医药 | 2005年报 | `10派1.5 元（含税）` | needs_review | **add_small_parser_patch_later** | open_parser_patch_issue |
| 5 | 002041 登海种业 | 2014年报 | `10送14转増1股派3.5元(含税)` | needs_review | **accept_as_long_tail_manual_review** | close_as_manual_review_queue |
| 6 | 002060 广东建工 | 2007年报 | `10派1.2 元（含税）` | needs_review | **add_small_parser_patch_later** | open_parser_patch_issue |
| 7 | 600702 舍得酒业 | 1995年报 | `95年度利润滚存至96年度一并分配` | needs_review | **mark_as_no_distribution** | close_as_manual_review_queue |
| 8 | 600716 凤凰股份 | 1995年报 | `95年7月至12月利润全部上交` | needs_review | **mark_as_unparseable_but_raw_traceable** | close_as_manual_review_queue |
| 9 | 600728 佳都科技 | 1995年报 | `95年度利润只对老股东分配` | needs_review | **mark_as_unparseable_but_raw_traceable** | close_as_manual_review_queue |
| 10 | 600777 *ST新潮 | 1995年报 | `未分配利润滚存96年度合并派发` | needs_review | **mark_as_no_distribution** | close_as_manual_review_queue |
| 11 | 600877 电科芯片 | 1995年报 | `10送3.5元` | needs_review | **accept_as_long_tail_manual_review** | close_as_manual_review_queue |
| 12 | 603023 威帝股份 | 2015年报 | `10送5转增15派1.5元(含税)` | needs_review | **accept_as_long_tail_manual_review** | close_as_manual_review_queue |

### P1 模式判断

| pattern | 条数 | 处理策略 |
|---------|------|----------|
| 送股/转增+派现组合 | 3 | 长尾人工队列；无重复 dominant pattern |
| 其他无法解析文本 | 5 | `no_distribution` 或 `unparseable_but_raw_traceable` |
| 送股/转增组合 | 2 | 长尾人工队列 |
| 含税空格变体 `10派X 元（含税）` | 2 | **open_parser_patch_issue**（小 patch 候选，本轮不实施） |

**本轮红线：** 不修改 `parse_dividend_f007v()` · 不 re-map normalized。

---

## 5. P2 Source Caveat Plan

**54** 条 `source_caveat` / `empty_but_valid_response`。均符合已定义政策：`source_partial` / `proceed_testing_with_caveat` **不自动 FAIL**。

| 子类 | 条数 | policy_action | closure_action |
|------|------|---------------|----------------|
| executive empty_but_valid | 9 | **accept_caveat** | close_as_accepted_source_caveat |
| share_capital empty_but_valid | 10 | **accept_caveat** | close_as_accepted_source_caveat |
| top_shareholders empty_but_valid | 16 | **accept_caveat** | close_as_accepted_source_caveat |
| top_float empty_but_valid | 19 | **accept_caveat** | close_as_accepted_source_caveat |

### needs_manual_review 评估

经逐条核对 `flag_detail` 与 `source_quality.csv` 聚合：

- **needs_manual_review：0**
- **accept_caveat：54**

**理由：** 全部为 HTTP 200 + 业务空表/空数组，与 scale smoke 阶段 `empty_but_valid` 政策一致；无 blocked/http_error；无与 P0 重叠的 mapper 异常。

---

## 6. Closure Decision Rules

### P0 — missing_normalized_core

| 条件 | closure_action |
|------|----------------|
| 确认 nullable derived、basic 源端 null | **close_as_accepted_nullable_gap** |
| 确认 mapper bug（raw 有值但 normalized 空） | **open_mapper_issue** |
| 确认 raw 缺失/损坏需重 harvest | **open_data_quality_issue** |

### P1 — dividend_parse needs_review

| 条件 | closure_action |
|------|----------------|
| 长尾不可稳定解析、单条/零散 | **close_as_manual_review_queue** |
| 重复 pattern 明显（≥10 或 ≥50%） | **open_parser_patch_issue** |
| 本轮 2 条空格含税变体 | **open_parser_patch_issue**（延后实施） |

### P2 — source_caveat

| 条件 | closure_action |
|------|----------------|
| empty_but_valid 符合政策 | **close_as_accepted_source_caveat** |
| 不符合政策（应 endpoint_found 却有数据缺失） | **open_source_quality_issue** |

---

## 7. Acceptance Criteria

QA queue 可视为**关闭**（非 C-class 整体完成）当且仅当：

| # | 条件 | 本计划状态 |
|---|------|-----------|
| 1 | **72** flags 全部分配 `closure_action` | **已规划**（CSV 72 rows） |
| 2 | P0 **6** 家均有判断 | **已完成** |
| 3 | P1 **12** 条均有 `review_action` | **已完成** |
| 4 | P2 **54** 条均有 `policy_action` | **已完成** |
| 5 | 不要求全部修复 | 允许 accepted caveat / manual queue |
| 6 | 不写 verified | **遵守** |

**closure_action 分布（规划）：**

| closure_action | 数量 |
|----------------|------|
| close_as_accepted_nullable_gap | 6 |
| close_as_manual_review_queue | 10 |
| open_parser_patch_issue | 2 |
| close_as_accepted_source_caveat | 54 |

---

## 8. Next Step After This Plan

**只允许下一步：**

> **执行 QA queue closure classification** — 将本计划 CSV 落账为 `qa_flags_closure_log`（或等价 artifact），更新 flag `current_status` → `closed` / `deferred`。

**禁止跳转：**

- company_snapshot 设计与实现
- registry backfill 决策与执行
- DB / MinIO / RAG
- harvest 重跑 / parser patch 实施

---

## 输入

- `outputs/validation/cninfo_c_class_full_harvest_qa_flags.csv`
- `outputs/validation/cninfo_c_class_full_harvest_qa_flag_triage.csv`
- `outputs/validation/cninfo_c_class_full_harvest_qa_review.md`
- `outputs/validation/cninfo_c_class_full_harvest_qa_flag_triage.md`
- `outputs/harvest/cninfo_c_class/quality/source_quality.csv`
- `outputs/harvest/cninfo_c_class/quality/company_harvest_status.csv`
- `outputs/harvest/cninfo_c_class/quality/field_fill_rate.csv`
- `outputs/harvest/cninfo_c_class/raw/basic_profile/`（P0 离线核对）
- `outputs/harvest/cninfo_c_class/normalized/dividend_history/`（P1 离线核对）

## 输出

- 本计划：`plans/cninfo_c_class_qa_review_queue_closure_plan.md`
- 分类 CSV：`outputs/validation/cninfo_c_class_qa_review_queue_closure_plan.csv`

## 红线确认

- 未请求 CNINFO · 未重跑 live harvest
- 未修改 raw / normalized 数据
- 未 YAML backfill · 未入库 / MinIO / RAG
- 未写 verified · 未升级 testing_stable_sample
