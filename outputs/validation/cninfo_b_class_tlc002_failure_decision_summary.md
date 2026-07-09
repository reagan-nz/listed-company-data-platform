# TLC002 Failure Decision Summary

_生成时间：2026-07-09_

> **性质：** 离线分诊决策包；**无 CNINFO** · **无自动重试**

---

## Decision

```text
decision = A (retry_candidate)
```

| 选项 | 含义 | 选定 |
|------|------|------|
| A | retry_candidate — 后续可安全重试，schema 不变 | **是** |
| B | schema_issue — freeze v1 受影响 | 否 |
| C | endpoint_issue — endpoint 处理须变更 | 否 |

---

## Rationale（简要）

- 失败归类为 **EP002 瞬态 `network_error`**，非 orgId 逻辑缺陷或 schema 缺口。
- 300009 在首次 tiny live 及 C-class harvest 语境下均可解析，孤立失败不支持 freeze 变更。
- EP001 在 orgId 失败后正确跳过；lineage 保持 `needs_review`，未误标 pass/verified。

---

## Actions

| 动作 | 状态 |
|------|------|
| 自动 live 重试 | **未执行** |
| raw_metadata 修改 | **未执行** |
| quality 修改 | **未执行** |
| schema freeze 修改 | **未执行** |
| verified 升级 | **未执行** |

### 待人工（未来回合）

- 批准 isolated TLC002 single-case retry（仍无 PDF）
- 或接受 `PASS_WITH_CAVEAT` 下 4/5 为 sufficient tiny sample

---

## Gate

```text
b_class_tlc002_failure_triage_gate = READY_FOR_REVIEW
```

---

## Parallel Safety

- C-class status: **`SNAPSHOT_GENERATED_QA_REVIEW`**
- CNINFO calls during triage: **0**
- PDF download / parse: **0**

---

## Related

- [cninfo_b_class_tlc002_failure_analysis.md](cninfo_b_class_tlc002_failure_analysis.md)
- [cninfo_b_class_tiny_live_validation_report.csv](cninfo_b_class_tiny_live_validation_report.csv)
- [cninfo_b_class_tiny_live_validation_summary.md](cninfo_b_class_tiny_live_validation_summary.md)
