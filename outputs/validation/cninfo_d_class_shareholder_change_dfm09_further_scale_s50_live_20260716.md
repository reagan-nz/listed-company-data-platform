# CNINFO D 类 shareholder_change Further-Scale — D-FM-09 Live Evidence

_生成时间：2026-07-16_

> **性质：** SC further-scale ~50 isolated live · R19 excellence-gated · **NOT verified** · **NOT production_ready** · **无 commit** · **无 push**
>
> **任务：** D-FM-09 · d-class-executor · shareholder_change further-scale starting ~50

---

## 1. Authorization Boundary

| 项 | 值 |
|----|-----|
| HEAD（sync after D-FM-08） | `d85141b` |
| worktree | `listed_company_data_collector-worktrees/d-class` |
| branch | `agent/d-class` |
| scope | **shareholder_change** further-scale only |
| Live CNINFO | **allowed**（R19 standing D bounded） |
| shared CNINFO | **2**（type=desc · 2026-07-01 + 2026-07-14） |
| commit / push | **未执行** |
| DLC006R / ESS H3/H4 | **未触碰** |
| A/B/C tracks | **未触碰** |

---

## 2. Universe / Mode

| 项 | 值 |
|----|-----|
| cases | DSC201–DSC250（**50**） |
| found slots | **48** · `captured_normal` |
| empty controls | **2** · `empty_but_valid`（000895 · 601988） |
| endpoint | `https://www.cninfo.com.cn/data20/shareholeder/detail` |
| query | **type=desc** multi-day union |
| denser days | **2026-07-01** + **2026-07-14** |
| forbidden sole found | type=inc + 2026-07-03 |
| isolated root | `outputs/validation/cninfo_d_class_shareholder_change_further_scale` |
| universe sha256 | `30ebf132d443f1c6cd2c9ad3699675b8e1e660e9fb4f1da6b18dd1711cbd614d` |

---

## 3. Commands

```bash
# universe lock cite（CNINFO=2）
.venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale.py --build-universe-lock

# dry-run（CNINFO=0）
.venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale.py --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_change_further_scale_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_change_further_scale

# bounded live（CNINFO=2）
.venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale.py --live \
  --approve-d-class-shareholder-change-further-scale \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_change_further_scale_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_change_further_scale
```

---

## 4. Result

| 项 | 值 |
|----|-----|
| dry-run | planned_ok **50/50** · CNINFO=**0** |
| live acceptable | **50/50**（**100.00%**） |
| found | **48** |
| empty_but_valid | **2** |
| fail / http_error | **0 / 0** |
| CNINFO live | **2** |
| execution gate | **`PASS_WITH_CAVEAT`** |
| excellence | **YES**（≥95% · fail/http=0） |

---

## 5. Freeze Confirmation

SC next-slice / first-slice · ESH further-scale s50/s200/s1000 · AT further-scale s50 live roots：**sha256 未变**（见 freeze attestation）。

---

## 6. Artifacts

| artifact | path |
|----------|------|
| universe lock | `outputs/validation/cninfo_d_class_shareholder_change_further_scale_universe_lock_20260716.csv` |
| cite json | `outputs/validation/cninfo_d_class_shareholder_change_further_scale_shareholder_detail_cite_20260716.json` |
| dry-run report | `.../cninfo_d_class_shareholder_change_further_scale/reports/d_class_shareholder_change_further_scale_dryrun_report.csv` |
| live report | `.../cninfo_d_class_shareholder_change_further_scale/reports/d_class_shareholder_change_further_scale_live_report.csv` |
| live summary | `.../cninfo_d_class_shareholder_change_further_scale/reports/d_class_shareholder_change_further_scale_live_summary.md` |
| quality report | `.../cninfo_d_class_shareholder_change_further_scale/reports/d_class_shareholder_change_further_scale_quality_report.csv` |
| this evidence | `outputs/validation/cninfo_d_class_shareholder_change_dfm09_further_scale_s50_live_20260716.md` |

---

## 7. Next

excellence=YES → **SC further-scale ~200** on NEW isolated root（勿 inflate ESH；勿 mutate 本根）。
