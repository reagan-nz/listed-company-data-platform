# CNINFO B 类 Phase 2 Expansion — Command Draft

_生成时间：2026-07-09_

> **性质：** 未来 Phase 2 live metadata expansion 命令草案。**不执行** · **NOT APPROVED**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**Phase 1 closure gate：** `b_class_phase1_tiny_live_closure_gate = PASS_WITH_CAVEAT`

**runner_extension_required：** **true**（需扩展 tiny live runner 或新建 Phase 2 expansion runner）

---

## 1. 范围约束

| 项 | 值 |
|----|-----|
| universe | [cninfo_b_class_phase2_expansion_universe_draft.csv](../outputs/validation/cninfo_b_class_phase2_expansion_universe_draft.csv)（**20** 家 draft · 规模须人工批准） |
| schema | phase1_freeze_v1 · **15** required fields（**不变**） |
| endpoints | EP001 · EP002 · EP004 · EP005 only |
| max cases | **20**（Option A draft；Option B/C 须更新 universe CSV） |
| CNINFO calls（本回合） | **0** |

### 禁止

- PDF download / parse / OCR / text extraction
- harvest 写入 `outputs/harvest/`
- DB / MinIO / RAG
- verified / testing_stable_sample
- production registry 更新
- 触碰 `outputs/harvest/cninfo_c_class/`
- 修改 Phase 1 tiny live / TLC002 retry 输出根

---

## 2. 输出隔离

**专用输出根（强制）：**

```text
outputs/validation/cninfo_b_class_phase2_expansion/
```

建议子路径：

```text
outputs/validation/cninfo_b_class_phase2_expansion/
  raw_metadata/
  quality/
  reports/
  run_status.csv
```

---

## 3. 规划 Runner 扩展（本轮不实现）

```python
# 规划扩展 — 未来回合实现

parser.add_argument(
    "--universe-csv",
    default="outputs/validation/cninfo_b_class_phase2_expansion_universe_draft.csv",
    help="Phase 2 expansion universe CSV",
)
parser.add_argument(
    "--output-root",
    default="outputs/validation/cninfo_b_class_phase2_expansion",
    help="Phase 2 expansion 产物根目录（强制隔离）",
)
parser.add_argument(
    "--approve-b-class-phase2-expansion",
    action="store_true",
    help="显式批准 B-class Phase 2 expansion live metadata validation",
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
    default=20,
    help="最大执行 case 数（须与批准样本规模一致）",
)
```

---

## 4. Live Command Draft（扩展后 · NOT APPROVED）

```bash
# NOT APPROVED — 须 runner 扩展 + 用户显式批准后方可执行

cd listed_company_data_collector

python lab/run_cninfo_b_class_phase2_expansion.py \
  --live \
  --universe-csv outputs/validation/cninfo_b_class_phase2_expansion_universe_draft.csv \
  --output-root outputs/validation/cninfo_b_class_phase2_expansion \
  --approve-b-class-phase2-expansion \
  --sleep-seconds 0.6 \
  --limit 20 \
  --resume
```

> **注：** `run_cninfo_b_class_phase2_expansion.py` 为规划脚本名；可在未来回合由 `run_cninfo_b_class_tiny_live_validation.py` 扩展参数化。**本回合不创建该脚本。**

---

## 5. Rate Limit

| 项 | 值 |
|----|-----|
| `--sleep-seconds` | **0.6** |
| 并发 | **1** |
| 超时 | **10s** |
| HTTP 429 | 立即停止 · `failure_reason=rate_limited` · **不** retry storm |
| 与 C-class 并发 | **禁止** |

---

## 6. Resume 行为

1. 读取 `{output-root}/run_status.csv`
2. `status=completed` 跳过
3. `status=failed` / `partial` 可由 `--resume` 续跑
4. 每 case 完成后原子更新 `run_status.csv`
5. 中断保留 partial 结果

---

## 7. Failure Handling

| 失败类型 | 处理 |
|----------|------|
| `network_error` | 停止当前 case；triage 后可选 isolated retry（须单独批准） |
| `http_429` | 全局停止 |
| `org_id_missing` | EP002 单次；失败 `needs_review` |
| `pdf_url_missing` | `needs_review` |
| `duplicate_announcement_id` | `dedup_decision_required=true` |
| `unknown_category` | `review_later` |

---

## 8. 预期产物（批准后）

| 文件 | 路径 |
|------|------|
| expansion report | `outputs/validation/cninfo_b_class_phase2_expansion/reports/expansion_report.csv` |
| expansion summary | `outputs/validation/cninfo_b_class_phase2_expansion/reports/expansion_summary.md` |
| quality report | `outputs/validation/cninfo_b_class_phase2_expansion/reports/quality_report.csv` |
| run status | `outputs/validation/cninfo_b_class_phase2_expansion/run_status.csv` |
| raw metadata | `outputs/validation/cninfo_b_class_phase2_expansion/raw_metadata/` |
| quality JSON | `outputs/validation/cninfo_b_class_phase2_expansion/quality/` |

**无 PDF 文件。**

---

## 9. Approval Gate

```text
b_class_phase2_expansion_planning_gate = READY_FOR_APPROVAL
```

**NOT APPROVED** — 本 draft 仅为未来命令规划。

---

## 10. Red Lines

- No CNINFO in this planning round
- No live execution in this planning round
- No PDF download · No PDF parse
- No DB · No MinIO · No RAG
- No verified · No production_ready · No testing_stable_sample upgrade
