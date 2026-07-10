# CNINFO A 类 Phase 2 Network Recovery Retry v2 规划

_生成时间：2026-07-09_

> **性质：** 离线规划 only · **无 CNINFO** · **无 live** · **无 retry 执行** · **不是 verified** · **不是 production_ready**

---

## 1. Objective

在网络恢复后，对 Phase 2 中 **8 个 unresolved network failure** case 执行 **isolated retry v2**，验证 metadata 可检索性，不改变 schema / matching / universe。

**前置 closure gate：** `a_class_phase2_metadata_closure_gate = PASS_WITH_CAVEAT_NETWORK_UNRESOLVED`

**本规划 gate（规划完成后）：** `a_class_phase2_network_recovery_retry_v2_planning_gate = READY_FOR_APPROVAL`

---

## 2. Why Retry v2 Is Needed

| 轮次 | 结果 | 问题 |
|------|------|------|
| Phase 2 original live | 12/20 success · 8 failed | 6 orgId network_error · 2 proxy 503 |
| Retry v1 (isolated) | 0/8 success | 全部 orgId network_error · CNINFO requests=0（网络 outage） |

Retry v1 报告保留于 `cninfo_a_class_phase2_metadata_retry/`，记录的是 **network outage 窗口**，不能作为最终 metadata 结论。

Retry v2 需要：

- **新隔离输出根** `cninfo_a_class_phase2_metadata_retry_v2/`
- **新批准 flag** `--approve-a-class-phase2-network-recovery-retry-v2`
- **与 v1 / original 报告并存**，便于审计 network outage vs recovery

---

## 3. Why Only 8 Unresolved Cases

| 类别 | case_ids | 处理 |
|------|----------|------|
| accepted original success | A2M001–A2M004, A2M006–A2M009, A2M014–A2M017（**12**） | **不重跑** |
| unresolved network failure | A2M005, A2M010–A2M013, A2M018–A2M020（**8**） | retry v2 only |

Merged result 已确认：

- wrong_report_type = **0** on retrievable cases
- period_mismatch = **0** on success cases
- 8 failed cases 归因 **orgid_resolution_network_error**，非 schema / matching defect

---

## 4. Why 12 Successful Cases Must Not Be Rerun

- 12 case 已 `accepted_original_success`（title pass · period pass · wrong_report_type=0）
- 重跑将产生重复 CNINFO 调用与报告污染
- Runner 内置 `SUCCESSFUL_CASE_IDS` 拒绝 successful case 进入 retry universe
- Closure 已接受 12/20 baseline；retry v2 仅补全剩余 8/20

---

## 5. Why No Schema or Matching Change

| 项 | 状态 |
|----|------|
| schema_change_needed | **no** |
| matching_logic_change_needed | **no** |
| universe_replacement_needed | **no** |
| matching version | v2（与 Phase 1 / Phase 2 original 一致） |
| phase1_freeze_v1 | unchanged |

失败归因均为基础设施 / 网络，非字段或匹配逻辑缺陷。

---

## 6. Output Isolation Plan

| 输出根 | 角色 | retry v2 写入 |
|--------|------|---------------|
| `cninfo_a_class_phase2_metadata_expansion/` | original Phase 2 live | **禁止** |
| `cninfo_a_class_phase2_metadata_retry/` | retry v1 (network outage) | **禁止** |
| `cninfo_a_class_phase2_metadata_retry_v2/` | retry v2 (network recovery) | **允许** |
| Phase 1 tiny live | baseline | **禁止** |

预期产物：

```text
outputs/validation/cninfo_a_class_phase2_metadata_retry_v2/
  reports/
    a_class_phase2_network_recovery_retry_v2_dryrun_report.csv
    a_class_phase2_network_recovery_retry_v2_dryrun_summary.md
    a_class_phase2_network_recovery_retry_v2_report.csv
    a_class_phase2_network_recovery_retry_v2_summary.md
    a_class_phase2_network_recovery_retry_v2_quality_report.csv
  raw_metadata/
    A2M005_retry_v2.json
    ...
```

---

## 7. Approval Requirement

| 项 | 要求 |
|----|------|
| 人工批准 | **必须** |
| approval flag | `--approve-a-class-phase2-network-recovery-retry-v2` |
| 当前状态 | **NOT_APPROVED** |
| dry-run | 无需批准 · CNINFO=0 |
| live | 须显式批准 + 网络恢复确认 |

批准检查清单：[cninfo_a_class_phase2_network_recovery_retry_v2_approval_checklist.md](../outputs/validation/cninfo_a_class_phase2_network_recovery_retry_v2_approval_checklist.md)

---

## 8. Expected Result Interpretation

| retry v2 结果 | 解释 | 后续 |
|---------------|------|------|
| ≥6/8 found + title/period pass + wrong_report_type=0 | network recovery 有效 · metadata 可补全 | merge closure update review |
| 部分 success + 部分 network_error | 混合基础设施问题 | triage + 可选 retry v3 |
| 0/8 network_error | 网络仍未恢复或 CNINFO 持续不可用 | hold · 不扩展 50 家 |
| wrong_report_type > 0 | **非预期** · 需 matching review | 暂停 expansion |

**不自动升级：** verified · production_ready · testing_stable_sample

---

## 9. Red Lines

- No CNINFO（本规划回合）
- No live / no retry 执行（本规划回合）
- No successful 12 rerun
- No 50-company expansion
- No PDF download / parse
- No OCR / extraction
- No DB / MinIO / RAG
- No verified / production_ready / testing_stable_sample

---

## 10. Next Step After Planning

1. Runner extension（见 [runner extension plan](cninfo_a_class_phase2_network_recovery_retry_v2_runner_extension_plan.md)）
2. Dry-run（CNINFO=0 · 8/8 planned_ok）
3. 人工批准 checklist
4. 网络恢复后 live retry v2（**仅 8 case**）
5. Merge closure update（**不修改** original / v1 报告）

**禁止：** 在 8 unresolved 未解决或未正式接受为 permanent network caveat 前，启动 50-company expansion。

---

## Artifacts

| 项 | 路径 |
|----|------|
| universe | [cninfo_a_class_phase2_network_recovery_retry_v2_universe.csv](../outputs/validation/cninfo_a_class_phase2_network_recovery_retry_v2_universe.csv) |
| approval checklist | [cninfo_a_class_phase2_network_recovery_retry_v2_approval_checklist.md](../outputs/validation/cninfo_a_class_phase2_network_recovery_retry_v2_approval_checklist.md) |
| command draft | [cninfo_a_class_phase2_network_recovery_retry_v2_command_draft.md](cninfo_a_class_phase2_network_recovery_retry_v2_command_draft.md) |
| planning summary | [cninfo_a_class_phase2_network_recovery_retry_v2_planning_summary.md](../outputs/validation/cninfo_a_class_phase2_network_recovery_retry_v2_planning_summary.md) |
