# CNINFO C-Class Phase 2 Smoke 200 Live Harvest Command Draft

_生成时间：2026-07-08_

> **性质：** Live harvest 命令草案。**不执行** · **NOT APPROVED**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**runner_extension_required：** **true**

---

# 1. Runner 现状

当前 `harvest_cninfo_c_class.py`：

| 参数 | 存在 | 说明 |
|------|------|------|
| `--sample-file` | 是 | universe YAML |
| `--live` | 是 | live 模式 |
| `--limit N` | 是 | smoke live 限制 N 家 |
| `--approve-full-harvest` | 是 | 863 full 批准（**不适用** phase2） |
| `--resume` | 是 | 读 `quality/company_harvest_status.csv` |
| `--output-root` | **否** | **须扩展** |
| `--approve-phase2-smoke-harvest` | **否** | **须扩展** |

**HARVEST_OUTPUT_ROOT** 硬编码：`outputs/harvest/cninfo_c_class`

---

# 2. Minimal Runner Extension（规划）

```python
# 规划扩展 — 本轮不实现

parser.add_argument(
    "--output-root",
    default="outputs/harvest/cninfo_c_class",
    help="harvest 产物根目录（phase2 须隔离）",
)
parser.add_argument(
    "--approve-phase2-smoke-harvest",
    action="store_true",
    help="显式批准 Phase 2 smoke 200 live harvest",
)

# HARVEST_OUTPUT_ROOT = args.output_root  # 运行时覆盖
# resume CSV: {output_root}/quality/company_harvest_status.csv
```

### 隔离目标

```
outputs/harvest/cninfo_c_class/phase2_smoke_200/
├── raw/
├── normalized/
└── quality/
    └── company_harvest_status.csv   # 独立 resume marker
```

---

# 3. Live Command Draft（扩展后 · NOT APPROVED）

```bash
# NOT APPROVED — 须 runner 扩展 + 显式用户批准后方可执行

cd listed_company_data_collector

python lab/harvest_cninfo_c_class.py \
  --live \
  --sample-file lab/eval_companies_c_class_phase2_smoke_200.yaml \
  --limit 200 \
  --output-root outputs/harvest/cninfo_c_class/phase2_smoke_200 \
  --approve-phase2-smoke-harvest \
  --smoke-csv outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_live_report.csv \
  --smoke-md outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_live_summary.md
```

## 3.1 预期行为（批准后）

| 项 | 值 |
|----|-----|
| companies | **200** |
| HTTP cases | **1400** |
| output root | `phase2_smoke_200/` |
| 863 目录 | **不写入** |
| CNINFO | **会调用**（live 模式） |

---

# 4. 当前 Runner 可用命令（不推荐 · 未隔离）

```bash
# NOT RECOMMENDED — 写入共享 HARVEST_OUTPUT_ROOT · resume 与 863 冲突

python lab/harvest_cninfo_c_class.py \
  --live \
  --sample-file lab/eval_companies_c_class_phase2_smoke_200.yaml \
  --limit 200
```

| 风险 | 说明 |
|------|------|
| output 未隔离 | 写入 `outputs/harvest/cninfo_c_class/raw/` 等同 863 根 |
| resume 冲突 | 共享 `company_harvest_status.csv` |
| 批准语义 | `--limit 200` 走 smoke 路径 · 无 phase2 专用 approve |

**在 runner 扩展完成前，不得执行上述命令。**

---

# 5. Post-Live QA（未来）

| 产物 | 路径 |
|------|------|
| live report | `outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_live_report.csv` |
| live summary | `outputs/validation/cninfo_c_class_phase2_smoke_200_harvest_live_summary.md` |
| offline QA | `review_cninfo_c_class_full_harvest_qa.py`（phase2 路径） |

---

# 6. 红线

- **本轮不执行** 任何 live 命令
- **无 CNINFO**（规划轮）
- **无 snapshot** during harvest
