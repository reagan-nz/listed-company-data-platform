# CNINFO A 类 Phase 2 CNINFO Reachability Precheck 规划

_生成时间：2026-07-09_

> **性质：** 离线规划 only · **无 CNINFO** · **无 live** · **无 precheck 执行** · **不是 verified** · **不是 production_ready**

---

## 1. Objective

在任意 **retry_v3** live 批准之前，准备一套 **轻量级 CNINFO/orgId 可达性 precheck** 规划包，用于验证基础设施是否恢复，避免 v1/v2 类 **零 CNINFO 空跑**。

**前置 closure gate：** `a_class_phase2_retry_v2_closure_gate = PASS_WITH_CAVEAT_NETWORK_UNRESOLVED`

**本规划 gate：** `a_class_phase2_cninfo_reachability_precheck_planning_gate = READY_FOR_APPROVAL`

---

## 2. Why Precheck Is Needed Before retry_v3

| 轮次 | 结果 | CNINFO requests |
|------|------|-----------------|
| Phase 2 original | 12/20 success · 8 failed | 28（部分 case 到达 query） |
| Retry v1 | 0/8 acceptable | **0**（orgId network_error） |
| Retry v2 | 0/8 acceptable | **0**（orgId network_error） |

v1 与 v2 均在 **orgId resolution** 阶段失败，未计入有效 CNINFO metadata 请求。直接批准 retry_v3 将再次消耗 runner 时间与审计成本，且无法区分「网络仍不可用」与「metadata 仍不可检索」。

Precheck 目的：

- 在 **最小请求预算** 内探测 CNINFO topSearch / orgId 路径是否可达
- 为 retry_v3 人工批准提供 **基础设施 go/no-go** 信号
- **不** 执行 metadata retry · **不** 执行 report matching · **不** 下载 PDF

---

## 3. How Original / retry_v1 / retry_v2 Failed

| case 组 | original failure stage | v1 / v2 failure stage |
|---------|------------------------|------------------------|
| network_error（6 case） | orgId_resolution | orgId_resolution · CNINFO **0** |
| not_found / proxy 503（2 case：A2M010 · A2M018） | announcement_query（proxy 503） | orgId_resolution · CNINFO **0** |

**共同结论：** 基础设施 / orgId 网络不可达，**非** schema defect · **非** matching logic defect。

---

## 4. Why This Is Infrastructure-Focused

| 证据 | 含义 |
|------|------|
| wrong_report_type = **0** | 无 report-type 误匹配 |
| period_mismatch = **0** | 无 period 误匹配 |
| schema_impact = **none** | 不改 schema |
| matching_logic_impact = **none** | 不改 matching |
| retry_v2 CNINFO = **0** | 失败发生在 counted request 之前 |

Precheck 仅验证 **CNINFO endpoint + orgId resolution 可达性**，不重新裁定 metadata 质量。

---

## 5. Target Endpoint / orgId Resolution Checks

| 检查项 | 说明 |
|--------|------|
| `topsearch_reachability` | CNINFO topSearch 接口 HTTP 可达（可选 1 次全局 probe） |
| `orgid_resolution_reachability` | 对候选 company_code 执行 orgId 解析，记录 HTTP 状态与 orgId 是否返回 |

**不接受：** announcement query · title/period matching · PDF URL 获取

**planned_check_type（候选 CSV）：** `orgid_resolution_reachability`

---

## 6. Expected Request Cap

| 项 | 值 |
|----|-----|
| precheck 候选数 | **3**（自 unresolved 8 中选取） |
| 未来 live precheck 请求上限 | **≤ 6** |
| 典型预算 | 1 次 topSearch probe + 每候选 1–2 次 orgId 尝试 |

Runner 须在 live 模式 **硬拒绝** 超过 cap 的执行计划。

---

## 7. Approval Requirements

| 项 | 要求 |
|----|------|
| 人工批准 | **必须** · `approved_for_live = false`（当前） |
| 批准 flag | `--approve-a-class-phase2-cninfo-reachability-precheck` |
| 前置确认 | retry_v2 closure 已审阅 · unresolved 8 已确认 |
| 候选范围 | 仅 unresolved 8 子集 · **不含** successful 12 |
| 输出根 | `outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck/` |

**当前状态：NOT_APPROVED**

---

## 8. Output Isolation

| 输出根 | precheck 写入 | 说明 |
|--------|---------------|------|
| `cninfo_a_class_phase2_metadata_expansion/` | **禁止** | original Phase 2 |
| `cninfo_a_class_phase2_metadata_retry/` | **禁止** | retry v1 |
| `cninfo_a_class_phase2_metadata_retry_v2/` | **禁止** | retry v2 |
| `cninfo_a_class_phase2_cninfo_reachability_precheck/` | **允许** | 本 precheck 专用 |

不得修改 merged result v2 · unresolved ledger v2 · retry_v2 closure 产物。

---

## 9. Interpretation Rules

| precheck 结果 | 解读 |
|---------------|------|
| 全部候选 orgId 可达 | 基础设施 **可能** 恢复 · 可进入 retry_v3 **规划** 审批（仍非 PASS） |
| 部分候选可达 | **caveat** · 需人工判断是否按市场/板块分批 retry_v3 |
| 全部 orgId network_error | 基础设施 **仍未恢复** · **hold** retry_v3 · 考虑 Option C signoff |
| orgId 可达但 retry_v3 仍失败 | 升级为 case-level metadata 调查 · **仍非** schema/matching 变更依据 |

Precheck **通过** 不等于 metadata **accepted** · **不等于** verified · **不等于** production_ready。

---

## 10. Red Lines

- 无 metadata retry · 无 full report matching
- 无 PDF download / parse · 无 OCR / extraction
- 无 DB / MinIO / RAG
- 无 successful 12 rerun
- 无 50-company expansion
- 无 schema / matching logic change
- 无 verified / production_ready / testing_stable_sample

---

## 11. Next Step After Precheck

1. 审阅 precheck live 报告（**批准后**）
2. 若基础设施 go → 准备 **retry_v3 isolated package**（8 case only · 新输出根 · **NOT APPROVED**）
3. 若基础设施 no-go → hold 或 Option C permanent network caveat signoff
4. **不推荐** 50-company expansion

---

## Artifacts

| 项 | 路径 |
|----|------|
| candidates | [cninfo_a_class_phase2_cninfo_reachability_precheck_candidates.csv](../outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck_candidates.csv) |
| approval checklist | [cninfo_a_class_phase2_cninfo_reachability_precheck_approval_checklist.md](../outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck_approval_checklist.md) |
| command draft | [cninfo_a_class_phase2_cninfo_reachability_precheck_command_draft.md](cninfo_a_class_phase2_cninfo_reachability_precheck_command_draft.md) |
| runner design | [cninfo_a_class_phase2_cninfo_reachability_precheck_runner_design.md](cninfo_a_class_phase2_cninfo_reachability_precheck_runner_design.md) |
| planning summary | [cninfo_a_class_phase2_cninfo_reachability_precheck_planning_summary.md](../outputs/validation/cninfo_a_class_phase2_cninfo_reachability_precheck_planning_summary.md) |
