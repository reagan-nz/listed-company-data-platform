# CNINFO C 类 Era D — Fuller-Market Slice1 Live Execution Summary

_生成时间：2026-07-13_

> **Human approval accepted** · **isolated root only** · **863/phase3/phase35 untouched** · **no commit/push**

---

## Human Approval（verbatim）

> **I approve C-class Era D fuller-market slice1 live harvest — CE1E001–CE1E200 isolated root.**

---

## Sessions

| Session | 命令 | 结果 |
|---------|------|------|
| **1** | `--limit 100 --resume` | **PASS** · 700 CNINFO · ~39.5 min |
| **2** | `--resume`（全量 200 · skip complete） | **PASS** · 700 CNINFO · ~34.3 min |

**Session 2 说明：** 若重复 `--limit 100`，resume 将跳过 Session 1 已 complete 的 93 家后仅剩 7 家 partial，无法覆盖 CE1E101–200。故 Session 2 使用 **`--resume` 无 limit**（同批准 · 续跑剩余 100 家）。`resume_skip_count=100` · `resume_pending_count=100`。

---

## 合计指标

| 指标 | 值 |
|------|-----|
| **CNINFO HTTP requests** | **~1400**（700 + 700） |
| **raw files** | **1400** |
| **normalized files** | **~1958**（含 derived） |
| **isolated root** | `outputs/harvest/cninfo_c_class/fuller_market_slice1_200/`（**~32M**） |
| **universe** | **200** / CE1E001–CE1E200 |

---

## 公司状态（磁盘推断 · 10 normalized 源）

| 状态 | count | 说明 |
|------|-------|------|
| **complete（10/10）** | **193** | 磁盘 normalized 齐全 |
| **missing / failed** | **7** | 退市/合并/PT · 无 basic_profile |
| **partial** | **0** | Session 2 后磁盘无残留 partial 桶 |

### 7 家 missing（预期 caveat）

| company_code | name |
|--------------|------|
| 000003 | PT金田A |
| 000015 | PT中浩A |
| 000022 | 深赤湾A |
| 000024 | 招商地产 |
| 600001 | 邯郸钢铁 |
| 600005 | 武钢股份 |
| 600068 | 葛洲坝 |

---

## Status CSV caveat

`company_harvest_status.csv` **仅 100 行**（Session 2 覆盖写入 Session 1 ledger · 已知 runner 行为）。**磁盘 200 家 raw 齐全** · 离线 audit 应以磁盘+YAML 为准。建议下一刀：**offline status ledger 重建**（从 slice1 根 regenerate · CNINFO=0）。

---

## 生产根确认

| 根 | 状态 |
|----|------|
| `outputs/harvest/cninfo_c_class/`（863） | **未修改**（status CSV mtime 2026-07-10） |
| `phase3_batch_500_001/` | **未修改** |
| `phase35_batch_500_001_resume/` | **未修改** |
| `outputs/snapshot/` | **未修改** |

---

## Post-live Audit（offline · CNINFO 0）

```bash
python3 lab/run_cninfo_c_class_harvest_resume_audit.py --dry-run \
  --harvest-root outputs/harvest/cninfo_c_class/fuller_market_slice1_200/ \
  --universe-yaml lab/eval_companies_c_class_fuller_market_slice1_200.yaml \
  --output-root outputs/validation/cninfo_c_class_erad_fuller_market_slice1_live_audit/
```

**注：** audit 读 status CSV 时显示 needs_review 100（CSV 不完整）· 磁盘实际 **193+7**。

---

## Gates

```
c_class_erad_fuller_market_slice1_execution_gate = PASS_WITH_CAVEAT
c_class_erad_fuller_market_slice1_live_path_gate = APPROVED
c_class_erad_fuller_market_planning_gate = APPROVED
approval_status = APPROVED_LIVE_EXECUTED
approved_for_live = true (slice1 only · spent)
approved_for_snapshot_rebuild = false
```

**NOT verified** · **NOT production_ready** · Era D **not finished**

---

## 红线确认

- Isolated root only · **863/phase3/phase35 untouched**
- No snapshot rebuild · no holdout promotion · no commit/push

---

## 下一步

1. **Offline slice1 status ledger rebuild**（regenerate from disk · CNINFO=0）
2. **Slice1 post-harvest QA closure package**（193 complete + 7 documented hold/fail）
3. Optional：7 家 delisted **accept_with_caveat** · no further live
