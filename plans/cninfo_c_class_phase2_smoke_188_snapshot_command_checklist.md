# CNINFO C-Class Phase 2 Smoke 188 Snapshot Command Checklist

_生成时间：2026-07-09_

> **性质：** Phase 2 smoke 188 snapshot 命令检查清单。**本轮不执行** · **NOT APPROVED**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**依据：**
- [snapshot dry-run plan](cninfo_c_class_phase2_smoke_188_snapshot_dryrun_plan.md)
- [subset design](../outputs/validation/cninfo_c_class_phase2_smoke_188_snapshot_subset_design.csv)
- [snapshot batch runner](../lab/build_cninfo_c_class_snapshot_batch.py)
- [company snapshot builder](../lab/build_cninfo_c_class_company_snapshot.py)

---

# 1. Builder 现状

## `build_cninfo_c_class_snapshot_batch.py`

| 参数 | 存在 | 说明 |
|------|------|------|
| `--dry-run` | 是 | 默认 · 不构建 snapshot |
| `--execute` | 是 | 构建 snapshot（须批准） |
| `--approve-full-snapshot-batch` | 是 | **863 full** 批准（**不适用** phase2 188） |
| `--universe-file` | 是 | universe YAML（默认 863） |
| `--resume` | 是 | 跳过终态公司 |
| `--force` | 是 | 忽略 resume |
| `--harvest-root` | **否** | **须扩展** |
| `--output-dir` | **否** | **须扩展** |
| `--approve-phase2-smoke-188-snapshot` | **否** | **须扩展**（与 full 批准独立） |

**硬编码路径：**
- output: `outputs/snapshot/cninfo_c_class/full/`
- universe: `lab/eval_companies_c_class_harvest_863_non_bse.yaml`

## `build_cninfo_c_class_company_snapshot.py`

| 项 | 现状 |
|----|------|
| `HARVEST_ROOT` | 硬编码 `outputs/harvest/cninfo_c_class` |
| `NORM_ROOT` | `{HARVEST_ROOT}/normalized` |
| `build_snapshot()` | 无 harvest-root 参数 |

---

# 2. snapshot_builder_extension_required

**`snapshot_builder_extension_required = true`**

## 最小扩展（规划）

```python
# build_cninfo_c_class_company_snapshot.py
parser.add_argument("--harvest-root", default="outputs/harvest/cninfo_c_class")
# 运行时覆盖 NORM_ROOT / QUALITY_DIR

# build_cninfo_c_class_snapshot_batch.py
parser.add_argument("--output-dir", default="outputs/snapshot/cninfo_c_class/full")
parser.add_argument(
    "--approve-phase2-smoke-188-snapshot",
    action="store_true",
    help="显式批准 Phase 2 smoke 188 snapshot batch",
)
# universe-file 指向 188 子集 YAML
```

### 须支持的三项

| 能力 | 目标 |
|------|------|
| custom harvest root | `outputs/harvest/cninfo_c_class/phase2_smoke_200` |
| custom company subset | `lab/eval_companies_c_class_phase2_smoke_188.yaml`（188 家） |
| custom output root | `outputs/snapshot/cninfo_c_class/phase2_smoke_188/` |

### 批准范围分离

- `--approve-full-snapshot-batch` → 863 `full/` only
- `--approve-phase2-smoke-188-snapshot` → phase2 188 only

---

# 3. Future Dry-Run Command（扩展后 · NOT APPROVED）

```bash
# NOT APPROVED — 须 builder 扩展后方可执行

cd listed_company_data_collector

python lab/build_cninfo_c_class_snapshot_batch.py \
  --dry-run \
  --universe-file lab/eval_companies_c_class_phase2_smoke_188.yaml \
  --harvest-root outputs/harvest/cninfo_c_class/phase2_smoke_200 \
  --output-dir outputs/snapshot/cninfo_c_class/phase2_smoke_188 \
  --output-csv outputs/validation/cninfo_c_class_phase2_smoke_188_snapshot_dryrun_report.csv \
  --output-md outputs/validation/cninfo_c_class_phase2_smoke_188_snapshot_dryrun_summary.md
```

> 注：`--output-csv` / `--output-md` 亦为规划扩展；当前 batch runner 写死 863 dry-run 路径。

## 3.1 Dry-run 预期

| 项 | 期望 |
|----|------|
| companies | **188** |
| excluded | **12** all-direct-failure |
| planned snapshots | **188** JSON |
| harvest root | `phase2_smoke_200/normalized/` |
| output root | `phase2_smoke_188/` |
| 863 snapshot | **不写入** |
| CNINFO | **0** |
| snapshot files written | **0** |

---

# 4. Future Execute Command（扩展后 · NOT APPROVED）

```bash
# NOT APPROVED — 须 dry-run PASS + 显式用户批准

python lab/build_cninfo_c_class_snapshot_batch.py \
  --execute \
  --universe-file lab/eval_companies_c_class_phase2_smoke_188.yaml \
  --harvest-root outputs/harvest/cninfo_c_class/phase2_smoke_200 \
  --output-dir outputs/snapshot/cninfo_c_class/phase2_smoke_188 \
  --approve-phase2-smoke-188-snapshot
```

---

# 5. 当前不可用命令（不推荐）

```bash
# NOT RECOMMENDED — 读取 863 harvest root · 写入 full/ · universe 863

python lab/build_cninfo_c_class_snapshot_batch.py --dry-run
```

| 风险 | 说明 |
|------|------|
| harvest root 错误 | 读 `outputs/harvest/cninfo_c_class/normalized/`（863）而非 phase2 |
| output 未隔离 | 写入 `outputs/snapshot/cninfo_c_class/full/` |
| universe 错误 | 863 家而非 188 子集 |

**在 builder 扩展完成前，不得对 Phase 2 子集执行上述命令。**

---

# 6. Post-Snapshot QA（未来）

| 产物 | 路径 |
|------|------|
| snapshot JSON | `outputs/snapshot/cninfo_c_class/phase2_smoke_188/*.json` |
| dry-run report | `outputs/validation/cninfo_c_class_phase2_smoke_188_snapshot_dryrun_report.csv` |
| quality review | extend `review_cninfo_c_class_snapshot_full_quality.py` |

---

# 7. 红线

- **本轮不执行** 任何 snapshot 命令
- **无 CNINFO**
- **无 harvest rerun**
- **无 snapshot build**
