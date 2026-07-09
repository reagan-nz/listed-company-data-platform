# CNINFO B 类 TLC002 Isolated Retry Plan

_生成时间：2026-07-09_

> **性质：** 单 case 隔离重试批准规划 only；**不执行 retry** · **NOT APPROVED**

**前置：** [TLC002 failure analysis](../outputs/validation/cninfo_b_class_tlc002_failure_analysis.md) · [decision summary](../outputs/validation/cninfo_b_class_tlc002_failure_decision_summary.md)

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

## 1. Retry Reason

| 项 | 内容 |
|----|------|
| case_id | **TLC002** |
| company | **300009** 安科生物 |
| original failure | EP002 `topSearch/query` · `network_error` |
| failure category | `transient_network_error_at_ep002_orgid_resolution` |
| triage decision | **retry_candidate**（A） |
| tiny live gate | `b_class_tiny_live_validation_execution_gate = PASS_WITH_CAVEAT`（**保持**） |

### 为何值得 isolated retry

1. **瞬态网络失败** — 同批次 TLC001/003/004/005 成功；300009 在首次 tiny live 曾 `found`。
2. **非身份/逻辑缺陷** — C-class 对 300009 有成功 harvest；错误类型为 `network_error` 而非 `empty_response`。
3. **EP001 跳过行为正确** — 原 run 未伪造 lineage；重试目标为补全 metadata，而非改 contract。

---

## 2. Schema Unchanged

| 项 | 状态 |
|----|------|
| phase1_freeze_v1 field catalog | **不变** |
| 15 required fields | **不变** |
| quality_status 规则 | **不变**（`needs_review` / `pass` / `caveat`；**无 verified**） |
| freeze fixtures / lint | **不修改** |

**结论：** retry 使用与 tiny live 相同的 freeze v1 映射；**无 schema freeze 变更**。

---

## 3. Endpoint Contract Unchanged

| Endpoint | 角色 | 变更 |
|----------|------|------|
| EP002 | orgId helper（topSearch/query） | **无** |
| EP001 | hisAnnouncement/query | **无** |
| EP005 | cninfo_general_announcement_pdf（TLC002 primary） | **无** |
| EP003 | removed | **仍禁止** |
| EP006/EP007 | deferred | **仍禁止** |

**结论：** 重试仅复跑 EP002→EP001 标准链；**endpoint contract 不变**。

---

## 4. Retry Scope

| 约束 | 值 |
|------|-----|
| companies | **1**（仅 TLC002 / 300009） |
| universe 扩展 | **否** — 不新增 TLC006+ |
| sample size | **不扩大** — 仍为 tiny live 5-case universe 的子集重试 |
| PDF download | **禁止** |
| PDF parse | **禁止** |
| DB / MinIO / RAG | **禁止** |
| verified | **禁止** |

---

## 5. Output Isolation（不复用原 live 输出）

**专用根（强制）：**

```text
outputs/validation/cninfo_b_class_tlc002_retry/
├── raw_metadata/
├── quality/
└── reports/
```

| 规则 | 说明 |
|------|------|
| 禁止写入 | `outputs/validation/cninfo_b_class_tiny_live_validation/`（原 tiny live 产物只读保留） |
| 禁止写入 | `outputs/harvest/` · C-class Phase 3 路径 |
| 报告 | `reports/tlc002_retry_report.csv` · `reports/tlc002_retry_summary.md` |

---

## 6. Approval Workflow

1. 人工 review [retry checklist](../outputs/validation/cninfo_b_class_tlc002_retry_checklist.md)
2. 人工 review [command draft](cninfo_b_class_tlc002_retry_command_draft.md)
3. 用户显式批准 `--approve-b-class-tlc002-retry`
4. 未来回合执行 isolated retry（**本 plan 不执行**）
5. 产出写入 `cninfo_b_class_tlc002_retry/` only
6. **仍不写 verified** · execution gate **不升级为 PASS**

---

## 7. Gate

```text
b_class_tlc002_isolated_retry_gate = READY_FOR_APPROVAL
```

**NOT EXECUTED** — retry **未运行**。

---

## 8. Red Lines

- No CNINFO in this planning round
- No retry execution in this planning round
- No schema / endpoint catalog / freeze artifact modification
- No PDF · No DB · No MinIO · No RAG · No verified
