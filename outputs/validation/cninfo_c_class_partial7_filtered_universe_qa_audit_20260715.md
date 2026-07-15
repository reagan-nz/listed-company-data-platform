# CNINFO C 类 — Partial7 × Wave1 Filtered Universe QA 审计（Run 12 Wave 2）

_生成时间：2026-07-15 · c-class-executor · offline · CNINFO **0**_

> **validation only** · **no production snapshot execute** · **no commit/push** ·
> **execute_production_snapshot_rebuild=false** · **harvest / 863/phase3/phase35 生产根未改**

---

## 1. 任务结论

在 Wave 1 `filtered_universe_included.yaml`（190 included）之上，补齐 **partial7 原因对账 + QA 矩阵硬化** 离线工具：验证 7 家 partial 不泄漏进 included 池，并对齐 caveat ledger / exclusion reconcile / offline QA matrix。

| 项 | 结果 |
|----|------|
| gate | **`PASS_OFFLINE`** |
| filtered included | **190** |
| partial7 audited | **7/7** |
| reason_reconcile_ok | **7/7** |
| leaked into filtered | **0** |
| CNINFO | **0** |
| snapshot JSON writes | **0** |
| harvest mutated | **false** |
| batch builder `--execute` | **未调用** |
| production roots mutated | **false** |

---

## 2. 实现内容

| 文件 | 作用 |
|------|------|
| `lab/cninfo_c_class_partial7_filtered_universe_qa_audit.py` | 纯逻辑：filtered_universe 提取 · 单行 reason reconcile · 硬化矩阵 |
| `lab/run_cninfo_c_class_partial7_filtered_universe_qa_audit_dryrun.py` | 离线 runner：写 validation 产物 |
| `lab/test_cninfo_c_class_partial7_filtered_universe_qa_audit.py` | 10 个离线单测 |

**未改：** `build_cninfo_c_class_snapshot_batch.py` · harvest · 生产 snapshot 根 · Wave 1 adapter 本体。

---

## 3. 输入 / 输出

### 输入（只读）

| 项 | 路径 |
|----|------|
| Wave 1 filtered universe | `outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter/filtered_universe_included.yaml` |
| caveat ledger | `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_caveat_ledger.csv` |
| Run 11 reconcile | `outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/exclusion_reconcile.csv` |
| offline QA matrix | `outputs/validation/cninfo_c_class_partial7_offline_qa_matrix_20260714.csv` |

### 输出（仅 validation）

根目录：`outputs/validation/cninfo_c_class_erad_partial7_filtered_universe_qa_audit/`

| 产物 | 说明 |
|------|------|
| `partial7_reason_reconcile.csv` | 7 行跨源原因对账 |
| `partial7_offline_qa_matrix_hardened.csv` | QA 矩阵 + Wave1 排除校验列 |
| `run_meta.json` | 机器可读指标 |
| `audit_summary.md` | gate 摘要 |

测试摘要：`outputs/validation/cninfo_c_class_partial7_filtered_universe_qa_audit_test_summary_20260715.md`

---

## 4. Partial7 对账结果

| case_id | code | name | in_filtered | caveat_class | reason_ok |
|---------|------|------|-------------|--------------|-----------|
| CE1E002 | 600001 | 邯郸钢铁 | no | delisted_or_merged_partial_normalized | yes |
| CE1E003 | 600005 | 武钢股份 | no | delisted_or_merged_partial_normalized | yes |
| CE1E034 | 600068 | 葛洲坝 | no | delisted_or_merged_partial_normalized | yes |
| CE1E061 | 000003 | PT金田A | no | delisted_or_merged_partial_normalized | yes |
| CE1E067 | 000015 | PT中浩A | no | delisted_or_merged_partial_normalized | yes |
| CE1E070 | 000022 | 深赤湾A | no | delisted_or_merged_partial_normalized | yes |
| CE1E071 | 000024 | 招商地产 | no | delisted_or_merged_partial_normalized | yes |

共性：`harvest_status=partial` · `disposition=accept_with_caveat` · `pool_decision=excluded` · `cohort_families` 含 `partial7` · QA matrix evidence_gap 非空。

---

## 5. 测试

```text
python3 lab/test_cninfo_c_class_partial7_filtered_universe_qa_audit.py
→ Ran 10 tests · OK
```

覆盖：

- filtered_universe 代码提取（含 Wave1 实文件 190 / 无 partial7）
- 单行 reason reconcile（ok / 泄漏 / disposition 漂移）
- 硬化 QA 矩阵列追加
- dry-run CLI → `PASS_OFFLINE` · 7/7
- `execute_production_snapshot_rebuild` 硬拒绝

---

## 6. Capability gain

- Wave 1 `filtered_universe_included.yaml` **可被离线 QA 审计消费**（不再只是 prep 中间件）
- partial7 **原因字段跨源对账可重复执行**：ledger · reconcile · QA matrix · filtered pool
- QA matrix 硬化列显式记录 `wave1_filtered_universe_check=excluded_ok`
- 泄漏进 included 池 / disposition 漂移会 **硬失败**（禁止静默）

---

## 7. Remaining C gaps

1. `build_cninfo_c_class_snapshot_batch.py` **仍未原生接受** `--exclusion-csv`
2. production snapshot **EXECUTE** 仍 human-gated
3. partial7 **仍 caveat hold**（不进 complete pool；本轮未 re-live / 未补 normalized）
4. mock-root dry-run **仍未实际调用** batch builder（仅 Wave1 command-draft）
5. PT 标的（CE1E061/067）仍缺独立 termination sidecar（既有证据缺口，本轮未扩源）

---

## 8. Gate / 状态报告

```
c_class_erad_partial7_filtered_universe_qa_audit_gate = PASS_OFFLINE
execute_production_snapshot_rebuild = false
cninfo_calls = 0
snapshot_json_writes = 0
harvest_mutated = false
production_roots_mutated = false
batch_builder_execute_invoked = false
git_commit = NOT_REQUESTED
push = NOT_REQUESTED
```

**下一步（可选 · 非本轮）：** dry-run-only 边界内向 batch builder 最小接线 `--exclusion-csv`；或人批后在 `_mock_*` 根执行 Option B dry-run。

---

## 9. HEAD / 边界

| 项 | 值 |
|----|-----|
| HEAD（执行时） | `594866a` |
| commit/push | **未执行**（按指令） |
| 生产 snapshot / harvest | **未触碰** |
| 他线文件 | **未故意修改**（D-class 既有脏文件保持原样） |
