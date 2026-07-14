# CNINFO B 类 Empty-Response Edge Taxonomy — Fuller Slice2

_生成时间：2026-07-14 · offline taxonomy + ledger · **CNINFO = 0** · **无 live** · **无 commit** · **无 push**_

> **性质：** reusable edge taxonomy for disclosure/event quality · **NOT verified** · **NOT production_ready**

---

## 1. Scope & Sources

| 项 | 值 |
|----|-----|
| task_id | **B-GEN-20260714-03** |
| cohort | `fuller_next_slice2`（BD2E501–800 live，已发生） |
| edge universe | **8** `empty_response` · `acceptable_edge` |
| excluded | **BD2E624**（`network_error` · deferred）— 见 [BD2E624 offline triage](cninfo_b_class_bd2e624_offline_triage_20260714.md)（cite only · 本包不重做） |
| merge closure | [slice2 merge closure summary](cninfo_b_class_erad_fuller_next_slice2_merge_closure_summary.md) — **299/300 acceptable** · gate `PASS_WITH_CAVEAT` |
| ledger | [empty_response edge ledger](cninfo_b_class_empty_response_edge_ledger_20260714.csv)（**8 rows**） |
| classification seed | [edge-case classification](cninfo_b_class_erad_fuller_next_slice2_edge_case_classification.csv) rows 2–9 |

**边界：** 本包仅分类 slice2 八例 `empty_response`；不升级 gate · 不 force-resolve · 不触发 live。

---

## 2. Taxonomy Definition

### 2.1 根类：`ER-VAL`（Valid Empty Corpus）

| 字段 | 定义 |
|------|------|
| retrieval_status | `empty_response` |
| 语义 | EP001 orgId 解析成功；目标端点（EP004 或 EP005）HTTP 成功但公告列表为空（`no announcements in response`） |
| 与 failed 区分 | **非** `network_error` · **非** EP002 orgId 失败 · **非** `universe_validation_failed` |
| 与 not_found 区分 | 无返回记录可匹配标题；不是「有记录但标题不匹配」 |
| acceptability | `empty_but_valid`（runner `classify_case_acceptability`）→ merge closure `accept_with_caveat` |
| closure 角色 | 计入 acceptable（291 found + 8 empty = **299**）· **非 failed blocker** |

**Rationale（与 slice1 对齐）：** `empty_response` 表示 CNINFO 返回空列表，属有效检索结果信号，不代表采集管线故障。见 [slice1 merge closure decision](cninfo_b_class_erad_next_scale_slice1_merge_closure_decision.md) §Edge-Case Disposition。

### 2.2 子类标签

| taxonomy_tag | 条件 | count | endpoint_used | announcement_type |
|--------------|------|-------|---------------|-------------------|
| **ER-VAL-EP004-PERIODIC** | EP001 成功 + EP004 空列表 + `periodic_report` | **6** | EP004 | periodic_report |
| **ER-VAL-EP005-GENERAL** | EP001 成功 + EP005 空列表 + `general_announcement` | **2** | EP005 | general_announcement |

### 2.3 市场分布（辅助维度 · 非独立 tag）

| 市场信号 | case_ids | count |
|----------|----------|-------|
| SZSE主板 | BD2E537 | 1 |
| SSE主板 | BD2E751 | 1 |
| ChiNext / market_other（universe `market_other`） | BD2E725, BD2E738, BD2E739, BD2E743, BD2E745, BD2E746 | 6 |

### 2.4 统一质量/谱系信号

| 字段 | 八例共性 |
|------|----------|
| quality_status | `needs_review` |
| lineage_status | `needs_review` |
| announcement_id / title / date | 空 |
| pdf_url_present / pdf_downloaded | 0 |
| retained_evidence_mode | `fresh_metadata` |
| notes | `no announcements in response` |

---

## 3. Case Ledger（摘要）

| case_id | company_code | company_name | session | taxonomy_tag | disposition |
|---------|--------------|--------------|---------|--------------|-------------|
| BD2E537 | 002710 | 慈铭体检 | Session 1 | ER-VAL-EP004-PERIODIC | accept_with_caveat |
| BD2E725 | 301449 | 天溯计量 | Session 2 | ER-VAL-EP004-PERIODIC | accept_with_caveat |
| BD2E738 | 301583 | 托伦斯 | Session 2 | ER-VAL-EP005-GENERAL | accept_with_caveat |
| BD2E739 | 301584 | 建发致新 | Session 2 | ER-VAL-EP004-PERIODIC | accept_with_caveat |
| BD2E743 | 301638 | 南网数字 | Session 2 | ER-VAL-EP004-PERIODIC | accept_with_caveat |
| BD2E745 | 301669 | 高特电子 | Session 2 | ER-VAL-EP004-PERIODIC | accept_with_caveat |
| BD2E746 | 301687 | 新广益 | Session 2 | ER-VAL-EP005-GENERAL | accept_with_caveat |
| BD2E751 | 601206 | 海尔施 | Session 2 | ER-VAL-EP004-PERIODIC | accept_with_caveat |

完整机器可读行见 [ledger CSV](cninfo_b_class_empty_response_edge_ledger_20260714.csv)。

**证据路径：**
- combined report：`outputs/validation/cninfo_b_class_erad_fuller_next_slice2/reports/b_class_erad_fuller_next_slice2_report.csv`
- quality：`outputs/validation/cninfo_b_class_erad_fuller_next_slice2/reports/b_class_erad_fuller_next_slice2_session{1,2}_quality_report.csv`
- live log：`outputs/validation/cninfo_b_class_erad_fuller_next_slice2_session{1,2}_live.log`

---

## 4. Disposition Rules（offline）

| 规则 | 八例默认 |
|------|----------|
| classification | `acceptable_edge` |
| disposition | `accept_with_caveat` |
| live_required | **no** |
| retry_again | **no**（merge closure 已收口） |
| offline_next_action | `retain_caveat;ledger_only;optional_broadened_window_plan_if_human_approves` |
| gate impact | 不阻塞 `PASS_WITH_CAVEAT` · 阻止 bare PASS（与 BD2E624 共同构成 caveat） |

### 4.1 Deferred Blocker（cite only）

| case_id | 状态 | 引用 |
|---------|------|------|
| BD2E624 | `unresolved_failed` · EP002 orgId network_error · **deferred** | [bd2e624 offline triage](cninfo_b_class_bd2e624_offline_triage_20260714.md) |

BD2E624 **不在** 本 ledger 八行内；taxonomy 上属于 **EP002-NET** 族，与 `ER-VAL` 族互斥。

---

## 5. Cross-Slice Pattern Signal

| slice | empty_response count | taxonomy 对齐 |
|-------|---------------------|---------------|
| next-scale slice1 | **8** | 同 `ER-VAL-EP004-PERIODIC` / `ER-VAL-EP005-GENERAL` 模式 · 见 [slice1 edge triage ledger](cninfo_b_class_erad_next_scale_slice1_edge_case_triage_ledger.csv) |
| fuller slice2 | **8** | 本包 |

累计 **16** 例 `empty_response` acceptable_edge（两 slice 合计），提示空语料边缘在 B 类 Era D 扩规模中可复现，宜作为 mission event quality 的长期 caveat 类，而非单 slice 噪声。

---

## 6. Parser / Retrieval Prep Notes（IF human later approves retrieval work）

> **本段不构成 live 批准。** post-integration **HOLD** 下一切 CNINFO 调用仍阻断。以下仅为日后 human 显式批准「空响应边缘复询 / 扩窗检索」时的**离线准备**清单。

### 6.1 离线可先做的准备（无 CNINFO）

| 步骤 | 动作 | 说明 |
|------|------|------|
| 1 | 从本 ledger 导出 **8-case** isolated universe CSV | 参照 BD2E624 / TLC002 单 case universe 格式；cohort 标 `fuller_next_slice2_empty_response_edge` |
| 2 | 撰写 isolated requery plan + approval checklist + command draft | 参照 `plans/cninfo_b_class_tlc002_isolated_retry_plan.md` 模式；**不得**与 BD2E624 retry 混批 |
| 3 | 指定隔离 output root | 例：`outputs/validation/cninfo_b_class_erad_fuller_next_slice2_empty_response_requery/` · 不得覆写 slice2 主 report / merge closure |
| 4 | 按 taxonomy_tag 分组复询策略草案 | EP004 组（6）与 EP005 组（2）分开估算 request cap（≈2 CNINFO/case） |
| 5 | Broadened-window / alternate filter 参数表（offline） | 记录当前 runner 默认日期窗与 category filter；草案扩窗档位供 human 选用 |
| 6 | raw_metadata 对账模板 | 列：case_id · endpoint · response_record_count · orgId_resolved · empty_list_confirmed · 与 live notes 一致性 |

### 6.2 Parser 侧关注点

| 关注点 | 说明 |
|--------|------|
| empty vs not_found | `empty_response` = 零条记录；`not_found` = 有记录但无匹配标题（slice1 BD2E201 先例）· parser 不得合并分类 |
| empty vs network_error | EP002 失败（BD2E624）不得归入 `ER-VAL`；复询 parser 须保留 `root_cause_family` |
| quality / lineage | 八例均为 `needs_review`；若复询仍空，保持 `accept_with_caveat`  unless human 另定政策 |
| report 字段缺口 | live report `cninfo_request_count` 当前为 0（found 与 empty 均为 0）· 复询包应修复或旁路记录实际 request 计数 |
| disclosure vs capture | 空响应仅证明 metadata 层无匹配公告 · **不**推断 disclosure text 缺失 · 禁止 silent 升级为 structured capture |

### 6.3 Live 形状指针（DO NOT RUN）

```bash
# 形状示意 only — 须 separate approval · 须 isolated universe · 须 isolated output-root
python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --erad-b-fuller-slice2 \
  --approve-b-class-erad-fuller-slice2 \
  --universe-csv <isolated_empty_response_8case_universe.csv> \
  --output-root outputs/validation/cninfo_b_class_erad_fuller_next_slice2_empty_response_requery/ \
  --live \
  --case-range BD2E537:BD2E751
```

**红线：** 无 PDF / DB / MinIO / RAG · 不升级 verified / production_ready · 不与 BD2E624 同批 · HOLD 解除前禁止执行。

### 6.4 收口指针

- 复询后仍 `empty_response` → 保留 `ER-VAL-*` tag · 更新 ledger notes · gate 仍 `PASS_WITH_CAVEAT`
- 复询 `found` → separate merge closure 行 · 不得 retroactive 改写 slice2 主 merge closure 299/300 叙事
- BD2E624 成功/失败 → 走独立 retry 轨 · 见 [bd2e624 triage](cninfo_b_class_bd2e624_offline_triage_20260714.md) §4

---

## 7. Gate & Labels（本包）

```text
b_class_empty_response_edge_taxonomy_gate = PASS_OFFLINE
taxonomy_family = ER-VAL
ledger_rows = 8
deferred_blocker_cited = BD2E624
cninfo_calls_this_package = 0
live_calls_this_package = 0
```

**NOT verified** · **NOT production_ready** · **NOT approved for live** · **NOT committed** · **NOT pushed**

---

## 8. Progress Impact（一段）

本包将 fuller slice2 八例 `empty_response` 从 merge closure 叙事中提取为可复用 **ER-VAL** 边缘分类（`ER-VAL-EP004-PERIODIC` ×6 · `ER-VAL-EP005-GENERAL` ×2），并登记于独立 ledger，补齐 controller gap **GAP-B-EDGE-TAX** 所缺的 mission 级边缘工件。八例均已计入 **299/300 acceptable**，默认 **无需 live**；与 slice1 八例空响应合计形成跨 slice 模式信号。BD2E624（EP002 network_error）保持 deferred，由既有 triage 包处理，与本 taxonomy 族互斥。在 post-integration HOLD 下，parser/retrieval 段仅提供日后 isolated requery 的离线准备指针，不触发任何 CNINFO 调用。
