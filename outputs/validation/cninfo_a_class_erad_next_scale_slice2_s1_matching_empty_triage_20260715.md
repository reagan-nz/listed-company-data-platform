# A-class Slice2 S1 — Matching-Empty / Listing-Gap Triage（A-R16-02）

_生成时间：2026-07-15_  
_性质：离线诊断 + 能力门禁 · **CNINFO = 0** · **无 live** · **无 PDF** · **不是 verified** · **不是 production_ready_  

---

## 1. Task

| 项 | 值 |
|----|-----|
| task_id | **A-R16-02** |
| track | A |
| executor | a-class-executor |
| prior | A-R16-01（orgId fallback hook + isolated retry；org_id present 但 records=0） |
| CNINFO | **0** |
| closed S1 live root mutate | **no** |

## 2. Wall clock

| 项 | 值 |
|----|-----|
| wall_start | 2026-07-15 16:08:40 +0800 |
| wall_end | 2026-07-15 16:12:40 +0800 |
| duration | ~4m |

## 3. Question answered

A-R16-01 已证明三案 **orgId 正确解析** 后 `hisAnnouncement` 仍 `records=0; last_err=ok`。  
本任务判定：是 **query 窗 / keyword / title matching** 缺陷，还是 **上市日相对 expected_period 不可达（listing_gap）**？

## 4. Evidence（离线 · C-class basic_profile）

| case_id | code | name | expected_period | report_type | query seDate（runner） | listing_date | listing_vs_period |
|---------|------|------|-----------------|-------------|------------------------|--------------|-------------------|
| AD2E578 | 688605 | 先锋精科 | 2024-06-30 | semi_annual | 2024-01-01 ~ 2024-09-30 | **2024-12-12** | listing **after** period |
| AD2E590 | 688688 | 蚂蚁集团 | 2024-09-30 | quarterly_q3 | 2024-07-01 ~ 2024-11-30 | **null（F006D）** | unlisted / no IPO complete |
| AD2E598 | 688758 | 赛分科技 | 2024-06-30 | semi_annual | 2024-01-01 ~ 2024-09-30 | **2025-01-10** | listing **after** period |

源路径：`outputs/harvest/cninfo_c_class/normalized/company_basic_profile/{code}.json`

补充：
- AD2E590：C-class 侧 share_capital / dividend / top shareholders 亦多为 empty_but_valid；与「未正式上市」一致。
- 不改 universe 名称；identity caveat 仍为 offline_identity_consistent（A-R14）。

## 5. Failure-class refinement

```text
prior_a_r16_01   = org_id_resolved_but_periodic_matching_empty
refined_class    = listing_gap_true_not_found   # AD2E578 / AD2E598
                 | true_not_found_likely_unlisted  # AD2E590
matching_suspect = no   # records=0 发生在 API 返回层，非 v2 title filter
keyword_suspect  = no
se_date_suspect  = no   # 窗本身合理；问题是报告期早于上市日
retry_recommended = no
```

结论：**不是 matching bug**。正确 orgId + 现有 keyword/seDate 路径下空公告符合「报告期早于上市 / 未上市」预期。

## 6. Slice2 S1 breadth（capability signal）

对封闭 slice2 S1 live 报告 50 案做同样离线对照（只读）：

| 指标 | 值 |
|------|-----|
| live cases | 50 |
| listing_on_or_before_period | **47** |
| listing_after_period | **2**（AD2E578 / AD2E598） |
| listing_date_null | **1**（AD2E590） |
| not_found 与 listing 异常重合 | **3/3（100%）** |

→ 全市场扩展时，**expected_period 必须相对 listing_date 门禁**，否则会系统性制造 true_not_found。

## 7. Capability gain

| 项 | 路径 / 行为 |
|----|-------------|
| offline gate | `lab/cninfo_a_class_listing_period_gate.py` |
| API | `assess_listing_vs_expected_period(code, expected_period)` |
| 行为 | profile 缺失 / 日期空 / 期前上市显式分类；`blocks_periodic_retrieval`；CNINFO 恒 0；禁止伪造上市日 |
| tests | `lab/test_cninfo_a_class_listing_period_gate.py` |

```text
capability_gain = CAPABILITY_ADVANCED
ready_for_universe_filter_wire = yes   # 另开任务接入 runner/universe 构建；本包未改 live path
```

## 8. Tests

```text
python lab/test_cninfo_a_class_listing_period_gate.py → 7/7 OK
```

## 9. Explicit non-actions

- **无** CNINFO live / 无 isolated retry（retry ROI=0）
- **无** mutate 封闭 slice2 S1 live raw_metadata / live report
- **无** 改写 unresolved_caveat_ledger 生产行（本包另出 triage ledger）
- **无** PDF / DB / MinIO / RAG
- **无** commit / push
- **不**宣称 bare PASS / verified / production_ready

## 10. Artifacts

| 文件 | 用途 |
|------|------|
| 本报告 | 根因与门禁裁决 |
| `cninfo_a_class_erad_next_scale_slice2_s1_matching_empty_triage_ledger_20260715.csv` | 三案 triage |
| `cninfo_a_class_erad_next_scale_slice2_s1_listing_gap_breadth_20260715.csv` | slice2 50 案 breadth |
| `lab/cninfo_a_class_listing_period_gate.py` | 可复用离线门禁 |
| `lab/test_cninfo_a_class_listing_period_gate.py` | 单测 |

## 11. Allow-list for commit（A-R16-02 only）

1. `lab/cninfo_a_class_listing_period_gate.py`
2. `lab/test_cninfo_a_class_listing_period_gate.py`
3. `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_matching_empty_triage_ledger_20260715.csv`
4. `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_listing_gap_breadth_20260715.csv`
5. `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_matching_empty_triage_20260715.md`（本文件）

**Exclude：** 封闭 S1 live 根；C/D/其他 track；A-R16-01 已提交文件无必要再改。

## 12. Gates / next

```text
a_class_erad_next_scale_slice2_s1_matching_empty_triage_gate = PASS_OFFLINE
disposition_recommendation = accept_unresolved_with_listing_gap_caveat  # 三案均 defer_no_retry
ready_for_commit = yes   # 证据 + gate + tests；不含 push
next_hint = wire listing_period_gate into next-scale universe builder
            （expected_period >= listing_date；exclude listing_date null）
            · 或 Controller 关闭三案 caveat 升级后推进 slice2 下一闸
```
