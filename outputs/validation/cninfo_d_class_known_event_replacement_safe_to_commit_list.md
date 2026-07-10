# CNINFO D 类 Known Event Replacement — Safe-to-Commit List

_生成时间：2026-07-10_

> **性质：** commit 准备清单 only · **本任务不执行 git commit** · 需单独人工批准

完整清单见 [final artifact inventory](cninfo_d_class_known_event_replacement_final_artifact_inventory.csv)（**58** 条 · 全部 `should_commit = yes`）。

---

## 1. Source Code

| 路径 | 说明 |
|------|------|
| `lab/run_cninfo_d_class_tiny_live_validation.py` | replacement + targeted probe runner 扩展 |
| `lab/validate_cninfo_d_class_known_event_candidates.py` | candidate intake 离线校验 |

---

## 2. Tests

| 路径 | 说明 |
|------|------|
| `lab/test_cninfo_d_class_known_event_candidate_validation.py` | intake tests **10/10** |
| `lab/test_cninfo_d_class_known_event_replacement_runner.py` | replacement runner **20/20** |
| `lab/test_cninfo_d_class_known_event_replacement_live_path.py` | replacement live-path **22/22** |
| `lab/test_cninfo_d_class_known_event_targeted_probe_runner.py` | targeted probe runner **27/27** |
| `lab/test_cninfo_d_class_known_event_targeted_probe_live_path.py` | targeted probe live-path **29/29** |

---

## 3. Plans

`plans/cninfo_d_class_known_event_*` · `plans/cninfo_d_class_dlc003r_*` · `plans/cninfo_d_class_dlc006r_*` — 含 planning、runner design、closure、human decision、boundary review（见 inventory）

---

## 4. Validation Ledgers & Summaries

- replacement / targeted probe universes · approval checklists · ledgers · metrics
- live reports · dry-run reports · quality reports · live_snapshots（JSON metadata only）
- final effective status · caveat ledger · artifact inventory

---

## 5. Status Docs

| 路径 | 说明 |
|------|------|
| `CURRENT_STATUS.md` | D-class known-event replacement 全轨道状态 |
| `PROJECT_MAP.md` | artifact 导航 |
| `plans/eraC_execution_plan.md` | §7dzaa–§7dzaf + boundary |

---

## 6. Explicitly Excluded

| 类别 | 状态 |
|------|------|
| PDF 文件 | **不包含** |
| DB 文件 | **不包含** |
| MinIO artifacts | **不包含** |
| RAG artifacts | **不包含** |
| raw downloaded files | **不包含** |
| unstaged unrelated A-class artifacts | **不包含**（如 `cninfo_a_class_phase2_*` retry_v2/v3/reachability） |
| unstaged unrelated B-class artifacts | **不包含**（如 `cninfo_b_class_phase3_100_*`） |
| unstaged unrelated C-class artifacts | **不包含**（如 `cninfo_c_class_phase35_*` harvest） |
| verified / production_ready flags | **未标记** |

---

## 7. Commit Scope Recommendation

建议 **单独 commit** 或 **小批次 commit** 仅含本 inventory 中 `artifact_group` 为：

- `source_code` · `test` · `planning` · `candidate_intake` · `replacement_*` · `targeted_probe_*` · `failure_review` · `human_decision` · `final_closure` · `boundary_review` · `status`

**不** 与无关 A/B/C 工作区变更混 commit。

---

## 8. Gate

```text
d_class_known_event_replacement_boundary_review_gate = READY_FOR_COMMIT_REVIEW
d_class_known_event_replacement_final_closure_gate = PASS_WITH_CAVEAT
```

**commit 仍需单独人工批准** · **本任务不 commit**
