# CNINFO B 类 Era D Next-Scale Slice1 Do-Not-Commit List

_生成时间：2026-07-10_

> **性质：** commit boundary exclusion list · **CNINFO = 0** · **no commit in this task**

---

## Bulk Live Output（default exclude）

| 路径模式 | 约计 | 原因 |
|----------|------|------|
| `outputs/validation/cninfo_b_class_erad_next_scale_slice1/raw_metadata/**` | **~300** | per-case JSON sidecars · regeneratable · local-first |
| `outputs/validation/cninfo_b_class_erad_next_scale_slice1/quality/**` | **~300** | per-case quality JSON · regeneratable · bulk |

**Policy:** retain locally for audit; do **not** include in explicit-path commit unless project policy changes（follow scale-200 `e738fa9` precedent）.

---

## Scale-200 Bulk（already excluded · do not re-include）

| 路径模式 | 约计 | 原因 |
|----------|------|------|
| `outputs/validation/cninfo_b_class_erad_scale_200/raw_metadata/**` | **200** | committed in `e738fa9` boundary as excluded |
| `outputs/validation/cninfo_b_class_erad_scale_200/quality/**` | **200** | same |

---

## Test / Temp Trees

| 路径模式 | 原因 |
|----------|------|
| `outputs/validation/cninfo_b_class_erad_next_scale_slice1/_mock_test/**` | isolated test temp |
| `outputs/validation/cninfo_b_class_erad_next_scale_slice1/_mock_live_test/**` | isolated live-path mock temp |
| `**/__pycache__/**` | Python cache |
| `/tmp/**` | local temp |

---

## Phase 3 Production Roots（out of scope · do not touch）

| 路径模式 | 原因 |
|----------|------|
| `outputs/validation/cninfo_b_class_phase3_100_expansion/**` | Phase 3 production |
| `outputs/validation/cninfo_b_class_phase3_100_failed_retry/**` | Phase 3 failed-retry |
| `outputs/validation/cninfo_b_class_phase3_100_retry_v2/**` | Phase 3 retry_v2 |
| `outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck/**` | EP002 precheck |

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
| commit `e738fa9` | scale-200 explicit-path · do not amend |
| commits `5f29ae6` · `cb6ffcb` · `f3f6077` · `5b8498d` | explicit no-amend per project policy |

---

## Unrelated Dirty Working Tree

Any path **not** listed in [safe-to-commit list](cninfo_b_class_erad_next_scale_slice1_safe_to_commit_list.md) should be **excluded** from slice1 explicit-path commit unless human expands scope in a separate decision.
