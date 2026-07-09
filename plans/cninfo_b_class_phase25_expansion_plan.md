# CNINFO B 类 Phase 2.5 Expansion Plan

_生成时间：2026-07-09_

> **性质：** Phase 2（20 家）收口后的中等扩大样本规划；**离线 only** · **NOT APPROVED** · **不是 verified** · **不是 production_ready**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`（不变）

**Phase 2 commit：** `b4a6e6e`（已推送）

---

## 1. Phase 1 Recap

| 项 | 值 |
|----|-----|
| closure gate | `b_class_phase1_tiny_live_closure_gate = PASS_WITH_CAVEAT` |
| cases | **5** · resolved **5** · failed **0** |
| TLC002 | EP002 `network_error` → isolated retry recovered |
| endpoints | EP001 · EP002 · EP004 · EP005 |
| PDF / DB / MinIO / RAG | **0** |

---

## 2. Phase 2 Recap

| 项 | 值 |
|----|-----|
| execution gate | `b_class_phase2_expansion_execution_gate = PASS_WITH_CAVEAT` |
| closure gate | `b_class_phase2_expansion_closure_gate = PASS_WITH_CAVEAT` |
| cases | **20** · acceptable **20** · failed **0** |
| CNINFO requests | **40** |
| endpoint hits | EP001 **20** · EP002 **20** · EP004 **12** · EP005 **8** |
| URL lineage | pdf_url_present **20/20** · adjunct_url_present **20/20** |
| PDF download / parse | **0** |
| markets | SZSE主板 · SSE主板 · 创业板 · 科创板 |

Phase 2 Option A 证明 20 家批次可全量 `found/pass/discovered`；仍不足以支撑全市场失败率统计或长期批次稳定性结论。

---

## 3. Why Phase 2.5 Is Needed

1. **样本量翻倍：** 从 20 → 50，可初步观察 `needs_review` / transient network error 频率。
2. **板块与 bucket 补全：** Phase 2 已覆盖四板块，但 bucket 分布仍可扩展（更多 SSE/SZSE 一般公告分流、金融子类、制造/科技长尾）。
3. **无重叠 universe：** Phase 2.5 刻意避开 Phase 1/2 已测公司，扩大 **公司维度** 而非重复验证。
4. **为后续决策积累证据：** 50 家结果可 inform Option C（lineage integration）或 title matching hardening（Option D），**仍不进入 PDF 阶段**。
5. **不推荐 100：** Phase 2 虽 20/20 成功，但批次时长与 EP002 风险随规模上升；50 为推荐上限前一步。

---

## 4. Expansion Objective

在 **phase1_freeze_v1 schema 不变** 的前提下：

- 将 live metadata validation 扩大至 **50** 家（人工批准）
- 维持 metadata + pdf URL lineage only
- 使用 **独立输出根** `cninfo_b_class_phase25_expansion/`
- 约 **25** EP004 periodic · **25** EP005 general
- **不**标 verified · **不**宣称 production_ready

---

## 5. 50-Company Scope

| 项 | 值 |
|----|-----|
| sample size | **50**（Option B from Phase 2 plan） |
| case ID | B25E001–B25E050 |
| overlap Phase 1 | **0**（刻意避免） |
| overlap Phase 2 | **0**（刻意避免） |
| periodic_report | **25** |
| general_announcement | **25** |

**不推荐：** 100-company live expansion（本阶段）

---

## 6. Endpoint Strategy

沿用 phase1_freeze_v1 endpoint catalog：

| ID | Role | Phase 2.5 预期 |
|----|------|----------------|
| EP001 | hisAnnouncement/query | 全 **50** case 主检索 |
| EP002 | topSearch/orgId | 金融/大型样本约 **7–10** case |
| EP004 | periodic report metadata | **25** case |
| EP005 | general announcement metadata | **25** case |

**排除：** EP003 removed · EP006/EP007 deferred

---

## 7. Universe Selection Rules

- 活跃 A 股上市公司 only
- 非 ST / *ST · 非退市 · 非 BSE legacy
- 无 manual identity review
- **避免** Phase 1（TLC001–005）与 Phase 2（B2E001–020）公司代码重复
- metadata + URL lineage only；**无 PDF 下载/解析**
- bucket 覆盖见 [candidate universe design](../outputs/validation/cninfo_b_class_phase25_candidate_universe_design.csv)

---

## 8. Quality Policy

对齐 Phase 1/2 口径：

| 场景 | quality_status | lineage_status |
|------|----------------|----------------|
| 必填齐全 · 明确匹配 | `pass` | `discovered` |
| pdf_url 缺失 | `needs_review` | `needs_review` |
| unknown category | `caveat` | `discovered` |
| network_error | `needs_review` | `needs_review` |

**禁止：** verified · testing_stable_sample upgrade

---

## 9. Failure Handling

| 失败类型 | 处理 |
|----------|------|
| `network_error` | 停止当前 case；记录；triage 后可选 isolated retry |
| `http_429` | 全局停止 |
| `empty_response` | `needs_review`；继续下一 case |
| `org_id_missing` | EP002 单次；失败 `needs_review` |

批次结束后产出 failure summary；**不** inline retry storm。

---

## 10. Retry Policy

1. 主批次 **不**自动 inline retry
2. isolated retry 仅对 `transient_network_error` 经 **人工批准** 后执行
3. retry 输出 **禁止**覆盖 Phase 2 / Phase 2.5 主批次 baseline
4. **禁止**与 C-class live harvest 并发

---

## 11. Output Isolation

**Phase 2.5 专用输出根：**

```text
outputs/validation/cninfo_b_class_phase25_expansion/
```

**禁止写入：**

- `cninfo_b_class_tiny_live_validation/`（Phase 1）
- `cninfo_b_class_tlc002_retry/`
- `cninfo_b_class_phase2_expansion/`（Phase 2 baseline）
- `outputs/harvest/cninfo_c_class/`

---

## 12. Approval Requirements

| # | 要求 |
|---|------|
| 1 | Phase 2 closure gate = `PASS_WITH_CAVEAT` 已审阅 |
| 2 | 50-company universe draft 已审阅 |
| 3 | endpoint mix（25/25）已确认 |
| 4 | [approval checklist](../outputs/validation/cninfo_b_class_phase25_expansion_approval_checklist.md) 全勾选 |
| 5 | runner 扩展 + `--approve-b-class-phase25-expansion`（未来回合） |
| 6 | 用户显式批准 live execution |

**当前 gate：**

```text
b_class_phase25_expansion_planning_gate = READY_FOR_APPROVAL
```

---

## 13. Risks

| 风险 | 级别 | 缓解 |
|------|------|------|
| EP002 transient network_error 复现 | medium | rate limit · isolated retry 纪律 |
| 批次时长 ~100+ CNINFO requests | medium | resume · 禁止并发 C-class harvest |
| general 公告选取非代表性标题 | low–medium | Option D title matching 可并行 |
| 50 家仍非全市场代表 | low | 不宣称 production_ready |
| 与 Phase 2 runner 参数化不足 | low | 未来回合扩展 runner 或新建 Phase 2.5 runner |

---

## 14. Related Artifacts

| 文档 | 路径 |
|------|------|
| candidate design | [cninfo_b_class_phase25_candidate_universe_design.csv](../outputs/validation/cninfo_b_class_phase25_candidate_universe_design.csv) |
| universe draft | [cninfo_b_class_phase25_expansion_universe_draft.csv](../outputs/validation/cninfo_b_class_phase25_expansion_universe_draft.csv) |
| command draft | [cninfo_b_class_phase25_expansion_command_draft.md](cninfo_b_class_phase25_expansion_command_draft.md) |
| approval checklist | [cninfo_b_class_phase25_expansion_approval_checklist.md](../outputs/validation/cninfo_b_class_phase25_expansion_approval_checklist.md) |
| approval summary | [cninfo_b_class_phase25_expansion_approval_summary.md](../outputs/validation/cninfo_b_class_phase25_expansion_approval_summary.md) |
| Phase 2 closure | [cninfo_b_class_phase2_expansion_closure_review.md](cninfo_b_class_phase2_expansion_closure_review.md) |

---

## 15. Red Lines

- No CNINFO in this planning round
- No live · No retry · No PDF · No DB/MinIO/RAG
- No verified · No production_ready · No commit in this round
