# CNINFO D 类 shareholder_change First-Slice — S5 Live Evidence

_生成时间：2026-07-15_

> **性质：** S5 isolated live validation · Run 12 Wave 1 · **NOT verified** · **NOT production_ready** · **无 commit** · **无 push**
>
> **任务：** d-class-executor · shareholder_change first-slice live · scope authorized · Live CNINFO allowed

---

## 1. Authorization Boundary

| 项 | 值 |
|----|-----|
| HEAD | `8a5fe26` |
| scope | **shareholder_change** only |
| Live CNINFO | **allowed**（本任务） |
| total cap | **≤20** |
| per-case cap | **≤4** |
| preferred | **~5** |
| DLC006R / 301259 | **未重开** |
| universe lock | **未修改**（sha256 不变） |
| commit / push | **未执行** |

Universe lock sha256（执行前后一致）:

```text
49e6ece0c0a5c5ecce32328e4e1fe990b48d7d46d3cc1f32da1c8d2245a3c402
```

---

## 2. Command Executed

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --shareholder-change-first-slice \
  --live \
  --approve-d-class-shareholder-change-first-slice \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_change_first_slice_universe_lock_20260714.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_change_first_slice/
```

**exit code：** **0**

---

## 3. Result

| 项 | 值 |
|----|-----|
| universe | DSC001–DSC005（**5**） |
| component | **shareholder_change** only |
| endpoint | `https://www.cninfo.com.cn/data20/shareholeder/detail` |
| query | **type=inc** + **tdate=2026-07-03**（禁止 desc / multi-tdate） |
| CNINFO requests | **5**（1/case · cap ≤20 · ≤4/case） |
| acceptable | **4/5** |
| executed | **5/5** |
| execution gate | **`PASS_WITH_CAVEAT`** |
| http_error | **0** |
| found rows | **0**（全 universe sparse-day empty） |
| excluded | **688671** · **301259** 不在 universe |

### Per-case outcomes

| case_id | company | expected_behavior | retrieval_status | acceptable | outcome | failure_type |
|---------|---------|-------------------|------------------|------------|---------|--------------|
| DSC001 | 000550 江铃汽车 | captured_normal_or_empty_but_valid | empty_but_valid | yes | empty_but_valid | — |
| DSC002 | 000895 双汇发展 | captured_normal_or_empty_but_valid | empty_but_valid | yes | empty_but_valid | — |
| DSC003 | 600000 浦发银行 | captured_normal_or_empty_but_valid | empty_but_valid | yes | empty_but_valid | — |
| DSC004 | 002415 海康威视 | captured_normal_or_needs_review | empty_but_valid | **no** | empty_but_valid | expectation_mismatch |
| DSC005 | 601988 中国银行 | empty_but_valid | empty_but_valid | yes | empty_but_valid | — |

**outcome mix：** empty_but_valid **×5** · found **0** · needs_review **0** · http_error **0**

---

## 4. Caveat（DSC004）

DSC004（002415 海康威视）标注为 `captured_normal_or_needs_review`，但 anchor `tdate=2026-07-03` 公司级过滤后 **0 行** → `empty_but_valid`。

- 符合 quality policy 的合法空结果（**未**升级为 found / captured_normal）
- 与 `captured_normal_or_needs_review` 期望不一致 → `expectation_mismatch`
- 不影响 execution gate（**4/5 ≥ 3/5** → `PASS_WITH_CAVEAT`）
- 本回合无 `found` 样本（sparse-day）

---

## 5. Artifacts

| artifact | path |
|----------|------|
| live report | [d_class_shareholder_change_first_slice_live_report.csv](cninfo_d_class_shareholder_change_first_slice/reports/d_class_shareholder_change_first_slice_live_report.csv) |
| quality report | [d_class_shareholder_change_first_slice_quality_report.csv](cninfo_d_class_shareholder_change_first_slice/reports/d_class_shareholder_change_first_slice_quality_report.csv) |
| live summary | [d_class_shareholder_change_first_slice_live_summary.md](cninfo_d_class_shareholder_change_first_slice/reports/d_class_shareholder_change_first_slice_live_summary.md) |
| outcome ledger | [cninfo_d_class_shareholder_change_first_slice_live_outcome_ledger.csv](cninfo_d_class_shareholder_change_first_slice_live_outcome_ledger.csv) |
| live snapshots | `cninfo_d_class_shareholder_change_first_slice/live_snapshots/DSC00{1-5}_shareholder_change.json`（gitignored · on-disk · `cninfo_called=true` · http_status=200） |
| this evidence | [cninfo_d_class_shareholder_change_s5_live_20260715.md](cninfo_d_class_shareholder_change_s5_live_20260715.md) |

---

## 6. Safety Confirmations

- [x] output root isolated → `outputs/validation/cninfo_d_class_shareholder_change_first_slice/`
- [x] universe lock CSV **未修改**
- [x] DLC006R / 301259 **未重开**
- [x] no PDF / OCR / extraction / DB / MinIO / RAG
- [x] no verified / production_ready / bare PASS
- [x] no commit · no push
- [x] offline mock live-path guards 已存在于 `lab/test_cninfo_d_class_shareholder_change_first_slice_runner.py`（本回合未新增测试）

---

## 7. Gates

```text
d_class_shareholder_change_first_slice_live_path_gate = READY_FOR_APPROVAL
d_class_shareholder_change_first_slice_execution_gate = PASS_WITH_CAVEAT
approval_status = APPROVED_FOR_THIS_LIVE_ONLY
approved_for_live = true
cninfo_calls = 5
acceptable = 4/5
```

**NOT bare PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

---

## 8. CAPABILITY

**CAPABILITY_ADVANCED** — shareholder_change first-slice **S5 live path executed** with evidence（CNINFO=5 · acceptable=4/5 · `PASS_WITH_CAVEAT`）。

增益边界：

- 获得 first-slice live_snapshots + live/quality reports + outcome ledger
- **不**宣称 verified / production_ready / bare PASS
- **不**自动授权下一组件或 commit boundary

---

## 9. Next Step（建议 · 未执行）

Offline closure / commit-boundary package（CNINFO **0** · **无 commit** · human gate）。
