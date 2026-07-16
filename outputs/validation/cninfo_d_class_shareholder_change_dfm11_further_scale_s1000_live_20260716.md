# CNINFO D 类 shareholder_change Further-Scale — D-FM-11 Live Evidence

_生成时间：2026-07-16_

> **性质：** SC further-scale ~1000 isolated live · R19 excellence-gated · **NOT verified** · **NOT production_ready** · **无 commit** · **无 push**
>
> **任务：** D-FM-11 · d-class-executor · shareholder_change further-scale ~1000

---

## 1. Authorization Boundary

| 项 | 值 |
|----|-----|
| HEAD（sync after D-FM-10） | `2011026` |
| worktree | `listed_company_data_collector-worktrees/d-class` |
| branch | `agent/d-class` |
| scope | **shareholder_change** further-scale S1000 only |
| Live CNINFO | **allowed**（R19 standing D bounded） |
| shared CNINFO live | **11**（type=desc · 11 denser trading days） |
| commit / push | **未执行** |
| DLC006R / ESS H3/H4 | **未触碰** |
| A/B/C tracks | **未触碰** |
| ESH inflate | **禁止 / 未执行** |

---

## 2. Universe / Mode（found vs empty pad · honest）

| 项 | 值 |
|----|-----|
| cases | DSC501–DSC1500（**1000**） |
| found slots | **132** · `captured_normal` |
| empty controls（pad） | **868** · `empty_but_valid` |
| empty_control_min | **10**（实际 pad 远高于下限；诚实记录） |
| endpoint | `https://www.cninfo.com.cn/data20/shareholeder/detail` |
| query | **type=desc** multi-day adaptive union |
| denser days used | **2026-06-27 … 2026-07-15**（11 交易日；禁 2026-07-03） |
| forbidden sole found | type=inc + 2026-07-03 |
| excluded | SC s50 found · SC s200 found · next-slice · first-slice codes |
| isolated root | `outputs/validation/cninfo_d_class_shareholder_change_further_scale_s1000` |
| universe sha256 | `bc764fa2054794ad064202331e05f200296459af5a92c40c1a3e446cfff134db` |

**诚实说明：** 在排除 SC s50/s200 found 后，多日 type=desc 并集仅剩 **132** 个新 found 码；其余 **868** 槽以 empty-control pad 填满 1000。不虚报 found 密度。

---

## 3. Commands

```bash
# universe lock cite（CNINFO=20）
.venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale_s1000.py --build-universe-lock

# dry-run（CNINFO=0）
.venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale_s1000.py --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_change_further_scale_s1000_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_change_further_scale_s1000

# bounded live（CNINFO=11）
.venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale_s1000.py --live \
  --approve-d-class-shareholder-change-further-scale-s1000 \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_change_further_scale_s1000_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_change_further_scale_s1000
```

---

## 4. Result

| 项 | 值 |
|----|-----|
| dry-run | planned_ok **1000/1000** · CNINFO=**0** |
| live acceptable | **1000/1000**（**100.00%**） |
| found | **132** |
| empty_but_valid | **868** |
| fail / http_error | **0 / 0** |
| CNINFO cite | **20** |
| CNINFO live | **11** |
| CNINFO package formal | **31**（cite 20 + dry 0 + live 11） |
| execution gate | **`PASS_WITH_CAVEAT`** |
| excellence | **YES**（≥95% · fail/http=0） |

---

## 5. Freeze Confirmation

SC s50 / s200 further-scale · SC next-slice · ESH further-scale s50 · AT further-scale s50：**sha256 未变**（见 freeze attestation）。

---

## 6. Artifacts

| artifact | path |
|----------|------|
| universe lock | `outputs/validation/cninfo_d_class_shareholder_change_further_scale_s1000_universe_lock_20260716.csv` |
| cite json | `outputs/validation/cninfo_d_class_shareholder_change_further_scale_s1000_shareholder_detail_cite_20260716.json` |
| dry-run report | `.../cninfo_d_class_shareholder_change_further_scale_s1000/reports/d_class_shareholder_change_further_scale_s1000_dryrun_report.csv` |
| live report | `.../cninfo_d_class_shareholder_change_further_scale_s1000/reports/d_class_shareholder_change_further_scale_s1000_live_report.csv` |
| live summary | `.../cninfo_d_class_shareholder_change_further_scale_s1000/reports/d_class_shareholder_change_further_scale_s1000_live_summary.md` |
| quality report | `.../cninfo_d_class_shareholder_change_further_scale_s1000/reports/d_class_shareholder_change_further_scale_s1000_quality_report.csv` |
| freeze attestation | `outputs/validation/cninfo_d_class_shareholder_change_further_scale_s1000_freeze_attestation_20260716.csv` |
| this evidence | `outputs/validation/cninfo_d_class_shareholder_change_dfm11_further_scale_s1000_live_20260716.md` |

---

## 7. Next

excellence=YES → **component switch** EP / RSU / FIA ~50 on NEW isolated root（勿 inflate ESH；勿 mutate SC s50/s200/s1000；勿 harden @1000）。
