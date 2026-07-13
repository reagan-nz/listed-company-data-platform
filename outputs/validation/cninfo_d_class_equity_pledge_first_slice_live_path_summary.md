# CNINFO D 类 equity_pledge First-Slice — Live Path Summary

_生成时间：2026-07-10_

> **性质：** offline live-path implementation · mock CNINFO only · **NOT APPROVED for production live**

---

## 1. Scope

| 项 | 值 |
|----|-----|
| component | `equity_pledge` |
| universe | DEP001–DEP005（**5** 行） |
| anchor_tdate | **2026-07-03** |
| endpoint | `https://www.cninfo.com.cn/data20/equityPledge/list` |
| output root | `outputs/validation/cninfo_d_class_equity_pledge_first_slice/` |
| excluded codes | **688671** · **301259** |
| request cap | **≤20**（planned **5** · 1/case） |

---

## 2. Implementation

| 项 | 内容 |
|----|------|
| runner | `lab/run_cninfo_d_class_tiny_live_validation.py` |
| live entry | `execute_equity_pledge_first_slice_live()` |
| approval flag | `--approve-d-class-equity-pledge-first-slice`（live 前强制） |
| live without approval | 拒绝于 CNINFO 之前 |
| write-blocks | v1/v2 · known-event · margin_trading · disclosure_schedule · block_trade · restricted_shares_unlock roots |

**移除 stub：** `equity_pledge_first_slice_live_not_implemented`（`execute_equity_pledge_first_slice_live` 已接线）

---

## 3. Test Results（mock only · CNINFO 0 in offline task）

| suite | result |
|-------|--------|
| `lab/test_cninfo_d_class_equity_pledge_first_slice_live_path.py` | **22/22 PASS** |
| `lab/test_cninfo_d_class_equity_pledge_first_slice_runner.py` | **20/20 PASS** |
| **combined** | **42/42 PASS** |

**mock live：** acceptable **5/5** · mock CNINFO calls **5**（仅 `_cninfo_request` mock · `requests.get/post` **0**）

**dry-run reconfirm：** **5/5 planned_ok** · planned **5** · CNINFO **0**

**block_trade smoke：** dry-run **PASS** · CNINFO **0**

---

## 4. Artifacts（mock live only）

Mock live 写入隔离子目录 `_mock_live_tests/live_*`（测试后清理）：

- `d_class_equity_pledge_first_slice_live_report.csv`
- `d_class_equity_pledge_first_slice_quality_report.csv`
- `d_class_equity_pledge_first_slice_live_summary.md`

**production live report：** `reports/d_class_equity_pledge_first_slice_live_report.csv` — **NOT CREATED**

---

## 5. Gates

```text
d_class_equity_pledge_first_slice_live_path_gate = READY_FOR_APPROVAL
d_class_equity_pledge_first_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_equity_pledge_first_slice_approval_gate = READY_FOR_APPROVAL
approval_status = NOT_APPROVED
approved_for_live = false
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

Future acceptance threshold：**≥3/5 acceptable → PASS_WITH_CAVEAT**

---

## 6. Closed Tracks（未触碰）

- known-event replacement / targeted probe
- margin_trading first-slice（commit **`116f875`**）
- disclosure_schedule first-slice（commit **`d37ce0a`**）
- block_trade first-slice（commit **`403472d`** · **NOT verified**）
- restricted_shares_unlock first-slice（commit **`aa087b5`** · **NOT verified**）

---

## 7. Next Step

Human approve isolated live with exact phrase（separate gate · **not now**）:

> I approve D-class equity_pledge first-slice live validation.
