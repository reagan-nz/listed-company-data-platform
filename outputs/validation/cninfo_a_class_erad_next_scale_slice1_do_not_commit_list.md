# CNINFO A 类 Era D Next-Scale Slice1 Do-Not-Commit List

_生成时间：2026-07-13_  
_共享文件核对：2026-07-13（OPTION 1）_

> **性质：** commit boundary exclusion list · **CNINFO = 0** · **no stage/commit in this task**  
> **禁止：** `git add .` / `git add -A`

---

## Mixed shared files（excluded from whole-file A commit）

| 路径 | 原因 |
|------|------|
| `CURRENT_STATUS.md` | mixed A/B/C/D hunks · do **not** whole-file stage |
| `PROJECT_MAP.md` | mixed hunks · do **not** whole-file stage |
| `plans/eraD_execution_plan.md` | mixed §9.x tracks · do **not** whole-file stage |
| `PROJECT_CONTROL.md` | Controller-owned · Executor must not mutate · not A data commit |

Unless a **future human-approved hunk-level plan** exists, treat the above as do-not-commit for this A slice1 package.  
A authoritative state remains in slice1 validation / merge / boundary artifacts.

---

## Bulk Live Output（default exclude · scale-200 / B slice1 precedent）

| 路径模式 | 约计 | 原因 |
|----------|------|------|
| `outputs/validation/cninfo_a_class_erad_next_scale_slice1/raw_metadata/**` | **300** | per-case JSON sidecars · regeneratable · local-first |

**Policy:** retain locally for audit; do **not** include in explicit-path commit.

---

## Test / Temp Trees

| 路径模式 | 原因 |
|----------|------|
| `outputs/validation/cninfo_a_class_erad_next_scale_slice1/_mock_live_test/**` | live-path mock temp |
| `**/__pycache__/**` | Python cache |
| `**/.DS_Store` | macOS noise |
| `/tmp/**` | local temp |

---

## Historical A Production Roots（do not rewrite / do not re-include bulk）

| 路径模式 | 原因 |
|----------|------|
| `outputs/validation/cninfo_a_class_erad_scale_200/` production root bulk | scale-200 lineage（`41dc049`）· do not rewrite historical |
| `outputs/validation/cninfo_a_class_erad_scale_200/raw_metadata/**` | bulk · already excluded by scale-200 boundary |
| `outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/raw_metadata/**` | bulk |
| `outputs/validation/cninfo_a_class_erad_scale_200/_production_guard/**` | local guard |
| `outputs/validation/cninfo_a_class_phase3_50_company_expansion/**` | Phase 3 production |
| `outputs/validation/cninfo_a_class_phase3_a3m017_isolated_retry/**` | A3M017 production |

---

## Other Tracks（unrelated · do not touch）

| 路径模式 | 原因 |
|----------|------|
| `outputs/validation/cninfo_b_class_**` | B-class |
| `outputs/validation/cninfo_c_class_**` | C-class |
| `outputs/validation/cninfo_d_class_**` | D-class |
| `outputs/harvest/**` | harvest |
| B/C/D lab runners / tests not listed in safe list | out of scope |

---

## Secrets / Binary / Storage

| 类别 | 原因 |
|------|------|
| `.env` · `*.pem` · `credentials*` | secrets |
| `**/*.pdf` · OCR outputs | no PDF/OCR in this package |
| DB / MinIO / RAG / vector stores | out of scope |

---

## Git History（do not amend）

| 项 | 原因 |
|----|------|
| commit `41dc049` | A scale-200 explicit-path · do not amend |
| commits `bbc15c3` · `cad5ed1` · `01617c6` | historical A · do not amend |
| commit `350cdda` | B slice1 · unrelated · do not touch |

---

## Unrelated Dirty Working Tree

Any path **not** listed in [safe-to-commit list](cninfo_a_class_erad_next_scale_slice1_safe_to_commit_list.md) / [file list](cninfo_a_class_erad_next_scale_slice1_commit_boundary_file_list.txt) should be **excluded** from slice1 explicit-path commit unless human expands scope in a separate decision.
