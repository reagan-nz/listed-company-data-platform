# CNINFO B 类 TLC002 Isolated Retry — Command Draft

_生成时间：2026-07-09_

> **性质：** 未来 TLC002 isolated retry 命令草案。**不执行** · **NOT APPROVED**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**runner_extension_required：** **true**（须扩展 `run_cninfo_b_class_tiny_live_validation.py` 或专用 retry 入口）

---

## 1. Scope

| 项 | 值 |
|----|-----|
| case_id | **TLC002** only |
| company_code | **300009** |
| company_name | 安科生物 |
| source_type | `cninfo_general_announcement_pdf` |
| endpoints | EP002 → EP001（EP005 primary reporting） |
| CNINFO calls（本回合） | **0** |

---

## 2. Output Isolation

```text
outputs/validation/cninfo_b_class_tlc002_retry/
├── raw_metadata/
│   └── TLC002_EP005.json
├── quality/
│   └── TLC002.json
└── reports/
    ├── tlc002_retry_report.csv
    └── tlc002_retry_summary.md
```

**禁止写入：**

- `outputs/validation/cninfo_b_class_tiny_live_validation/`（原 tiny live · 只读）
- `outputs/harvest/`
- `outputs/harvest/cninfo_c_class/phase3_batch_500_001/`

---

## 3. 规划 Runner 扩展（本轮不实现）

```python
# 规划扩展 — 未来回合

parser.add_argument(
    "--case-id",
    default=None,
    help="isolated retry 单 case（TLC002）",
)
parser.add_argument(
    "--output-root",
    default="outputs/validation/cninfo_b_class_tlc002_retry",
    help="TLC002 retry 隔离根（强制）",
)
parser.add_argument(
    "--approve-b-class-tlc002-retry",
    action="store_true",
    help="显式批准 TLC002 isolated retry",
)
```

### Approval 规则

| Flag | 行为 |
|------|------|
| `--approve-b-class-tlc002-retry` | **必须**（isolated retry） |
| `--approve-b-class-tiny-live-validation` | **单独使用则拒绝**；仅在与 TLC002 flag **同时**显式提供时允许组合 |
| `--approve-full-harvest` 等 C-class flags | **拒绝** |

---

## 4. Command Draft（扩展后 · NOT APPROVED）

```bash
# NOT APPROVED — 须 runner 扩展 + 用户显式批准后方可执行

cd listed_company_data_collector

python lab/run_cninfo_b_class_tiny_live_validation.py \
  --live \
  --case-id TLC002 \
  --universe-csv outputs/validation/cninfo_b_class_phase1_tiny_live_validation_universe.csv \
  --output-root outputs/validation/cninfo_b_class_tlc002_retry \
  --approve-b-class-tlc002-retry \
  --sleep-seconds 0.6 \
  --output-csv outputs/validation/cninfo_b_class_tlc002_retry/reports/tlc002_retry_report.csv \
  --output-md outputs/validation/cninfo_b_class_tlc002_retry/reports/tlc002_retry_summary.md
```

> **注：** `--case-id` 与 `--approve-b-class-tlc002-retry` 为规划参数；**本回合不实现、不执行**。

---

## 5. Rate Limit

| 项 | 值 |
|----|-----|
| sleep_seconds | **0.6** |
| max CNINFO requests | **≤2**（1×EP002 + 1×EP001） |
| HTTP 429 | 停止 · 记录 · 无 retry storm |

---

## 6. Expected Outcomes（批准后）

| 成功 | 失败（可接受） |
|------|----------------|
| `retrieval_status=found` | `network_error`（再次记录，不自动循环） |
| `quality_status=pass` 或 `needs_review` | `needs_review` |
| `lineage_status=discovered` | `needs_review` |

**永不：** `verified` · PDF 落盘

---

## 7. Gate

```text
b_class_tlc002_isolated_retry_gate = READY_FOR_APPROVAL
```

**NOT EXECUTED**

---

## 8. Red Lines

- No CNINFO in this planning round
- No retry execution in this planning round
- No schema / freeze modification
- No PDF · No DB · No MinIO · No RAG · No verified
