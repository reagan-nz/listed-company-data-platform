# CNINFO D 类 shareholder_data First-Slice — S4 Runner Extension Summary

_生成时间：2026-07-15 · D-FM-08_

> **性质：** S4 runner extension + dry-run + offline tests · **CNINFO calls = 0** · **live 未执行** · **NOT verified** · **NOT production_ready** · **无 commit** · **无 push**
>
> **任务：** D-FM-08 · standing_scope full-market shareholder / capital · `controller_execution_allowed=false`

---

## 1. Implementation

| 项 | 值 |
|----|-----|
| runner | `lab/run_cninfo_d_class_tiny_live_validation.py` |
| mode flag | `--shareholder-data-first-slice` |
| approval flag | `--approve-d-class-shareholder-data-first-slice`（live only · 本任务未授权） |
| universe lock（只读） | `outputs/validation/cninfo_d_class_shareholder_data_first_slice_universe_lock_20260715.csv` |
| output root | `outputs/validation/cninfo_d_class_shareholder_data_first_slice/` |
| tests | `lab/test_cninfo_d_class_shareholder_data_first_slice_runner.py`（**19/19 PASS**） |
| fixture regression | `lab/test_cninfo_d_class_shareholder_data_fixtures.py`（**15/15 PASS**） |

### Query plan（VR-003/006/007）

- **仅** `query_mode=rdate_report_period` + `rdate=20260331`
- **prefer 1 shared** 全市场截面请求 · 离线按 SECCODE 过滤 DSD001–DSD005
- 独立 builder：`_build_shareholder_data_first_slice_params(row)` → `[{"rdate":"20260331"}]`
- per-case budget ≤ **1** · total cap ≤ **5** · planned_shared = **1**
- endpoint：`https://www.cninfo.com.cn/data20/shareholeder/data`（拼写 shareholeder 保留）
- records_path：`data.records`

---

## 2. Dry-Run Result

| 指标 | 值 |
|------|-----|
| planned_ok | **5/5** |
| planned_shared_cninfo_requests | **1** |
| planned_request_count_total | **1** |
| CNINFO calls | **0** |
| cases | DSD001–DSD005 |

| 产物 | 路径 |
|------|------|
| dry-run report | [d_class_shareholder_data_first_slice_dryrun_report.csv](cninfo_d_class_shareholder_data_first_slice/reports/d_class_shareholder_data_first_slice_dryrun_report.csv) |
| dry-run summary | [d_class_shareholder_data_first_slice_dryrun_summary.md](cninfo_d_class_shareholder_data_first_slice/reports/d_class_shareholder_data_first_slice_dryrun_summary.md) |
| planned_snapshots | `cninfo_d_class_shareholder_data_first_slice/planned_snapshots/DSD00{1-5}_shareholder_data.json`（`cninfo_called=false` · `shared_request=true`） |

### Dry-run 命令

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --shareholder-data-first-slice \
  --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_data_first_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_data_first_slice/
```

---

## 3. Offline Tests

```text
python lab/test_cninfo_d_class_shareholder_data_first_slice_runner.py
Ran 19 tests · OK · CNINFO=0（requests.get/post mocked unused）

python lab/test_cninfo_d_class_shareholder_data_fixtures.py
Ran 15 tests · OK · regression
```

覆盖：universe 校验 · 301259 拒绝 · anchor_rdate · output-root write-block（含 AT/ES） · mixed-mode · live 无 approval 拒绝 · live+approval 仍 `live_not_implemented` · PDF/OCR/DB/MinIO/RAG 阻断 · planned_snapshots · shared plan=1。

---

## 4. Guards Enforced

- universe size = **5** · case_id **DSD001–DSD005** only
- component = **shareholder_data** · anchor_rdate = **20260331**
- exclude **688671** · **301259**
- write-block: v1/v2 tiny-live · replacement · targeted_probe · ES · SC · equity_pledge · margin · disclosure · block_trade · RSU · abnormal_trading
- universe lock CSV / fixtures：**未修改内容**（只读引用）
- live without `--approve-d-class-shareholder-data-first-slice` → reject · CNINFO=0
- live with approval → `shareholder_data_first_slice_live_not_implemented` · CNINFO=0
- PDF/OCR/extraction/DB/MinIO/RAG/verified/production_ready blocked

---

## 5. Live Status

| 项 | 值 |
|----|-----|
| live executed | **no** |
| CNINFO live calls | **0** |
| live_gate | **NOT_APPROVED** |
| reason | D-FM-08 仅 S4 dry-run；`execute_*_live` 骨架显式 `live_not_implemented` |

---

## 6. Files Modified / Created

| 路径 | 动作 |
|------|------|
| `lab/run_cninfo_d_class_tiny_live_validation.py` | modified（SD first-slice mode + dispatch + mutual exclusion） |
| `lab/test_cninfo_d_class_shareholder_data_first_slice_runner.py` | created |
| `lab/test_cninfo_d_class_shareholder_data_fixtures.py` | modified（runner_gate → READY_FOR_APPROVAL） |
| `outputs/validation/cninfo_d_class_shareholder_data_first_slice/` | dry-run 产物（reports + planned_snapshots） |
| `outputs/validation/cninfo_d_class_shareholder_data_offline_prep_checklist_20260715.csv` | CHK-005–008 更新 |
| `outputs/validation/cninfo_d_class_shareholder_data_s4_runner_extension_summary_20260715.md` | created（本文件） |
| `outputs/validation/cninfo_d_class_shareholder_data_first_slice_next_step_recommendation_20260715.md` | updated |

**未修改：** universe lock · Tier-1 fixtures · A/B/C 轨 · DLC006R

---

## 7. Gates

```text
component = shareholder_data
d_class_shareholder_data_first_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_shareholder_data_first_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_shareholder_data_first_slice_live_gate = NOT_APPROVED
d_class_shareholder_data_first_slice_execution_gate = NOT_APPLICABLE
verified = false
production_ready = false
cninfo_calls = 0
```

---

## 8. Next Step

Primary：**controller commit-boundary** for D-FM-08 runner+S4 package

Secondary（standing scope allows）：abnormal_trading bounded live（DAT001–DAT005 · `--approve-d-class-abnormal-trading-first-slice` · 须 `controller_execution_allowed`）

Explicit non-goals：**不** Level-2 IDLE · **不** reopen DLC006R · **不** shareholder_data 真实 live（直至 shared live path 实现 + 单独批准）
