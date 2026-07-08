# CNINFO C-Class Snapshot Full Execution Approval Summary

_生成时间：2026-07-08_

> 863 家 snapshot full batch **执行前审核摘要**。**本轮不执行 batch** · **无 CNINFO**

**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`

**Checklist：** [cninfo_c_class_snapshot_full_execution_approval_checklist.md](../../plans/cninfo_c_class_snapshot_full_execution_approval_checklist.md)

---

## 1. Current Status

| 项 | 状态 |
|----|------|
| C-class harvest | **PASS_WITH_RESUME**（863 家） |
| QA / field freeze / promotion | 已完成 |
| Snapshot architecture + builder PoC | 已完成 |
| Smoke 10 | `snapshot_smoke_gate = PASS_WITH_CAVEAT` |
| Full batch planning | `snapshot_full_batch_gate = PASS_WITH_CAVEAT` |
| Batch runner dry-run | `snapshot_batch_dryrun_gate = PASS_WITH_CAVEAT` · test **5/5 PASS** |
| **Full execution** | **尚未执行** |

---

## 2. Dry-Run Result

| 项 | 值 |
|----|-----|
| company_count | **863** |
| hold_overlap | **0** |
| status CSV rows | **863**（全部 `pending`） |
| error CSV | header only（0 错误） |
| dry-run report rows | **863** |
| full `*.json` 生成 | **0** |

---

## 3. Safety Controls

| 控制 | 实现 |
|------|------|
| 默认 dry-run | 无参数不 build |
| 双开关批准 | `--execute` + `--approve-full-snapshot-batch` |
| 无批准拒绝 | `FULL_SNAPSHOT_BATCH_APPROVAL_REQUIRED` |
| 路径隔离 | `full/` 与 `smoke/` · `company_snapshot_demo/` 分离 |
| normalized 只读 | 不修改 harvest 产物 |
| 无 CNINFO | 离线读 normalized |

---

## 4. Known Caveats

- 全部 863 家预期主流 `snapshot_status = complete_with_caveat`
- `technology_profile`：**863/863** `not_available`（无源）
- executive empty_but_valid：**~9** 家 → executive partial
- share_capital empty_but_valid：**~10** 家 → financial / capital_action partial
- dividend valid_empty：**~38** 家 → dividend / event_timeline partial
- shareholder / market / investor / risk：**partial 为主**（设计预期）
- cross_company schema drift：smoke 已记录，**不阻塞** full batch

---

## 5. Execution Command

**批准后在项目根目录执行（本轮未运行）：**

```bash
cd listed_company_data_collector
python lab/build_cninfo_c_class_snapshot_batch.py \
  --execute \
  --approve-full-snapshot-batch
```

**可选参数：**

```bash
# 中断后续跑（跳过终态公司）
python lab/build_cninfo_c_class_snapshot_batch.py \
  --execute \
  --approve-full-snapshot-batch \
  --resume

# 全量重建
python lab/build_cninfo_c_class_snapshot_batch.py \
  --execute \
  --approve-full-snapshot-batch \
  --force
```

---

## 6. Rollback / Resume Strategy

| 场景 | 策略 |
|------|------|
| 中断续跑 | `--resume`；读取 `company_snapshot_status.csv` 跳过终态 |
| 单公司失败 | 记入 `company_snapshot_error.csv`；`retry_status=pending` |
| 全量重做 | `--force` 忽略 resume 跳过 |
| 回滚 snapshot | 删除 `full/*.json`；将 status 重置为 pending（手动） |
| 不回滚 normalized | harvest 产物保持不变 |

---

## 7. Approval Recommendation

| 项 | 建议 |
|----|------|
| 框架就绪 | **是** — universe / safety / resume / error isolation 全部 PASS |
| 质量预期 | **PASS_WITH_CAVEAT** — partial/not_available 为政策允许 |
| 人工批准 | **建议批准执行** offline full batch |
| 执行后验收 | 生成 `snapshot_quality_summary.md`；核对 failed_count 阈值 |

```
snapshot_full_execution_gate = READY_FOR_APPROVAL
```

**下一步：** 人工批准后执行 `--execute --approve-full-snapshot-batch`；执行后做 post-batch quality review。

---

## 红线确认

- 本轮 **未执行** full batch · **未生成** snapshot JSON
- raw / normalized / field_inventory **未修改**
- 未入库 / MinIO / RAG · 未写 verified · 未 testing_stable_sample
