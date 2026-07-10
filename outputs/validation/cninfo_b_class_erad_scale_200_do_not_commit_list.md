# CNINFO B 类 Era D ~200 Do-Not-Commit List

_生成时间：2026-07-10_

> **性质：** commit boundary exclusion list · **CNINFO 0** · **no commit in this task**

---

## Bulk Live Output（default exclude）

| 路径模式 | 约计 | 原因 |
|----------|------|------|
| `outputs/validation/cninfo_b_class_erad_scale_200/raw_metadata/**` | **200** | per-case JSON sidecars · regeneratable from approved live rerun · local-first |
| `outputs/validation/cninfo_b_class_erad_scale_200/quality/**` | **200** | per-case quality JSON · regeneratable · bulk |

**Policy:** retain locally for audit; do **not** include in explicit-path commit unless project policy changes.

---

## Test / Temp Trees

| 路径模式 | 原因 |
|----------|------|
| `outputs/validation/cninfo_b_class_erad_scale_200/_mock_test/**` | isolated runner test temp |
| `outputs/validation/cninfo_b_class_erad_scale_200/_mock_live_test/**` | isolated live-path mock temp |
| `**/__pycache__/**` | Python cache |
| `/tmp/**` | local temp |

---

## Phase 3 Production Roots（out of scope · do not touch）

| 路径模式 | 原因 |
|----------|------|
| `outputs/validation/cninfo_b_class_phase3_100_expansion/**` | Phase 3 production · already on `origin/main` |
| `outputs/validation/cninfo_b_class_phase3_100_failed_retry/**` | Phase 3 failed-retry production |
| `outputs/validation/cninfo_b_class_phase3_100_retry_v2/**` | Phase 3 retry_v2 production |
| `outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck/**` | EP002 precheck production |

---

## Other B-Class / A/C/D Tracks（unrelated）

| 路径模式 | 原因 |
|----------|------|
| `outputs/validation/cninfo_b_class_phase1_**` | unrelated |
| `outputs/validation/cninfo_b_class_phase2_**` | unrelated |
| `outputs/validation/cninfo_b_class_phase25_**` | unrelated |
| `outputs/validation/cninfo_a_class_**` | unrelated A-class |
| `outputs/validation/cninfo_c_class_**` | unrelated C-class |
| `outputs/validation/cninfo_d_class_**` | unrelated D-class |
| `outputs/harvest/**` | harvest outputs |

---

## Secrets / Binary Artifacts

| 类别 | 原因 |
|------|------|
| `.env` · `*.pem` · `credentials*` · API keys | secrets |
| `**/*.pdf` | no PDF download in Era D track |
| `**/minio/**` | no MinIO |
| `**/rag/**` | no RAG |

---

## Git History（do not amend）

| 项 | 原因 |
|----|------|
| commits `5f29ae6` · `cb6ffcb` · `f3f6077` · `5b8498d` | explicit no-amend per project policy |

---

## Unrelated Dirty Working Tree

Any path **not** listed in [safe-to-commit list](cninfo_b_class_erad_scale_200_safe_to_commit_list.md) should be **excluded** from an Era D explicit-path commit unless human expands scope in a separate decision.
