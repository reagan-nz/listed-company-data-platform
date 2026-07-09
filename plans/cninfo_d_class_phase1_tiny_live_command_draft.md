# CNINFO D 类 Phase 1 Tiny Live Metadata Validation — Command Draft

_生成时间：2026-07-09_

> **性质：** 未来 tiny live metadata 命令草案。**不执行** · **NOT APPROVED**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**runner_extension_required：** **true**（Phase 1 freeze v1 专用 D-class tiny live runner **未实现**）

---

## 1. 范围约束

| 项 | 值 |
|----|-----|
| universe | [cninfo_d_class_phase1_tiny_live_universe.csv](../outputs/validation/cninfo_d_class_phase1_tiny_live_universe.csv)（**7** 家 · 每组件 1 case） |
| schema | `d_class_phase1_freeze_v1` · **49** required fields（7 组件 + market_event 信封） |
| components | margin_trading · block_trade · restricted_shares_unlock · disclosure_schedule · equity_pledge · shareholder_change · executive_shareholding |
| max cases | **7**（与 DLC001–DLC007 对齐） |
| CNINFO calls（本回合） | **0** |

### 禁止

- harvest 写入 `outputs/harvest/`
- market data 全市场采集
- DB / MinIO / RAG
- verified / testing_stable_sample
- production registry 更新
- 触碰 C-class / A-class / B-class 输出
- 扩大样本超出 tiny universe

---

## 2. 输出隔离

**专用输出根（强制）：**

```text
outputs/validation/cninfo_d_class_tiny_live_validation/
```

建议子路径：

```text
outputs/validation/cninfo_d_class_tiny_live_validation/
  phase1_tiny_sample/
    live_report.csv
    live_summary.md
    raw_event_snapshots/
    run_status.csv          # resume marker
```

---

## 3. 规划 Runner 扩展（本轮不实现）

```python
# 规划扩展 — 未来回合实现

parser.add_argument(
    "--universe-csv",
    default="outputs/validation/cninfo_d_class_phase1_tiny_live_universe.csv",
    help="D-class tiny live universe CSV（本回合仅 CSV，无 YAML）",
)
parser.add_argument(
    "--output-root",
    default="outputs/validation/cninfo_d_class_tiny_live_validation",
    help="tiny live 产物根目录（强制隔离）",
)
parser.add_argument(
    "--approve-d-class-tiny-live-validation",
    action="store_true",
    help="显式批准 D-class Phase 1 tiny live metadata validation",
)
parser.add_argument(
    "--sleep-seconds",
    type=float,
    default=0.6,
    help="CNINFO 请求间隔（秒）",
)
parser.add_argument(
    "--resume",
    action="store_true",
    help="从 output-root/run_status.csv 恢复未完成 case",
)
parser.add_argument(
    "--limit",
    type=int,
    default=7,
    help="最大执行 case 数（tiny sample 上限 7）",
)
```

---

## 4. Live Command Draft（扩展后 · NOT APPROVED）

```bash
# NOT APPROVED — 须 runner 实现 + 用户显式批准后方可执行

cd listed_company_data_collector

python lab/validate_cninfo_d_class_phase1_tiny_live_metadata.py \
  --live-metadata \
  --universe-csv outputs/validation/cninfo_d_class_phase1_tiny_live_universe.csv \
  --output-root outputs/validation/cninfo_d_class_tiny_live_validation/phase1_tiny_sample \
  --approve-d-class-tiny-live-validation \
  --sleep-seconds 0.6 \
  --limit 7 \
  --resume \
  --output-csv outputs/validation/cninfo_d_class_tiny_live_validation/phase1_tiny_sample/live_report.csv \
  --output-md outputs/validation/cninfo_d_class_tiny_live_validation/phase1_tiny_sample/live_summary.md
```

> **注：** `validate_cninfo_d_class_phase1_tiny_live_metadata.py` 为规划脚本名；未来回合新建专用 runner。**本回合不创建该脚本。**

---

## 5. Rate Limit（placeholder）

| 项 | 值 |
|----|-----|
| `--sleep-seconds` | **0.6**（与 registry defaults 一致） |
| 并发 | **1**（禁止并行 CNINFO 请求） |
| 超时 | **10s** |
| HTTP 429 | 立即停止 · 写入 `failure_reason=rate_limited` · **不** retry storm |
| 与 C-class 并发 | **禁止**同时跑 C-class live harvest |

---

## 6. Resume 行为（placeholder）

1. 启动时读取 `{output-root}/run_status.csv`
2. `status=completed` 的 `case_id` 跳过
3. `status=failed` / `status=partial` 可由 `--resume` 重试（仍遵守 rate limit）
4. 每 case 完成后原子更新 `run_status.csv`
5. 中断（Ctrl+C / network_error）保留 partial 结果，不清理 isolation root

---

## 7. Failure Handling（placeholder）

| 失败类型 | 处理 |
|----------|------|
| `empty_but_valid` | 记录 `retrieval_status=empty_but_valid` · `quality_status=pass`；对齐 DC001/DC004 |
| `network_error` | 记录并停止当前 case；`--resume` 可续跑 |
| `http_429` | **全局停止**；报告中标记 `rate_limited` |
| `mapping_ambiguity` | 对齐 DC007：`quality_status=needs_review` · `lineage_status=needs_review` |
| `required_field_missing` | 非合法空态时 `quality_status=needs_review` 或 `blocked` |
| `component_mismatch` | envelope `event_type` 与 registry source_id 不一致 → `needs_review` |

---

## 8. 预期产物（批准后）

| 文件 | 路径 |
|------|------|
| live report | `outputs/validation/cninfo_d_class_tiny_live_validation/phase1_tiny_sample/live_report.csv` |
| live summary | `outputs/validation/cninfo_d_class_tiny_live_validation/phase1_tiny_sample/live_summary.md` |
| run status | `outputs/validation/cninfo_d_class_tiny_live_validation/phase1_tiny_sample/run_status.csv` |
| raw snapshots | `outputs/validation/cninfo_d_class_tiny_live_validation/phase1_tiny_sample/raw_event_snapshots/` |

**无 harvest 产物 · 无 PDF 文件 · 无 DB/MinIO。**

---

## 9. Approval Gate

```text
d_class_phase1_tiny_live_validation_gate = READY_FOR_APPROVAL
```

**NOT APPROVED** — 本 draft 仅为未来命令规划。

---

## 10. Red Lines

- No CNINFO in this planning round
- No live execution in this planning round
- No harvest · No market data ingestion beyond tiny probe
- No DB · No MinIO · No RAG
- No verified · No testing_stable_sample upgrade
- No C-class / A-class / B-class output touch
- No commit in this round
