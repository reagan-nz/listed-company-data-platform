# CNINFO C 类 — Filtered Universe Mock-Root Dry-Run（Run 12 Wave 3）

_生成时间：2026-07-15 · c-class-executor · offline · CNINFO **0**_

> **validation/_mock_* only** · **no production snapshot execute** · **no commit/push** ·
> **execute_production_snapshot_rebuild=false** · **harvest / 863/phase3/phase35 生产根未改**

---

## 1. 任务结论

在 Wave 1 `filtered_universe_included.yaml` / `--exclusion-csv` 语义之上，落地 **mock-root dry-run**：
**实际调用** batch builder 的 `run_dry_run`（程序化 API），产物仅写入
`outputs/validation/_mock_*`，证明 filtered universe 可被真实 dry-run 路径消费。

| 项 | 结果 |
|----|------|
| gate | **`PASS_OFFLINE`** |
| company_count | **190** |
| execution_list | **190** |
| partial7 / empty_dividend3 leak | **0** |
| snapshot JSON writes | **0** |
| CNINFO | **0** |
| batch builder `--execute` | **未调用** |
| production roots mutated | **false**（full/phase3/phase35 status mtime 仍为 2026-07-10） |

**未改：** `build_cninfo_c_class_snapshot_batch.py` 源码 · harvest · 863/phase3/phase35 生产 snapshot 根。

---

## 2. 为何不用 batch CLI Option B 直跑

Wave 1 `builder_command_draft.sh` Option B 形如：

```bash
# python3 lab/build_cninfo_c_class_snapshot_batch.py --dry-run \
#   --sample-file .../filtered_universe_included.yaml \
#   --output-root outputs/snapshot/cninfo_c_class/_mock_.../
```

实测风险：非 phase35 入口下 CLI **忽略 `--output-root`**，`run_dry_run` 收到的
`out_dir` 来自 `--output-dir`（默认空）→ 回落到
`outputs/snapshot/cninfo_c_class/full/quality/`，会污染生产 status/error。

因此本轮采用 **tiny lab adapter**（程序化传入 `out_dir=<validation/_mock_*>`），
不接线 `--exclusion-csv` 进 batch CLI，也不碰生产 snapshot 根。

---

## 3. 实现内容

| 文件 | 作用 |
|------|------|
| `lab/run_cninfo_c_class_filtered_universe_mock_root_dryrun.py` | mock-root adapter：守卫 + 调 `run_dry_run` + 对账 |
| `lab/test_cninfo_c_class_filtered_universe_mock_root_dryrun.py` | 10 个离线单测 |

能力：

1. `--filtered-universe`（Wave 1 产物）直接喂给 batch dry-run
2. `--universe-yaml` + `--exclusion-csv` 现场过滤后再 dry-run（同语义）
3. 硬拒绝：非 `outputs/validation/_mock_*` · execute · production rebuild 标志
4. 校验：190 · 无 partial7/empty3 泄漏 · status 190 行 · snapshot JSON=0

---

## 4. 实际执行的命令（已跑通）

### 4.1 Wave1 filtered_universe（主路径）

```bash
python3 lab/run_cninfo_c_class_filtered_universe_mock_root_dryrun.py \
  --filtered-universe outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter/filtered_universe_included.yaml \
  --harvest-root outputs/harvest/cninfo_c_class/fuller_market_slice1_200/ \
  --output-root outputs/validation/_mock_erad_filtered_universe_slice1_190_dryrun/
```

结果：`gate: PASS_OFFLINE` · `company_count: 190` · `snapshot_json_writes: 0`

### 4.2 `--exclusion-csv` 现场过滤（并行证明）

```bash
python3 lab/run_cninfo_c_class_filtered_universe_mock_root_dryrun.py \
  --universe-yaml lab/eval_companies_c_class_fuller_market_slice1_200.yaml \
  --exclusion-csv outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/exclusion_reconcile.csv \
  --output-root outputs/validation/_mock_erad_filtered_universe_exclusion_csv_dryrun/
```

结果：`gate: PASS_OFFLINE` · `sample_mode: exclusion_csv_filter` · `company_count: 190`

---

## 5. 输出产物

### Mock root A（Wave1 filtered）

`outputs/validation/_mock_erad_filtered_universe_slice1_190_dryrun/`

| 产物 | 说明 |
|------|------|
| `dryrun_report.csv` | batch dry-run 190 行计划 |
| `dryrun_summary.md` | builder 摘要（既有行为：成功 dry-run 固定 `PASS_WITH_CAVEAT`） |
| `mock_root_dryrun_capability_summary.md` | 本适配器 gate 摘要 |
| `run_meta.json` | 机器可读指标 |
| `quality/company_snapshot_status.csv` | 190 行 pending 框架 |
| `quality/company_snapshot_error.csv` | header only |

### Mock root B（exclusion-csv）

`outputs/validation/_mock_erad_filtered_universe_exclusion_csv_dryrun/`（同上结构 + 现场写出的 `filtered_universe_included.yaml`）

测试摘要：`outputs/validation/cninfo_c_class_filtered_universe_mock_root_dryrun_test_summary_20260715.md`

---

## 6. 测试

```text
python3 lab/test_cninfo_c_class_filtered_universe_mock_root_dryrun.py
→ Ran 10 tests · OK
```

覆盖：mock 根守卫 · execute 硬拒绝 · Wave1 filtered 消费 `run_dry_run` ·
`--exclusion-csv` 现场过滤 · CLI `PASS_OFFLINE`。

---

## 7. Capability gain

- Wave 1 filtered universe **已被真实 batch `run_dry_run` 消费**（不再只是 command-draft / QA 审计）
- `--exclusion-csv` 语义在 mock 根上有可重复执行证明
- 写入严格限制在 `outputs/validation/_mock_*`；生产 snapshot status mtime 未变
- 文档化并规避了 batch CLI `--output-root` 在非 phase35 dry-run 被忽略的缺口

---

## 8. Remaining C gaps

1. `build_cninfo_c_class_snapshot_batch.py` **仍未原生接受** `--exclusion-csv`
2. batch CLI 非 phase35 dry-run **仍忽略 `--output-root`**（本轮以 adapter 绕过，未改 builder）
3. production snapshot **EXECUTE** 仍 human-gated
4. builder 自身 dry-run gate 对成功路径固定报 `PASS_WITH_CAVEAT`（既有行为，非失败）
5. partial7 仍 caveat hold（本轮未 re-live）

---

## 9. Gate / 状态报告

```
c_class_erad_filtered_universe_mock_root_dryrun_gate = PASS_OFFLINE
execute_production_snapshot_rebuild = false
cninfo_calls = 0
snapshot_json_writes = 0
harvest_mutated = false
production_roots_mutated = false
batch_builder_execute_invoked = false
git_commit = NOT_REQUESTED
push = NOT_REQUESTED
```

**下一步（可选 · 非本轮）：** 人批后在 dry-run-only 边界内修复 batch CLI
`--output-root` 别名，或最小接线 `--exclusion-csv`；仍禁止 production execute。

---

## 10. HEAD / 边界

| 项 | 值 |
|----|-----|
| HEAD | `17bc0fe` |
| 本轮写入 | `lab/run_cninfo_c_class_filtered_universe_mock_root_dryrun.py` · `lab/test_*.py` · `outputs/validation/_mock_*` · 本证据 md |
| 未触碰 | harvest · `outputs/snapshot/cninfo_c_class/{full,phase3*,phase35*}` · builder 源码 |
| commit/push | **未执行** |
