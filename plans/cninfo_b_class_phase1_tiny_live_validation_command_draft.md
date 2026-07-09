# CNINFO B 类 Phase 1 Tiny Live Metadata Validation — Command Draft

_生成时间：2026-07-09_

> **性质：** 未来 tiny live metadata 命令草案。**不执行** · **NOT APPROVED**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**runner_extension_required：** **true**（Phase 1 freeze v1 专用 tiny live runner 或现有 corpus retrieval 脚本扩展）

---

## 1. 范围约束

| 项 | 值 |
|----|-----|
| universe | [cninfo_b_class_phase1_tiny_live_validation_universe.csv](../outputs/validation/cninfo_b_class_phase1_tiny_live_validation_universe.csv)（**5** 家） |
| schema | phase1_freeze_v1 · **15** required fields |
| endpoints | EP001 · EP002 · EP004 · EP005 only |
| max cases | **5**（与 TLC001–TLC005 对齐） |
| CNINFO calls（本回合） | **0** |

### 禁止

- PDF download / parse / OCR / text extraction
- harvest 写入 `outputs/harvest/`
- DB / MinIO / RAG
- verified / testing_stable_sample
- production registry 更新
- 触碰 `outputs/harvest/cninfo_c_class/phase3_batch_500_001/`

---

## 2. 输出隔离

**专用输出根（强制）：**

```text
outputs/validation/cninfo_b_class_tiny_live_validation/
```

建议子路径：

```text
outputs/validation/cninfo_b_class_tiny_live_validation/
  phase1_tiny_sample/
    live_report.csv
    live_summary.md
    raw_metadata_snapshots/
    run_status.csv          # resume marker
```

---

## 3. 规划 Runner 扩展（本轮不实现）

```python
# 规划扩展 — 未来回合实现

parser.add_argument(
    "--universe-csv",
    default="outputs/validation/cninfo_b_class_phase1_tiny_live_validation_universe.csv",
    help="tiny live universe CSV（本回合仅 CSV，无 YAML）",
)
parser.add_argument(
    "--output-root",
    default="outputs/validation/cninfo_b_class_tiny_live_validation",
    help="tiny live 产物根目录（强制隔离）",
)
parser.add_argument(
    "--approve-phase1-tiny-live-metadata",
    action="store_true",
    help="显式批准 Phase 1 tiny live metadata validation",
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
    default=5,
    help="最大执行 case 数（tiny sample 上限 5）",
)
```

---

## 4. Live Command Draft（扩展后 · NOT APPROVED）

```bash
# NOT APPROVED — 须 runner 扩展 + 用户显式批准后方可执行

cd listed_company_data_collector

python lab/validate_cninfo_b_class_phase1_tiny_live_metadata.py \
  --live-metadata \
  --universe-csv outputs/validation/cninfo_b_class_phase1_tiny_live_validation_universe.csv \
  --output-root outputs/validation/cninfo_b_class_tiny_live_validation/phase1_tiny_sample \
  --approve-phase1-tiny-live-metadata \
  --sleep-seconds 0.6 \
  --limit 5 \
  --resume \
  --output-csv outputs/validation/cninfo_b_class_tiny_live_validation/phase1_tiny_sample/live_report.csv \
  --output-md outputs/validation/cninfo_b_class_tiny_live_validation/phase1_tiny_sample/live_summary.md
```

> **注：** `validate_cninfo_b_class_phase1_tiny_live_metadata.py` 为规划脚本名；可在未来回合由 `validate_cninfo_b_class_corpus_retrieval.py` 扩展或新建专用 runner。**本回合不创建该脚本。**

---

## 5. Rate Limit（placeholder）

| 项 | 值 |
|----|-----|
| `--sleep-seconds` | **0.6**（与 registry defaults 一致） |
| 并发 | **1**（禁止并行 CNINFO 请求） |
| 超时 | **10s** |
| HTTP 429 | 立即停止 · 写入 `failure_reason=rate_limited` · **不** retry storm |
| 与 C-class 并发 | **禁止**同时跑 C-class Phase 3 live harvest |

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
| `empty_response` | 记录 `quality_status=needs_review`；继续下一 case |
| `network_error` | 记录并停止当前 case；`--resume` 可续跑 |
| `http_429` | **全局停止**；报告中标记 `rate_limited` |
| `org_id_missing` | EP002 单次尝试；失败则 `needs_review`（不猜测 orgId） |
| `pdf_url_missing` | 对齐 RC003：`needs_review`；**不得**标 verified |
| `duplicate_announcement_id` | 对齐 RC004：保留多候选 · `dedup_decision_required=true` |
| `unknown_category` | 对齐 RC005：`category_status=review_later`；不 forced mapping |

---

## 8. 预期产物（批准后）

| 文件 | 路径 |
|------|------|
| live report | `outputs/validation/cninfo_b_class_tiny_live_validation/phase1_tiny_sample/live_report.csv` |
| live summary | `outputs/validation/cninfo_b_class_tiny_live_validation/phase1_tiny_sample/live_summary.md` |
| run status | `outputs/validation/cninfo_b_class_tiny_live_validation/phase1_tiny_sample/run_status.csv` |
| raw snapshots | `outputs/validation/cninfo_b_class_tiny_live_validation/phase1_tiny_sample/raw_metadata_snapshots/` |

**无 PDF 文件。**

---

## 9. Approval Gate

```text
b_class_phase1_tiny_live_validation_gate = READY_FOR_APPROVAL
```

**NOT APPROVED** — 本 draft 仅为未来命令规划。

---

## 10. Red Lines

- No CNINFO in this planning round
- No live execution in this planning round
- No harvest · No PDF download · No PDF parse
- No DB · No MinIO · No RAG
- No verified · No testing_stable_sample upgrade
- No C-class phase3 output touch
