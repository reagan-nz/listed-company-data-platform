# eval1000_v2 vs eval1000 Baseline Comparison

_Run date: 2026-06-22 | Same cohort: `lab/eval_companies_1000.yaml` (1020 companies)_

## Commands run

```bash
# Pre-run
git status --short          # clean working tree
df -h .                     # 93 GiB available

# Copy cached PDFs + meta only (no old JSON outputs)
mkdir -p outputs/generalization/eval1000_v2
rsync -a \
  --include="*/" --include="*.pdf" --include="meta.json" --exclude="*" \
  outputs/generalization/eval1000/ outputs/generalization/eval1000_v2/
# → 947 PDFs, 947 meta.json copied

# Full eval (~58 min)
.venv/bin/python lab/eval_generalize.py \
  --companies lab/eval_companies_1000.yaml \
  --out outputs/generalization/eval1000_v2 \
  --throttle 1.5 \
  2>&1 | tee outputs/generalization/eval1000_v2/run.log

# SQLite import
.venv/bin/python lab/db_init.py
.venv/bin/python lab/db_import.py \
  --eval-dir outputs/generalization/eval1000_v2 \
  --run-name eval1000_v2 \
  --limit 0
```

## Status counts

| Metric | eval1000 (baseline) | eval1000_v2 | Delta |
|---|---:|---:|---:|
| Total | 1020 | 1020 | 0 |
| ok | 947 | 947 | 0 |
| no_announcement | 73 | 73 | 0 |
| errors | 0 | 0 | 0 |
| non-financial (ok) | 936 | 936 | 0 |
| financial (ok) | 11 | 11 | 0 |

Financial YAML tags: 12 companies; 1 (`000562` 宏源证券) is `no_announcement`.

## Non-financial headline (936 companies)

| Metric | eval1000 | eval1000_v2 | Delta |
|---|---:|---:|---:|
| Mean plausible / company | **10.54 / 11** | **10.33 / 11** | **−0.21** |
| Percentage | 95.8% | 93.9% | −1.9 pp |

> Strict-usable (**10.16 / 11**) was **not** re-run on v2. Do not treat proxy delta as strict improvement.

## Targeted field comparison (non-financial, 936 ok)

| Field | eval1000 found | eval1000 plausible | eval1000_v2 found | eval1000_v2 plausible | Delta plausible | Mechanism |
|---|---:|---:|---:|---:|---:|---|
| rnd_investment | 742 | 742 | 619 | 619 | **−123** | Extraction tightening (Issue #1); all found pass new proxy |
| revenue_by_region | 899 | 899 | 899 | 849 | **−50** | Proxy tightening only (Issue #2); found unchanged |
| revenue_by_segment | 920 | 920 | 920 | 896 | **−24** | Proxy tightening only (Issue #2); found unchanged |

Other 8 industrial fields: **0 plausible delta** (no regression).

### Alignment with cached validation (2026-06-22)

Cached validation re-computed proxy on **old** extraction values. Full v2 rerun confirms direction:

| Field | Cached proxy delta | Full v2 plausible delta |
|---|---:|---:|
| rnd_investment | −101 (proxy on old found) | −123 (extraction + proxy) |
| revenue_by_region | −51 | −50 |
| revenue_by_segment | −24 | −24 |

rnd delta is larger in v2 because extraction also rejects bad values before proxy (742→619 found).

## Financial sub-schema (first real coverage numbers)

| Subtype | Count | Companies |
|---|---:|---|
| bank | 4 | 601988, 601398, 601939, 601328 |
| broker | 5 | 600958, 601901, 601162, 002500, 002736 |
| insurer | 1 | 601336 |
| other_financial | 1 | 600927 |

| Company | Schema | Found | Plausible |
|---|---|---:|---:|
| 中国银行 | bank | 12/13 | 12/13 |
| 工商银行 | bank | 9/13 | 9/13 |
| 建设银行 | bank | 8/13 | 8/13 |
| 交通银行 | bank | 7/13 | 7/13 |
| 东方证券 | broker | 9/12 | 9/12 |
| 方正证券 | broker | 11/12 | 11/12 |
| 天风证券 | broker | 8/12 | 8/12 |
| 山西证券 | broker | 11/12 | 11/12 |
| 国信证券 | broker | 9/12 | 9/12 |
| 新华保险 | insurer | 11/12 | 11/12 |
| 永安期货 | other_financial | 6/8 | 6/8 |

Note: banks tagged `financial: false` in YAML (e.g. `601825` 沪农商行) still use industrial 11-field schema — sample tagging gap, not a v2 regression.

## SQLite import (eval1000_v2)

| Table | Rows | Notes |
|---|---:|---|
| company_basic | 1020 | 0 profile_errors |
| report_source | 1020 | |
| extracted_field | 10428 | +11 vs baseline (10417) — financial sub-schemas have more fields |
| evaluation_result | 10428 | run_name=`eval1000_v2` |

Import completed without abort. DB path: `outputs/db/listed_companies_v1.db` (gitignored).

## Pass / fail judgment

| Check | Result |
|---|---|
| Same cohort reproducibility (ok / no_announcement) | **PASS** (947 / 73 unchanged) |
| Zero hard errors | **PASS** |
| rnd / revenue proxy direction matches cached validation | **PASS** |
| No regression on other 8 industrial fields | **PASS** |
| Financial sub-schema dispatch | **PASS** (11/11 ok financial companies classified) |
| Strict-usable re-audit | **NOT RUN** |

## Remaining risks

1. **strict-usable still stale** at 10.16/11 (pre-fix adversarial audit on eval1000).
2. **Financial numeric quality**: generic `extract_numeric` may pick year-noise (e.g. `2024` as value) — smoke-tested on 601988, not audited at scale.
3. **Sample tagging**: some banks (601825 沪农商行) not marked `financial: true` — evaluated with industrial schema.
4. **Revenue empty-label rows**: known false negatives at 603132, 605090 (pdfplumber label loss).
5. **DB overwrite**: `db_import --run-name eval1000_v2` replaced prior eval1000 rows in the same `.db` file; baseline eval1000 JSON/PDF outputs untouched.

## Files preserved (not deleted / not overwritten)

- `outputs/generalization/eval1000/` — full baseline intact
- `lab/eval_companies_1000.yaml` — unchanged
