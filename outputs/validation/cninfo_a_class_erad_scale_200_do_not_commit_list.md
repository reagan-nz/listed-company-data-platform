# CNINFO A 类 Era D ~200 Do-Not-Commit List

_生成时间：2026-07-10_

> **性质：** commit boundary exclusion list · **CNINFO 0** · **no commit in this task**

---

## Bulk Live Output（default exclude）

| 路径模式 | 约计 | 原因 |
|----------|------|------|
| `outputs/validation/cninfo_a_class_erad_scale_200/raw_metadata/**` | **200** | per-case JSON sidecars · regeneratable from approved live rerun · local-first |
| `outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/raw_metadata/**` | **7** | retry per-case JSON · regeneratable · local-first |
| `outputs/validation/cninfo_a_class_erad_scale_200/quality/**` | **0**（if created later） | per-case quality JSON · bulk |

**Policy:** retain locally for audit; do **not** include in explicit-path commit unless project policy changes.

---

## Local Guard / Test Trees

| 路径模式 | 原因 |
|----------|------|
| `outputs/validation/cninfo_a_class_erad_scale_200/_production_guard/**` | write-isolation guard artifact |
| `outputs/validation/cninfo_a_class_erad_scale_200/_mock_test/**` | isolated runner test temp（if present） |
| `outputs/validation/cninfo_a_class_erad_scale_200/_mock_live_test/**` | isolated live-path mock temp（if present） |
| `outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/_mock_test/**` | retry test temp（if present） |
| `**/__pycache__/**` | Python cache |
| `/tmp/**` | local temp |

---

## Phase 3 / A3M017 Production Roots（out of scope · do not touch）

| 路径模式 | 原因 |
|----------|------|
| `outputs/validation/cninfo_a_class_phase3_50_company_expansion/**` | Phase 3 production · committed in **`bbc15c3`** |
| `outputs/validation/cninfo_a_class_phase3_a3m017_isolated_retry/**` | A3M017 retry production（if live later） |
| `outputs/validation/cninfo_a_class_phase1_**` | Phase 1 production |
| `outputs/validation/cninfo_a_class_phase2_**` | Phase 2 production |

**Do not amend `bbc15c3` / `cb9f3fc`.**

---

## Other A/B/C/D Tracks（unrelated）

| 路径模式 | 原因 |
|----------|------|
| `outputs/validation/cninfo_b_class_**` | unrelated B-class |
| `outputs/validation/cninfo_c_class_**` | unrelated C-class |
| `outputs/validation/cninfo_d_class_**` | unrelated D-class |
| `outputs/harvest/**` | harvest production |

---

## Operational Exclusions

| 项 | 原因 |
|----|------|
| PDF downloads / OCR outputs | not in scope |
| DB / MinIO / RAG artifacts | not in scope |
| verified / production_ready labels | prohibited |
| bare `PASS` gate wording | use `PASS_WITH_CAVEAT` only |

---

## Summary

| Category | Approx count | Commit? |
|----------|--------------|---------|
| bulk raw_metadata（main） | **200** | **no** |
| bulk raw_metadata（retry） | **7** | **no** |
| explicit-path boundary package | **~47** | **yes**（after separate approval） |
