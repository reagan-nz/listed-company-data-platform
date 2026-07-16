# CNINFO D 类 shareholder_change Further-Scale — D-FM-10 Live Evidence

_生成时间：2026-07-16_

> **性质：** SC further-scale ~200 isolated live · R19 excellence-gated · **NOT verified** · **NOT production_ready** · **无 commit** · **无 push**
>
> **任务：** D-FM-10 · d-class-executor · shareholder_change further-scale ~200

---

## 1. Authorization Boundary

| 项 | 值 |
|----|-----|
| HEAD（sync after D-FM-09） | `45fea02` |
| worktree | `listed_company_data_collector-worktrees/d-class` |
| branch | `agent/d-class` |
| scope | **shareholder_change** further-scale S200 only |
| Live CNINFO | **allowed**（R19 standing D bounded） |
| shared CNINFO live | **9**（type=desc · 9 denser trading days） |
| commit / push | **未执行** |
| DLC006R / ESS H3/H4 | **未触碰** |
| A/B/C tracks | **未触碰** |
| ESH inflate | **禁止 / 未执行** |

---

## 2. Universe / Mode

| 项 | 值 |
|----|-----|
| cases | DSC301–DSC500（**200**） |
| found slots | **198** · `captured_normal` |
| empty controls | **2** · `empty_but_valid`（000895 · 601988） |
| endpoint | `https://www.cninfo.com.cn/data20/shareholeder/detail` |
| query | **type=desc** multi-day adaptive union |
| denser days used | **2026-06-16 … 2026-06-27**（9 交易日；禁 2026-07-03） |
| forbidden sole found | type=inc + 2026-07-03 |
| excluded | SC s50 found（DSC201–250）· next-slice · first-slice codes |
| isolated root | `outputs/validation/cninfo_d_class_shareholder_change_further_scale_s200` |
| universe sha256 | `e653b9624056eec86516d75000ffc4c6e14fcfacd37a65eb49eb1f0084324823` |

---

## 3. Commands

```bash
# universe lock cite（CNINFO=9）
.venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale_s200.py --build-universe-lock

# dry-run（CNINFO=0）
.venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale_s200.py --dry-run \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_change_further_scale_s200_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_change_further_scale_s200

# bounded live（CNINFO=9）
.venv/bin/python lab/run_cninfo_d_class_shareholder_change_further_scale_s200.py --live \
  --approve-d-class-shareholder-change-further-scale-s200 \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_change_further_scale_s200_universe_lock_20260716.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_change_further_scale_s200
```

---

## 4. Result

| 项 | 值 |
|----|-----|
| dry-run | planned_ok **200/200** · CNINFO=**0** |
| live acceptable | **200/200**（**100.00%**） |
| found | **198** |
| empty_but_valid | **2** |
| fail / http_error | **0 / 0** |
| CNINFO cite | **9** |
| CNINFO live | **9** |
| CNINFO package formal | **18**（cite 9 + dry 0 + live 9） |
| execution gate | **`PASS_WITH_CAVEAT`** |
| excellence | **YES**（≥95% · fail/http=0） |

---

## 5. Freeze Confirmation

SC s50 further-scale · SC next-slice · ESH further-scale s50/s200/s1000 · AT further-scale s50/s200：**sha256 未变**（见 freeze attestation）。

---

## 6. Artifacts

| artifact | path |
|----------|------|
| universe lock | `outputs/validation/cninfo_d_class_shareholder_change_further_scale_s200_universe_lock_20260716.csv` |
| cite json | `outputs/validation/cninfo_d_class_shareholder_change_further_scale_s200_shareholder_detail_cite_20260716.json` |
| dry-run report | `.../cninfo_d_class_shareholder_change_further_scale_s200/reports/d_class_shareholder_change_further_scale_s200_dryrun_report.csv` |
| live report | `.../cninfo_d_class_shareholder_change_further_scale_s200/reports/d_class_shareholder_change_further_scale_s200_live_report.csv` |
| live summary | `.../cninfo_d_class_shareholder_change_further_scale_s200/reports/d_class_shareholder_change_further_scale_s200_live_summary.md` |
| quality report | `.../cninfo_d_class_shareholder_change_further_scale_s200/reports/d_class_shareholder_change_further_scale_s200_quality_report.csv` |
| freeze attestation | `outputs/validation/cninfo_d_class_shareholder_change_further_scale_s200_freeze_attestation_20260716.csv` |
| this evidence | `outputs/validation/cninfo_d_class_shareholder_change_dfm10_further_scale_s200_live_20260716.md` |

---

## 7. Next

excellence=YES → **SC further-scale ~1000** on NEW isolated root（勿 inflate ESH；勿 mutate 本根 / s50）。
