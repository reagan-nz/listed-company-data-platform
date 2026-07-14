# CNINFO B 类 Era D Fuller Next-Slice2 Do-Not-Commit List

_生成时间：2026-07-13_  
_共享文件核对：2026-07-13_

> **性质：** commit boundary exclusion list · **CNINFO = 0** · **no stage/commit in this task**  
> **禁止：** `git add .` / `git add -A`

---

## Mixed shared files（excluded from whole-file B commit）

| 路径 | 原因 |
|------|------|
| `CURRENT_STATUS.md` | mixed A/B/C/D hunks · do **not** whole-file stage |
| `PROJECT_MAP.md` | mixed hunks · count wording fixed in WT but **excluded** from B boundary |
| `plans/eraD_execution_plan.md` | mixed §9.x tracks · do **not** whole-file stage |
| `PROJECT_CONTROL.md` | Controller / Evidence Auditor workflow control · not B data commit |

Unless a **future human-approved hunk-level plan** exists, treat the above as do-not-commit for this B slice2 package.

---

## Bulk Live Output

| 路径模式 | 约计 | 原因 |
|----------|------|------|
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2/raw_metadata/**` | **~300** | sidecars · local-first |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2/quality/**` | **~300** | quality JSON · bulk |

---

## Test / Temp Trees

| 路径模式 | 原因 |
|----------|------|
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2/_mock_test/**` | test temp |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2/_mock_live_test/**` | live-path mock temp |
| `**/__pycache__/**` | cache |
| `**/.DS_Store` | macOS noise |
| `/tmp/**` | temp |

---

## Other B-Class Roots

| 路径模式 | 原因 |
|----------|------|
| `outputs/validation/cninfo_b_class_erad_scale_200/**` | scale-200 · separate lineage（`e738fa9`） |
| `outputs/validation/cninfo_b_class_erad_next_scale_slice1/**` | slice1 · separate lineage（`350cdda`） |
| `outputs/validation/cninfo_b_class_phase3_**` | Phase 3 |
| `outputs/validation/cninfo_b_class_phase1_**` / `phase2_**` / `phase25_**` | unrelated historical B |

---

## A / C / D / Harvest / Portrait

| 路径模式 | 原因 |
|----------|------|
| `outputs/validation/cninfo_a_class_**` | unrelated A |
| `outputs/validation/cninfo_c_class_**` | unrelated C |
| `outputs/validation/cninfo_d_class_**` | unrelated D |
| `outputs/harvest/**` | harvest |
| portrait / ontology unrelated paths | out of scope |

---

## Secrets / Binary / Storage

| 类别 | 原因 |
|------|------|
| `.env` · `*.pem` · `credentials*` | secrets |
| `**/*.pdf` · OCR outputs | no PDF/OCR in this track |
| DB / MinIO / RAG / vector stores | out of scope |

---

## Git History

| 项 | 原因 |
|----|------|
| amend `e738fa9` / `350cdda` | forbidden |

---

## Working-Tree Safety

- B slice2 whole-file package = **36** explicit paths only
- Mixed shared files above must stay **unstaged** for this commit
- Branch divergence（ahead 11 / behind 4 local refs）is a **separate** sync decision — not part of this boundary
